import sys
import os
import json

# Adiciona a pasta src ao caminho de execução para importar seus módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Importa a função real do seu arquivo
from processors.validador_esus import interpretar_resposta_cadsus


def rodar_teste_mock_sucesso():
    print("==================================================")
    print(" 🧪 TESTE UNITÁRIO: VALIDADOR DE EXCEÇÕES E-SUS   ")
    print("==================================================")

    # 1. Preparação (Arrange): O payload exato que você capturou no F12
    payload_sucesso_mock = [{
        "data": {
            "buscaCidadaosCadsusCompletoPolling": {
                "usuario": "758",
                "uuid": "562a946e-2a9c-477c-9b70-b209f688ed7a",
                "resultCadsus": "SUCESSO",
                "cidadaos": [{
                    "cpf": "54435217805",
                    "cns": "704809512150948",
                    "nome": "CESAR AUGUSTO NOGUEIRA DOS SANTOS MARTINS",
                    "dataNascimento": "2005-02-22",
                    "sexo": "MASCULINO",
                    "obito": "false"
                }]
            }
        }
    }]

    # 2. Ação (Act): Passa o mock para a sua função oficial
    resultado = interpretar_resposta_cadsus(payload_sucesso_mock)

    # 3. Verificação (Assert visual no terminal)
    print(f"Resultado processado pelo Pydantic:\n{json.dumps(resultado, indent=2, ensure_ascii=False)}")
    
    if resultado.get("status") == "SUCESSO":
        print("\n✅ TESTE PASSOU: O modelo converteu a resposta limpa corretamente!")
    else:
        print("\n❌ TESTE FALHOU: O processador não entendeu a estrutura do Mock.")

if __name__ == "__main__":
    rodar_teste_mock_sucesso()