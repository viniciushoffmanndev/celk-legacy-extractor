from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from uuid import UUID
from uuid6 import uuid7

class PacienteSchema(BaseModel):
    """
    Schema de validação para os pacientes extraídos do banco legado, CELK.
    Garante que a nossa API só receba dados higienizados e CPFs reais.
    """
    
    id_novo: UUID = Field(default_factory=uuid7)
    id_legado: int = Field(alias="cd_usu_cadsus")

    nome: str = Field(alias="nm_usuario", max_length=70)
    sexo: str = Field(alias="sg_sexo", max_length=1)
    data_nascimento: Optional[date] = Field(alias="dt_nascimento", default=None)
    
    cpf: Optional[str] = Field(default=None, max_length=14)
    rg: Optional[str] = Field(default=None, max_length=20)
    celular: Optional[str] = Field(default=None, max_length=15)
    vivo: bool = Field(default=True)

    @field_validator('cpf', mode='before')
    @classmethod
    def validar_cpf_receita(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        
        # 1. Remove pontos, traços e espaços
        cpf_limpo = ''.join(filter(str.isdigit, str(v)))

        # 2. Verifica se tem exatamente 11 dígitos
        if len(cpf_limpo) != 11:
            return None
            
        # 3. Bloqueia sequências repetidas (ex: 11111111111, 22222222222)
        # (Isso burla o cálculo matemático, então precisamos barrar antes)
        if cpf_limpo == cpf_limpo[0] * 11:
            return None

        # 4. Algoritmo da Receita Federal (Módulo 11)
        # Calcula o primeiro dígito verificador
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1

        # Calcula o segundo dígito verificador
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2

        # Verifica se os dois últimos números informados batem com o cálculo
        if cpf_limpo[-2:] != f"{digito1}{digito2}":
            return None
        
        # Se sobreviveu a tudo isso, o CPF é quente!
        return cpf_limpo
    
    @field_validator('vivo', mode='before')
    @classmethod
    def converter_status(cls, v) -> bool:
        return v == 1