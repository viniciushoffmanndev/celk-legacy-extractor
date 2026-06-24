import json
import os
import re

def normalizar_texto(texto):
    """Remove espaços extras e padroniza para maiúsculo"""
    if not texto:
        return ""
    return re.sub(r'\s+', ' ', str(texto).strip().upper())

def limpar_rg(rg):
    """Remove pontos, traços e espaços do RG para não dar falso negativo no Merge"""
    if not rg:
        return None
    return re.sub(r'[^a-zA-Z0-9]', '', str(rg)).upper()

def consolidar_pacientes():
    caminho_entrada = os.path.join("data", "raw", "pacientes_celk.json")
    caminho_saida = os.path.join("data", "raw", "pacientes_consolidados.json")

    print("==================================================")
    print("INICIANDO CONSOLIDAÇÃO E DESDUPLICAÇÃO (MULTI-KEY)")
    print("==================================================")

    try:
        with open(caminho_entrada, "r", encoding="utf-8") as f:
            pacientes_brutos = json.load(f)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {caminho_entrada}")
        return

    # Lista final que vai guardar apenas os "Mestres"
    pacientes_mestre = []

    # Dicionários de busca rápida (A Peneira de 4 Camadas)
    mapa_cpf = {}
    mapa_cns = {}
    mapa_rg = {}
    mapa_nome_data = {}

    stats = {
        "celulares_recuperados": 0,
        "rgs_recuperados": 0,
        "cns_recuperados": 0,
        "cpfs_recuperados": 0,
        "clones_derretidos": 0
    }

    for p in pacientes_brutos:
        cpf = p.get('cpf')
        cns = p.get('cns')
        rg_limpo = limpar_rg(p.get('rg'))
        
        nome_limpo = normalizar_texto(p.get('nome', ''))
        data_nasc = p.get('data_nascimento', '')
        chave_nome_data = f"{nome_limpo}_{data_nasc}"

        # ==================================================
        # 1. TENTA ACHAR O MESTRE NOS ÍNDICES (A ORDEM IMPORTA)
        # ==================================================
        mestre = None
        if cpf and cpf in mapa_cpf:
            mestre = mapa_cpf[cpf]
        elif cns and cns in mapa_cns:
            mestre = mapa_cns[cns]
        elif rg_limpo and rg_limpo in mapa_rg:
            mestre = mapa_rg[rg_limpo]
        elif chave_nome_data in mapa_nome_data:
            mestre = mapa_nome_data[chave_nome_data]

        # ==================================================
        # 2. SE NÃO ACHOU, É NOVO. SE ACHOU, FAZ O MERGE!
        # ==================================================
        if mestre is None:
            # Novo paciente, adiciona na lista de mestres
            mestre = p.copy()
            pacientes_mestre.append(mestre)
        else:
            # Achamos um Clone! Derrete os dados novos para dentro do mestre
            stats["clones_derretidos"] += 1
            
            if not mestre.get('cns') and p.get('cns'):
                mestre['cns'] = p['cns']
                stats["cns_recuperados"] += 1
            
            if not mestre.get('cpf') and p.get('cpf'):
                mestre['cpf'] = p['cpf']
                stats["cpfs_recuperados"] += 1

            if not mestre.get('rg') and p.get('rg'):
                mestre['rg'] = p['rg']
                stats["rgs_recuperados"] += 1
                
            if not mestre.get('celular') and p.get('celular'):
                mestre['celular'] = p['celular']
                stats["celulares_recuperados"] += 1
                
            # Mantém o nome mais bem escrito/completo
            if len(p.get('nome', '')) > len(mestre.get('nome', '')):
                mestre['nome'] = p['nome']

        # ==================================================
        # 3. ATUALIZA TODOS OS ÍNDICES COM O MESTRE ATUALIZADO
        # ==================================================
        if mestre.get('cpf'): 
            mapa_cpf[mestre['cpf']] = mestre
        if mestre.get('cns'): 
            mapa_cns[mestre['cns']] = mestre
        if mestre.get('rg'): 
            mapa_rg[limpar_rg(mestre['rg'])] = mestre
            
        m_nome = normalizar_texto(mestre.get('nome', ''))
        m_data = mestre.get('data_nascimento', '')
        mapa_nome_data[f"{m_nome}_{m_data}"] = mestre

    # 4. Salva o novo arquivo Dourado
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(pacientes_mestre, f, indent=4, ensure_ascii=False)

    print(f"Total de Registros Brutos (CELK): {len(pacientes_brutos)}")
    print(f"Total de Pacientes Únicos Reais: {len(pacientes_mestre)}")
    print(f"Clones Removidos (Mergeados): {stats['clones_derretidos']}")
    print(f"CPFs Salvos na Fusão: {stats['cpfs_recuperados']}")
    print(f"CNS Salvos na Fusão: {stats['cns_recuperados']}")
    print(f"RGs Salvos na Fusão: {stats['rgs_recuperados']}")
    print(f"Celulares Salvos na Fusão: {stats['celulares_recuperados']}")
    print(f"\nArquivo consolidado salvo em: {caminho_saida}")
    print("==================================================")

if __name__ == "__main__":
    consolidar_pacientes()