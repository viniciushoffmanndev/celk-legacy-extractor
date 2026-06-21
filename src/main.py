import asyncio
import sys
import time
from extractors.pacientes import extrair_pacientes

async def main():
    print("==================================================")
    print("         INICIANDO PIPELINE DE EXTRAÇÃO CELK      ")
    print("==================================================")
    
    # Registra o tempo de início para sabermos quanto tempo levou a extração total
    tempo_inicio = time.time()
    
    # Executa a extração total mapeando em lotes (padrão: 1000 por lote)
    # Você pode passar um valor menor aqui se quiser testar, ex: extrair_pacientes(tamanho_lote=500)
    pacientes = await extrair_pacientes(tamanho_lote=1000)
    
    tempo_total = time.time() - tempo_inicio
    
    print("==================================================")
    print("               RESUMO DA OPERAÇÃO                 ")
    print("==================================================")
    print("Processo concluído com sucesso!")
    print(f"Total de pacientes higienizados: {len(pacientes)}")
    print(f"Tempo total de execução: {tempo_total:.2f} segundos")
    print("==================================================")

if __name__ == "__main__":
    # Garante o funcionamento correto do loop de eventos assíncronos no Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())