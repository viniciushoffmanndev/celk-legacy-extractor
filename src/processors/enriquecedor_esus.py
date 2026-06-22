import json
import time
import re
import requests
import os

def enriquecer_dados_esus():
    print("==================================================")
    print("    INICIANDO O ROBÔ ENRIQUECEDOR E-SUS (POC)     ")
    print("==================================================")

    # O "Crachá" que você pescou na aba Network
    # Se expirar (der erro 401 ou redirecionar pro login), basta trocar esta string!
    COOKIE = "JSESSIONID=mHvKNXWKX2Ytq414G8Mi9qKzXbxhLTSD1-Hu56ps; BIGipServerpool_app_esus=3189035180.20480.0000; f5avraaaaaaaaaaaaaaaa_session_=EKLENODADOHLBEHMLCOCLNJBKLILDKHNDABDBAKIFMBHOGBCHCLMEKPHIGEKAMKCDDFEIKCMGPNMBMIGODBCMGGDBOMINODOMFODPGFGLHPMCHGKEAGFOPGOGOPODMBK"
    
    headers = {
        "Cookie": COOKIE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    caminho_json = os.path.join("data", "raw", "pacientes_consolidados.json")
    caminho_saida = os.path.join("data", "raw", "pacientes_enriquecidos.json")

    with open(caminho_json, "r", encoding="utf-8") as f:
        pacientes = json.load(f)

    # Filtra quem precisa de salvamento (Não tem CPF, mas TEM o CNS)
    alvos = [p for p in pacientes if p.get('cpf') is None and p.get('cns') is not None]
    
    print(f"Total de pacientes precisando de CPF: {len(alvos)}")
    print("Vamos testar com os 5 primeiros para validar a conexão...\n")

    sucessos = 0
    # LIMITAMOS A 5 PARA O NOSSO TESTE INICIAL
    for paciente in alvos[:5]:
        cns = paciente['cns']
        nome = paciente['nome']
        # Pega a data de nascimento (se for null, manda vazio para não quebrar a URL)
        data_nasc = paciente.get('data_nascimento') or "" 
        
        print(f"🔎 Buscando CPF para: {nome} (CNS: {cns} | Nasc: {data_nasc})...")

        # A URL agora vai com os DOIS parâmetros obrigatórios!
        url = f"https://esus.eparaguacu.sp.gov.br/cidadao?form%5BnomeCpfCns%5D={cns}&form%5BdataNascimento%5D={data_nasc}"
        
        try:
            # O robô bate na porta do servidor
            resposta = requests.get(url, headers=headers, timeout=10)
            
            # Como a busca do e-SUS pode retornar uma tabela, a forma mais ninja de achar 
            # o CPF é usar uma Expressão Regular (Regex) para achar o formato XXX.XXX.XXX-XX no HTML
            cpfs_encontrados = re.findall(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', resposta.text)
            
            if cpfs_encontrados:
                # Pega o primeiro CPF encontrado, limpa os pontos e traços
                cpf_limpo = ''.join(filter(str.isdigit, cpfs_encontrados[0]))
                paciente['cpf'] = cpf_limpo
                sucessos += 1
                print(f"SUCESSO! CPF Encontrado: {cpf_limpo}")
            else:
                # Se cair aqui, a sessão pode ter expirado ou o paciente não tem CPF nem no e-SUS
                if "autenticacao" in resposta.text.lower() or "login" in resposta.url:
                    print("ERRO: Sessão expirou! O Cookie não é mais válido.")
                    break
                print("Paciente não encontrado no e-SUS ou sem CPF cadastrado lá.")
                
        except Exception as e:
            print(f"Erro de conexão: {e}")

        # REGRA DE OURO DA ENGENHARIA DE DADOS: Não faça DDoSing no servidor do cliente!
        # Dorme 2 segundos entre cada busca para fingir ser um humano digitando.
        time.sleep(2)

    # Salvamos o progresso (mesmo que seja só o teste) num novo arquivo
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, ensure_ascii=False, indent=4)

    print("\n==================================================")
    print(f"Teste concluído! {sucessos} CPFs resgatados com sucesso.")
    print(f"Arquivo salvo em: {caminho_saida}")
    print("==================================================")

if __name__ == "__main__":
    enriquecer_dados_esus()