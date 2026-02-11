"""
Ferramenta para consulta de Modalidades de Contratação Pública
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
import json


def obter_modalidades_contratacao():
    """Retorna o mapeamento de modalidades de contratação do PNCP"""
    return [
        {"codigo": 1, "nome": "Leilão - Eletrônico", "tipo": "Leilão"},
        {"codigo": 4, "nome": "Concorrência - Eletrônica", "tipo": "Concorrência"},
        {"codigo": 5, "nome": "Concorrência - Presencial", "tipo": "Concorrência"},
        {"codigo": 6, "nome": "Pregão - Eletrônico", "tipo": "Pregão"},
        {"codigo": 7, "nome": "Pregão - Presencial", "tipo": "Pregão"},
        {"codigo": 8, "nome": "Dispensa", "tipo": "Dispensa"},
        {"codigo": 9, "nome": "Inexigibilidade", "tipo": "Inexigibilidade"},
        {"codigo": 11, "nome": "Pré-qualificação", "tipo": "Pré-qualificação"},
        {"codigo": 12, "nome": "Credenciamento", "tipo": "Credenciamento"},
        {"codigo": 13, "nome": "Leilão - Presencial", "tipo": "Leilão"},
    ]


def consultar_modalidade(nome: Optional[str] = None) -> str:
    """
    Consulta informações sobre modalidades de contratação do PNCP
    
    Args:
        nome: Nome completo ou parcial da modalidade (ex: 'Pregão', 'Eletrônico', 'Dispensa')
    
    Returns:
        Informações da(s) modalidade(s) em formato JSON string
    """
    
    modalidades = obter_modalidades_contratacao()
    
    if nome:
        # Normalizar para busca (remover hífens, espaços extras e converter para minúsculo)
        def normalizar(texto):
            return ' '.join(texto.replace('-', ' ').lower().split())
        
        nome_normalizado = normalizar(nome)
        resultados = [
            m for m in modalidades 
            if nome_normalizado in normalizar(m["nome"]) or 
               nome_normalizado in normalizar(m["tipo"]) or
               any(palavra in normalizar(m["nome"]) for palavra in nome_normalizado.split())
        ]
    else:
        # Se não especificar filtro, retornar todas
        resultados = modalidades
    
    if resultados:
        return json.dumps({
            "success": True,
            "total_encontrados": len(resultados),
            "modalidades": resultados
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "success": False,
            "message": "Nenhuma modalidade encontrada com os critérios especificados",
            "modalidades_disponiveis": modalidades
        }, ensure_ascii=False, indent=2)


class ConsultaModalidadeInput(BaseModel):
    """Schema de entrada para a ferramenta de consulta de modalidades"""
    nome: Optional[str] = Field(
        default=None,
        description="Nome completo ou parcial da modalidade (ex: 'Pregão', 'Eletrônico', 'Dispensa', 'Concorrência'). "
                    "Se não especificado, retorna todas as modalidades disponíveis."
    )


def create_consulta_modalidade_tool() -> StructuredTool:
    """Cria e retorna a ferramenta de consulta de modalidades"""
    return StructuredTool.from_function(
        func=consultar_modalidade,
        name="ConsultarModalidade",
        description=(
            "Consulta modalidades de contratação pública (Pregão, Concorrência, Dispensa, etc). "
            "Retorna o CODIGO da modalidade que deve ser usado no parâmetro 'codigo_modalidade' da ferramenta ConsultarEditaisPNCP. "
            "Sem parâmetros retorna todas as 10 modalidades."
        ),
        args_schema=ConsultaModalidadeInput
    )
