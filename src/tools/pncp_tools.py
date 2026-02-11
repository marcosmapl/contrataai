"""
Ferramenta para consulta ao Portal Nacional de Contratações Públicas (PNCP)
"""
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import requests
from typing import Optional
import json
from datetime import datetime, timedelta


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
        
        # Log da URL completa sendo chamada
        print(f"\n🌐 URL da API: {api_url}")
        print(f"📋 Parâmetros (camelCase): {params}")
        
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        # Log da URL final com query string
        print(f"🔗 Request URL completa: {response.url}")
        print(f"📊 Status Code: {response.status_code}")
        
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


# Permite executar o teste diretamente
if __name__ == "__main__":
    test_pncp_consultation()
