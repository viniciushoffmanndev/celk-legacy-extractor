from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from uuid6 import uuid7, UUID

class PacienteSchema(BaseModel):
    """
    Schema de validação para os pacientes extraídos do banco legado, CELK.
    Garante que a nossa API, só receba dados higienizados.
    """
    
    #Novo ID moderno, mas ainda guardo a referência antiga
    id_novo: UUID = Field(default_factory=uuid7)
    id_legado: int = Field(alias="cd_usu_cadsus")

    nome: str = Field(alias="nm_usuario", max_length=70)
    sexo: str = Field(alias="sg_sexo", max_length=1)

    # Alguns pacientes muito antigos podem não ter data de nascimento no sistema
    data_nascimento: Optional[date] = Field(alias="dt_nascimento", default=None) 
    cpf: Optional[str] = Field(default=None, max_length=14)
    rg: Optional[str] = Field(default=None, max_length=20)
    celular: Optional[str] = Field(default=None, max_length=15)
    vivo: bool = Field(default=True)

    @field_validator('cpf', mode='before')
    @classmethod
    def limpar_cpf(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        
        # Remove pontos, traços e espaços, deixando apenas números
        cpf_limpo = ''.join(filter(str.isdigit, str(v)))

        # Se após limpar não conter 11 dígitos, tratamos como inválido, retorna None.
        # Em um sistema rigoroso levantaríamos um erro, mas em migração de legado
        # é comun CPFs cortados pela metade. É melhor salvar como nulo do que quebrar
        if len(cpf_limpo) != 11:
            return None
        
        return cpf_limpo
    
    @field_validator('vivo', mode='before')
    @classmethod
    def converter_status(cls, v) -> bool:
        # Se for 1 é verdadeiro, vivo, qualquer outra coisa é falso, óbito/inativo;
        return v == 1
