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
                return {"status": "SUCESSO", "dados": polling.cidadaos[0].model_dump()}
            return {"status": "PACIENTE_NAO_ENCONTRADO", "mensagem": f"Resultado CADSUS: {polling.resultCadsus}"}

    except ValidationError as ve:
        return {"status": "ERRO_SCHEMA", "mensagem": f"Contrato quebrado: {ve.errors()[0]['msg']}"}
        
    return {"status": "RESPOSTA_INCOMPLETA", "mensagem": "Estrutura JSON incompleta ou inesperada."}