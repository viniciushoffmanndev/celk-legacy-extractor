import asyncio
import sys
from database.connection import get_connection

async def testar_banco():
    print("Iniciando teste de conexão com banco na Neon...")

    conn = None
    try:
        # Chamando a função assíncrona
        conn = await get_connection()
        print("conexão assíncrona realizada no banco!")

        # Query para exibir algo na tela para provar que está puxando uma tabela no banco
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT current_database(), current_date;")
            resultado = await cursor.fetchone()
            print(f"Detalhes da conexão: {resultado}")

    except Exception as e:
        print(f"Falha no teste: {e}")
    
    finally:
        # garante que a porta será fechada, mesmo se der erro
        if conn:
            await conn.close()
            print("Conexão encerrada com segurança")

if __name__ == "__main__":

    # Se o sistema operacional for windows, troca o motor do asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Inicia o loop assíncrono do Python
    asyncio.run(testar_banco())