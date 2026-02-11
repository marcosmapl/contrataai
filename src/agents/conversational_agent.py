"""
Módulo de implementação do agente de IA
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from ..config import settings
from ..tools import get_all_tools
from ..prompts import prompt_loader


class ConversationalAgent:
    """Agente conversacional com memória e ferramentas"""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Inicializa o agente conversacional
        
        Args:
            model_name: Nome do modelo OpenAI (padrão: configurado em .env)
            temperature: Temperatura do modelo (padrão: configurado em .env)
            max_tokens: Máximo de tokens na resposta (padrão: configurado em .env)
        """
        # Valida as configurações
        settings.validate()
        
        # Configura parâmetros do modelo
        self.model_name = model_name or settings.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else settings.TEMPERATURE
        self.max_tokens = max_tokens or settings.MAX_TOKENS
        
        # Inicializa o modelo LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        
        # Carrega ferramentas
        self.tools = get_all_tools()
        
        # Vincula as ferramentas ao modelo
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Configura o prompt do sistema com data atual
        base_system_prompt = prompt_loader.get_system_prompt()
        hoje = datetime.now()
        data_atual = hoje.strftime("%d/%m/%Y")
        data_atual_yyyymmdd = hoje.strftime("%Y%m%d")
        data_30_dias = (hoje + timedelta(days=30)).strftime("%Y%m%d")
        
        self.system_prompt = f"{base_system_prompt}\n\n📅 CONTEXTO TEMPORAL IMPORTANTE:\n" \
                             f"Data atual: {data_atual} (formato API: {data_atual_yyyymmdd})\n" \
                             f"Ao consultar editais no PNCP, a data final (dataFinal) DEVE ser maior ou igual à data atual.\n" \
                             f"Para consultas futuras, calcule a data no formato YYYYMMDD a partir de hoje.\n" \
                             f"Exemplos: 'próximo mês' use uma data 30-60 dias à frente, " \
                             f"'este mês' use o final do mês atual, 'daqui 30 dias' = {data_30_dias}"
        
        # Inicializa a memória da conversa
        self.chat_history = []
    
    def _execute_tool(self, tool_name: str, tool_input: Any) -> str:
        """
        Executa uma ferramenta
        
        Args:
            tool_name: Nome da ferramenta
            tool_input: Entrada da ferramenta
        
        Returns:
            Resultado da ferramenta
        """
        print(f"\n🔧 EXECUTANDO FERRAMENTA: {tool_name}")
        print(f"📥 Parâmetros: {tool_input}")
        
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    # Usar invoke() ao invés de func() para que o LangChain
                    # desempacote corretamente os parâmetros do dicionário
                    result = tool.invoke(tool_input)
                    # Mostra preview do resultado (primeiras 200 caracteres)
                    preview = result[:200] + "..." if len(result) > 200 else result
                    print(f"📤 Resultado (preview): {preview}")
                    return result
                except Exception as e:
                    error_msg = f"Erro ao executar ferramenta: {str(e)}"
                    print(f"❌ {error_msg}")
                    print(f"🔍 Debug - tool_input type: {type(tool_input)}")
                    print(f"🔍 Debug - tool_input value: {tool_input}")
                    return error_msg
        
        error_msg = f"Ferramenta '{tool_name}' não encontrada."
        print(f"❌ {error_msg}")
        return error_msg
    
    def chat(self, user_input: str, max_iterations: int = 15) -> str:
        """
        Envia uma mensagem para o agente e retorna a resposta
        
        Args:
            user_input: Mensagem do usuário
            max_iterations: Número máximo de iterações (padrão: 15 para consultas complexas)
        
        Returns:
            Resposta do agente
        """
        print("\n" + "="*100)
        print("🤖 AGENTE CONTRATAI - INICIANDO PROCESSAMENTO")
        print("="*100)
        print(f"💬 Pergunta do usuário: {user_input}")
        print(f"⚙️  Max iterações: {max_iterations}")
        print("="*100)
        
        try:
            # Constrói a lista de mensagens com o histórico
            messages = [SystemMessage(content=self.system_prompt)]
            messages.extend(self.chat_history)
            messages.append(HumanMessage(content=user_input))
            
            # Loop de execução do agente
            for i in range(max_iterations):
                print(f"\n🔄 ITERAÇÃO {i+1}/{max_iterations}")
                print("-" * 100)
                
                # Invoca o modelo com as ferramentas
                print(f"🧠 Invocando modelo {self.model_name}...")
                response = self.llm_with_tools.invoke(messages)
                
                # Verifica se há tool calls
                if not response.tool_calls:
                    # Não há mais ferramentas a chamar, retorna a resposta
                    print("\n✅ RESPOSTA FINAL GERADA (sem tool calls)")
                    output = response.content
                    print(f"💭 Resposta: {output[:150]}{'...' if len(output) > 150 else ''}")
                    
                    # Adiciona à memória
                    self.chat_history.append(HumanMessage(content=user_input))
                    self.chat_history.append(AIMessage(content=output))
                    
                    # Limita o tamanho da memória (mantém últimas 20 mensagens)
                    if len(self.chat_history) > 20:
                        self.chat_history = self.chat_history[-20:]
                    
                    print("\n" + "="*100)
                    print("✨ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
                    print("="*100 + "\n")
                    return output
                
                # Adiciona a resposta do modelo às mensagens
                print(f"\n🛠️  Modelo solicitou {len(response.tool_calls)} chamada(s) de ferramenta")
                messages.append(response)
                
                # Executa as ferramentas chamadas
                for idx, tool_call in enumerate(response.tool_calls, 1):
                    print(f"\n📌 Tool Call {idx}/{len(response.tool_calls)}")
                    tool_name = tool_call["name"]
                    tool_input = tool_call["args"]
                    tool_call_id = tool_call["id"]
                    
                    # Executa a ferramenta
                    tool_output = self._execute_tool(tool_name, tool_input)
                    
                    # Adiciona o resultado da ferramenta às mensagens como ToolMessage
                    messages.append(
                        ToolMessage(
                            content=tool_output,
                            tool_call_id=tool_call_id,
                        )
                    )
            
            # Se chegou aqui, atingiu o número máximo de iterações
            print("\n" + "="*100)
            print(f"⚠️  LIMITE DE ITERAÇÕES ATINGIDO ({max_iterations})")
            print("="*100 + "\n")
            erro_msg = "Desculpe, não consegui completar a tarefa. A consulta pode ser muito complexa ou " \
                      "pode haver um problema temporário. Tente: (1) reformular a pergunta de forma mais simples, " \
                      "(2) dividir em perguntas menores, ou (3) tentar novamente em alguns instantes."
            return erro_msg
        
        except Exception as e:
            error_msg = f"Erro ao processar mensagem: {str(e)}"
            print("\n" + "="*100)
            print(f"❌ ERRO NO PROCESSAMENTO")
            print("="*100)
            print(f"💥 {error_msg}")
            print("="*100 + "\n")
            
            # Retorna mensagem de erro amigável
            agent_prompts = prompt_loader.get_agent_prompts()
            return agent_prompts.get("error_message", "Desculpe, ocorreu um erro.")
    
    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.chat_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Retorna o histórico da conversa em formato de lista de dicionários
        
        Returns:
            Lista com o histórico formatado
        """
        history = []
        for msg in self.chat_history:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        return history


def create_agent(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> ConversationalAgent:
    """
    Função auxiliar para criar uma instância do agente
    
    Args:
        model_name: Nome do modelo OpenAI
        temperature: Temperatura do modelo
        max_tokens: Máximo de tokens na resposta
    
    Returns:
        Instância do ConversationalAgent
    """
    return ConversationalAgent(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
