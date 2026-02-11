"""
Módulo para carregar prompts de arquivos JSON
"""
import json
import os
from typing import Dict, Any
from pathlib import Path


class PromptLoader:
    """Classe para carregar e gerenciar prompts de arquivos JSON"""
    
    def __init__(self, prompts_dir: str = None):
        """
        Inicializa o carregador de prompts
        
        Args:
            prompts_dir: Diretório onde os prompts estão armazenados
        """
        if prompts_dir is None:
            # Obtém o diretório atual do arquivo
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir
        else:
            self.prompts_dir = Path(prompts_dir)
    
    def load_prompt_file(self, filename: str) -> Dict[str, Any]:
        """
        Carrega um arquivo JSON de prompt
        
        Args:
            filename: Nome do arquivo JSON (com ou sem extensão)
        
        Returns:
            Dicionário com os prompts carregados
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.prompts_dir / filename
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Arquivo de prompt não encontrado: {filepath}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Erro ao decodificar JSON do arquivo {filepath}: {e}"
            )
    
    def get_agent_prompts(self) -> Dict[str, str]:
        """Carrega os prompts do agente"""
        return self.load_prompt_file("agent_prompts.json")
    
    def get_tool_prompts(self) -> Dict[str, str]:
        """Carrega os prompts das ferramentas"""
        return self.load_prompt_file("tool_prompts.json")
    
    def get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para o agente"""
        agent_prompts = self.get_agent_prompts()
        return agent_prompts.get("system_prompt", "")
    
    def get_welcome_message(self) -> str:
        """Retorna a mensagem de boas-vindas"""
        agent_prompts = self.get_agent_prompts()
        return agent_prompts.get("welcome_message", "Olá! Como posso ajudá-lo?")


# Instância global do carregador de prompts
prompt_loader = PromptLoader()
