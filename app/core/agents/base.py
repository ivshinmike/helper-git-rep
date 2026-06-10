import logging
from typing import Any, Dict, Optional
from app.core.llm_client import LLMClient

# Configure logging for agents
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseAgent:
    """Base class for all agents in the helper-git-rep system."""

    def __init__(self, name: str, llm_client: Optional[LLMClient] = None):
        self.name = name
        self.logger = logging.getLogger(f"Agent[{name}]")
        self.llm_client = llm_client or LLMClient()

    def log(self, message: str, level: str = "info"):
        """Standardized logging for agents."""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)

    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to be implemented by specific agents.
        :param task_data: Dictionary containing input parameters for the task.
        :return: Dictionary containing the result of the execution.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
