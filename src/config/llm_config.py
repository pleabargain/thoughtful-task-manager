"""
LLM Configuration Manager
"""
import json
import os
from typing import Optional, Dict, Any

class LLMConfig:
    CONFIG_FILE = "llm_session.json"
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file if it exists."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self._config = json.load(f)
            except Exception:
                self._config = {}
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Failed to save LLM configuration: {str(e)}")
    
    def get_model_name(self) -> Optional[str]:
        """Get the selected model name."""
        return self._config.get('model_name')
    
    def set_model_name(self, model_name: str) -> None:
        """Set the selected model name."""
        self._config['model_name'] = model_name
        self.save_config() 