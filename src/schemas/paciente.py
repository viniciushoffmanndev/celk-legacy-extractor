from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date
from uuid import UUID
from uuid6 import uuid7

class PacienteSchema(BaseModel):
    """
    Schema de validação para os pacientes extraídos do banco legado, CELK.
    Garante que a nossa API só receba dados higienizados, no tamanho correto e CPFs reais.
    """
    
    id_novo: UUID = Field(default_factory=uuid7)
    id_legado: int = Field(alias="cd_usu_cadsus")

    nome: str = Field(alias="nm_usuario", max_length=70)
    sexo: Optional[str] = Field(alias="sg_sexo", default=None, max_length=1)
    data_nascimento: Optional[date] = Field(alias="dt_nascimento", default=None)
    
    cpf: Optional[str] = Field(default=None, max_length=14)
    cns: Optional[str] = Field(default=None, max_length=15)
    rg: Optional[str] = Field(default=None, max_length=20)
    celular: Optional[str] = Field(default=None, max_length=15)
    vivo: bool = Field(default=True)

    @field_validator('sexo', mode='before')
    @classmethod
    def validar_sexo(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        sexo_limpo = str(v).strip().upper()
        # Se digitaram algo maluco no legado, neutraliza para None
        if sexo_limpo not in ['M', 'F']:
            return None
        return sexo_limpo

    @field_validator('cns', mode='before')
    @classmethod
    def validar_cns(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        # Remove qualquer formatação (ex: 700.5023.2190.0458)
        cns_limpo = ''.join(filter(str.isdigit, str(v)))
        # CNS precisa ter cravados 15 dígitos
        if len(cns_limpo) != 15:
            return None
        return cns_limpo

    @field_validator('rg', mode='before')
    @classmethod
    def validar_rg(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        # O RG pode ter letras (ex: SSP-SP 12.345.678-X), então filtramos mantendo letras e números
        rg_limpo = ''.join(char for char in str(v) if char.isalnum()).upper()
        # Um RG real no Brasil raramente tem menos de 5 caracteres. Barra os "1", "123", "00".
        if len(rg_limpo) < 5:
            return None
        return rg_limpo

    @field_validator('celular', mode='before')
    @classmethod
    def validar_celular(cls, v: Optional[str]) -> Optional[str]:
        if not v or str(v).strip() == "":
            return None
        # Limpa parênteses e traços (ex: (18) 99999-9999 vira 18999999999)
        celular_limpo = ''.join(filter(str.isdigit, str(v)))
        # Deve ter o DDD (2 dígitos) + 8 ou 9 dígitos do número
        if len(celular_limpo) not in [10, 11]:
            return None
        return celular_limpo

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
            
        # 3. Bloqueia sequências repetidas (ex: 11111111111)
        if cpf_limpo == cpf_limpo[0] * 11:
            return None

        # 4. Algoritmo da Receita Federal (Módulo 11)
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        digito1 = 11 - (soma % 11)
        digito1 = 0 if digito1 > 9 else digito1

        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        digito2 = 11 - (soma % 11)
        digito2 = 0 if digito2 > 9 else digito2

        if cpf_limpo[-2:] != f"{digito1}{digito2}":
            return None
        
        return cpf_limpo
    
    @field_validator('vivo', mode='before')
    @classmethod
    def converter_status(cls, v) -> bool:
        return v == 1