import os
import json
from typing import Dict, Optional

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "ai_config.json")

class ConfigService:
    def __init__(self):
        self.config_dir = os.path.dirname(CONFIG_FILE)
        os.makedirs(self.config_dir, exist_ok=True)
        self._load_config()
    
    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self):
        return {
            "api_key": os.getenv("AI_API_KEY", ""),
            "api_base": os.getenv("AI_API_BASE", "https://api.openai.com/v1"),
            "model": os.getenv("AI_MODEL", "gpt-4o-mini"),
            "timeout": int(os.getenv("AI_TIMEOUT", "300")),
            "max_tokens": int(os.getenv("AI_MAX_TOKENS", "8000")),
            "temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
            "provider": os.getenv("AI_PROVIDER", "openai"),
            "default_strategy": os.getenv("DEFAULT_GENERATION_STRATEGY", "hybrid"),
            "enabled": bool(os.getenv("AI_API_KEY", ""))
        }
    
    def _save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_config(self) -> Dict:
        config = self.config.copy()
        config["enabled"] = bool(self.config.get("api_key"))
        return config
    
    def get_raw_config(self) -> Dict:
        return self.config.copy()
    
    def update_config(self, updates: Dict) -> Dict:
        valid_keys = ["api_key", "api_base", "model", "timeout", "max_tokens", "temperature", "provider", "default_strategy"]
        
        for key, value in updates.items():
            if key in valid_keys:
                self.config[key] = value
        
        self.config["enabled"] = bool(self.config.get("api_key"))
        
        self._save_config()
        
        return self.get_config()
    
    def test_connection(self) -> Dict:
        api_key = self.config.get("api_key", "")
        api_base = self.config.get("api_base", "")
        
        if not api_key or not api_base:
            return {"success": False, "message": "请配置API Key和API Base"}
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.get("model", "gpt-4o-mini"),
                "messages": [{"role": "user", "content": "hello"}],
                "max_tokens": 1
            }
            
            response = requests.post(
                f"{api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "连接成功", "status_code": response.status_code}
            elif response.status_code == 401:
                return {"success": False, "message": "API Key无效", "status_code": response.status_code}
            elif response.status_code == 403:
                return {"success": False, "message": "API Key权限不足", "status_code": response.status_code}
            else:
                return {"success": False, "message": f"连接失败: {response.status_code}", "status_code": response.status_code}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"连接异常: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"测试失败: {str(e)}"}
    
    def get_providers(self) -> Dict:
        return {
            "openai": {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"]
            },
            "deepseek": {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com/v1",
                "models": ["deepseek-v4-pro", "deepseek-v4-flash"]
            },
            "moonshot": {
                "name": "Moonshot",
                "base_url": "https://api.moonshot.cn/v1",
                "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
            },
            "anthropic": {
                "name": "Anthropic",
                "base_url": "https://api.anthropic.com/v1",
                "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            },
            "custom": {
                "name": "自定义",
                "base_url": "",
                "models": []
            }
        }