from database.connection import get_connection
from schemas.paciente import PacienteSchema
from pydantic import ValidationError

async def extrair_pacientes(limite: int = 10):
    """
    Conecta no banco legado, extrai um lote de pacientes e os valida
    usando o Pydantic para garantir a qualidade dos dados.
    """
    print(f"Iniciando extração de {limite} pacientes do sistema CELK...")
    
    # Chama o motor de conexão
    conn = await get_connection()
    pacientes_processados = []

    try:
        async with conn.cursor() as cursor:
            # Query apenas com as colunas que precisamos
            query = """
                SELECT 
                    cd_usu_cadsus, nm_usuario, sg_sexo, 
                    dt_nascimento, cpf, rg, celular, st_vivo 
                FROM usuario_cadsus 
                LIMIT %s;
            """
            
            # Executa passando o limite de forma segura contra SQL Injection
            await cursor.execute(query, (limite,))
            registros_brutos = await cursor.fetchall()
            
            print(f"Foram encontrados {len(registros_brutos)} registros no banco. Iniciando limpeza...\n")

            # Passa cada registro pelo Pydantic
            for linha in registros_brutos:
                try:
                    # model_validate é a função do Pydantic V2 que lê o dicionário e aplica as regras
                    paciente_limpo = PacienteSchema.model_validate(linha)
                    pacientes_processados.append(paciente_limpo)
                    
                    print(f"{paciente_limpo.nome}")
                    print(f"CPF Limpo: {paciente_limpo.cpf}")
                    print(f"Novo UUID: {paciente_limpo.id_novo}")
                    print(f"Vivo: {paciente_limpo.vivo}\n")
                    
                except ValidationError as e:
                    # Se um paciente for TÃO sujo que quebre as regras, nós logamos o erro,
                    # mas não paramos o sistema inteiro! O loop continua para o próximo.
                    print(f"ALERTA: Dados inválidos no ID legado {linha.get('cd_usu_cadsus')}")
                    print(f"Detalhes do erro: {e.errors()}\n")
                    
    except Exception as e:
        print(f"Erro fatal na extração: {e}")
        
    finally:
        await conn.close()
        print("Conexão encerrada.")
        
    return pacientes_processados