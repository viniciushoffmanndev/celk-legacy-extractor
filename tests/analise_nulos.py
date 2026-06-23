import json
import os

def analisar_campos_nulos():
    caminho_entrada = os.path.join("data", "raw", "pacientes_celk.json")

    print("==================================================")
    print(" ANÁLISE QUANTITATIVA DE CAMPOS NULOS (NULL)      ")
    print("==================================================")

    try:
        with open(caminho_entrada, "r", encoding="utf-8") as f:
            pacientes = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo não encontrado em: {caminho_entrada}")
        return

    total_registros = len(pacientes)
    if total_registros == 0:
        print("O arquivo JSON está vazio.")
        return

    # Dicionário para armazenar a contagem
    contagem_nulos = {}

    # Inicializa as chaves baseando-se no primeiro registro
    for chave in pacientes[0].keys():
        contagem_nulos[chave] = 0

    # Varre todos os pacientes e conta os 'null' (que no Python viram 'None')
    for p in pacientes:
        for chave, valor in p.items():
            if valor is None:
                contagem_nulos[chave] = contagem_nulos.get(chave, 0) + 1

    print(f"Total de Pacientes Analisados: {total_registros}\n")

    # Ordena para mostrar os campos com MAIS nulos primeiro
    campos_ordenados = sorted(contagem_nulos.items(), key=lambda item: item[1], reverse=True)

    for chave, nulos in campos_ordenados:
        percentual = (nulos / total_registros) * 100
        # Formatação condicional visual
        alerta = "CRÍTICO" if percentual > 50 else "ATENÇÃO" if percentual > 10 else "OK"
        
        print(f"[{alerta}] Campo '{chave}': {nulos} valores nulos ({percentual:.2f}%)")
        
    print("==================================================")

if __name__ == "__main__":
    analisar_campos_nulos()