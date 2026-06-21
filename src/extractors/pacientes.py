import json
import os
from database.connection import get_connection
from schemas.paciente import PacienteSchema
from pydantic import ValidationError

async def extrair_pacientes(tamanho_lote: int = 1000):
    """
    Extrai todos os pacientes válidos do sistema legado usando paginação (batching).
    Garante baixo consumo de memória e alta performance.
    """
    print(f"Iniciando extração total em lotes de {tamanho_lote}...")
    
    conn = await get_connection()
    pacientes_processados = []
    offset = 0
    lote_atual = 1

    try:
        async with conn.cursor() as cursor:
            while True:
                # O OFFSET é quem faz a "paginação", pulando os registros já processados
                query = """
                    SELECT 
                        cd_usu_cadsus, nm_usuario, sg_sexo, 
                        dt_nascimento, cpf, rg, celular, st_vivo 
                    FROM usuario_cadsus 
                    WHERE flag_unificado = 0 
                      AND (cpf IS NULL OR cpf <> '00000000000')
                    ORDER BY cd_usu_cadsus  -- O ORDER BY é obrigatório na paginação!
                    LIMIT %s OFFSET %s;
                """
                
                print(f"Buscando Lote {lote_atual} (Pulando {offset} registros)...")
                await cursor.execute(query, (tamanho_lote, offset))
                registros_brutos = await cursor.fetchall()
                
                # Se não veio nenhum registro, significa que chegamos ao fim da tabela!
                if not registros_brutos:
                    print("Fim da tabela alcançado. Todos os pacientes foram extraídos!")
                    break
                
                for linha in registros_brutos:
                    try:
                        paciente_limpo = PacienteSchema.model_validate(linha)
                        pacientes_processados.append(paciente_limpo)
                    except ValidationError as e:
                        print(f"Erro no ID {linha.get('cd_usu_cadsus')}: CPF inválido ou dado corrompido. Motivo: {e}")
                
                # Prepara para a próxima página
                offset += tamanho_lote
                lote_atual += 1
                
        # --- SALVANDO O CHECKPOINT FINAL EM JSON ---
        if pacientes_processados:
            dados_serializados = [p.model_dump(mode='json') for p in pacientes_processados]
            caminho_arquivo = os.path.join("data", "raw", "pacientes_limpos.json")
            
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo_json:
                json.dump(dados_serializados, arquivo_json, indent=4, ensure_ascii=False)
                
            print(f"\nExtração concluída! {len(pacientes_processados)} pacientes salvos com sucesso em: {caminho_arquivo}")
            
    except Exception as e:
        print(f"Erro fatal na extração: {e}")
        
    finally:
        await conn.close()
        print("Conexão encerrada.")
        
    return pacientes_processados