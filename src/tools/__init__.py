"""
Módulo de ferramentas do agente ContratAI
Organizado em arquivos separados para melhor manutenção
"""
from typing import List
from langchain_core.tools import StructuredTool

# Importar ferramentas dos módulos separados
from .uf_tools import create_consulta_uf_tool, consultar_uf
from .municipio_tools import create_consulta_municipio_tool, consultar_municipio
from .modalidade_tools import create_consulta_modalidade_tool, consultar_modalidade
from .pncp_tools import create_editais_pncp_tool, consultar_editais_pncp, test_pncp_consultation


def get_all_tools() -> List[StructuredTool]:
    """
    Retorna todas as ferramentas disponíveis para o agente ContratAI
    
    Returns:
        Lista com todas as ferramentas: ConsultarUF, ConsultarMunicipio, 
        ConsultarModalidade e ConsultarEditaisPNCP
    """
    return [
        create_consulta_uf_tool(),
        create_consulta_municipio_tool(),
        create_consulta_modalidade_tool(),
        create_editais_pncp_tool()
    ]


__all__ = [
    # Função principal
    "get_all_tools",
    
    # Ferramentas individuais
    "create_consulta_uf_tool",
    "create_consulta_municipio_tool", 
    "create_consulta_modalidade_tool",
    "create_editais_pncp_tool",
    
    # Funções de consulta diretas
    "consultar_uf",
    "consultar_municipio",
    "consultar_modalidade",
    "consultar_editais_pncp",
    
    # Utilitários
    "test_pncp_consultation"
]
