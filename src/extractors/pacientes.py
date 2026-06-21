import json
import os
from database.connection import get_connection
from schemas.paciente import PacienteSchema
from pydantic import ValidationError

async def extrair_pacientes(limite: int = 10):
    """
    Conecta no banco legado, extrai um lote de pacientes válidos (não unificados),
    valida com Pydantic e salva o resultado higienizado em um arquivo JSON local.
    """
    print(f"Iniciando extração de {limite} pacientes válidos do sistema CELK...")
    
    conn = await get_connection()
    pacientes_processados = []

    try:
        async with conn.cursor() as cursor:
            # Query atualizada com filtros estratégicos baseados na nossa investigação
            query = """
                SELECT 
                    cd_usu_cadsus, nm_usuario, sg_sexo, 
                    dt_nascimento, cpf, rg, celular, st_vivo 
                FROM usuario_cadsus 
                WHERE flag_unificado = 0                -- Garante que só traremos cadastros "Mestres"
                  AND (cpf IS NULL OR cpf <> '00000000000') -- Descarta a máscara falsa de CPFs zerados
                LIMIT %s;
            """
            await cursor.execute(query, (limite,))
            registros_brutos = await cursor.fetchall()
            
            print(f"Foram encontrados {len(registros_brutos)} registros válidos no banco. Iniciando limpeza...\n")

            for linha in registros_brutos:
                try:
                    paciente_limpo = PacienteSchema.model_validate(linha)
                    pacientes_processados.append(paciente_limpo)
                    print(f"{paciente_limpo.nome} [Higienizado]")
                    
                except ValidationError as e:
                    print(f"ALERTA: Dados inválidos no ID legado {linha.get('cd_usu_cadsus')}")
                    print(f"Detalhes do erro: {e.errors()}\n")
                    
        # --- SALVANDO O CHECKPOINT EM JSON ---
        if pacientes_processados:
            dados_serializados = [p.model_dump(mode='json') for p in pacientes_processados]
            caminho_arquivo = os.path.join("data", "raw", "pacientes_limpos.json")
            
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo_json:
                json.dump(dados_serializados, arquivo_json, indent=4, ensure_ascii=False)
                
            print(f"\nCheckpoint de segurança atualizado em: {caminho_arquivo}")
            
    except Exception as e:
        print(f"Erro fatal na extração: {e}")
        
    finally:
        await conn.close()
        print("Conexão encerrada.")
        
    return pacientes_processados