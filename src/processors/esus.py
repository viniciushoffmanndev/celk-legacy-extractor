import json
import time
import re
import requests
import os
import uuid
import random

# Importa da mesma pasta (processors)
from validador_esus import interpretar_resposta_cadsus

def executar_etl_cadsus():
    print("==================================================")
    print("    NIS PARAGUAÇU - MOTOR ETL E-SUS (PRODUÇÃO)    ")
    print("==================================================")

    # SEU COOKIE ATIVO (Lembre-se de renovar se for rodar lote muito grande!)
    COOKIE = "JSESSIONID=e8Ja4fLvgioEex_0kb74ZeBpkIFg914165tPvv5J; XSRF-TOKEN=c5d02899-4345-4f70-8011-b84e876e3d10"
    xsrf_match = re.search(r'XSRF-TOKEN=([^;]+)', COOKIE)
    xsrf_token = xsrf_match.group(1) if xsrf_match else ""

    headers = {
        "Host": "esus.eparaguacu.sp.gov.br",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "X-XSRF-TOKEN": xsrf_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Cookie": COOKIE,
        "Origin": "https://esus.eparaguacu.sp.gov.br",
        "apollographql-client-name": "PEC Web",
        "apollographql-client-version": "5.4.38"
    }

    url_graphql = "https://esus.eparaguacu.sp.gov.br/api/graphql"

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    caminho_raw = os.path.join(base_dir, "data", "raw", "pacientes_consolidados.json")
    caminho_saida = os.path.join(base_dir, "data", "staging", "pacientes_staging_atualizados.json")
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    if os.path.exists(caminho_saida):
        print("Base Staging encontrada! Retomando de onde paramos...")
        with open(caminho_saida, "r", encoding="utf-8") as f:
            pacientes = json.load(f)
    else:
        print("Primeira execução: Carregando base Raw...")
        with open(caminho_raw, "r", encoding="utf-8") as f:
            pacientes = json.load(f)

    alvos = [p for p in pacientes if not p.get('cpf') and p.get('cns')]
    print(f"Fila de Processamento: {len(alvos)} pacientes pendentes de enriquecimento.\n")

    estatisticas = {"sucessos": 0, "nao_encontrados": 0, "falhas_api": 0}

    # Mantemos o lote de 10 para teste!
    for paciente in alvos[:2]:
        cns = paciente.get('cns', '')
        nome = paciente.get('nome', '')
        data_nasc_us = paciente.get('data_nascimento') or ""
        
        print(f"\nConsultando: {nome} (CNS: {cns})")

        # =====================================================================
        # LISTA DE ESTRATÉGIAS (FALLBACKS)
        # =====================================================================
        combinacoes = []
        if cns:
            combinacoes.append({"desc": "Apenas CNS", "q": cns, "dn": None})
        if cns and data_nasc_us:
            combinacoes.append({"desc": "CNS + Data Nasc", "q": cns, "dn": data_nasc_us})
        if nome and data_nasc_us:
            combinacoes.append({"desc": "Nome + Data Nasc", "q": nome, "dn": data_nasc_us})

        paciente_resolvido = False

        for comb in combinacoes:
            print(f"Tentando por: {comb['desc']}...")
            uuid_sessao = str(uuid.uuid4())

            # --- PASSO A: Abrir Sessão de Busca ---
            payload_busca = [{
                "operationName": "BuscaCidadaoCadsus",
                "variables": {
                    "filter": {
                        "query": {
                            "query": comb["q"], 
                            "dataNascimento": comb["dn"],
                            "nomeMae": None,
                            "pageParams": {}
                        },
                        "uuid": uuid_sessao
                    }
                },
                "query": "query BuscaCidadaoCadsus($filter: BuscaListaCidadaoCadsusInput!) {\n  buscaCidadaosCadsus(filtro: $filter)\n}\n"
            }]

            try:
                resp_busca = requests.post(url_graphql, headers=headers, json=payload_busca, timeout=10)
                dados_busca = resp_busca.json()
                if isinstance(dados_busca, list) and len(dados_busca) > 0 and "errors" in dados_busca[0]:
                    print(f"Rejeitado pelo e-SUS: {dados_busca[0]['errors'][0]['message']}")
                    continue # Tenta a próxima combinação
            except Exception as e:
                print(f"Erro de Rede no Passo A: {e}")
                continue

            time.sleep(random.uniform(4.0, 7.0)) # Aguarda Brasília

            # --- PASSO B: Colher Resultado (Polling) ---
            payload_polling = [{
                "operationName": "BuscaCidadaoCadsusPolling",
                "variables": {"uuid": uuid_sessao},
                "query": "query BuscaCidadaoCadsusPolling($uuid: String!) {\n  buscaCidadaosCadsusCompletoPolling(uuid: $uuid) {\n    usuario\n    uuid\n    resultCadsus\n    cidadaos {\n      cpf\n      cns\n      nome\n      nomeSocial\n      nomeMae\n      nomePai\n      racaCor {\n        id\n        nome\n        racaCorDbEnum\n        __typename\n      }\n      etnia {\n        id\n        nome\n        __typename\n      }\n      telefoneContato\n      telefoneResidencial\n      telefoneCelular\n      dataNascimento\n      dataObito\n      obito\n      sexo\n      email\n      nacionalidade {\n        id\n        nacionalidadeDbEnum\n        __typename\n      }\n      municipioNascimento {\n        id\n        ibge\n        nome\n        uf {\n          id\n          nome\n          sigla\n          __typename\n        }\n        __typename\n      }\n      paisNascimento {\n        id\n        nome\n        __typename\n      }\n      portariaNaturalizacao\n      dataEntradaBrasil\n      dataNaturalizacao\n      endereco {\n        bairro\n        cep\n        complemento\n        logradouro\n        municipio {\n          id\n          ibge\n          nome\n          uf {\n            id\n            nome\n            sigla\n            __typename\n          }\n          __typename\n        }\n        numero\n        pontoReferencia\n        semNumero\n        tipoLogradouro {\n          id\n          nome\n          numeroDne\n          __typename\n        }\n        uf {\n          id\n          nome\n          sigla\n          __typename\n        }\n        __typename\n      }\n      paisResidencia {\n        id\n        nome\n        __typename\n      }\n      municipioResidenciaExterior\n      numeroPisPasep\n      __typename\n    }\n    __typename\n  }\n}"
            }]

            try:
                resp_polling = requests.post(url_graphql, headers=headers, json=payload_polling, timeout=10)
                dados_brutos = resp_polling.json()
                
                # Validação Pydantic
                resultado_etl = interpretar_resposta_cadsus(dados_brutos)
                status = resultado_etl.get("status")
                
                if status == "SUCESSO":
                    dados_limpos = resultado_etl["dados"]
                    cpf_encontrado = dados_limpos.get("cpf")
                    
                    # Injeta TODOS os dados enriquecidos da ficha do Governo no paciente local
                    paciente.update(dados_limpos)
                    
                    if cpf_encontrado:
                        print(f"SUCESSO! Ficha Rica capturada. CPF: {cpf_encontrado}")
                    else:
                        paciente['status_busca'] = "SEM_CPF_NO_GOVERNO"
                        print(f"Cadastro enriquecido, mas o paciente NÃO POSSUI CPF no e-SUS.")
                    
                    estatisticas["sucessos"] += 1
                    paciente_resolvido = True
                    break # Cai fora do loop de combinações, já resolvemos esse!

                elif status == "PACIENTE_NAO_ENCONTRADO":
                    print("Não encontrado com esta combinação.")
                    time.sleep(random.uniform(2.0, 4.0)) # Pausa curta antes de tentar a próxima combinação
                else:
                    print(f"Erro de API: {resultado_etl.get('mensagem')}")

            except Exception as e:
                print(f"Erro executando Polling: {e}")

        # Fim do loop de combinações. Verificamos se o paciente foi resolvido em alguma delas.
        if not paciente_resolvido:
            paciente['status_busca'] = "NAO_ENCONTRADO_NENHUMA_COMBINACAO"
            estatisticas["nao_encontrados"] += 1
            print("Esgotadas todas as opções. Paciente não consta na base nacional.")

        # Pausa longa humanizada antes de pular para o próximo paciente
        time.sleep(random.uniform(5.0, 10.0))

        # Salva o progresso a cada paciente
        with open(caminho_saida, "w", encoding="utf-8") as f:
            json.dump(pacientes, f, ensure_ascii=False, indent=4)

    print("\n==================================================")
    print(f"Fim do Lote! Resolvidos: {estatisticas['sucessos']} | Não Encontrados: {estatisticas['nao_encontrados']}")
    print("==================================================")

if __name__ == "__main__":
    executar_etl_cadsus()