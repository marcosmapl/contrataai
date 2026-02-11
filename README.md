# 🏛️ ContrataAI - Assistente de Contratações Públicas

Aplicativo de chat com Agente de IA especializado em **contratações públicas** construído com **Streamlit**, **LangChain** e **OpenAI API**. O agente auxilia usuários com dúvidas sobre licitações, contratos administrativos e informações do Portal Nacional de Contratações Públicas (PNCP).

## 📋 Características

- 🤖 Agente conversacional inteligente especializado em contratações públicas
- 🔍 Consulta em tempo real ao Portal Nacional de Contratações Públicas (PNCP)
- 📊 Busca de editais, licitações e processos de compras públicas
- 🛠️ Sistema modular de ferramentas (Tools)
- 📝 Prompts configuráveis via arquivos JSON
- 💬 Interface de chat moderna com Streamlit
- 🔧 Configurações via arquivo `.env`
- 📦 Arquitetura modular e extensível

## 🗂️ Estrutura do Projeto

```
contrataai/
├── app.py                          # Aplicativo principal Streamlit
├── requirements.txt                # Dependências do projeto
├── .env.example                    # Exemplo de configurações
├── .gitignore                      # Arquivos ignorados pelo Git
├── README.md                       # Documentação
└── src/                           # Código fonte modularizado
    ├── __init__.py
    ├── config/                    # Configurações
    │   ├── __init__.py
    │   └── settings.py            # Carregamento de variáveis .env
    ├── prompts/                   # Prompts em JSON
    │   ├── __init__.py
    │   ├── loader.py              # Carregador de prompts
    │   ├── agent_prompts.json     # Prompts do agente
    │   └── tool_prompts.json      # Prompts das ferramentas
    ├── tools/                     # Ferramentas do agente
    │   ├── __init__.py
    │   └── agent_tools.py         # Implementação das tools
    └── agents/                    # Implementação dos agentes
        ├── __init__.py
        └── conversational_agent.py # Agente conversacional
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/contratai.git
cd contratai
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da OpenAI:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=2000
```

## ▶️ Como Usar

Execute o aplicativo Streamlit:

```bash
streamlit run app.py
```

O aplicativo abrirá automaticamente no navegador em `http://localhost:8501`

## 🛠️ Ferramentas Disponíveis

O agente possui as seguintes ferramentas especializadas:

1. **Consulta Editais PNCP**: Busca editais e avisos de contratações públicas no Portal Nacional de Contratações Públicas
   - Filtros por estado (UF)
   - Filtros por CNPJ do órgão
   - Filtros por município (código IBGE)
   - Filtros por modalidade de contratação
   - Filtros por data
   - Suporte a paginação para grandes volumes de resultados

### Exemplos de Consultas

- "Quais são os pregões eletrônicos abertos em São Paulo?"
- "Mostre licitações abertas do CNPJ 00394684000153"
- "Busque editais de credenciamento em Minas Gerais"
- "Quais são as contratações públicas com data final até 20260220?"

### Adicionando Novas Ferramentas

Para adicionar uma nova ferramenta:

1. Edite `src/tools/agent_tools.py`
2. Crie uma função para a ferramenta
3. Crie uma função `create_[nome]_tool()` que retorna um `StructuredTool`
4. Adicione a ferramenta em `get_all_tools()`
5. Adicione a descrição em `src/prompts/tool_prompts.json`

### Testando Ferramentas

Execute o script de teste para validar a consulta ao PNCP:

```bash
python test_extraction.py
```

## 📝 Personalizando Prompts

Os prompts são configurados em arquivos JSON no diretório `src/prompts/`:

- **agent_prompts.json**: Prompts do sistema, mensagens de boas-vindas e erro
- **tool_prompts.json**: Descrições das ferramentas

Edite esses arquivos para personalizar o comportamento do agente.

## 🔧 Configurações Avançadas

### Alterando o Modelo

Edite o arquivo `.env`:

```env
OPENAI_MODEL=gpt-4o        # Para GPT-4 Turbo
OPENAI_MODEL=gpt-3.5-turbo # Para GPT-3.5
```

### Ajustando a Temperatura

```env
TEMPERATURE=0.5  # Mais determinístico
TEMPERATURE=1.0  # Mais criativo
```

## 🏗️ Arquitetura

### Módulos

- **config**: Gerencia configurações e variáveis de ambiente
- **prompts**: Carrega e gerencia prompts de arquivos JSON
- **tools**: Implementa ferramentas que o agente pode usar
- **agents**: Implementa o agente conversacional com LangChain

### Fluxo de Dados

```
Usuário → Streamlit → Agent → LLM (OpenAI)
                        ↓
                      Tools
                        ↓
                    Resposta
```

## � Sistema de Logs e Debug

