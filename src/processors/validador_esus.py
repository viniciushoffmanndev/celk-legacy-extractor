import sys
import os
import json
from pydantic import ValidationError

# Garante que o Python consiga enxergar a pasta src/schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas.schemas_esus import GraphQLSingleResponse

def interpretar_resposta_cadsus(resposta_bruta_api: list) -> dict:
    if not isinstance(resposta_bruta_api, list) or len(resposta_bruta_api) == 0:
        return {"status": "ERRO_SISTEMA", "mensagem": "Resposta física inválida ou vazia."}

    try:
        item_validado = GraphQLSingleResponse.model_validate(resposta_bruta_api[0])
        
        if item_validado.errors:
            return {"status": "FALHA_API", "mensagem": f"Erro interno: {item_validado.errors[0].message}"}
            
        if item_validado.data and item_validado.data.buscaCidadaosCadsusCompletoPolling:
            polling = item_validado.data.buscaCidadaosCadsusCompletoPolling
            if polling.resultCadsus == "SUCESSO" and len(polling.cidadaos) > 0:
                c = polling.cidadaos[0] # Objeto validado pelo seu CidadaoCadsusSchema
                
                # Achatamento (Flattening) seguro utilizando os objetos do Pydantic
                dados_limpos = {
                    "cpf": c.cpf,
                    "cns_gov": c.cns,
                    "nome_gov": c.nome,
                    "nome_mae_gov": c.nomeMae,
                    "nome_pai_gov": c.nomePai,
                    "data_nascimento_gov": c.dataNascimento,
                    "sexo_gov": c.sexo,
                    "obito_gov": c.obito,
                    "raca_cor_gov": c.racaCor.nome if c.racaCor else None,
                    "telefone_celular_gov": c.telefoneCelular[0] if c.telefoneCelular else None,
                    "telefone_residencial_gov": c.telefoneResidencial[0] if c.telefoneResidencial else None,
                    "endereco_cep_gov": c.endereco.cep if c.endereco else None,
                    "endereco_logradouro_gov": c.endereco.logradouro if c.endereco else None,
                    "endereco_numero_gov": c.endereco.numero if c.endereco else None,
                    "endereco_bairro_gov": c.endereco.bairro if c.endereco else None,
                    "endereco_municipio_gov": c.endereco.municipio.nome if c.endereco and c.endereco.municipio else None,
                    "endereco_uf_gov": c.endereco.municipio.uf.sigla if c.endereco and c.endereco.municipio and c.endereco.municipio.uf else None
                }
                return {"status": "SUCESSO", "dados": dados_limpos}
                
            return {"status": "PACIENTE_NAO_ENCONTRADO", "mensagem": f"Resultado CADSUS: {polling.resultCadsus}"}

    except ValidationError as ve:
        return {"status": "ERRO_SCHEMA", "mensagem": f"Contrato quebrado: {ve.errors()[0]['msg']}"}
        
    return {"status": "RESPOSTA_INCOMPLETA", "mensagem": "Estrutura JSON incompleta ou inesperada."}