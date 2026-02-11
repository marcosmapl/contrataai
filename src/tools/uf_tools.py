"""
Ferramenta para consulta de Unidades Federativas (Estados) do Brasil
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
import json
from pathlib import Path


def carregar_estados_brasil():
    """Carrega os dados dos estados brasileiros do arquivo JSON"""
    try:
        # Caminho relativo ao arquivo atual
        current_dir = Path(__file__).parent
        json_path = current_dir.parent / "data" / "estados_brasil.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return []


def consultar_uf(
    id: Optional[int] = None,
    sigla: Optional[str] = None,
    nome: Optional[str] = None,
    regiao_nome: Optional[str] = None
) -> str:
    """
    Consulta informações sobre Unidades Federativas (Estados) do Brasil
    
    Args:
        id: ID do estado (ex: 35 para São Paulo)
        sigla: Sigla do estado (ex: SP, RJ, MG)
        nome: Nome completo do estado (ex: São Paulo, Rio de Janeiro)
        regiao_nome: Nome da região (ex: Sudeste, Sul, Norte, Nordeste, Centro-Oeste)
    
    Returns:
        Informações do(s) estado(s) em formato JSON string
    """
    
    estados = carregar_estados_brasil()
    
    if not estados:
        return json.dumps({
            "success": False,
            "error": "Não foi possível carregar os dados dos estados"
        }, ensure_ascii=False, indent=2)
    
    resultados = []
    
    # Filtrar por ID
    if id is not None:
        resultados = [e for e in estados if e["id"] == id]
    
    # Filtrar por sigla
    elif sigla:
        sigla_upper = sigla.upper().strip()
        resultados = [e for e in estados if e["sigla"] == sigla_upper]
    
    # Filtrar por nome (busca parcial, case-insensitive)
    elif nome:
        nome_lower = nome.lower().strip()
        resultados = [e for e in estados if nome_lower in e["nome"].lower()]
    
    # Filtrar por região
    elif regiao_nome:
        regiao_lower = regiao_nome.lower().strip()
        resultados = [e for e in estados if regiao_lower in e["regiao"]["nome"].lower()]
    
    # Se nenhum filtro, retornar todos
    else:
        resultados = estados
    
    if resultados:
        return json.dumps({
            "success": True,
            "total_encontrados": len(resultados),
            "estados": resultados
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "success": False,
            "message": "Nenhum estado encontrado com os critérios especificados"
        }, ensure_ascii=False, indent=2)


class ConsultaUFInput(BaseModel):
    """Schema de entrada para a ferramenta de consulta de UF"""
    id: Optional[int] = Field(
        default=None,
        description="ID do estado brasileiro (ex: 35 para São Paulo, 33 para Rio de Janeiro)"
    )
    sigla: Optional[str] = Field(
        default=None,
        description="Sigla do estado (ex: SP, RJ, MG, RS, PR)"
    )
    nome: Optional[str] = Field(
        default=None,
        description="Nome completo ou parcial do estado (ex: 'São Paulo', 'Rio', 'Minas')"
    )
    regiao_nome: Optional[str] = Field(
        default=None,
        description="Nome da região para listar todos os estados (ex: Sudeste, Sul, Norte, Nordeste, Centro-Oeste)"
    )


def create_consulta_uf_tool() -> StructuredTool:
    """Cria e retorna a ferramenta de consulta de UF"""
    return StructuredTool.from_function(
        func=consultar_uf,
        name="ConsultarUF",
        description=(
            "Consulta informações sobre estados brasileiros. "
            "Retorna ID, sigla e nome do estado. "
            "Use para obter a SIGLA de um estado quando o usuário menciona o nome (ex: 'Amazonas' → 'AM'). "
            "A sigla deve ser usada no parâmetro 'uf' da ferramenta ConsultarEditaisPNCP."
        ),
        args_schema=ConsultaUFInput
    )
