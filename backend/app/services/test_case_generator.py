import re
import uuid
import os
from datetime import datetime
from typing import List, Dict

class TestCaseGenerator:
    def __init__(self):
        self.templates = {
            "normal": {"name": "正常流程", "description": "验证功能在正常输入下的表现"},
            "exception": {"name": "异常流程", "description": "验证功能在异常输入下的表现"},
            "boundary": {"name": "边界值", "description": "验证功能在边界条件下的表现"},
            "security": {"name": "安全性", "description": "验证功能的安全防护能力"},
            "performance": {"name": "性能", "description": "验证功能的性能表现"}
        }
        
        self.ai_service = None
        self._init_ai_service()
        
        self.generation_rules = {
            "ai_first": {
                "name": "AI优先",
                "description": "优先使用AI生成，失败时回退到规则模板",
                "strategy": self._generate_ai_first
            },
            "rule_first": {
                "name": "规则优先",
                "description": "优先使用规则模板，AI作为补充",
                "strategy": self._generate_rule_first
            },
            "ai_only": {
                "name": "纯AI",
                "description": "仅使用AI生成",
                "strategy": self._generate_ai_only
            },
            "rule_only": {
                "name": "纯规则",
                "description": "仅使用规则模板生成",
                "strategy": self._generate_rule_only
            },
            "hybrid": {
                "name": "混合模式",
                "description": "AI生成核心用例，规则模板补充覆盖",
                "strategy": self._generate_hybrid
            }
        }
        
        self.default_strategy = os.getenv("DEFAULT_GENERATION_STRATEGY", "hybrid")
        
        self.ui_patterns = {
            "login": ["登录", "用户名", "密码", "账号", "验证码"],
            "search": ["查询", "搜索", "条件", "筛选"],
            "form": ["表单", "输入", "提交", "保存"],
            "table": ["表格", "列表", "数据", "行", "列"],
            "button": ["按钮", "点击", "操作"],
            "navigation": ["菜单", "导航", "首页", "返回"],
            "upload": ["上传", "文件", "图片"],
            "delete": ["删除", "移除", "删除确认"],
            "edit": ["编辑", "修改", "更新"],
            "add": ["新增", "添加", "创建"],
            "pagination": ["分页", "页码", "每页", "下一页"],
            "export": ["导出", "下载", "Excel", "CSV"],
            "detail": ["详情", "查看", "明细"]
        }

        self.module_patterns = {
            "ai_case_generator": ["AI智能测试用例生成", "用例生成", "AI生成", "智能生成", "用例自动生成"],
            "case_management": ["测试用例管理", "用例管理", "用例编辑", "用例筛选", "用例统计"],
            "api_automation": ["接口自动化", "API测试", "接口测试", "HTTP接口", "接口编排"],
            "ui_automation": ["UI自动化", "页面自动化", "Web自动化", "浏览器自动化"],
            "task_scheduler": ["任务调度", "定时任务", "CI/CD", "持续集成"],
            "report_statistics": ["测试报告", "质量统计", "统计分析", "可视化图表"],
            "permission_management": ["权限管理", "角色", "用户管理", "登录日志", "操作日志"],
            "project_management": ["项目管理", "版本管理", "项目创建", "数据隔离"]
        }

    def generate(self, content: str, doc_type: str = "auto", strategy: str = None) -> Dict:
        strategy = strategy or self.default_strategy
        
        if strategy in self.generation_rules:
            return self.generation_rules[strategy]["strategy"](content, doc_type)
        
        return self._generate_rule_only(content, doc_type)
    
    def generate_with_strategy(self, content: str, doc_type: str = "auto", 
                               strategy: str = "hybrid", case_count: int = 10) -> Dict:
        if strategy in self.generation_rules:
            return self.generation_rules[strategy]["strategy"](content, doc_type, case_count)
        return self._generate_rule_only(content, doc_type)
    
    def _init_ai_service(self):
        try:
            from .ai_service import AIService
            import os
            import json
            
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "ai_config.json")
            config = {}
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except Exception:
                    pass
            
            self.ai_service = AIService(config)
        except Exception as e:
            print(f"AI服务初始化失败: {str(e)}")
            self.ai_service = None
    
    def _generate_ai_first(self, content: str, doc_type: str = "auto", case_count: int = 10) -> Dict:
        if self.ai_service and self.ai_service.api_key:
            try:
                result = self.ai_service.generate_test_cases(content, doc_type, case_count)
                if result and result.get("test_cases"):
                    return {
                        "test_cases": result["test_cases"],
                        "analysis": result.get("analysis", {}),
                        "generation_mode": "ai",
                        "strategy": "ai_first"
                    }
            except Exception as e:
                print(f"AI生成失败，回退到规则模板: {str(e)}")
        
        return self._generate_rule_only(content, doc_type)
    
    def _generate_rule_first(self, content: str, doc_type: str = "auto", case_count: int = 10) -> Dict:
        rule_cases = self._generate_by_rules(content, doc_type)
        
        if self.ai_service and self.ai_service.api_key:
            try:
                ai_result = self.ai_service.generate_test_cases(content, doc_type, max(1, case_count - len(rule_cases)))
                if ai_result and ai_result.get("test_cases"):
                    ai_cases = ai_result["test_cases"]
                    rule_cases.extend(ai_cases)
                    return {
                        "test_cases": rule_cases,
                        "analysis": ai_result.get("analysis", {}),
                        "generation_mode": "hybrid",
                        "strategy": "rule_first",
                        "rule_cases_count": len(rule_cases) - len(ai_cases),
                        "ai_cases_count": len(ai_cases)
                    }
            except Exception as e:
                print(f"AI补充失败，仅使用规则模板结果: {str(e)}")
        
        return {
            "test_cases": rule_cases,
            "analysis": {},
            "generation_mode": "rule",
            "strategy": "rule_first"
        }
    
    def _generate_ai_only(self, content: str, doc_type: str = "auto", case_count: int = 10) -> Dict:
        if self.ai_service and self.ai_service.api_key:
            try:
                result = self.ai_service.generate_test_cases(content, doc_type, case_count)
                return {
                    "test_cases": result.get("test_cases", []),
                    "analysis": result.get("analysis", {}),
                    "generation_mode": "ai",
                    "strategy": "ai_only"
                }
            except Exception as e:
                print(f"纯AI生成失败: {str(e)}")
        
        return {
            "test_cases": [],
            "analysis": {"error": "AI服务不可用"},
            "generation_mode": "ai",
            "strategy": "ai_only"
        }
    
    def _generate_rule_only(self, content: str, doc_type: str = "auto", case_count: int = 10) -> Dict:
        test_cases = self._generate_by_rules(content, doc_type)
        return {
            "test_cases": test_cases,
            "analysis": {},
            "generation_mode": "rule",
            "strategy": "rule_only"
        }
    
    def _generate_hybrid(self, content: str, doc_type: str = "auto", case_count: int = 10) -> Dict:
        ai_cases = []
        rule_cases = self._generate_by_rules(content, doc_type)
        
        ai_count = max(3, int(case_count * 0.7))
        
        if self.ai_service and self.ai_service.api_key:
            try:
                ai_result = self.ai_service.generate_test_cases(content, doc_type, ai_count)
                if ai_result and ai_result.get("test_cases"):
                    ai_cases = ai_result["test_cases"]
            except Exception as e:
                print(f"AI混合生成失败: {str(e)}")
        
        all_cases = self._merge_cases(ai_cases, rule_cases)
        
        return {
            "test_cases": all_cases,
            "analysis": {"ai_cases_count": len(ai_cases), "rule_cases_count": len(rule_cases)},
            "generation_mode": "hybrid",
            "strategy": "hybrid"
        }
    
    def _generate_by_rules(self, content: str, doc_type: str = "auto") -> List[Dict]:
        test_cases = []
        
        text_cases = self._generate_from_text(content, doc_type)
        
        if text_cases:
            test_cases.extend(text_cases)
        else:
            modules = self._detect_modules(content)
            for module_type, features in modules.items():
                if features:
                    test_cases.extend(self._generate_cases_for_module(module_type, features))
            
            if not test_cases:
                ui_features = self._detect_ui_features(content)
                for feature_type, features in ui_features.items():
                    if features:
                        test_cases.extend(self._generate_cases_for_ui_feature(feature_type, features))
        
        if not test_cases:
            test_cases = self._generate_default_cases(content)
        
        return test_cases
    
    def _merge_cases(self, ai_cases: List[Dict], rule_cases: List[Dict]) -> List[Dict]:
        merged = []
        seen_names = set()
        
        for case in ai_cases:
            name = case.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                merged.append(case)
        
        for case in rule_cases:
            name = case.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                merged.append(case)
        
        return merged

    def _detect_modules(self, content: str) -> Dict[str, List[str]]:
        modules = {}
        for module_type, patterns in self.module_patterns.items():
            found_patterns = []
            for pattern in patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            if found_patterns:
                modules[module_type] = found_patterns
        return modules

    def _generate_cases_for_module(self, module_type: str, patterns: List[str]) -> List[Dict]:
        generators = {
            "ai_case_generator": self._generate_ai_case_generator_cases,
            "case_management": self._generate_case_management_cases,
            "api_automation": self._generate_api_automation_cases,
            "ui_automation": self._generate_ui_automation_cases,
            "task_scheduler": self._generate_task_scheduler_cases,
            "report_statistics": self._generate_report_statistics_cases,
            "permission_management": self._generate_permission_management_cases,
            "project_management": self._generate_project_management_cases
        }
        
        if module_type in generators:
            return generators[module_type](patterns)
        return []

    def _generate_ai_case_generator_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 需求文档导入生成",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在有效的需求文档（Word/Markdown/TXT）",
                "steps": [
                    "进入AI用例生成模块",
                    "选择需求文档导入方式",
                    "上传有效的需求文档",
                    "点击生成测试用例按钮",
                    "等待生成结果",
                    "验证生成的测试用例"
                ],
                "expected_result": "成功生成标准化测试用例，覆盖正向、反向、边界场景，用例格式规范",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 接口文档导入生成",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在有效的接口文档（Swagger/OpenAPI/YApi）",
                "steps": [
                    "进入AI用例生成模块",
                    "选择接口文档导入方式",
                    "上传或输入接口文档链接",
                    "点击生成测试用例按钮",
                    "等待生成结果",
                    "验证生成的接口测试用例"
                ],
                "expected_result": "成功解析接口字段、请求方式、参数约束，生成接口测试用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 手动输入业务场景生成",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入AI用例生成模块",
                    "选择手动输入方式",
                    "输入业务场景描述",
                    "点击生成测试用例按钮",
                    "等待生成结果",
                    "验证生成的测试用例"
                ],
                "expected_result": "根据业务场景描述成功生成相关测试用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 页面元素解析生成",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，提供页面元素信息",
                "steps": [
                    "进入AI用例生成模块",
                    "选择页面元素解析方式",
                    "录入或导入页面元素信息",
                    "点击生成测试用例按钮",
                    "等待生成结果",
                    "验证生成的UI测试用例"
                ],
                "expected_result": "根据页面元素信息生成对应的UI自动化测试用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 重复用例自动剔除",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，生成的用例存在重复",
                "steps": [
                    "生成包含重复场景的测试用例",
                    "检查生成结果",
                    "验证重复用例处理情况"
                ],
                "expected_result": "系统自动识别并剔除重复用例，合并相似用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 用例优先级自动标注",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "生成测试用例",
                    "检查生成的用例优先级标注",
                    "验证优先级分配合理性"
                ],
                "expected_result": "系统根据功能重要性自动标注用例优先级（高/中/低）",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 大文档处理性能",
                "type": "性能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，准备100个用例级别的需求文档",
                "steps": [
                    "上传大型需求文档",
                    "点击生成测试用例按钮",
                    "记录生成耗时",
                    "验证生成结果完整性"
                ],
                "expected_result": "100个用例以内生成耗时≤30s，生成结果完整无报错",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "AI用例生成 - 格式错误文档处理",
                "type": "异常",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，准备格式错误的文档",
                "steps": [
                    "上传格式错误的文档",
                    "点击生成测试用例按钮",
                    "验证系统反馈"
                ],
                "expected_result": "系统提示文档格式错误，给出正确格式要求",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_case_management_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例新增",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入用例管理模块",
                    "点击新增用例按钮",
                    "填写用例信息（标题、模块、步骤、预期结果等）",
                    "点击保存按钮",
                    "验证保存结果"
                ],
                "expected_result": "用例成功保存，列表中显示新增用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例编辑",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可编辑用例",
                "steps": [
                    "进入用例管理模块",
                    "选择一条用例点击编辑",
                    "修改用例信息",
                    "点击保存按钮",
                    "验证修改结果"
                ],
                "expected_result": "用例成功修改，信息更新正确",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例删除",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可删除用例",
                "steps": [
                    "进入用例管理模块",
                    "选择一条用例点击删除",
                    "确认删除操作",
                    "验证删除结果"
                ],
                "expected_result": "用例成功删除，列表中不再显示",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例筛选",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在多条用例",
                "steps": [
                    "进入用例管理模块",
                    "设置筛选条件（模块、优先级、类型等）",
                    "点击筛选按钮",
                    "验证筛选结果"
                ],
                "expected_result": "列表只显示符合筛选条件的用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 关键词检索",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在多条用例",
                "steps": [
                    "进入用例管理模块",
                    "在搜索框输入关键词",
                    "点击搜索按钮或按回车键",
                    "验证搜索结果"
                ],
                "expected_result": "快速定位到包含关键词的用例",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例导出Excel",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在可导出用例",
                "steps": [
                    "进入用例管理模块",
                    "选择要导出的用例",
                    "选择导出格式为Excel",
                    "点击导出按钮",
                    "验证导出文件"
                ],
                "expected_result": "成功导出Excel文件，包含完整用例信息",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例批量操作",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在多条用例",
                "steps": [
                    "进入用例管理模块",
                    "批量选择多条用例",
                    "执行批量操作（修改优先级、归类等）",
                    "验证操作结果"
                ],
                "expected_result": "批量操作成功，所有选中用例按要求更新",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "用例管理 - 用例统计",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入用例管理模块",
                    "查看用例统计信息",
                    "验证统计数据准确性"
                ],
                "expected_result": "正确显示总用例数、有效用例、高优先级用例、AI生成用例占比",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_api_automation_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - GET请求",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可用的GET接口",
                "steps": [
                    "进入接口自动化模块",
                    "创建新的接口测试用例",
                    "选择请求方式为GET",
                    "填写接口URL和参数",
                    "点击执行按钮",
                    "验证执行结果"
                ],
                "expected_result": "成功发送GET请求，返回200状态码，响应数据正确",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - POST请求",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可用的POST接口",
                "steps": [
                    "进入接口自动化模块",
                    "创建新的接口测试用例",
                    "选择请求方式为POST",
                    "填写接口URL和JSON Body参数",
                    "点击执行按钮",
                    "验证执行结果"
                ],
                "expected_result": "成功发送POST请求，返回200或201状态码，数据成功保存",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - 业务场景串联",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在多个关联接口",
                "steps": [
                    "进入接口自动化模块",
                    "创建业务场景",
                    "添加多个接口并设置执行顺序",
                    "配置接口间参数传递",
                    "执行业务场景",
                    "验证执行结果"
                ],
                "expected_result": "所有接口按顺序执行，参数正确传递，场景执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - 状态码断言",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入接口自动化模块",
                    "创建接口测试用例",
                    "配置状态码断言（期望200）",
                    "执行用例",
                    "验证断言结果"
                ],
                "expected_result": "断言通过，用例执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - JSON路径断言",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入接口自动化模块",
                    "创建接口测试用例",
                    "配置JSON路径断言（如$.data.id）",
                    "执行用例",
                    "验证断言结果"
                ],
                "expected_result": "JSON路径断言通过，验证指定字段值正确",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - 多环境切换",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，已配置多环境",
                "steps": [
                    "进入接口自动化模块",
                    "选择开发环境执行接口",
                    "验证执行成功",
                    "切换到测试环境",
                    "再次执行同一接口",
                    "验证执行成功"
                ],
                "expected_result": "不同环境下接口均可正常执行，环境隔离有效",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - 未授权访问",
                "type": "安全",
                "priority": "高",
                "preconditions": "系统正常运行，存在需要认证的接口",
                "steps": [
                    "进入接口自动化模块",
                    "创建接口测试用例，不携带认证信息",
                    "执行用例",
                    "验证响应"
                ],
                "expected_result": "接口返回401或403状态码，拒绝未授权访问",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "接口自动化 - 参数缺失",
                "type": "边界",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在需要参数的接口",
                "steps": [
                    "进入接口自动化模块",
                    "创建接口测试用例，不填写必要参数",
                    "执行用例",
                    "验证响应"
                ],
                "expected_result": "接口返回400状态码，提示参数错误",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_ui_automation_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 元素定位(XPath)",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可测试的Web页面",
                "steps": [
                    "进入UI自动化模块",
                    "创建新的UI测试用例",
                    "使用XPath方式定位元素",
                    "添加操作步骤（点击、输入等）",
                    "执行用例",
                    "验证执行结果"
                ],
                "expected_result": "元素成功定位，操作步骤执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 元素定位(CSS)",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可测试的Web页面",
                "steps": [
                    "进入UI自动化模块",
                    "创建新的UI测试用例",
                    "使用CSS选择器方式定位元素",
                    "添加操作步骤",
                    "执行用例",
                    "验证执行结果"
                ],
                "expected_result": "元素成功定位，操作步骤执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 业务流程编排",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可测试的业务流程",
                "steps": [
                    "进入UI自动化模块",
                    "创建新的UI测试场景",
                    "添加多个步骤编排业务流程（登录→查询→操作）",
                    "执行场景",
                    "验证执行结果"
                ],
                "expected_result": "整个业务流程自动执行完成，所有步骤通过",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 文本断言",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入UI自动化模块",
                    "创建UI测试用例",
                    "添加文本断言步骤",
                    "执行用例",
                    "验证断言结果"
                ],
                "expected_result": "文本断言通过，页面显示预期文本",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 元素存在断言",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入UI自动化模块",
                    "创建UI测试用例",
                    "添加元素存在断言步骤",
                    "执行用例",
                    "验证断言结果"
                ],
                "expected_result": "元素存在断言通过，目标元素存在于页面",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 失败截图",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在会失败的用例",
                "steps": [
                    "进入UI自动化模块",
                    "创建会失败的UI测试用例",
                    "执行用例",
                    "查看失败截图"
                ],
                "expected_result": "用例执行失败时自动截图，截图清晰展示失败场景",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - PO模式元素管理",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入UI自动化模块",
                    "使用PO模式管理页面元素",
                    "创建页面元素对象",
                    "引用元素对象创建测试用例",
                    "执行用例"
                ],
                "expected_result": "元素与流程解耦，用例执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "UI自动化 - 超时配置",
                "type": "边界",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入UI自动化模块",
                    "创建UI测试用例",
                    "配置元素查找超时时间",
                    "执行用例",
                    "验证超时处理"
                ],
                "expected_result": "在超时时间内元素未找到时，用例正确标记失败并记录错误",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_task_scheduler_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - 手动执行",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在可执行的自动化任务",
                "steps": [
                    "进入任务调度模块",
                    "选择一个自动化任务",
                    "点击执行按钮",
                    "查看执行进度",
                    "验证执行结果"
                ],
                "expected_result": "任务立即执行，执行进度实时更新，执行完成后显示结果",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - 定时任务配置",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入任务调度模块",
                    "创建定时任务",
                    "配置执行时间（如每天凌晨2点）",
                    "选择要执行的自动化任务",
                    "保存定时任务",
                    "验证任务配置"
                ],
                "expected_result": "定时任务配置成功，在指定时间自动执行",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - CI触发配置",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，已配置CI工具",
                "steps": [
                    "进入任务调度模块",
                    "配置CI触发规则",
                    "关联自动化任务",
                    "提交代码触发CI",
                    "验证自动化任务执行"
                ],
                "expected_result": "代码提交后CI自动触发，自动化任务执行成功",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - 任务终止",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在正在执行的任务",
                "steps": [
                    "进入任务调度模块",
                    "找到正在执行的任务",
                    "点击终止按钮",
                    "确认终止操作",
                    "验证任务状态"
                ],
                "expected_result": "任务成功终止，状态更新为已终止",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - 任务重试",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在失败的任务",
                "steps": [
                    "进入任务调度模块",
                    "找到失败的任务",
                    "点击重试按钮",
                    "验证任务重新执行"
                ],
                "expected_result": "任务重新执行，执行结果正确",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "任务调度 - 历史记录查看",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在已执行的任务",
                "steps": [
                    "进入任务调度模块",
                    "查看任务历史记录",
                    "筛选历史任务",
                    "查看详细执行日志"
                ],
                "expected_result": "历史记录完整显示，可查看每次执行的详细信息",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_report_statistics_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "测试报告 - 可视化报告生成",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在已执行的自动化任务",
                "steps": [
                    "进入测试报告模块",
                    "查看最新的自动化执行报告",
                    "验证报告内容"
                ],
                "expected_result": "报告包含执行总数、通过数、失败数、跳过数、通过率、执行时长等信息",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "测试报告 - 失败用例详情",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在失败的自动化任务",
                "steps": [
                    "进入测试报告模块",
                    "查看失败用例详情",
                    "检查报错信息、请求日志、页面截图"
                ],
                "expected_result": "失败用例精准定位，报错原因清晰，日志和截图完整",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "测试报告 - PDF导出",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在可导出的报告",
                "steps": [
                    "进入测试报告模块",
                    "选择一份报告",
                    "点击导出PDF按钮",
                    "验证导出文件"
                ],
                "expected_result": "成功导出PDF文件，报告内容完整",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "质量统计 - 项目维度统计",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在多个项目数据",
                "steps": [
                    "进入质量统计模块",
                    "选择项目维度统计",
                    "查看统计数据"
                ],
                "expected_result": "正确显示各项目的用例覆盖率、自动化通过率等指标",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "质量统计 - 时间维度趋势",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在历史执行数据",
                "steps": [
                    "进入质量统计模块",
                    "查看时间维度趋势图",
                    "验证趋势数据准确性"
                ],
                "expected_result": "折线图/柱状图正确展示质量趋势变化",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "质量统计 - 高频失败模块",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在多次执行数据",
                "steps": [
                    "进入质量统计模块",
                    "查看高频失败模块统计",
                    "验证统计结果"
                ],
                "expected_result": "正确识别并展示高频失败模块，便于问题定位",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_permission_management_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 多角色登录",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，存在不同角色的用户账号",
                "steps": [
                    "使用超级管理员账号登录",
                    "验证可访问所有模块",
                    "使用测试工程师账号登录",
                    "验证只能访问指定模块"
                ],
                "expected_result": "不同角色用户登录后看到不同的功能菜单，权限隔离有效",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 项目级权限分配",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录超级管理员",
                "steps": [
                    "进入权限管理模块",
                    "选择一个项目",
                    "为用户分配项目权限（查看、编辑、执行等）",
                    "使用该用户账号登录",
                    "验证权限生效"
                ],
                "expected_result": "用户只能访问和操作分配了权限的项目",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 用户账号管理",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录超级管理员",
                "steps": [
                    "进入用户管理模块",
                    "创建新用户账号",
                    "编辑用户信息",
                    "禁用用户账号",
                    "验证操作结果"
                ],
                "expected_result": "用户账号管理操作成功，禁用用户无法登录",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 操作日志记录",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "执行一些操作（新增、编辑、删除）",
                    "进入操作日志模块",
                    "查看操作记录",
                    "验证日志内容"
                ],
                "expected_result": "所有操作均有日志记录，包含操作人、时间、操作类型、操作内容",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 越权访问拦截",
                "type": "安全",
                "priority": "高",
                "preconditions": "系统正常运行，存在无权限访问资源的用户",
                "steps": [
                    "使用无权限用户登录",
                    "尝试访问受限资源（直接输入URL）",
                    "验证系统响应"
                ],
                "expected_result": "系统拒绝访问，跳转到无权限提示页面或登录页面",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "权限管理 - 密码修改",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入个人设置页面",
                    "点击修改密码",
                    "输入旧密码和新密码",
                    "保存修改",
                    "使用新密码登录验证"
                ],
                "expected_result": "密码修改成功，使用新密码可正常登录",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _generate_project_management_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理 - 项目创建",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入项目管理模块",
                    "点击创建项目按钮",
                    "填写项目信息（名称、描述等）",
                    "保存项目",
                    "验证项目创建"
                ],
                "expected_result": "项目创建成功，显示在项目列表中",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理 - 项目数据隔离",
                "type": "功能",
                "priority": "高",
                "preconditions": "系统正常运行，用户已登录，存在多个项目",
                "steps": [
                    "创建两个项目A和B",
                    "在项目A中创建测试用例",
                    "切换到项目B",
                    "验证项目B中是否显示项目A的用例"
                ],
                "expected_result": "项目B中不显示项目A的用例，数据隔离有效",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理 - 版本迭代管理",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在项目",
                "steps": [
                    "进入项目管理模块",
                    "选择一个项目",
                    "创建版本迭代",
                    "关联测试用例到版本",
                    "验证版本关联"
                ],
                "expected_result": "版本迭代创建成功，用例正确关联到版本",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理 - 项目成员配置",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录，存在项目",
                "steps": [
                    "进入项目管理模块",
                    "选择一个项目",
                    "添加项目成员",
                    "分配成员角色",
                    "验证成员权限"
                ],
                "expected_result": "成员添加成功，权限正确分配",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "项目管理 - 项目分类管理",
                "type": "功能",
                "priority": "中",
                "preconditions": "系统正常运行，用户已登录",
                "steps": [
                    "进入项目管理模块",
                    "创建项目分类",
                    "将项目归类到分类中",
                    "按分类筛选项目",
                    "验证筛选结果"
                ],
                "expected_result": "项目分类管理成功，按分类筛选结果正确",
                "status": "未执行",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _detect_ui_features(self, content: str) -> Dict[str, List[str]]:
        features = {}
        for feature_type, patterns in self.ui_patterns.items():
            found_patterns = []
            for pattern in patterns:
                if pattern in content:
                    found_patterns.append(pattern)
            if found_patterns:
                features[feature_type] = found_patterns
        return features

    def _generate_cases_for_ui_feature(self, feature_type: str, patterns: List[str]) -> List[Dict]:
        generators = {
            "login": self._generate_login_cases,
            "search": self._generate_search_cases,
            "form": self._generate_form_cases,
            "table": self._generate_table_cases,
            "button": self._generate_button_cases,
            "navigation": self._generate_navigation_cases,
            "upload": self._generate_upload_cases,
            "delete": self._generate_delete_cases,
            "edit": self._generate_edit_cases,
            "add": self._generate_add_cases,
            "pagination": self._generate_pagination_cases,
            "export": self._generate_export_cases,
            "detail": self._generate_detail_cases
        }
        if feature_type in generators:
            return generators[feature_type](patterns)
        return []

    def _generate_login_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "用户登录 - 正常登录", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，用户已注册", "steps": ["打开登录页面", "输入正确的用户名", "输入正确的密码", "点击登录按钮", "验证登录结果"],
             "expected_result": "成功登录系统，跳转到主页面", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "用户登录 - 错误密码", "type": "异常", "priority": "高",
             "preconditions": "系统正常运行", "steps": ["打开登录页面", "输入正确用户名", "输入错误密码", "点击登录按钮", "验证系统反馈"],
             "expected_result": "系统提示密码错误，不允许登录", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "用户登录 - 空用户名", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行", "steps": ["打开登录页面", "不输入用户名", "输入密码", "点击登录按钮", "验证系统反馈"],
             "expected_result": "系统提示用户名不能为空", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "用户登录 - 空密码", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行", "steps": ["打开登录页面", "输入用户名", "不输入密码", "点击登录按钮", "验证系统反馈"],
             "expected_result": "系统提示密码不能为空", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_search_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "数据查询 - 正常查询", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据查询页面", "输入有效的查询条件", "点击查询按钮", "验证查询结果"],
             "expected_result": "查询结果正确显示，符合查询条件", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据查询 - 空条件查询", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据查询页面", "不输入任何查询条件", "点击查询按钮", "验证系统处理"],
             "expected_result": "系统显示全部数据或提示输入查询条件", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据查询 - 无结果查询", "type": "异常", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据查询页面", "输入不存在的查询条件", "点击查询按钮", "验证系统反馈"],
             "expected_result": "系统提示无匹配数据，页面显示为空", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_form_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "表单提交 - 完整填写", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入表单页面", "填写所有必填字段", "填写可选字段", "点击提交按钮", "验证提交结果"],
             "expected_result": "表单提交成功，数据保存到系统", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "表单提交 - 缺少必填字段", "type": "边界", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入表单页面", "填写部分必填字段", "跳过某些必填字段", "点击提交按钮", "验证系统反馈"],
             "expected_result": "系统提示缺少必填字段，高亮显示未填项", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "表单提交 - 格式错误", "type": "异常", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入表单页面", "填写格式不正确的数据", "点击提交按钮", "验证系统反馈"],
             "expected_result": "系统提示数据格式错误，给出正确格式提示", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_table_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "表格展示 - 正常显示", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，存在数据", "steps": ["进入数据列表页面", "等待表格加载", "验证表格内容"],
             "expected_result": "表格正确显示数据，列对齐，内容完整", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "表格展示 - 空数据", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录，无数据", "steps": ["进入数据列表页面", "等待表格加载", "验证空状态显示"],
             "expected_result": "表格显示空状态提示，无报错", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "表格排序 - 点击排序", "type": "功能", "priority": "中",
             "preconditions": "系统正常运行，已登录，表格存在可排序列", "steps": ["进入数据列表页面", "点击列标题进行排序", "验证排序结果"],
             "expected_result": "数据按指定列正确排序，显示排序方向标识", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_button_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "按钮点击 - 正常点击", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["定位到目标按钮", "点击按钮", "验证按钮响应"],
             "expected_result": "按钮正常响应，执行对应操作", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "按钮状态 - 禁用状态", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，按钮处于禁用状态", "steps": ["定位到禁用状态的按钮", "尝试点击按钮", "验证按钮状态"],
             "expected_result": "按钮保持禁用状态，不执行任何操作", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_navigation_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "页面导航 - 菜单跳转", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["点击菜单项", "等待页面跳转", "验证目标页面"],
             "expected_result": "成功跳转到目标页面，菜单项高亮显示", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "页面导航 - 返回上一页", "type": "功能", "priority": "中",
             "preconditions": "系统正常运行，已登录，存在历史页面", "steps": ["点击返回按钮", "等待页面跳转", "验证返回结果"],
             "expected_result": "成功返回上一页，页面状态保持", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_upload_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "文件上传 - 正常上传", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入上传页面", "选择有效的文件", "点击上传按钮", "验证上传结果"],
             "expected_result": "文件上传成功，显示上传进度和结果", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "文件上传 - 超过大小限制", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入上传页面", "选择超过大小限制的文件", "点击上传按钮", "验证系统反馈"],
             "expected_result": "系统提示文件大小超过限制，不允许上传", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "文件上传 - 不支持格式", "type": "异常", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入上传页面", "选择不支持格式的文件", "点击上传按钮", "验证系统反馈"],
             "expected_result": "系统提示文件格式不支持，不允许上传", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_delete_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "数据删除 - 正常删除", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，存在可删除数据", "steps": ["进入数据列表页面", "选择要删除的数据", "点击删除按钮", "确认删除操作", "验证删除结果"],
             "expected_result": "数据成功删除，提示删除成功，列表更新", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据删除 - 取消删除", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据列表页面", "选择数据点击删除", "在确认对话框中点击取消", "验证数据状态"],
             "expected_result": "数据保持不变，未被删除", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据删除 - 关联数据", "type": "异常", "priority": "中",
             "preconditions": "系统正常运行，已登录，数据存在关联", "steps": ["选择存在关联的数据", "点击删除按钮", "验证系统反馈"],
             "expected_result": "系统提示数据存在关联，无法删除或提供级联删除选项", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_edit_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "数据修改 - 正常修改", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，存在可修改数据", "steps": ["进入数据列表页面", "选择数据点击编辑", "修改数据内容", "点击保存按钮", "验证修改结果"],
             "expected_result": "数据成功修改，提示修改成功", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据修改 - 修改后取消", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入编辑页面", "修改数据内容", "点击取消按钮", "验证数据状态"],
             "expected_result": "数据保持原值，未被修改", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_add_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "数据新增 - 正常新增", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据新增页面", "填写完整的新增数据", "点击保存按钮", "验证保存结果"],
             "expected_result": "数据成功新增，提示保存成功，返回列表", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据新增 - 重复数据", "type": "异常", "priority": "中",
             "preconditions": "系统正常运行，已登录，存在重复数据", "steps": ["进入数据新增页面", "填写与现有数据重复的唯一字段", "点击保存按钮", "验证系统反馈"],
             "expected_result": "系统提示数据重复，不允许新增", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_pagination_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "分页功能 - 翻页", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，数据超过一页", "steps": ["进入数据列表页面", "点击下一页按钮", "验证分页结果"],
             "expected_result": "成功跳转到下一页，数据正确显示", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "分页功能 - 跳转到指定页", "type": "功能", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据列表页面", "输入目标页码", "点击跳转按钮", "验证跳转结果"],
             "expected_result": "成功跳转到指定页码，数据正确显示", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "分页功能 - 首页和末页", "type": "边界", "priority": "中",
             "preconditions": "系统正常运行，已登录，数据超过一页", "steps": ["点击首页按钮", "验证跳转结果", "点击末页按钮", "验证跳转结果"],
             "expected_result": "正确跳转到首页和末页", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_export_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "数据导出 - 正常导出", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，存在数据", "steps": ["进入数据列表页面", "点击导出按钮", "选择导出格式", "确认导出", "验证导出结果"],
             "expected_result": "文件成功导出并下载，内容正确", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据导出 - 大量数据", "type": "性能", "priority": "中",
             "preconditions": "系统正常运行，已登录，存在大量数据", "steps": ["进入数据列表页面", "选择大量数据", "点击导出按钮", "验证导出过程"],
             "expected_result": "系统正常处理，导出成功，无超时", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_detail_cases(self, patterns: List[str]) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "详情查看 - 正常查看", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行，已登录，存在数据", "steps": ["进入数据列表页面", "点击数据查看详情", "验证详情内容"],
             "expected_result": "详情页面正确显示数据所有信息", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_from_text(self, content: str, doc_type: str) -> List[Dict]:
        test_cases = []
        if doc_type == "api":
            test_cases.extend(self._generate_api_cases(content))
        else:
            functions = self._extract_functions(content)
            requirements = self._extract_requirements(content)
            key_features = self._extract_key_features(content)
            
            for func in functions:
                test_cases.extend(self._generate_cases_for_function(func))
            for req in requirements:
                test_cases.extend(self._generate_cases_for_requirement(req))
            for feature in key_features:
                test_cases.extend(self._generate_cases_for_feature(feature, content))
        
        return test_cases

    def _extract_functions(self, content: str) -> List[str]:
        functions = []
        
        patterns = [
            r'功能[:：]\s*(.+?)(?=\n|$)',
            r'功能点[:：]\s*(.+?)(?=\n|$)',
            r'模块[:：]\s*(.+?)(?=\n|$)',
            r'接口[:：]\s*(.+?)(?=\n|$)',
            r'操作[:：]\s*(.+?)(?=\n|$)',
            r'可以(.+?)(?=，|。|；|$)',
            r'支持(.+?)(?=，|。|；|$)',
            r'能够(.+?)(?=，|。|；|$)',
            r'实现(.+?)(?=，|。|；|$)',
            r'提供(.+?)(?=，|。|；|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for m in matches:
                func = m.strip()
                if func and len(func) > 2 and len(func) < 50:
                    functions.append(func)
        
        return list(set(functions))

    def _extract_requirements(self, content: str) -> List[str]:
        requirements = []
        
        patterns = [
            r'需求[:：]\s*(.+?)(?=\n|$)',
            r'要求[:：]\s*(.+?)(?=\n|$)',
            r'必须[:：]\s*(.+?)(?=\n|$)',
            r'应该[:：]\s*(.+?)(?=\n|$)',
            r'需要(.+?)(?=，|。|；|$)',
            r'不得(.+?)(?=，|。|；|$)',
            r'禁止(.+?)(?=，|。|；|$)',
            r'允许(.+?)(?=，|。|；|$)',
            r'不允许(.+?)(?=，|。|；|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for m in matches:
                req = m.strip()
                if req and len(req) > 2 and len(req) < 100:
                    requirements.append(req)
        
        return list(set(requirements))
    
    def _extract_key_features(self, content: str) -> List[str]:
        features = []
        
        keywords = [
            '登录', '注册', '认证', '验证', '授权', '密码', '用户名', '邮箱', '手机',
            '查询', '搜索', '筛选', '过滤', '排序', '分页',
            '新增', '创建', '添加', '删除', '修改', '编辑', '更新',
            '导入', '导出', '下载', '上传',
            '审批', '审核', '确认', '拒绝',
            '配置', '设置', '管理', '监控',
            '报表', '统计', '分析', '图表',
            '任务', '调度', '定时', '执行'
        ]
        
        for keyword in keywords:
            if keyword in content:
                features.append(keyword)
        
        return features

    def _generate_api_cases(self, content: str) -> List[Dict]:
        test_cases = []
        endpoints = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/]+)', content)
        for method, endpoint in endpoints:
            test_cases.extend([
                {"id": str(uuid.uuid4()), "name": f"{method} {endpoint} - 正常请求", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": [f"发送{method}请求到{endpoint}", "验证响应状态码为200", "验证响应数据格式正确"],
                 "expected_result": f"{endpoint}接口正常返回数据", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{method} {endpoint} - 参数缺失", "type": "边界", "priority": "中",
                 "preconditions": "系统正常运行", "steps": [f"发送{method}请求到{endpoint}，不携带必要参数", "验证响应状态码为400"],
                 "expected_result": "接口返回参数错误提示", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{method} {endpoint} - 未授权访问", "type": "安全", "priority": "高",
                 "preconditions": "系统正常运行，用户未登录", "steps": [f"发送{method}请求到{endpoint}，不携带认证信息", "验证响应状态码为401或403"],
                 "expected_result": "接口拒绝未授权访问", "status": "未执行", "created_at": datetime.now().isoformat()}
            ])
        return test_cases

    def _generate_cases_for_function(self, func_name: str) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": f"{func_name} - 正常操作", "type": "功能", "module": func_name,
             "priority": "高", "preconditions": "系统正常运行",
             "steps": [f"进入{func_name}功能页面", "按照正常流程操作", "验证操作结果"],
             "expected_result": f"{func_name}功能正常执行", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": f"{func_name} - 异常输入", "type": "异常", "module": func_name,
             "priority": "中", "preconditions": "系统正常运行",
             "steps": [f"进入{func_name}功能页面", "输入无效数据", "验证系统反馈"],
             "expected_result": "系统给出友好的错误提示", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": f"{func_name} - 边界条件", "type": "边界", "module": func_name,
             "priority": "中", "preconditions": "系统正常运行",
             "steps": [f"进入{func_name}功能页面", "输入边界值数据", "验证系统处理能力"],
             "expected_result": "系统正确处理边界情况", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_cases_for_feature(self, feature: str, content: str) -> List[Dict]:
        feature_templates = {
            '登录': [
                {"id": str(uuid.uuid4()), "name": f"{feature} - 正常登录", "type": "功能", "module": "用户认证", "priority": "高",
                 "preconditions": "系统正常运行，存在有效用户账号", "steps": ["进入登录页面", "输入正确用户名", "输入正确密码", "点击登录按钮", "验证登录结果"],
                 "expected_result": "成功登录系统，跳转到首页", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature} - 错误密码", "type": "异常", "module": "用户认证", "priority": "高",
                 "preconditions": "系统正常运行，存在有效用户账号", "steps": ["进入登录页面", "输入正确用户名", "输入错误密码", "点击登录按钮", "验证系统反馈"],
                 "expected_result": "系统提示密码错误，不允许登录", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature} - 空用户名", "type": "边界", "priority": "中",
                 "preconditions": "系统正常运行", "steps": ["进入登录页面", "不输入用户名", "输入密码", "点击登录按钮", "验证系统反馈"],
                 "expected_result": "系统提示用户名不能为空", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '注册': [
                {"id": str(uuid.uuid4()), "name": f"{feature} - 正常注册", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行", "steps": ["进入注册页面", "填写完整注册信息", "点击注册按钮", "验证注册结果"],
                 "expected_result": "注册成功，自动登录或跳转到登录页面", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature} - 重复用户名", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行，存在已注册用户", "steps": ["进入注册页面", "使用已存在的用户名注册", "点击注册按钮", "验证系统反馈"],
                 "expected_result": "系统提示用户名已存在", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '密码': [
                {"id": str(uuid.uuid4()), "name": f"{feature}修改 - 正常修改", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入密码修改页面", "输入原密码", "输入新密码", "确认新密码", "点击确认按钮", "验证修改结果"],
                 "expected_result": "密码修改成功，下次登录需使用新密码", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}修改 - 原密码错误", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入密码修改页面", "输入错误原密码", "输入新密码", "点击确认按钮", "验证系统反馈"],
                 "expected_result": "系统提示原密码错误，不允许修改", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '查询': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 关键字查询", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入查询页面", "输入关键字", "点击查询按钮", "验证查询结果"],
                 "expected_result": "正确显示包含关键字的记录", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 空关键字", "type": "边界", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入查询页面", "不输入关键字直接查询", "验证查询结果"],
                 "expected_result": "显示全部数据或提示输入关键字", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '新增': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常新增", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入新增页面", "填写完整信息", "点击保存按钮", "验证保存结果"],
                 "expected_result": "数据新增成功，返回列表页面", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 必填项缺失", "type": "边界", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入新增页面", "不填写必填字段", "点击保存按钮", "验证系统反馈"],
                 "expected_result": "系统提示必填项不能为空", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '删除': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常删除", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在可删除数据", "steps": ["进入列表页面", "选择要删除的数据", "点击删除按钮", "确认删除", "验证删除结果"],
                 "expected_result": "数据删除成功，列表中不再显示", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 删除不存在数据", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["尝试删除已被删除的数据", "验证系统反馈"],
                 "expected_result": "系统提示数据不存在或已被删除", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '修改': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常修改", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在可修改数据", "steps": ["进入编辑页面", "修改数据信息", "点击保存按钮", "验证修改结果"],
                 "expected_result": "数据修改成功，信息更新正确", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '导出': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常导出", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入列表页面", "选择数据", "点击导出按钮", "选择导出格式", "验证导出结果"],
                 "expected_result": "文件成功导出并下载", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '导入': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常导入", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入导入页面", "选择正确格式的文件", "点击导入按钮", "验证导入结果"],
                 "expected_result": "数据导入成功，列表中显示新数据", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 格式错误", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入导入页面", "选择格式错误的文件", "点击导入按钮", "验证系统反馈"],
                 "expected_result": "系统提示文件格式错误，不允许导入", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '上传': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常上传", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入上传页面", "选择符合要求的文件", "点击上传按钮", "验证上传结果"],
                 "expected_result": "文件上传成功", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 文件过大", "type": "边界", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入上传页面", "选择超过大小限制的文件", "点击上传按钮", "验证系统反馈"],
                 "expected_result": "系统提示文件大小超过限制", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '报表': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 生成报表", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入报表页面", "选择报表类型", "设置查询条件", "点击生成按钮", "验证报表内容"],
                 "expected_result": "报表生成成功，数据准确", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '统计': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 查看统计", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入统计页面", "查看各项统计数据", "验证数据准确性"],
                 "expected_result": "统计数据正确显示", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '审核': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 通过审核", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待审核数据", "steps": ["进入审核页面", "查看待审核数据", "点击通过按钮", "验证审核结果"],
                 "expected_result": "数据审核通过，状态更新", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 拒绝审核", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待审核数据", "steps": ["进入审核页面", "查看待审核数据", "点击拒绝按钮", "填写拒绝原因", "验证审核结果"],
                 "expected_result": "数据审核被拒绝，状态更新，记录拒绝原因", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '认证': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常认证", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行", "steps": ["进入认证页面", "输入认证信息", "提交认证", "验证认证结果"],
                 "expected_result": "认证成功，获得相应权限", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '授权': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 分配权限", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，管理员已登录", "steps": ["进入权限管理页面", "选择用户或角色", "分配权限", "保存配置", "验证权限生效"],
                 "expected_result": "权限分配成功，用户获得相应访问权限", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '验证': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 验证码验证", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行", "steps": ["进入需要验证的页面", "获取验证码", "输入正确验证码", "提交验证", "验证结果"],
                 "expected_result": "验证码验证通过", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 错误验证码", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行", "steps": ["进入需要验证的页面", "输入错误验证码", "提交验证", "验证系统反馈"],
                 "expected_result": "系统提示验证码错误", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '搜索': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 精确搜索", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入搜索页面", "输入精确关键词", "点击搜索按钮", "验证搜索结果"],
                 "expected_result": "正确显示匹配的记录", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '筛选': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 多条件筛选", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入列表页面", "设置多个筛选条件", "点击筛选按钮", "验证筛选结果"],
                 "expected_result": "正确显示符合所有条件的记录", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '排序': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 升序排序", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入列表页面", "点击列标题进行升序排序", "验证排序结果"],
                 "expected_result": "数据按指定列升序排列", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 降序排序", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入列表页面", "再次点击列标题进行降序排序", "验证排序结果"],
                 "expected_result": "数据按指定列降序排列", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '分页': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 翻页", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录，数据超过一页", "steps": ["进入列表页面", "点击下一页按钮", "验证分页结果"],
                 "expected_result": "成功跳转到下一页，数据正确显示", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '配置': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 修改配置", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，管理员已登录", "steps": ["进入配置页面", "修改配置项", "点击保存按钮", "验证配置生效"],
                 "expected_result": "配置修改成功，系统按新配置运行", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '任务': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 创建任务", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入任务管理页面", "点击创建任务", "填写任务信息", "保存任务", "验证任务创建"],
                 "expected_result": "任务创建成功，显示在任务列表中", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 执行任务", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待执行任务", "steps": ["进入任务管理页面", "选择任务", "点击执行按钮", "验证任务执行结果"],
                 "expected_result": "任务执行成功，生成执行日志", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '调度': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 设置定时任务", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入调度页面", "创建定时任务", "设置执行时间", "保存配置", "验证定时任务"],
                 "expected_result": "定时任务创建成功，按设定时间执行", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '邮箱': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 发送邮件", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入邮件功能页面", "填写收件人邮箱", "填写邮件内容", "点击发送按钮", "验证发送结果"],
                 "expected_result": "邮件发送成功", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '手机': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 发送短信", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入短信功能页面", "填写手机号码", "填写短信内容", "点击发送按钮", "验证发送结果"],
                 "expected_result": "短信发送成功", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '监控': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 查看监控数据", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入监控页面", "查看各项监控指标", "验证数据实时性"],
                 "expected_result": "监控数据实时显示，准确反映系统状态", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '管理': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 查看管理列表", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入管理页面", "查看数据列表", "验证数据完整性"],
                 "expected_result": "数据列表正确显示，支持搜索和筛选", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '图表': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 查看图表", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入图表页面", "查看各类图表", "验证图表数据准确性"],
                 "expected_result": "图表正确渲染，数据准确", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '分析': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 数据分析", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入分析页面", "选择分析维度", "查看分析结果", "验证分析准确性"],
                 "expected_result": "分析结果正确显示，提供有价值的洞察", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '设置': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 修改设置", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入设置页面", "修改设置项", "点击保存按钮", "验证设置生效"],
                 "expected_result": "设置修改成功，系统按新设置运行", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '定时': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 设置定时任务", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入定时任务页面", "创建新任务", "设置执行时间", "保存任务", "验证任务执行"],
                 "expected_result": "定时任务创建成功，按设定时间执行", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '执行': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 执行操作", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入操作页面", "选择要执行的操作", "点击执行按钮", "验证执行结果"],
                 "expected_result": "操作执行成功，生成执行日志", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '确认': [
                {"id": str(uuid.uuid4()), "name": f"{feature}操作 - 正常确认", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待确认数据", "steps": ["进入确认页面", "查看待确认数据", "点击确认按钮", "验证确认结果"],
                 "expected_result": "数据确认成功，状态更新", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '拒绝': [
                {"id": str(uuid.uuid4()), "name": f"{feature}操作 - 正常拒绝", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待处理数据", "steps": ["进入处理页面", "查看待处理数据", "点击拒绝按钮", "填写拒绝原因", "验证拒绝结果"],
                 "expected_result": "数据被拒绝，状态更新，记录拒绝原因", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '审批': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 通过审批", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待审批数据", "steps": ["进入审批页面", "查看待审批数据", "点击通过按钮", "验证审批结果"],
                 "expected_result": "数据审批通过，状态更新", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 驳回审批", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在待审批数据", "steps": ["进入审批页面", "查看待审批数据", "点击驳回按钮", "填写驳回原因", "验证审批结果"],
                 "expected_result": "数据被驳回，状态更新，记录驳回原因", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '用户名': [
                {"id": str(uuid.uuid4()), "name": f"{feature}验证 - 正常用户名", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行", "steps": ["进入注册或登录页面", "输入符合规则的用户名", "验证系统反馈"],
                 "expected_result": "系统接受有效用户名", "status": "未执行", "created_at": datetime.now().isoformat()},
                {"id": str(uuid.uuid4()), "name": f"{feature}验证 - 特殊字符", "type": "异常", "priority": "中",
                 "preconditions": "系统正常运行", "steps": ["进入注册页面", "输入包含特殊字符的用户名", "验证系统反馈"],
                 "expected_result": "系统提示用户名格式错误", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '下载': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常下载", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在可下载文件", "steps": ["进入下载页面", "选择要下载的文件", "点击下载按钮", "验证下载结果"],
                 "expected_result": "文件成功下载到本地", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '创建': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常创建", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入创建页面", "填写完整信息", "点击创建按钮", "验证创建结果"],
                 "expected_result": "数据创建成功，返回列表页面", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '添加': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常添加", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录", "steps": ["进入添加页面", "填写添加信息", "点击添加按钮", "验证添加结果"],
                 "expected_result": "数据添加成功，显示在列表中", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '编辑': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常编辑", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在可编辑数据", "steps": ["进入编辑页面", "修改数据信息", "点击保存按钮", "验证编辑结果"],
                 "expected_result": "数据编辑成功，信息更新正确", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '更新': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常更新", "type": "功能", "priority": "高",
                 "preconditions": "系统正常运行，用户已登录，存在可更新数据", "steps": ["进入更新页面", "修改数据信息", "点击更新按钮", "验证更新结果"],
                 "expected_result": "数据更新成功，信息更新正确", "status": "未执行", "created_at": datetime.now().isoformat()}
            ],
            '过滤': [
                {"id": str(uuid.uuid4()), "name": f"{feature}功能 - 正常过滤", "type": "功能", "priority": "中",
                 "preconditions": "系统正常运行，用户已登录，存在数据", "steps": ["进入列表页面", "设置过滤条件", "验证过滤结果"],
                 "expected_result": "正确显示符合过滤条件的记录", "status": "未执行", "created_at": datetime.now().isoformat()}
            ]
        }
        
        return feature_templates.get(feature, [])

    def _generate_cases_for_requirement(self, requirement: str) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": f"需求验证 - {requirement[:30]}", "type": "功能", "priority": "高",
             "preconditions": "系统正常运行", "steps": [f"定位到与'{requirement}'相关的功能", "执行相关操作", "验证需求是否满足"],
             "expected_result": f"需求'{requirement}'得到满足", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def _generate_default_cases(self, content: str) -> List[Dict]:
        return [
            {"id": str(uuid.uuid4()), "name": "系统登录 - 正常登录", "type": "功能", "module": "用户认证", "priority": "高",
             "preconditions": "系统正常运行", "steps": ["打开登录页面", "输入正确的用户名和密码", "点击登录按钮", "验证跳转结果"],
             "expected_result": "成功登录系统，进入主页面", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "系统登录 - 错误密码", "type": "异常", "module": "用户认证", "priority": "高",
             "preconditions": "系统正常运行", "steps": ["打开登录页面", "输入正确用户名和错误密码", "点击登录按钮", "验证系统反馈"],
             "expected_result": "系统提示密码错误，不允许登录", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据查询 - 正常查询", "type": "功能", "module": "数据管理", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据查询页面", "输入查询条件", "点击查询按钮", "验证查询结果"],
             "expected_result": "查询结果正确显示", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据查询 - 空条件", "type": "边界", "module": "数据管理", "priority": "中",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据查询页面", "不输入任何查询条件", "点击查询按钮", "验证系统处理"],
             "expected_result": "系统正确处理空条件查询", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据新增 - 正常新增", "type": "功能", "module": "数据管理", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据新增页面", "填写完整的新增数据", "点击保存按钮", "验证保存结果"],
             "expected_result": "数据成功新增，提示保存成功", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据修改 - 正常修改", "type": "功能", "module": "数据管理", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据列表页面", "选择一条数据进行修改", "修改数据内容", "点击保存按钮", "验证修改结果"],
             "expected_result": "数据成功修改，提示修改成功", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "数据删除 - 正常删除", "type": "功能", "module": "数据管理", "priority": "高",
             "preconditions": "系统正常运行，已登录", "steps": ["进入数据列表页面", "选择一条数据进行删除", "确认删除操作", "验证删除结果"],
             "expected_result": "数据成功删除，提示删除成功", "status": "未执行", "created_at": datetime.now().isoformat()},
            {"id": str(uuid.uuid4()), "name": "权限验证 - 未授权访问", "type": "安全", "module": "权限管理", "priority": "高",
             "preconditions": "系统正常运行", "steps": ["未登录状态下直接访问受限页面", "验证系统响应"],
             "expected_result": "系统重定向到登录页面或拒绝访问", "status": "未执行", "created_at": datetime.now().isoformat()}
        ]

    def calculate_coverage(self, test_cases: List[Dict]) -> Dict:
        if isinstance(test_cases, dict) and "test_cases" in test_cases:
            test_cases = test_cases["test_cases"]
        
        total = len(test_cases)
        if total == 0:
            return {"total_cases": 0, "by_type": {}, "by_priority": {}, "coverage_rate": 0, "uncovered_items": []}
        
        by_type = {}
        by_priority = {}
        
        for case in test_cases:
            case_type = case.get("type", "其他")
            priority = case.get("priority", "中")
            by_type[case_type] = by_type.get(case_type, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        covered_items = len(by_type)
        total_items = 8
        
        return {
            "total_cases": total,
            "by_type": by_type,
            "by_priority": by_priority,
            "coverage_rate": min(100, int(covered_items / total_items * 100)),
            "uncovered_items": []
        }

    def get_templates(self) -> Dict:
        return self.templates
    
    def get_strategies(self) -> Dict:
        strategies = {}
        for key, value in self.generation_rules.items():
            strategies[key] = {
                "name": value["name"],
                "description": value["description"]
            }
        return strategies
    
    def analyze_requirements(self, content: str) -> Dict:
        if self.ai_service and self.ai_service.api_key:
            try:
                return self.ai_service.analyze_requirements(content)
            except Exception as e:
                print(f"AI需求分析失败: {str(e)}")
        
        return {"features": [], "test_points": [], "risks": [], "suggestions": []}
    
    def optimize_cases(self, test_cases: List[Dict], content: str) -> Dict:
        if isinstance(test_cases, dict) and "test_cases" in test_cases:
            test_cases = test_cases["test_cases"]
        
        if self.ai_service and self.ai_service.api_key:
            try:
                return self.ai_service.optimize_cases(test_cases, content)
            except Exception as e:
                print(f"AI用例优化失败: {str(e)}")
        
        return {"optimized_cases": test_cases, "changes": []}