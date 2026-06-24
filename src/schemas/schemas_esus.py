from pydantic import BaseModel, Field
from typing import List, Optional, Any

# ==========================================
# 1. SUB-SCHEMAS (Tudo Opcional por Segurança)
# ==========================================
class UFSchema(BaseModel):
    id: Optional[str] = None
    nome: Optional[str] = None
    sigla: Optional[str] = None

class MunicipioSchema(BaseModel):
    id: Optional[str] = None
    ibge: Optional[str] = None
    nome: Optional[str] = None
    uf: Optional[UFSchema] = None

class PaisSchema(BaseModel):
    id: Optional[str] = None
    nome: Optional[str] = None

class RacaCorSchema(BaseModel):
    id: Optional[str] = None
    nome: Optional[str] = None
    racaCorDbEnum: Optional[str] = None

class NacionalidadeSchema(BaseModel):
    id: Optional[str] = None
    nacionalidadeDbEnum: Optional[str] = None

class TipoLogradouroSchema(BaseModel):
    id: Optional[str] = None
    nome: Optional[str] = None
    numeroDne: Optional[str] = None

class EnderecoSchema(BaseModel):
    bairro: Optional[str] = None
    cep: Optional[str] = None
    complemento: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    semNumero: Optional[Any] = None
    pontoReferencia: Optional[str] = None
    municipio: Optional[MunicipioSchema] = None
    uf: Optional[UFSchema] = None
    tipoLogradouro: Optional[TipoLogradouroSchema] = None

# ==========================================
# 2. SCHEMA PRINCIPAL DO CIDADÃO
# ==========================================
class CidadaoCadsusSchema(BaseModel):
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    # CNS é a única coisa 100% obrigatória que esperamos na resposta válida
    cns: str = Field(..., min_length=15, max_length=15) 
    nome: Optional[str] = None
    nomeSocial: Optional[str] = None
    nomeMae: Optional[str] = None
    nomePai: Optional[str] = None
    dataNascimento: Optional[str] = None
    sexo: Optional[str] = None
    email: Optional[str] = None
    obito: Optional[Any] = None  # Blindado para aceitar "false", booleano ou null
    dataObito: Optional[str] = None
    racaCor: Optional[RacaCorSchema] = None
    nacionalidade: Optional[NacionalidadeSchema] = None
    municipioNascimento: Optional[MunicipioSchema] = None
    paisNascimento: Optional[PaisSchema] = None
    endereco: Optional[EnderecoSchema] = None
    
    # Listas blindadas contra retornos "null" do backend em Java do Governo
    telefoneResidencial: Optional[List[str]] = None
    telefoneCelular: Optional[List[str]] = None
    telefoneContato: Optional[List[str]] = None

# ==========================================
# 3. SCHEMAS DE ORQUESTRAÇÃO GRAPHQL
# ==========================================
class PollingResultSchema(BaseModel):
    usuario: Optional[str] = None
    uuid: Optional[str] = None
    resultCadsus: Optional[str] = None
    # Se vier nulo, cria lista vazia nativa para evitar quebra de índice
    cidadaos: Optional[List[CidadaoCadsusSchema]] = Field(default_factory=list)

class GraphQLDataSchema(BaseModel):
    buscaCidadaosCadsusCompletoPolling: Optional[PollingResultSchema] = None

class GraphQLErrorSchema(BaseModel):
    message: str
    # GraphQL Extensions é um objeto {}, Any impede falhas de parsing
    classification: Optional[Any] = Field(None, alias="extensions") 

class GraphQLSingleResponse(BaseModel):
    data: Optional[GraphQLDataSchema] = None
    errors: Optional[List[GraphQLErrorSchema]] = None