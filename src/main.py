import asyncio
import sys
from extractors.pacientes import extrair_pacientes

async def main():
    print("=== CELK LEGACY EXTRACTOR ===")
    
    # Chama a extração pedindo 5 pacientes para testarmos a limpeza
    pacientes = await extrair_pacientes(limite=5)
    
    print("===================================")
    print(f"Processo concluído! {len(pacientes)} pacientes prontos para o novo banco.")

if __name__ == "__main__":
    # --- CORREÇÃO PARA O WINDOWS ---
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # -------------------------------
    
    asyncio.run(main())