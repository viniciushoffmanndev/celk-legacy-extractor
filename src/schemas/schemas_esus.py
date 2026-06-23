from pydantic import BaseModel, Field
from typing import List, Optional

class UFSchema(BaseModel):
    id: str; nome: str; sigla: str

class MunicipioSchema(BaseModel):
    id: str; ibge: str; nome: str; uf: UFSchema

class PaisSchema(BaseModel):
    id: str; nome: str

class RacaCorSchema(BaseModel):
    id: str; nome: str; racaCorDbEnum: str

class NacionalidadeSchema(BaseModel):
    id: str; nacionalidadeDbEnum: str

class TipoLogradouroSchema(BaseModel):
    id: str; nome: str; numeroDne: str

class EnderecoSchema(BaseModel):
    bairro: Optional[str] = None
    cep: Optional[str] = None
    complemento: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    semNumero: bool
    pontoReferencia: Optional[str] = None
    municipio: Optional[MunicipioSchema] = None
    uf: Optional[UFSchema] = None
    tipoLogradouro: Optional[TipoLogradouroSchema] = None

class CidadaoCadsusSchema(BaseModel):
    cpf: Optional[str] = Field(None, min_length=11, max_length=11)
    cns: str = Field(..., min_length=15, max_length=15)
    nome: str
    nomeSocial: Optional[str] = None
    nomeMae: Optional[str] = None
    nomePai: Optional[str] = None
    dataNascimento: str
    sexo: str
    email: Optional[str] = None
    obito: str
    dataObito: Optional[str] = None
    racaCor: Optional[RacaCorSchema] = None
    nacionalidade: Optional[NacionalidadeSchema] = None
    municipioNascimento: Optional[MunicipioSchema] = None
    paisNascimento: Optional[PaisSchema] = None
    endereco: Optional[EnderecoSchema] = None
    telefoneResidencial: List[str] = []
    telefoneCelular: List[str] = []
    telefoneContato: List[str] = []

class PollingResultSchema(BaseModel):
    usuario: str
    uuid: str
    resultCadsus: str
    cidadaos: List[CidadaoCadsusSchema]

class GraphQLDataSchema(BaseModel):
    buscaCidadaosCadsusCompletoPolling: Optional[PollingResultSchema] = None

class GraphQLErrorSchema(BaseModel):
    message: str
    classification: Optional[str] = Field(None, alias="extensions")

class GraphQLSingleResponse(BaseModel):
    data: Optional[GraphQLDataSchema] = None
    errors: Optional[List[GraphQLErrorSchema]] = None