<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/POSTGRESQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/GRAPHQL-E10098?style=for-the-badge&logo=graphql&logoColor=white" />
  <img src="https://img.shields.io/badge/PYDANTIC-E92063?style=for-the-badge&logo=pydantic&logoColor=white" />
  <img src="https://img.shields.io/badge/DOTENV-ECD53F?style=for-the-badge&logo=dotenv&logoColor=black" />
</p>

<h2 align="center">✨ CELK Legacy Extractor & e-SUS Enrichment Engine ✨</h2>

<p align="center">
  Motor ETL (Extract, Transform, Load) assíncrono desenvolvido meticulosamente para extração, validação, consolidação e enriquecimento de dados de pacientes de um sistema legado (CELK). A plataforma cruza informações locais com a base de dados nacional do Ministério da Saúde (e-SUS / CADSUS), realizando higienização avançada de documentos, validação matemática de CPFs e web scraping inteligente via GraphQL para enriquecer fichas cadastrais desfalcadas de forma totalmente automatizada e resiliente.
</p>

---

## 🎯 Objetivo do Projeto
O objetivo central é realizar a higienização da base de dados municipal, extraindo pacientes do banco legado, validando documentos (CPF/CNS) com algoritmos matemáticos oficiais e, para pacientes sem CPF, realizar uma busca inteligente no barramento do Governo Federal para enriquecer a ficha cadastral com dados oficiais (Documentos, Endereço, Telefones, Filiação e Raça/Cor).

## 🚀 Principais Funcionalidades
- ⚡ **Extração e Validação (Pipeline Local)**: Paginação em lote (*Batch Processing*) para extração otimizada, filtrando nativamente registros unificados.
- 📐 **Contratos de Dados Invioláveis**: Consolidação e desduplicação rigorosa através de `PacienteSchema` utilizando **Pydantic V2**, com atribuição de identificadores universais UUIDv7.
- 🧮 **Validação Rígida (Receita Federal)**: Algoritmo matemático oficial embutido para validação e exclusão de CPFs com máscaras falsas ou inválidas.
- 🕵️ **Motor de Enriquecimento e-SUS**: Comunicação avançada e scraping direto da API GraphQL do e-SUS (PEC Web) utilizando sistema de *Polling*.
- 🧠 **Estratégias de Fallback Múltiplas**: Motores de inferência lógica que testam combinações secundárias (ex: Apenas CNS, CNS + Data) caso a busca principal ("Nome + Data") falhe por divergências de cadastro.
- 🛡️ **Micro-Batching e Resiliência**: Processamento em micro-lotes com pausas aleatórias (humanização) para contornar *rate limits* e bloqueios de firewall do Ministério da Saúde.
- 🔎 **Achatamento Profundo (Deep Flattening)**: Extração do payload complexo do e-SUS, estruturando a ficha completa do paciente (Endereço validado por CEP, Raça/Cor, Filiação e Contatos).
- 🔐 **Segurança e Governança (LGPD)**: Proteção de dados sensíveis (PHI) via `.gitignore` isolando o diretório `/data`, e gestão segura de cookies de sessão via `python-dotenv`.

## 🌟 Resultados e Impacto
- **Automatização Massiva:** Substitui milhares de horas de trabalho manual de busca individual no portal do e-SUS, processando e consolidando dezenas de milhares de pacientes de forma autônoma.
- **Recuperação Avançada (High Match Rate):** Graças às estratégias de *fallback*, a taxa de enriquecimento salta drasticamente, recuperando registros que seriam descartados por simples erros de digitação no sistema legado (ex: divergência na grafia do nome ou datas).
- **Enriquecimento Estratégico em Saúde:** A extração do "Deep Flattening" atualiza dados críticos (telefone, endereço, raça/cor) que são fundamentais para campanhas de vacinação, busca ativa da Atenção Básica e repasses de verbas do SUS.
- **Base de Dados Pronta para Produção:** O município passa a contar com um *Data Lake* de pacientes higienizado, livre de duplicidades e com todos os CPFs validados matematicamente.

---

## 📊 O Cenário Legado (O Desafio)
Uma análise quantitativa diagnóstica na base bruta (93.666 registros extraídos) revelou um cenário crítico de desfalque informacional crônico. Para o Ministério da Saúde (Programa Previne Brasil), pacientes sem CPF resultam em perda direta de repasses financeiros para o município:
- 🚨 **RG:** 77.24% nulos (72.351 registros sem identidade estadual)
- ⚠️ **Celular:** 43.28% nulos (40.541 registros gerando apagão de comunicação na Atenção Básica)
- ⚠️ **CPF:** 38.18% nulos (35.758 registros fantasmas para o Governo Federal)
- ⚠️ **CNS:** 21.16% nulos (19.821 registros sem identificação SUS)

---

## 🛠️ Tecnologias Utilizadas
* **Python 3.10+**
* **Pydantic:** Para validação estrita de esquemas e contratos de dados.
* **Requests / GraphQL:** Para integração e engenharia reversa do barramento do e-SUS.
* **Python-Dotenv:** Para gestão de segurança de credenciais e variáveis de ambiente.

---

## ⚙️ Como Configurar e Executar

### 1. Clonar o Repositório e Instalar Dependências
Crie seu ambiente virtual e instale as bibliotecas requeridas:
```bash
git clone [https://github.com/SEU_USUARIO/celk-legacy-extractor.git](https://github.com/SEU_USUARIO/celk-legacy-extractor.git)
cd celk-legacy-extractor

python -m venv venv
# No Windows (PowerShell): .\venv\Scripts\Activate.ps1
# No Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente (.env)
Crie o arquivo .env na raiz do projeto e insira suas credenciais capturadas (Network/F12) do portal e-SUS PEC:
```bash
ESUS_COOKIE="JSESSIONID=seu_jsession_id_aqui; XSRF-TOKEN=seu_token_aqui"
```

### 3. Executar o Motor de Enriquecimento
Após a extração primária do banco legado gerar o arquivo pacientes_consolidados.json dentro da pasta data/raw/, inicie a esteira de requisições:
```bash
python src/processors/esus.py
```
Nota de Resiliência: O motor é dotado de Lógica Incremental. Caso a sua sessão do e-SUS expire no meio do processamento, basta atualizar o .env com um novo cookie e rodar o script novamente. Ele pulará automaticamente os registros já enriquecidos.