O agente possui um sistema completo de logs que permite acompanhar em tempo real todas as ações, chamadas de ferramentas e parâmetros utilizados.

### Logs Detalhados

Quando você executa o agente, os logs mostram:

- 🤖 Início do processamento
- 💬 Pergunta do usuário
- 🔄 Cada iteração do loop de raciocínio
- 🧠 Invocações do modelo LLM
- 🛠️ Chamadas de ferramentas solicitadas
- 📥 Parâmetros enviados para cada ferramenta
- 📤 Resultados retornados (preview)
- ✅ Resposta final gerada
- ✨ Conclusão do processamento

### Exemplo de Log

```
====================================================================================================
🤖 AGENTE CONTRATAI - INICIANDO PROCESSAMENTO
====================================================================================================
💬 Pergunta do usuário: Quais editais no Amazonas até amanhã?
⚙️ Max iterações: 15
====================================================================================================

🔄 ITERAÇÃO 1/15
----------------------------------------------------------------------------------------------------
🧠 Invocando modelo gpt-4o-mini...

🛠️ Modelo solicitou 1 chamada(s) de ferramenta

📌 Tool Call 1/1

🔧 EXECUTANDO FERRAMENTA: ConsultarUF
📥 Parâmetros: {'nome': 'Amazonas'}
📤 Resultado (preview): {"success": true, "estados": [{"sigla": "AM"}]}

🔄 ITERAÇÃO 2/15
----------------------------------------------------------------------------------------------------
🧠 Invocando modelo gpt-4o-mini...

🛠️ Modelo solicitou 1 chamada(s) de ferramenta

📌 Tool Call 1/1

🔧 EXECUTANDO FERRAMENTA: ConsultarEditaisPNCP
📥 Parâmetros: {'data_final': '20260210', 'uf': 'AM'}
📤 Resultado (preview): {"success": true, "total_registros": 45, ...}

🔄 ITERAÇÃO 3/15
----------------------------------------------------------------------------------------------------
🧠 Invocando modelo gpt-4o-mini...

✅ RESPOSTA FINAL GERADA (sem tool calls)
💭 Resposta: Encontrei 45 editais no estado do Amazonas...

====================================================================================================
✨ PROCESSAMENTO CONCLUÍDO COM SUCESSO
====================================================================================================
```

### Documentação Completa

Para mais informações sobre como interpretar os logs, consulte [LOGS_DO_AGENTE.md](LOGS_DO_AGENTE.md).

### Testando com Logs

Execute o script de demonstração:

```bash
python test_agent_logs.py
```

Este script demonstra o sistema de logs com consultas reais ao agente.

## �📦 Dependências Principais

- **streamlit**: Interface web
- **langchain**: Framework para agentes de IA
- **langchain-openai**: Integração com OpenAI
- **openai**: API da OpenAI
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🐛 Troubleshooting

### Problema: "Não consegui completar a tarefa dentro do limite de iterações"

**Causa:** Consultas complexas que requerem múltiplas chamadas de ferramentas.

**Soluções aplicadas:**
- ✅ `max_iterations` aumentado de 5 para 15
- ✅ Descrições das ferramentas otimizadas e simplificadas
- ✅ System prompt melhorado com orientações claras
- ✅ Contexto temporal injetado automaticamente

**Se o problema persistir:**
1. Reformule a pergunta de forma mais simples
2. Divida em perguntas menores (ex: "Qual a sigla do Amazonas?" → "Editais no AM")
3. Tente novamente em alguns instantes

### Problema: Chave da OpenAI inválida

**Solução:**
```bash
# Verifique se a chave está configurada no .env
OPENAI_API_KEY=sk-...
```

### Problema: API do PNCP retorna erro 400

**Causa:** Parâmetros inválidos (data passada, tamanhoPagina < 10).

**Solução:** O agente agora valida automaticamente:
- Data final >= data atual
- Tamanho da página entre 10-500

### Outros Problemas Conhecidos

- O histórico da conversa é mantido apenas durante a sessão
- A API do PNCP pode ter limitações de taxa de requisições
- Para usar com Python 3.13+, certifique-se de ter todas as dependências atualizadas

## 📚 Recursos Adicionais

- [Portal Nacional de Contratações Públicas (PNCP)](https://pncp.gov.br/)
- [Lei 14.133/2021 - Nova Lei de Licitações](http://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/L14133.htm)
- [Documentação API PNCP](https://pncp.gov.br/api/swagger-ui/index.html)

## 📞 Suporte

Para problemas ou dúvidas, abra uma [issue](https://github.com/seu-usuario/contrataai/issues) no GitHub.

---

Desenvolvido com ❤️ usando Streamlit, LangChain e OpenAI  
Um assistente de IA especializado em contratações públicas e o Portal Nacional de Contratações Públicas (PNCP)
