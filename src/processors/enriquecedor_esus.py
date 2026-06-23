import json
import time
import re
import requests
import os

def enriquecedor_cadsus_nis_definitivo():
    print("==================================================")
    print(" 🏆 NIS PARAGUAÇU - ENRIQUECEDOR GRAPHQL OFICIAL  ")
    print("==================================================")

    # 1. COOKIE E TOKENS ATUALIZADOS DO SEU ÚLTIMO PRINT FRESQUINHO
    COOKIE = "JSESSIONID=yfgJEfyO_tDi3OYnBwNarkQZDQhyJ8p6TA4mr0Eg; XSRF-TOKEN=d6505230-cf3b-4e89-80bb-c24e2b6a8a6c"
    
    xsrf_match = re.search(r'XSRF-TOKEN=([^;]+)', COOKIE)
    xsrf_token = xsrf_match.group(1) if xsrf_match else ""

    caminho_json = os.path.join("data", "raw", "pacientes_consolidados.json")
    caminho_saida = os.path.join("data", "raw", "pacientes_teste_web.json")

    with open(caminho_json, "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    alvos = [p for p in pacientes if p.get('cpf') is None and p.get('cns') is not None]
    
    print(f"🎯 Pacientes na fila de processamento: {len(alvos)}")
    print("🚀 Executando lote de testes (5 alvos) com a rota limpa do CADSUS...\n")

    url_graphql = "https://esus.eparaguacu.sp.gov.br/api/graphql"

    # Gêmeo idêntico dos cabeçalhos do seu navegador (Aba Cabeçalhos)
    headers = {
        "Host": "esus.eparaguacu.sp.gov.br",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "X-XSRF-TOKEN": xsrf_token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0",
        "Cookie": COOKIE,
        "Origin": "https://esus.eparaguacu.sp.gov.br",
        "apollographql-client-name": "PEC Web",
        "apollographql-client-version": "5.4.38"
    }

    sucessos = 0
    for paciente in alvos[:5]:
        cns = paciente['cns']
        nome = paciente['nome']
        data_nasc_us = paciente.get('data_nascimento') or ""

        print(f"🔎 Solicitando barramento para: {nome}...")

        uuid_lote = None
        
        # JUNTANDO OS DOIS MUNDOS: Parâmetros inline dentro do formato de Lote do Apollo []
        tentativas_mutation = [
            f'mutation {{ buscaCidadaosCadsus(filtro: {{ nomeCpfCns: "{cns}", dataNascimento: "{data_nasc_us}" }}) }}',
            f'mutation {{ buscaCidadaosCadsus(nomeCpfCns: "{cns}", dataNascimento: "{data_nasc_us}") }}'
        ]

        # Varre os formatos para garantir compatibilidade com o Schema do PEC
        for query_inline in tentativas_mutation:
            payload_busca = [{
                "operationName": None,
                "variables": {},
                "query": query_inline
            }]
            try:
                resp_busca = requests.post(url_graphql, headers=headers, json=payload_busca, timeout=10)
                if resp_busca.status_code == 200:
                    dados_busca = resp_busca.json()
                    if isinstance(dados_busca, list) and len(dados_busca) > 0:
                        # Se houver erros do GraphQL estruturados pelo Spring, avisa no log
                        if "errors" in dados_busca[0]:
                            continue
                            
                        data_bloco = dados_busca[0].get("data", {})
                        if data_bloco and data_bloco.get("buscaCidadaosCadsus"):
                            uuid_lote = data_bloco["buscaCidadaosCadsus"]
                            break
            except Exception:
                continue

        if not uuid_lote:
            print("   ❌ O servidor rejeitou os formatos de Mutation ou a sessão expirou.")
            continue

        print(f"   🆔 UUID do barramento aceito: {uuid_lote}")
        
        # Delay de segurança para o barramento de Brasília responder o Polling
        time.sleep(3)

        # PASSO 2: Polling estruturado exatamente como o seu conteúdo capturado
        payload_polling = [{
            "operationName": "BuscaCidadaoCadsusPolling",
            "variables": {"uuid": str(uuid_lote)},
            "query": (
                "query BuscaCidadaoCadsusPolling($uuid: String!) {\n"
                "  buscaCidadaosCadsusCompletoPolling(uuid: $uuid) {\n"
                "    usuario\n"
                "    uuid\n"
                "    resultCadsus\n"
                "    cidadaos {\n"
                "      cpf\n"
                "      cns\n"
                "      nome\n"
                "    }\n"
                "    __typename\n"
                "  }\n"
                "}\n"
            )
        }]

        try:
            resp_polling = requests.post(url_graphql, headers=headers, json=payload_polling, timeout=10)
            
            if resp_polling.status_code == 200:
                dados_polling = resp_polling.json()
                
                if isinstance(dados_polling, list) and len(dados_polling) > 0:
                    item_resposta = dados_polling[0]
                    result_dto = item_resposta.get("data", {}).get("buscaCidadaosCadsusCompletoPolling", {})
                    
                    if result_dto and result_dto.get("resultCadsus") == "SUCESSO":
                        cidadaos = result_dto.get("cidadaos", [])
                        if cidadaos and cidadaos[0].get("cpf"):
                            cpf_capturado = cidadaos[0]["cpf"]
                            paciente['cpf'] = cpf_capturado
                            sucessos += 1
                            print(f"   ✅ SUCESSO ABSOLUTO! CPF Capturado: {cpf_capturado}")
                            continue
            
            print("   ⚠️ Sincronização pendente ou vazia no barramento nacional.")

        except Exception as e:
            print(f"   ❌ Erro durante a execução do Polling: {e}")

        time.sleep(2)

    # Grava o resultado do lote de teste
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, ensure_ascii=False, indent=4)

    print("\n==================================================")
    print(f"🏁 Fim do teste de rota limpa! Sucessos: {sucessos}/5")
    print("==================================================")

if __name__ == "__main__":
    enriquecedor_cadsus_nis_definitivo()