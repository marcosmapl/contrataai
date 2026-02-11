"""
Contrata.AI - Assistente Inteligente de Contratações Públicas
Agente de IA especializado no Portal Nacional de Contratações Públicas (PNCP)
Construído com Streamlit, LangChain e OpenAI
"""
import streamlit as st
from src.agents import create_agent
from src.prompts import prompt_loader
from src.config import settings


# Configuração da página
st.set_page_config(
    page_title="Contrata.AI - Assistente de Contratações Públicas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session_state():
    """Inicializa as variáveis de estado da sessão"""
    if "agent" not in st.session_state:
        try:
            st.session_state.agent = create_agent()
        except ValueError as e:
            st.error("❌ Erro ao inicializar o agente:")
            st.error(str(e))
            st.info("💡 Verifique se a variável OPENAI_API_KEY está configurada corretamente no arquivo .env")
            st.stop()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Adiciona mensagem de boas-vindas
        welcome_msg = prompt_loader.get_welcome_message()
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_msg
        })


def display_chat_history():
    """Exibe o histórico de mensagens do chat"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(user_input: str):
    """
    Processa a entrada do usuário e obtém resposta do agente
    
    Args:
        user_input: Mensagem do usuário
    """
    # Adiciona mensagem do usuário ao histórico
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Exibe mensagem do usuário
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Obtém resposta do agente
    with st.chat_message("assistant"):
        with st.spinner("🔍 Analisando sua solicitação e consultando o PNCP..."):
            response = st.session_state.agent.chat(user_input)
            st.markdown(response)
    
    # Adiciona resposta ao histórico
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


def sidebar():
    """Cria a barra lateral com configurações e informações"""
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        st.divider()
        
        # Informações do modelo
        st.subheader("🤖 Modelo Atual")
        st.info(f"**Modelo:** {settings.OPENAI_MODEL}")
        st.info(f"**Temperatura:** {settings.TEMPERATURE}")
        
        st.divider()
        
        # Botão para limpar histórico
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.agent.clear_history()
            st.session_state.messages = []
            # Adiciona mensagem de boas-vindas novamente
            welcome_msg = prompt_loader.get_welcome_message()
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome_msg
            })
            st.rerun()
        
        st.divider()
        
        # Informações sobre ferramentas
        st.subheader("🛠️ Ferramentas Disponíveis")
        tools = st.session_state.agent.tools
        st.info(f"✅ {len(tools)} ferramenta(s) ativa(s)")
        for tool in tools:
            with st.expander(f"📌 **{tool.name}**"):
                st.markdown(f"**Descrição:**")
                st.write(tool.description[:300] + "..." if len(tool.description) > 300 else tool.description)
        
        st.divider()
        
        # Informações adicionais
        st.subheader("ℹ️ Sobre")
        st.markdown("""
        **Contrata.AI** é um assistente de IA especializado em contratações públicas.
        
        **Recursos:**
        - 🔍 Consulta em tempo real ao PNCP
        - 📊 Busca de editais e licitações
        - 📋 Informações sobre modalidades
        - ⚖️ Auxílio com legislação
        - 💡 Orientações sobre processos
        
        **Tecnologias:**
        - Streamlit para interface
        - LangChain para orquestração
        - OpenAI GPT para IA
        - API oficial do PNCP
        """)


def main():
    """Função principal do aplicativo"""
    # Inicializa estado da sessão
    initialize_session_state()
    
    # Título principal
    st.title("🏛️ Contrata.AI")
    st.caption("Assistente inteligente para contratações públicas e consultas ao PNCP")
    
    # Card informativo com links úteis
    with st.expander("🔗 Links Úteis do PNCP"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Portal Principal:**
            - [PNCP - Portal Nacional](https://pncp.gov.br)
            - [Documentação da API](https://pncp.gov.br/api/swagger-ui/index.html)
            """)
        with col2:
            st.markdown("""
            **Legislação:**
            - [Lei 14.133/2021](http://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/L14133.htm)
            - [Lei 8.666/93](http://www.planalto.gov.br/ccivil_03/leis/l8666cons.htm)
            """)
    
    st.divider()
    
    # Barra lateral
    sidebar()
    
    # Exibe histórico de mensagens
    display_chat_history()
    
    # Campo de entrada do usuário
    if prompt := st.chat_input("Pergunte sobre editais, licitações ou contratações públicas..."):
        handle_user_input(prompt)
    
    # Rodapé com disclaimer
    st.divider()
    st.caption("""
    ⚠️ **Disclaimer:** Este assistente fornece informações gerais sobre contratações públicas. 
    Para decisões oficiais, sempre consulte a legislação vigente e órgãos competentes. 
    Os dados são obtidos do Portal Nacional de Contratações Públicas (PNCP).
    """)


if __name__ == "__main__":
    main()
