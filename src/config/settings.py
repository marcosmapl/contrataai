"""
Módulo de configurações do aplicativo.
Carrega variáveis de ambiente do arquivo .env
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Settings:
    """Classe para gerenciar as configurações do aplicativo"""
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se as configurações necessárias estão presentes"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY não configurada. "
                "Por favor, configure a variável no arquivo .env"
            )
        return True


# Instância global de configurações
settings = Settings()
