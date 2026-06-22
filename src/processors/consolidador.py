import json
import os

def consolidar_pacientes():
    """
    Lê o JSON sujo com duplicatas, agrupa os pacientes pelo CPF e faz um 'merge' cirúrgico
    para não perder NENHUMA informação valiosa (RG, celular) dos cadastros velhos.
    """
    caminho_entrada = os.path.join("data", "raw", "pacientes_limpos.json")
    caminho_saida = os.path.join("data", "raw", "pacientes_consolidados.json")

    print("==================================================")
    print("       INICIANDO A BATEDEIRA DE DADOS (MERGE)     ")
    print("==================================================")

    # 1. Carrega os 93.666 registros extraídos
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        pacientes_brutos = json.load(f)

    # Dicionário que vai guardar a nossa lista final
    # A chave será o CPF. Se não tiver CPF, a chave será "SEM_CPF_<id>"
    pacientes_fundidos = {}

    # Estatísticas de auditoria
    stats = {
        "celulares_recuperados": 0,
        "rgs_recuperados": 0,
        "clones_derretidos": 0
    }

    for p in pacientes_brutos:
        # Define a chave de fusão com a Regra de Ouro
        chave = p['cpf'] if p['cpf'] else f"SEM_CPF_{p['id_legado']}"

        if chave not in pacientes_fundidos:
            # É a primeira vez que vemos esse CPF. Cadastra como Mestre.
            pacientes_fundidos[chave] = p
        else:
            # ACHAMOS UM CLONE! Hora da Mágica do Merge.
            stats["clones_derretidos"] += 1
            mestre = pacientes_fundidos[chave]

            # Se o Mestre não tem RG, mas o Clone tem... pega o RG do clone!
            if not mestre['rg'] and p['rg']:
                mestre['rg'] = p['rg']
                stats["rgs_recuperados"] += 1

            # Se o Mestre não tem Celular, mas o Clone tem... pega o celular!
            if not mestre['celular'] and p['celular']:
                mestre['celular'] = p['celular']
                stats["celulares_recuperados"] += 1
            
            # Se o clone tiver um nome mais longo/completo, substituímos
            if len(p['nome']) > len(mestre['nome']):
                mestre['nome'] = p['nome']

    # Transforma o dicionário de volta numa lista simples
    resultado_final = list(pacientes_fundidos.values())

    # 2. Salva o novo arquivo Dourado
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print(f"Total de Registros Iniciais: {len(pacientes_brutos)}")
    print(f"Total de Pacientes Únicos Reais: {len(resultado_final)}")
    print(f"Clones Removidos (Mergeados): {stats['clones_derretidos']}")
    print(f"Celulares Salvos: {stats['celulares_recuperados']}")
    print(f"RGs Salvos: {stats['rgs_recuperados']}")
    print(f"\nArquivo consolidado salvo em: {caminho_saida}")
    print("==================================================")

if __name__ == "__main__":
    consolidar_pacientes()