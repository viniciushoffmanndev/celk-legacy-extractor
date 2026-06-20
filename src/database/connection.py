import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Carrega as variáveis protegidas do arquivo .env
load_dotenv()

async def get_connection():
    """
    Estabelece e retorna a conexão assíncrona com o PostgreSQL.
    O 'dict_row' para que as linhas do banco voltem como dicionários Python, ideal para alta concorrência com FastAPI
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("ERRO: A variável DATABASE_URL não foi encontrada no arquivo .env")
    
    try:
        conn = await psycopg.AsyncConnection.connect(
            conninfo=database_url,
            row_factory=dict_row
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar no banco de dados: {e}")
        raise