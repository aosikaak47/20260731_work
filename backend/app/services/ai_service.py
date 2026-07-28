import os
import json
import time
import uuid
import requests
from typing import List, Dict, Optional
from datetime import datetime

class AIService:
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        self.api_key = config.get("api_key", os.getenv("AI_API_KEY", ""))
        self.api_base = config.get("api_base", os.getenv("AI_API_BASE", "https://api.openai.com/v1"))
        self.model = config.get("model", os.getenv("AI_MODEL", "gpt-4o-mini"))
        self.timeout = int(config.get("timeout", os.getenv("AI_TIMEOUT", "300")))
        self.max_tokens = int(config.get("max_tokens", os.getenv("AI_MAX_TOKENS", "8000")))
        self.temperature = float(config.get("temperature", os.getenv("AI_TEMPERATURE", "0.7")))
        self.provider = config.get("provider", os.getenv("AI_PROVIDER", "openai"))
        self._init_prompt()
    
    def update_config(self, config: Dict):
        self.api_key = config.get("api_key", self.api_key)
        self.api_base = config.get("api_base", self.api_base)
        self.model = config.get("model", self.model)
        self.timeout = int(config.get("timeout", self.timeout))
        self.max_tokens = int(config.get("max_tokens", self.max_tokens))
        self.temperature = float(config.get("temperature", self.temperature))
        self.provider = config.get("provider", self.provider)
    
    def is_enabled(self) -> bool:
        return bool(self.api_key)
    
    def _init_prompt(self):
        self.system_prompt = """
你是一个专业的测试用例生成专家。请根据用户提供的需求文档，按照以下规则和策略生成高质量的测试用例：

## 测试用例生成规则

### 1. 用例类型覆盖
- **功能测试**：验证正常业务流程
- **异常测试**：验证异常输入和错误场景
- **边界测试**：验证输入边界值和极端情况
- **安全测试**：验证系统安全性和权限控制
- **性能测试**：验证系统响应时间和并发处理

### 2. 优先级分配策略
- **高优先级**：核心业务流程、关键功能点、安全相关
- **中优先级**：辅助功能、边界条件、非关键异常
- **低优先级**：次要功能、UI细节、兼容性

### 3. 用例编写规范
- 前置条件：明确测试执行前的系统状态
- 测试步骤：清晰、可执行的操作步骤
- 预期结果：明确、可验证的结果描述
- 用例名称：简洁明了，包含功能点和测试场景

### 4. 覆盖策略
- 确保每个需求点至少有一个测试用例覆盖
- 关键路径和核心流程需要多场景覆盖
- 接口参数需要覆盖必填项、选填项、边界值

### 5. 模块和功能点
- **模块**：用例所属的功能模块名称（如"用户登录与认证"、"考试作答"）
- **功能点**：用例覆盖的具体功能点（如"账号密码登录"、"验证码验证"）

## 输出格式要求

请严格按照以下JSON格式输出测试用例，不要包含任何其他文字：

```json
{
  "test_cases": [
    {
      "id": "唯一标识符",
      "name": "用例名称",
      "module": "功能模块名称",
      "feature": "功能点名称",
      "type": "功能/异常/边界/安全/性能",
      "priority": "高/中/低",
      "preconditions": "前置条件描述",
      "steps": ["步骤1", "步骤2", "步骤3"],
      "expected_result": "预期结果描述",
      "status": "未执行",
      "created_at": "当前时间ISO格式"
    }
  ],
  "analysis": {
    "requirements_covered": ["需求点1", "需求点2"],
    "coverage_rate": 85,
    "suggestions": ["优化建议"]
  }
}
```

请仔细分析需求文档，生成全面、专业的测试用例。
        """.strip()

    def generate_test_cases(self, content: str, doc_type: str = "requirement", 
                           case_count: int = 10) -> Dict:
        prompt = self._build_prompt(content, doc_type, case_count)
        try:
            response = self._call_llm(prompt)
            if response:
                return self._parse_response(response)
        except Exception as e:
            print(f"AI生成失败: {str(e)}")
        
        return {"test_cases": [], "analysis": {"requirements_covered": [], "coverage_rate": 0, "suggestions": []}}

    def _build_prompt(self, content: str, doc_type: str, case_count: int) -> str:
        doc_type_desc = {
            "requirement": "需求文档",
            "api": "接口文档",
            "ui": "UI设计文档",
            "auto": "自动识别"
        }
        
        return f"""
请根据以下{doc_type_desc.get(doc_type, '文档')}生成{case_count}个测试用例：

## 需求文档内容

{content}

## 要求

1. 根据文档内容分析功能点和需求
2. 生成覆盖不同测试类型（功能、异常、边界、安全、性能）的测试用例
3. 合理分配优先级
4. 严格按照指定的JSON格式输出
5. 用例名称和步骤要具体、可执行
6. 预期结果要明确、可验证

请直接输出JSON格式，不要包含任何markdown标记或额外解释。
        """.strip()

    def _call_llm(self, prompt: str) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"LLM请求失败: {str(e)}")
            return None

    def _parse_response(self, response: str) -> Dict:
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            result = json.loads(response)
            
            if "test_cases" not in result:
                result = {"test_cases": [], "analysis": {"requirements_covered": [], "coverage_rate": 0, "suggestions": []}}
            
            for case in result["test_cases"]:
                if "id" not in case or not case["id"]:
                    case["id"] = str(uuid.uuid4())
                if "status" not in case:
                    case["status"] = "未执行"
                if "created_at" not in case:
                    case["created_at"] = datetime.now().isoformat()
            
            return result
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {str(e)}")
            return {"test_cases": [], "analysis": {"requirements_covered": [], "coverage_rate": 0, "suggestions": []}}

    def analyze_requirements(self, content: str) -> Dict:
        prompt = f"""
请分析以下需求文档，提取功能点和测试要点：

## 需求文档

{content}

## 输出格式

请输出JSON格式：
{{
  "features": ["功能点1", "功能点2"],
  "test_points": ["测试要点1", "测试要点2"],
  "risks": ["风险点1", "风险点2"],
  "suggestions": ["测试建议"]
}}
        """.strip()
        
        try:
            response = self._call_llm(prompt)
            if response:
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:-3]
                elif response.startswith("```"):
                    response = response[3:-3]
                return json.loads(response)
        except Exception as e:
            print(f"需求分析失败: {str(e)}")
        
        return {"features": [], "test_points": [], "risks": [], "suggestions": []}

    def optimize_cases(self, test_cases: List[Dict], content: str) -> Dict:
        cases_json = json.dumps(test_cases, ensure_ascii=False, indent=2)
        prompt = f"""
请优化以下测试用例，使其更加全面和专业：

## 当前测试用例

{cases_json}

## 需求文档

{content}

## 优化要求

1. 补充遗漏的测试场景
2. 优化用例描述和步骤
3. 调整优先级分配
4. 确保覆盖全面

请输出优化后的JSON格式：
{{
  "optimized_cases": [...],
  "changes": ["变更说明"]
}}
        """.strip()
        
        try:
            response = self._call_llm(prompt)
            if response:
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:-3]
                elif response.startswith("```"):
                    response = response[3:-3]
                return json.loads(response)
        except Exception as e:
            print(f"用例优化失败: {str(e)}")
        
        return {"optimized_cases": test_cases, "changes": []} 