"""
Ferramentas para consulta ao Portal Nacional de Contratações Públicas (PNCP)
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests
from typing import Optional
import json
from datetime import datetime, timedelta
import os
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
        # Busca parcial, case-insensitive
        nome_lower = nome.lower().strip()
        resultados = [
            m for m in modalidades 
            if nome_lower in m["nome"].lower() or nome_lower in m["tipo"].lower()
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


def consultar_editais_pncp(
    data_final: str,
    pagina: int = 1,
    tamanho_pagina: int = 10,
    uf: Optional[str] = None,
    cnpj: Optional[str] = None,
    codigo_modalidade: Optional[int] = None,
    codigo_municipio_ibge: Optional[str] = None
) -> str:
    """
    Consulta editais e avisos de contratações no Portal Nacional de Contratações Públicas (PNCP)
    
    Args:
        data_final: Data final para busca no formato YYYYMMDD (ex: 20260220).
                   IMPORTANTE: Deve ser maior ou igual à data atual
        pagina: Número da página (padrão: 1)
        tamanho_pagina: Quantidade de registros por página (mínimo: 10, padrão: 10, máx: 500)
        uf: Sigla do estado (ex: SP, RJ, MG)
        cnpj: CNPJ do órgão/entidade (apenas números)
        codigo_modalidade: Código da modalidade de contratação
        codigo_municipio_ibge: Código IBGE do município
    
    Returns:
        Dados dos editais em formato JSON string
    """
    
    api_url = "https://pncp.gov.br/api/consulta/v1/contratacoes/proposta"
    
    # Construir parâmetros da requisição (API exige tamanhoPagina >= 10)
    tamanho_valido = max(10, min(tamanho_pagina, 500)) if tamanho_pagina else 10
    
    params = {
        "dataFinal": data_final,
        "pagina": pagina,
        "tamanhoPagina": tamanho_valido
    }
    
    if uf:
        params["uf"] = uf.upper()
    
    if cnpj:
        params["cnpj"] = cnpj.replace(".", "").replace("/", "").replace("-", "")
    
    if codigo_modalidade:
        params["codigoModalidadeContratacao"] = codigo_modalidade
    
    if codigo_municipio_ibge:
        params["codigoMunicipioIbge"] = codigo_municipio_ibge
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Formatar resposta de forma mais legível
            result = {
                "success": True,
                "fonte": "Portal Nacional de Contratações Públicas (PNCP)",
                "total_registros": data.get("totalRegistros", 0),
                "total_paginas": data.get("totalPaginas", 0),
                "pagina_atual": data.get("numeroPagina", pagina),
                "paginas_restantes": data.get("paginasRestantes", 0),
                "quantidade_resultados": len(data.get("data", [])),
                "editais": []
            }
            
            # Processar cada edital
            for item in data.get("data", []):
                edital = {
                    "numero_controle_pncp": item.get("numeroControlePNCP"),
                    "numero_compra": item.get("numeroCompra"),
                    "processo": item.get("processo"),
                    "objeto": item.get("objetoCompra"),
                    "modalidade": item.get("modalidadeNome"),
                    "modo_disputa": item.get("modoDisputaNome"),
                    "situacao": item.get("situacaoCompraNome"),
                    "valor_estimado": item.get("valorTotalEstimado"),
                    "valor_homologado": item.get("valorTotalHomologado"),
                    "srp": item.get("srp"),  # Sistema de Registro de Preços
                    "data_abertura_proposta": item.get("dataAberturaProposta"),
                    "data_encerramento_proposta": item.get("dataEncerramentoProposta"),
                    "data_publicacao_pncp": item.get("dataPublicacaoPncp"),
                    "orgao_entidade": {
                        "cnpj": item.get("orgaoEntidade", {}).get("cnpj"),
                        "razao_social": item.get("orgaoEntidade", {}).get("razaoSocial"),
                        "poder": item.get("orgaoEntidade", {}).get("poderId"),
                        "esfera": item.get("orgaoEntidade", {}).get("esferaId")
                    },
                    "unidade_orgao": {
                        "nome": item.get("unidadeOrgao", {}).get("nomeUnidade"),
                        "municipio": item.get("unidadeOrgao", {}).get("municipioNome"),
                        "uf": item.get("unidadeOrgao", {}).get("ufSigla"),
                        "codigo_ibge": item.get("unidadeOrgao", {}).get("codigoIbge")
                    },
                    "amparo_legal": {
                        "nome": item.get("amparoLegal", {}).get("nome"),
                        "descricao": item.get("amparoLegal", {}).get("descricao")
                    },
                    "tipo_instrumento": item.get("tipoInstrumentoConvocatorioNome"),
                    "link_sistema_origem": item.get("linkSistemaOrigem"),
                    "informacao_complementar": item.get("informacaoComplementar")
                }
                
                result["editais"].append(edital)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        else:
            # Tentar obter detalhes do erro da resposta
            error_detail = ""
            try:
                error_data = response.json()
                error_detail = f"\nDetalhes: {json.dumps(error_data, ensure_ascii=False, indent=2)}"
            except:
                error_detail = f"\nResposta: {response.text[:500]}"
            
            error_result = {
                "success": False,
                "error": f"Erro na requisição à API do PNCP",
                "status_code": response.status_code,
                "message": f"Não foi possível obter os dados. Verifique os parâmetros e tente novamente.{error_detail}",
                "parametros_enviados": params
            }
            return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    except requests.exceptions.Timeout:
        error_result = {
            "success": False,
            "error": "Timeout na requisição",
            "message": "A API do PNCP demorou muito para responder. Tente novamente."
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Erro ao consultar a API do PNCP"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


def test_pncp_consultation():
    """
    Função de teste para verificar a consulta ao PNCP
    Pode ser executada diretamente para debug
    """
    print("=" * 100)
    print("TESTE DE CONSULTA - PORTAL NACIONAL DE CONTRATAÇÕES PÚBLICAS (PNCP)")
    print("=" * 100)
    
    # Usar a data de hoje + 30 dias (API exige data >= data atual)
    data_final = (datetime.now() + timedelta(days=30)).strftime("%Y%m%d")
    
    print(f"\nBuscando editais com data final até: {data_final}")
    print("Parâmetros: 10 resultados por página\n")
    
    # Primeira tentativa: sem filtros adicionais
    print("📊 Consulta sem filtros adicionais...")
    result = consultar_editais_pncp(
        data_final=data_final,
        pagina=1,
        tamanho_pagina=10
    )
    
    print("\n" + "=" * 100)
    print("RESULTADO DA CONSULTA:")
    print("=" * 100)
    
    # Parse do JSON para análise
    try:
        data = json.loads(result)
        
        if data.get("success"):
            print(f"\n✅ Sucesso! {data['total_registros']} editais encontrados no total")
            print(f"📄 Exibindo página {data['pagina_atual']} de {data['total_paginas']}")
            print(f"📋 {data['quantidade_resultados']} editais nesta página")
            print(f"🔗 Fonte: {data['fonte']}")
            
            if data['quantidade_resultados'] > 0:
                print("\n" + "=" * 100)
                print("EDITAIS ENCONTRADOS:")
                print("=" * 100)
                
                for i, edital in enumerate(data['editais'], 1):
                    print(f"\n📌 EDITAL {i}")
                    print("-" * 100)
                    print(f"Número PNCP: {edital['numero_controle_pncp']}")
                    print(f"Processo: {edital['processo']}")
                    print(f"Modalidade: {edital['modalidade']}")
                    print(f"Situação: {edital['situacao']}")
                    
                    if edital['valor_estimado']:
                        print(f"Valor Estimado: R$ {edital['valor_estimado']:,.2f}")
                    
                    print(f"\nÓrgão: {edital['orgao_entidade']['razao_social']}")
                    print(f"CNPJ: {edital['orgao_entidade']['cnpj']}")
                    print(f"Localização: {edital['unidade_orgao']['municipio']}/{edital['unidade_orgao']['uf']}")
                    
                    print(f"\nObjeto:")
                    print(f"  {edital['objeto'][:200]}{'...' if len(edital['objeto']) > 200 else ''}")
                    
                    print(f"\nDatas:")
                    print(f"  Abertura: {edital['data_abertura_proposta']}")
                    print(f"  Encerramento: {edital['data_encerramento_proposta']}")
                    
                    if edital['link_sistema_origem']:
                        print(f"\n🔗 Link: {edital['link_sistema_origem']}")
            else:
                print("\n⚠️ Nenhum edital encontrado com os parâmetros especificados.")
                print("💡 Tente ajustar os filtros ou a data.")
        
        else:
            print(f"\n❌ Erro: {data.get('error')}")
            print(f"Mensagem: {data.get('message')}")
            if 'status_code' in data:
                print(f"Status Code: {data['status_code']}")
            if 'parametros_enviados' in data:
                print(f"\n📋 Parâmetros enviados:")
                print(json.dumps(data['parametros_enviados'], ensure_ascii=False, indent=2))
    
    except json.JSONDecodeError:
        print("\n❌ Erro ao decodificar JSON")
        print(result)
    
    print("\n" + "=" * 100)


class EditaisPNCPInput(BaseModel):
    """Schema de entrada para a ferramenta de consulta de editais do PNCP"""
    data_final: str = Field(
        description="Data final para busca no formato YYYYMMDD (ex: 20260220). "
                    "IMPORTANTE: Deve ser maior ou igual à data atual."
    )
    pagina: int = Field(
        default=1,
        description="Número da página para paginação dos resultados (padrão: 1)"
    )
    tamanho_pagina: int = Field(
        default=10,
        ge=10,
        le=500,
        description="Quantidade de registros por página (mínimo: 10, padrão: 10, máximo: 500)"
    )
    uf: Optional[str] = Field(
        default=None,
        description="Sigla do estado brasileiro para filtrar (ex: SP, RJ, MG, RS)"
    )
    cnpj: Optional[str] = Field(
        default=None,
        description="CNPJ do órgão/entidade para filtrar (apenas números ou com formatação)"
    )
    codigo_modalidade: Optional[int] = Field(
        default=None,
        description="Código da modalidade de contratação (ex: 6 para Pregão Eletrônico)"
    )
    codigo_municipio_ibge: Optional[str] = Field(
        default=None,
        description="Código IBGE do município para filtrar"
    )


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


class ConsultaModalidadeInput(BaseModel):
    """Schema de entrada para a ferramenta de consulta de modalidades"""
    nome: Optional[str] = Field(
        default=None,
        description="Nome completo ou parcial da modalidade (ex: 'Pregão', 'Eletrônico', 'Dispensa', 'Concorrência'). "
                    "Se não especificado, retorna todas as modalidades disponíveis."
    )


def create_editais_pncp_tool() -> StructuredTool:
    """Cria e retorna a ferramenta de consulta de editais do PNCP"""
    from ..prompts import prompt_loader
    
    tool_prompts = prompt_loader.get_tool_prompts()
    
    base_description = tool_prompts.get(
        "pncp_description",
        "Ferramenta essencial para consultar editais e avisos de contratações públicas no Portal Nacional "
        "de Contratações Públicas (PNCP). Permite buscar licitações, pregões, dispensas e outras modalidades "
        "de contratação com filtros por estado, CNPJ, município, modalidade e data. Retorna informações "
        "detalhadas incluindo: número do edital, órgão responsável, objeto da contratação, modalidade, "
        "valores estimados, datas de abertura/encerramento, situação e links para mais informações. "
        "Útil para acompanhar oportunidades de contratação pública, pesquisar licitações específicas, "
        "monitorar processos licitatórios e obter informações sobre compras governamentais."
    )
    
    enhanced_description = (
        f"{base_description} "
        "INSTRUCOES DE USO: "
        "(1) Para ESTADO/UF mencionado por nome completo (ex: 'Amazonas', 'São Paulo'): primeiro consulte ConsultarUF para obter a SIGLA (ex: 'AM', 'SP'), depois use a sigla no parametro 'uf'. "
        "(2) Para MUNICIPIO/CIDADE (ex: 'Campinas'): primeiro consulte ConsultarMunicipio para obter o CODIGO IBGE, depois use no parametro 'codigo_municipio_ibge'. "
        "(3) Para MODALIDADE por nome (ex: 'Pregão', 'Dispensa'): primeiro consulte ConsultarModalidade para obter o CODIGO, depois use no parametro 'codigo_modalidade'. "
        "(4) Data final DEVE ser formato YYYYMMDD e >= data atual. Calcule datas relativas (amanhã, próximo mês, etc) a partir da data atual informada no contexto."
    )
    
    return StructuredTool.from_function(
        func=consultar_editais_pncp,
        name="ConsultarEditaisPNCP",
        description=enhanced_description,
        args_schema=EditaisPNCPInput
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


def get_all_tools() -> list:
    """
    Retorna todas as ferramentas disponíveis para o agente
    
    Returns:
        Lista de ferramentas do LangChain
    """
    tools = [
        create_editais_pncp_tool(),
        create_consulta_uf_tool(),
        create_consulta_municipio_tool(),
        create_consulta_modalidade_tool(),
    ]
    
    return tools


# Permite executar o teste diretamente
if __name__ == "__main__":
    test_pncp_consultation()

