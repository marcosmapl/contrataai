"""
Ferramenta para consulta de Municípios do Brasil
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
import json
from pathlib import Path


def carregar_municipios_brasil():
    """Carrega os dados dos municípios brasileiros do arquivo JSON"""
    try:
        # Caminho relativo ao arquivo atual
        current_dir = Path(__file__).parent
        json_path = current_dir.parent / "data" / "municipios.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return []


def consultar_municipio(
    id: Optional[int] = None,
    nome: Optional[str] = None,
    uf_id: Optional[int] = None,
    uf_sigla: Optional[str] = None
) -> str:
    """
    Consulta informações sobre municípios brasileiros
    
    Args:
        id: Código IBGE do município (ex: 3550308 para São Paulo)
        nome: Nome completo ou parcial do município (ex: 'São Paulo', 'Rio')
        uf_id: ID do estado para listar municípios (ex: 35 para SP)
        uf_sigla: Sigla do estado para listar municípios (ex: 'SP', 'RJ')
    
    Returns:
        Informações do(s) município(s) em formato JSON string
    """
    
    municipios = carregar_municipios_brasil()
    
    if not municipios:
        return json.dumps({
            "success": False,
            "error": "Não foi possível carregar os dados dos municípios"
        }, ensure_ascii=False, indent=2)
    
    resultados = []
    
    # Filtrar por ID (código IBGE)
    if id is not None:
        resultados = [m for m in municipios if m["id"] == id]
    
    # Filtrar por nome (busca parcial, case-insensitive)
    elif nome:
        nome_lower = nome.lower().strip()
        resultados = [m for m in municipios if nome_lower in m["nome"].lower()]
        # Limitar resultados para evitar retornar muitos municípios
        if len(resultados) > 50:
            resultados = resultados[:50]
    
    # Filtrar por UF (ID ou sigla)
    elif uf_id is not None:
        for m in municipios:
            microregiao = m.get("microrregiao")
            if microregiao:
                mesorregiao = microregiao.get("mesorregiao")
                if mesorregiao:
                    uf = mesorregiao.get("UF")
                    if uf and uf.get("id") == uf_id:
                        resultados.append(m)
    
    elif uf_sigla:
        uf_sigla_upper = uf_sigla.upper().strip()
        for m in municipios:
            microregiao = m.get("microrregiao")
            if microregiao:
                mesorregiao = microregiao.get("mesorregiao")
                if mesorregiao:
                    uf = mesorregiao.get("UF")
                    if uf and uf.get("sigla") == uf_sigla_upper:
                        resultados.append(m)
    
    # Se nenhum filtro, retornar mensagem informativa
    else:
        return json.dumps({
            "success": False,
            "message": "Por favor, forneça ao menos um critério de busca (id, nome, uf_id ou uf_sigla)",
            "total_municipios": len(municipios)
        }, ensure_ascii=False, indent=2)
    
    if resultados:
        # Formatar resultados de forma mais compacta
        municipios_formatados = []
        for m in resultados:
            uf = m.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {})
            municipios_formatados.append({
                "id": m["id"],
                "nome": m["nome"],
                "uf": {
                    "id": uf.get("id"),
                    "sigla": uf.get("sigla"),
                    "nome": uf.get("nome")
                },
                "microrregiao": m.get("microrregiao", {}).get("nome"),
                "mesorregiao": m.get("microrregiao", {}).get("mesorregiao", {}).get("nome")
            })
        
        return json.dumps({
            "success": True,
            "total_encontrados": len(resultados),
            "municipios": municipios_formatados
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "success": False,
            "message": "Nenhum município encontrado com os critérios especificados"
        }, ensure_ascii=False, indent=2)


class ConsultaMunicipioInput(BaseModel):
    """Schema de entrada para a ferramenta de consulta de municípios"""
    id: Optional[int] = Field(
        default=None,
        description="Código IBGE do município (ex: 3550308 para São Paulo/SP, 3304557 para Rio de Janeiro/RJ)"
    )
    nome: Optional[str] = Field(
        default=None,
        description="Nome completo ou parcial do município (ex: 'São Paulo', 'Rio', 'Brasília'). "
                    "Retorna até 50 resultados."
    )
    uf_id: Optional[int] = Field(
        default=None,
        description="ID do estado (UF) para listar todos os municípios daquele estado. "
                    "Use a ferramenta ConsultarUF para obter o ID do estado."
    )
    uf_sigla: Optional[str] = Field(
        default=None,
        description="Sigla do estado (UF) para listar todos os municípios (ex: 'SP', 'RJ', 'MG'). "
                    "Use a ferramenta ConsultarUF para obter a sigla do estado."
    )


def create_consulta_municipio_tool() -> StructuredTool:
    """Cria e retorna a ferramenta de consulta de municípios"""
    return StructuredTool.from_function(
        func=consultar_municipio,
        name="ConsultarMunicipio",
        description=(
            "Consulta municípios brasileiros por nome ou código IBGE. "
            "Use para obter o CODIGO IBGE quando o usuário menciona uma cidade. "
            "O código IBGE deve ser usado no parâmetro 'codigo_municipio_ibge' da ferramenta ConsultarEditaisPNCP."
        ),
        args_schema=ConsultaMunicipioInput
    )
