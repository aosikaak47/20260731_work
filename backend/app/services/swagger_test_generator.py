import json
import uuid
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


HTTP_METHODS = ["get", "post", "put", "delete", "patch", "options", "head"]

SENSITIVE_KEYWORDS = [
    "password", "token", "secret", "key", "phone", "mobile", "idcard",
    "bankcard", "email", "address", "name", "身份证", "手机", "密码",
    "敏感", "token", "secret", "credential", "auth"
]

DATE_PATTERNS = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "日期格式(yyyy-MM-dd)"),
    (re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"), "ISO日期时间格式"),
    (re.compile(r"^\d{11}$"), "手机号格式"),
    (re.compile(r"^\d{17}[\dXx]$"), "身份证号格式"),
    (re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"), "UUID格式"),
    (re.compile(r"^\d{6}$"), "邮政编码格式"),
    (re.compile(r"^\d{4}[- ]?\d{3}[- ]?\d{4}$"), "电话号码格式"),
]


class SwaggerTestGenerator:
    def __init__(self):
        pass

    def parse_document(self, swagger_data: dict) -> dict:
        openapi_version = swagger_data.get("openapi", "")
        swagger_version = swagger_data.get("swagger", "")
        info = swagger_data.get("info", {})
        title = info.get("title", "API文档")
        version = info.get("version", "1.0.0")

        base_url = ""
        if openapi_version:
            servers = swagger_data.get("servers", [])
            if servers:
                base_url = servers[0].get("url", "")
        elif swagger_version:
            host = swagger_data.get("host", "")
            base_path = swagger_data.get("basePath", "")
            schemes = swagger_data.get("schemes", ["http"])
            if host:
                base_url = f"{schemes[0]}://{host}{base_path}"

        paths = swagger_data.get("paths", {})
        api_definitions = []
        shared_params = swagger_data.get("components", {}).get("parameters", {}) if openapi_version else {}
        shared_definitions = swagger_data.get("components", {}).get("schemas", {}) if openapi_version else swagger_data.get("definitions", {})

        for path, path_item in paths.items():
            path_level_params = path_item.get("parameters", [])
            if not path_level_params and shared_params:
                path_level_params = []

            for method, operation in path_item.items():
                if method.lower() not in HTTP_METHODS:
                    continue
                if method.startswith("x-") or method == "parameters":
                    continue

                op = self._resolve_operation(operation, shared_definitions)
                api_def = self._extract_api_metadata(
                    method=method,
                    path=path,
                    operation=op,
                    path_level_params=path_level_params,
                    shared_definitions=shared_definitions,
                    base_url=base_url,
                    doc_title=title
                )
                api_definitions.append(api_def)

        return {
            "title": title,
            "version": version,
            "base_url": base_url,
            "total_apis": len(api_definitions),
            "apis": api_definitions
        }

    def _resolve_operation(self, operation: dict, shared_defs: dict) -> dict:
        if "$ref" in operation:
            ref_path = operation["$ref"]
            ref_name = ref_path.split("/")[-1]
            if ref_name in shared_defs:
                return shared_defs[ref_name]
        return operation

    def _extract_api_metadata(self, method: str, path: str, operation: dict,
                               path_level_params: list, shared_definitions: dict,
                               base_url: str, doc_title: str) -> dict:
        summary = operation.get("summary", "")
        description = operation.get("description", "")
        operation_id = operation.get("operationId", "")
        tags = operation.get("tags", [])

        tag_name = tags[0] if tags else doc_title

        all_params = []
        if path_level_params:
            for p in path_level_params:
                all_params.append(self._resolve_param_ref(p, shared_definitions))
        op_params = operation.get("parameters", [])
        if op_params:
            for p in op_params:
                all_params.append(self._resolve_param_ref(p, shared_definitions))

        request_body = self._extract_request_body(operation, shared_definitions)
        responses = operation.get("responses", {})

        param_details = []
        for param in all_params:
            param_details.append(self._extract_param_detail(param, shared_definitions))

        response_details = self._extract_response_details(responses, shared_definitions)

        is_sensitive = self._detect_sensitive_data(param_details, request_body)

        case_name = summary or operation_id or f"{method.upper()} {path}"

        return {
            "id": str(uuid.uuid4()),
            "name": case_name,
            "module": tag_name,
            "method": method.upper(),
            "url": path,
            "base_url": base_url,
            "description": description or summary,
            "operation_id": operation_id,
            "is_sensitive": is_sensitive,
            "params": param_details,
            "request_body": request_body,
            "responses": response_details,
            "tags": tags,
            "has_path_params": any(p["in"] == "path" for p in param_details),
            "has_query_params": any(p["in"] == "query" for p in param_details),
            "has_body": request_body is not None and request_body.get("schema") is not None,
            "is_list_endpoint": self._is_list_endpoint(case_name, path, method.upper()),
            "is_write_endpoint": method.upper() in ["POST", "PUT", "PATCH", "DELETE"],
            "is_read_endpoint": method.upper() == "GET",
            "supports_auth": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _resolve_param_ref(self, param: dict, shared_defs: dict) -> dict:
        if "$ref" in param:
            ref_path = param["$ref"]
            ref_name = ref_path.split("/")[-1]
            if ref_name in shared_defs:
                resolved = shared_defs[ref_name]
                resolved["name"] = param.get("name", "")
                resolved["in"] = param.get("in", "")
                return resolved
        return param

    def _extract_param_detail(self, param: dict, shared_defs: dict) -> dict:
        schema = param.get("schema", {})
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in shared_defs:
                schema = shared_defs[ref_name]

        param_type = schema.get("type", param.get("type", "string"))
        if not param_type and "$ref" in schema:
            param_type = "object"

        enum_values = schema.get("enum", [])
        min_val = schema.get("minimum", None)
        max_val = schema.get("maximum", None)
        min_length = schema.get("minLength", None)
        max_length = schema.get("maxLength", None)
        pattern = schema.get("pattern", None)
        format_val = schema.get("format", "")
        description = param.get("description", "")
        example = param.get("example", None)

        nested_props = None
        if param_type == "object" and schema.get("properties"):
            nested_props = self._extract_nested_props(schema.get("properties", {}), shared_defs)
        elif "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in shared_defs and shared_defs[ref_name].get("properties"):
                nested_props = self._extract_nested_props(shared_defs[ref_name]["properties"], shared_defs)

        items_schema = None
        if param_type == "array" and schema.get("items"):
            items_schema = schema.get("items", {})
            if "$ref" in items_schema:
                ref_name = items_schema["$ref"].split("/")[-1]
                if ref_name in shared_defs:
                    items_schema = shared_defs[ref_name]

        is_required = param.get("required", False)
        param_in = param.get("in", "query")

        inferred_format = self._infer_param_format(param.get("name", ""), description, pattern, format_val)

        return {
            "name": param.get("name", ""),
            "in": param_in,
            "type": param_type,
            "required": is_required,
            "description": description,
            "example": example or self._generate_example_value(param_type, enum_values, min_val, max_val, param.get("name", "")),
            "enum": enum_values,
            "minimum": min_val,
            "maximum": max_val,
            "minLength": min_length,
            "maxLength": max_length,
            "pattern": pattern,
            "format": format_val,
            "nested_props": nested_props,
            "items_schema": items_schema,
            "is_sensitive": self._is_param_sensitive(param.get("name", ""), description),
            "inferred_format": inferred_format
        }

    def _extract_nested_props(self, properties: dict, shared_defs: dict) -> list:
        result = []
        for prop_name, prop_schema in properties.items():
            if "$ref" in prop_schema:
                ref_name = prop_schema["$ref"].split("/")[-1]
                if ref_name in shared_defs:
                    prop_schema = shared_defs[ref_name]

            prop_type = prop_schema.get("type", "string")
            if not prop_type and "$ref" in prop_schema:
                prop_type = "object"

            result.append({
                "name": prop_name,
                "type": prop_type,
                "required": prop_schema.get("required", False),
                "description": prop_schema.get("description", ""),
                "example": self._generate_example_value(prop_type, prop_schema.get("enum", []),
                                                          prop_schema.get("minimum"), prop_schema.get("maximum"),
                                                          prop_name),
                "enum": prop_schema.get("enum", []),
                "minimum": prop_schema.get("minimum"),
                "maximum": prop_schema.get("maximum"),
                "minLength": prop_schema.get("minLength"),
                "maxLength": prop_schema.get("maxLength"),
                "is_sensitive": self._is_param_sensitive(prop_name, prop_schema.get("description", ""))
            })
        return result

    def _extract_request_body(self, operation: dict, shared_defs: dict) -> Optional[dict]:
        request_body = operation.get("requestBody", {})
        if not request_body:
            return None

        content = request_body.get("content", {})
        for content_type, content_data in content.items():
            schema = content_data.get("schema", {})
            if "$ref" in schema:
                ref_name = schema["$ref"].split("/")[-1]
                if ref_name in shared_defs:
                    schema = shared_defs[ref_name]

            example = content_data.get("example", None)
            if example is None:
                examples = content_data.get("examples", {})
                if examples:
                    first_key = list(examples.keys())[0]
                    example = examples[first_key].get("value", None)

            return {
                "content_type": content_type,
                "schema": schema,
                "example": example,
                "required": request_body.get("required", False),
                "description": request_body.get("description", "")
            }
        return None

    def _extract_response_details(self, responses: dict, shared_defs: dict) -> list:
        result = []
        for code, resp in responses.items():
            resp_detail = {
                "code": code,
                "description": resp.get("description", ""),
                "is_success": code.startswith("2"),
                "schema": None,
                "example": None
            }

            content = resp.get("content", {})
            for content_type, content_data in content.items():
                schema = content_data.get("schema", {})
                if "$ref" in schema:
                    ref_name = schema["$ref"].split("/")[-1]
                    if ref_name in shared_defs:
                        schema = shared_defs[ref_name]

                resp_detail["schema"] = schema
                example = content_data.get("example", None)
                if example is None:
                    examples = content_data.get("examples", {})
                    if examples:
                        first_key = list(examples.keys())[0]
                        example = examples[first_key].get("value", None)
                resp_detail["example"] = example
                break

            result.append(resp_detail)
        return result

    def _detect_sensitive_data(self, params: list, request_body: Optional[dict]) -> bool:
        for p in params:
            if p.get("is_sensitive"):
                return True
        if request_body and request_body.get("schema"):
            schema = request_body["schema"]
            if schema.get("properties"):
                for prop_name in schema["properties"]:
                    if self._is_param_sensitive(prop_name, ""):
                        return True
        return False

    def _is_param_sensitive(self, name: str, description: str) -> bool:
        name_lower = name.lower()
        desc_lower = description.lower()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword.lower() in name_lower or keyword.lower() in desc_lower:
                return True
        return False

    def _infer_param_format(self, name: str, description: str, pattern: str, format_val: str) -> str:
        if format_val:
            return format_val
        if pattern:
            return pattern
        name_lower = name.lower()
        for keyword, fmt in [("phone", "手机号"), ("mobile", "手机号"), ("idcard", "身份证号"),
                             ("email", "邮箱"), ("password", "密码"), ("date", "日期"),
                             ("time", "时间"), ("uuid", "UUID"), ("token", "Token")]:
            if keyword in name_lower:
                return fmt
        return ""

    def _is_list_endpoint(self, name: str, path: str, method: str) -> bool:
        if method != "GET":
            return False
        list_indicators = ["列表", "list", "query", "search", "get all", "find", "分页"]
        name_lower = name.lower()
        for indicator in list_indicators:
            if indicator in name_lower or indicator in path.lower():
                return True
        return False

    def _generate_example_value(self, param_type: str, enum_values: list,
                                 min_val, max_val, name: str) -> Any:
        if enum_values:
            return enum_values[0]
        name_lower = name.lower()
        if "phone" in name_lower or "mobile" in name_lower:
            return "13800138000"
        if "idcard" in name_lower:
            return "110101199003071234"
        if "email" in name_lower:
            return "test@example.com"
        if "password" in name_lower:
            return "Test@123456"
        if "date" in name_lower:
            return "2024-01-15"
        if "time" in name_lower:
            return "2024-01-15 10:30:00"
        if "uuid" in name_lower:
            return "550e8400-e29b-41d4-a716-446655440000"

        if param_type == "string":
            return name or "test_string"
        elif param_type == "integer" or param_type == "number":
            if min_val is not None:
                return min_val + 1
            return 1
        elif param_type == "boolean":
            return True
        elif param_type == "array":
            return []
        elif param_type == "object":
            return {}
        return None

    def generate_all_test_cases(self, api_definitions: list) -> dict:
        functional_cases = []
        performance_cases = []
        security_cases = []

        for api in api_definitions:
            func_cases = self._generate_functional_cases(api)
            perf_cases = self._generate_performance_cases(api)
            sec_cases = self._generate_security_cases(api)

            functional_cases.extend(func_cases)
            performance_cases.extend(perf_cases)
            security_cases.extend(sec_cases)

        all_cases = functional_cases + performance_cases + security_cases

        features = self._aggregate_features(api_definitions, all_cases)

        risk_assessment = self._generate_risk_assessment(api_definitions, functional_cases,
                                                          performance_cases, security_cases)

        postman_collection = self._generate_postman_collection(api_definitions)
        jmeter_template = self._generate_jmeter_template(api_definitions)
        pytest_script = self._generate_pytest_script(api_definitions)

        return {
            "test_cases": all_cases,
            "functional_cases": functional_cases,
            "performance_cases": performance_cases,
            "security_cases": security_cases,
            "features": features,
            "risk_assessment": risk_assessment,
            "postman_collection": postman_collection,
            "jmeter_template": jmeter_template,
            "pytest_script": pytest_script,
            "stats": {
                "total": len(all_cases),
                "functional": len(functional_cases),
                "performance": len(performance_cases),
                "security": len(security_cases),
                "apis_count": len(api_definitions)
            }
        }

    def _generate_functional_cases(self, api: dict) -> list:
        cases = []
        api_name = api["name"]
        method = api["method"]
        url = api["url"]
        module = api["module"]
        params = api.get("params", [])
        request_body = api.get("request_body")
        responses = api.get("responses", [])
        success_code = self._get_success_code(responses)

        has_required = any(p["required"] for p in params)
        has_body = api.get("has_body", False)
        is_list = api.get("is_list_endpoint", False)
        is_write = api.get("is_write_endpoint", False)
        is_read = api.get("is_read_endpoint", False)

        base_precondition = f"API服务正常运行\nBase URL: {api.get('base_url', '')}"

        # ① 正向正常用例
        valid_params = self._build_valid_params(params, request_body)
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【功能-正向】{api_name} - 正常请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "正向正常",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": [
                f"构造有效请求参数: {json.dumps(valid_params, ensure_ascii=False)[:200]}",
                f"发送{method}请求: {url}",
                f"检查响应状态码为{success_code}"
            ],
            "expected_result": f"返回状态码{success_code}，响应数据结构正确，业务逻辑处理正常",
            "test_tags": ["功能", "正向"],
            "is_sensitive": api.get("is_sensitive", False),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_info": {
                "method": method,
                "url": url,
                "params": valid_params,
                "request_body": request_body
            }
        })

        # ② 必填参数缺失场景
        required_params = [p for p in params if p["required"]]
        for rp in required_params:
            missing_params = self._build_valid_params(params, request_body)
            self._remove_param_by_name(missing_params, rp["name"])
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-必填缺失】{api_name} - 缺少{rp['name']}",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "必填参数缺失",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"移除必填参数: {rp['name']}",
                    f"发送{method}请求: {url}"
                ],
                "expected_result": f"返回400错误，提示缺少必填参数{rp['name']}",
                "test_tags": ["功能", "异常", "必填缺失"],
                "is_sensitive": api.get("is_sensitive", False),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "api_info": {
                    "method": method,
                    "url": url,
                    "params": missing_params
                }
            })

        if len(required_params) > 1:
            all_missing = self._build_valid_params(params, request_body)
            for rp in required_params:
                self._remove_param_by_name(all_missing, rp["name"])
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-必填缺失】{api_name} - 批量缺失所有必填参数",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "必填参数缺失",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"移除所有必填参数: {[p['name'] for p in required_params]}",
                    f"发送{method}请求: {url}"
                ],
                "expected_result": "返回400错误，提示参数校验失败",
                "test_tags": ["功能", "异常", "必填缺失"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # ③ 参数边界值场景
        for p in params:
            if p["type"] == "string":
                if p.get("maxLength"):
                    cases.append(self._create_boundary_case(api, p, "字符串最大长度",
                                                             p["maxLength"], base_precondition, success_code))
                if p.get("minLength") is not None:
                    cases.append(self._create_boundary_case(api, p, "字符串最小长度",
                                                             p["minLength"], base_precondition, success_code))
                cases.append(self._create_boundary_case(api, p, "空字符串",
                                                         "", base_precondition, success_code))
                cases.append(self._create_boundary_case(api, p, "超长字符串(边界+1)",
                                                         "a" * ((p.get("maxLength") or 255) + 1),
                                                         base_precondition, success_code))

            elif p["type"] in ["integer", "number"]:
                if p.get("minimum") is not None:
                    cases.append(self._create_boundary_case(api, p, "数字最小值",
                                                             p["minimum"], base_precondition, success_code))
                    cases.append(self._create_boundary_case(api, p, "数字最小值-1(越界)",
                                                             p["minimum"] - 1, base_precondition, success_code))
                if p.get("maximum") is not None:
                    cases.append(self._create_boundary_case(api, p, "数字最大值",
                                                             p["maximum"], base_precondition, success_code))
                    cases.append(self._create_boundary_case(api, p, "数字最大值+1(越界)",
                                                             p["maximum"] + 1, base_precondition, success_code))
                cases.append(self._create_boundary_case(api, p, "数字0值",
                                                         0, base_precondition, success_code))
                cases.append(self._create_boundary_case(api, p, "数字负值",
                                                         -1, base_precondition, success_code))

            if p.get("enum"):
                for i, ev in enumerate(p["enum"]):
                    if i == 0:
                        cases.append(self._create_boundary_case(api, p, f"枚举合法值: {ev}",
                                                                 ev, base_precondition, success_code))

        # ④ 参数异常格式
        for p in params:
            if p["type"] == "string":
                cases.append(self._create_format_case(api, p, "数字类型传入字符串",
                                                       12345, base_precondition))
                cases.append(self._create_format_case(api, p, "日期格式错乱",
                                                       "2024/13/45", base_precondition))
                inferred_fmt = p.get("inferred_format", "")
                if inferred_fmt == "手机号":
                    cases.append(self._create_format_case(api, p, "手机号正则不匹配",
                                                           "12345", base_precondition))
                elif inferred_fmt == "身份证号":
                    cases.append(self._create_format_case(api, p, "身份证号格式错误",
                                                           "12345", base_precondition))
                elif inferred_fmt == "UUID":
                    cases.append(self._create_format_case(api, p, "UUID格式错误",
                                                           "not-a-uuid", base_precondition))
            elif p["type"] == "boolean":
                cases.append(self._create_format_case(api, p, "布尔值传入数字",
                                                       1, base_precondition))

        # ⑤ 特殊字符入参
        for p in params:
            if p["type"] == "string":
                cases.append({
                    "id": str(uuid.uuid4()),
                    "name": f"【功能-特殊字符】{api_name} - {p['name']}首尾空格",
                    "module": module,
                    "feature": f"{method} {url}",
                    "type": "功能",
                    "sub_type": "特殊字符",
                    "priority": "中",
                    "preconditions": base_precondition,
                    "steps": [f"在参数{p['name']}首尾添加空格", f"发送{method}请求"],
                    "expected_result": "系统正确处理首尾空格，不应导致异常",
                    "test_tags": ["功能", "边界", "特殊字符"],
                    "is_sensitive": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                cases.append({
                    "id": str(uuid.uuid4()),
                    "name": f"【功能-特殊字符】{api_name} - {p['name']}特殊符号",
                    "module": module,
                    "feature": f"{method} {url}",
                    "type": "功能",
                    "sub_type": "特殊字符",
                    "priority": "中",
                    "preconditions": base_precondition,
                    "steps": [f"参数{p['name']}传入特殊符号: @#￥%&*", f"发送{method}请求"],
                    "expected_result": "特殊符号正确处理，无解析异常",
                    "test_tags": ["功能", "边界", "特殊字符"],
                    "is_sensitive": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                cases.append({
                    "id": str(uuid.uuid4()),
                    "name": f"【功能-特殊字符】{api_name} - {p['name']}中文全角符号",
                    "module": module,
                    "feature": f"{method} {url}",
                    "type": "功能",
                    "sub_type": "特殊字符",
                    "priority": "中",
                    "preconditions": base_precondition,
                    "steps": [f"参数{p['name']}传入中文全角符号: ＠＃￥％", f"发送{method}请求"],
                    "expected_result": "全角符号正确处理，无编码异常",
                    "test_tags": ["功能", "边界", "特殊字符"],
                    "is_sensitive": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        # ⑥ 权限/Token校验
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【功能-权限校验】{api_name} - 无Token请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "权限校验",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": ["不携带Token", f"发送{method}请求: {url}"],
            "expected_result": "返回401未授权错误",
            "test_tags": ["功能", "权限", "安全"],
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【功能-权限校验】{api_name} - 过期Token请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "权限校验",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": ["使用过期Token", f"发送{method}请求: {url}"],
            "expected_result": "返回401 Token过期错误",
            "test_tags": ["功能", "权限", "安全"],
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【功能-权限校验】{api_name} - 错误Token请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "权限校验",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": ["使用错误格式Token", f"发送{method}请求: {url}"],
            "expected_result": "返回401认证失败错误",
            "test_tags": ["功能", "权限", "安全"],
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # ⑦ 分页/列表专属场景
        if is_list:
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-分页】{api_name} - 页码=0",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "分页场景",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": ["传入page=0", f"发送{method}请求: {url}"],
                "expected_result": "返回400错误或自动修正为page=1",
                "test_tags": ["功能", "分页", "边界"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-分页】{api_name} - 超大页码",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "分页场景",
                "priority": "中",
                "preconditions": base_precondition,
                "steps": ["传入page=99999", f"发送{method}请求: {url}"],
                "expected_result": "返回空数据或合理错误提示",
                "test_tags": ["功能", "分页", "边界"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-分页】{api_name} - 每页条数=0",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "分页场景",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": ["传入pageSize=0", f"发送{method}请求: {url}"],
                "expected_result": "返回400错误或使用默认值",
                "test_tags": ["功能", "分页", "边界"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-分页】{api_name} - 每页条数超限",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "分页场景",
                "priority": "中",
                "preconditions": base_precondition,
                "steps": ["传入pageSize=10000(超限值)", f"发送{method}请求: {url}"],
                "expected_result": "返回400错误或限制最大值",
                "test_tags": ["功能", "分页", "边界"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # ⑧ 业务逻辑异常
        if is_write:
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-业务异常】{api_name} - 重复提交(幂等性)",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "业务逻辑异常",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"发送{method}请求创建资源",
                    "使用相同参数再次发送请求"
                ],
                "expected_result": "幂等处理：返回相同资源或提示已存在",
                "test_tags": ["功能", "业务异常", "幂等性"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        if is_read:
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【功能-业务异常】{api_name} - 查询不存在的资源",
                "module": module,
                "feature": f"{method} {url}",
                "type": "功能",
                "sub_type": "业务逻辑异常",
                "priority": "中",
                "preconditions": base_precondition,
                "steps": ["查询不存在的资源ID", f"发送{method}请求: {url}/99999"],
                "expected_result": "返回404资源不存在错误",
                "test_tags": ["功能", "业务异常"],
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return cases

    def _create_boundary_case(self, api: dict, param: dict, scenario: str,
                               value, precondition: str, success_code: str) -> dict:
        api_name = api["name"]
        method = api["method"]
        url = api["url"]
        module = api["module"]

        return {
            "id": str(uuid.uuid4()),
            "name": f"【功能-边界值】{api_name} - {param['name']} {scenario}",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "边界值",
            "priority": "高",
            "preconditions": precondition,
            "steps": [
                f"参数{param['name']}设置为: {str(value)[:100]}",
                f"发送{method}请求: {url}"
            ],
            "expected_result": f"边界值{scenario}下系统正确处理，返回合理状态码",
            "test_tags": ["功能", "边界值"],
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _create_format_case(self, api: dict, param: dict, scenario: str,
                              value, precondition: str) -> dict:
        api_name = api["name"]
        method = api["method"]
        url = api["url"]
        module = api["module"]

        return {
            "id": str(uuid.uuid4()),
            "name": f"【功能-格式异常】{api_name} - {param['name']} {scenario}",
            "module": module,
            "feature": f"{method} {url}",
            "type": "功能",
            "sub_type": "格式异常",
            "priority": "高",
            "preconditions": precondition,
            "steps": [
                f"参数{param['name']}传入异常格式: {str(value)[:100]}",
                f"发送{method}请求: {url}"
            ],
            "expected_result": "返回400参数格式错误，提示格式不正确",
            "test_tags": ["功能", "格式异常"],
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _build_valid_params(self, params: list, request_body: Optional[dict]) -> dict:
        result = {}
        for p in params:
            result[p["name"]] = p.get("example") or self._generate_example_value(
                p["type"], p.get("enum", []), p.get("minimum"), p.get("maximum"), p["name"]
            )
        if request_body and request_body.get("example"):
            result["_body"] = request_body["example"]
        return result

    def _remove_param_by_name(self, params: dict, name: str):
        if name in params:
            del params[name]

    def _get_success_code(self, responses: list) -> str:
        for r in responses:
            if r.get("is_success"):
                return r["code"]
        return "200"

    def _generate_performance_cases(self, api: dict) -> list:
        cases = []
        api_name = api["name"]
        method = api["method"]
        url = api["url"]
        module = api["module"]
        base_precondition = f"API服务正常运行\nBase URL: {api.get('base_url', '')}"

        concurrency_levels = [
            (10, 30, "低并发"),
            (50, 30, "中并发"),
            (100, 60, "高并发"),
            (500, 120, "超高并发")
        ]

        for concurrency, duration, label in concurrency_levels:
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【性能-并发压测】{api_name} - {concurrency}并发用户",
                "module": module,
                "feature": f"{method} {url}",
                "type": "性能",
                "sub_type": "并发压测",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"设置并发用户数: {concurrency}",
                    f"持续压测时长: {duration}秒",
                    f"发送{method}请求: {url}"
                ],
                "expected_result": f"最大响应时间<{duration}s，错误率<0.1%，TPS稳定",
                "test_tags": ["性能", "并发压测", label],
                "performance_meta": {
                    "concurrency": concurrency,
                    "duration_seconds": duration,
                    "batch_size": concurrency * 10,
                    "max_response_time_ms": duration * 1000,
                    "error_rate_threshold": 0.001
                },
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【性能-持续加压】{api_name} - 1小时循环负载",
            "module": module,
            "feature": f"{method} {url}",
            "type": "性能",
            "sub_type": "长时间持续加压",
            "priority": "中",
            "preconditions": base_precondition,
            "steps": [
                "设置持续时间: 3600秒(1小时)",
                "稳定负载: 10并发用户",
                f"循环发送{method}请求: {url}"
            ],
            "expected_result": "系统稳定运行1小时，无内存泄漏，响应时间无明显上升",
            "test_tags": ["性能", "稳定性", "持续加压"],
            "performance_meta": {
                "concurrency": 10,
                "duration_seconds": 3600,
                "batch_size": 0,
                "max_response_time_ms": 5000,
                "error_rate_threshold": 0.005
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【性能-大数据量】{api_name} - 批量数据传参",
            "module": module,
            "feature": f"{method} {url}",
            "type": "性能",
            "sub_type": "大数据量传参",
            "priority": "中",
            "preconditions": base_precondition,
            "steps": [
                "构造批量数组参数(1000条数据)",
                f"发送{method}请求: {url}",
                "观察响应时间和内存使用"
            ],
            "expected_result": "大数据量处理正常，响应时间<10s，不造成系统崩溃",
            "test_tags": ["性能", "大数据量", "批量处理"],
            "performance_meta": {
                "concurrency": 1,
                "duration_seconds": 60,
                "batch_size": 1000,
                "max_response_time_ms": 10000,
                "error_rate_threshold": 0.01
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【性能-高频请求】{api_name} - 1秒内20次请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "性能",
            "sub_type": "高频重复请求",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": [
                "在1秒内连续发送20次相同请求",
                f"发送{method}请求: {url}",
                "检查限流/防刷机制"
            ],
            "expected_result": "触发限流机制，返回429状态码或合理限流提示",
            "test_tags": ["性能", "限流", "高频请求"],
            "performance_meta": {
                "concurrency": 20,
                "duration_seconds": 1,
                "batch_size": 20,
                "max_response_time_ms": 1000,
                "error_rate_threshold": 0.5
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【性能-混合并发】{api_name} - 多账号混合读写",
            "module": module,
            "feature": f"{method} {url}",
            "type": "性能",
            "sub_type": "混合读写并发",
            "priority": "中",
            "preconditions": base_precondition,
            "steps": [
                "多账号同时执行查询和写入操作",
                "查询操作: 50并发",
                "写入操作: 20并发",
                f"发送{method}请求: {url}"
            ],
            "expected_result": "读写锁冲突处理正常，数据一致性保证，响应时间可接受",
            "test_tags": ["性能", "混合读写", "并发冲突"],
            "performance_meta": {
                "concurrency": 70,
                "duration_seconds": 60,
                "batch_size": 0,
                "max_response_time_ms": 3000,
                "error_rate_threshold": 0.01
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if api.get("is_list_endpoint"):
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【性能-资源耗尽】{api_name} - 无分页全量查询",
                "module": module,
                "feature": f"{method} {url}",
                "type": "性能",
                "sub_type": "资源耗尽边界",
                "priority": "中",
                "preconditions": base_precondition,
                "steps": [
                    "查询所有数据不使用分页",
                    f"发送{method}请求: {url}",
                    "观察系统资源使用"
                ],
                "expected_result": "系统正常处理或返回合理错误，不导致OOM",
                "test_tags": ["性能", "资源耗尽", "全量查询"],
                "performance_meta": {
                    "concurrency": 1,
                    "duration_seconds": 120,
                    "batch_size": 0,
                    "max_response_time_ms": 30000,
                    "error_rate_threshold": 0.1
                },
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return cases

    def _generate_security_cases(self, api: dict) -> list:
        cases = []
        api_name = api["name"]
        method = api["method"]
        url = api["url"]
        module = api["module"]
        params = api.get("params", [])
        base_precondition = f"API服务正常运行\nBase URL: {api.get('base_url', '')}"

        # SQL注入
        sqli_payloads = [
            ("单引号注入", "'", "返回数据库错误或异常响应"),
            ("OR 1=1注入", "' OR '1'='1", "返回所有数据或认证绕过"),
            ("UNION注入", "' UNION SELECT 1,2,3--", "返回联合查询结果"),
            ("注释符注入", "'; DROP TABLE users;--", "返回错误或表被删除"),
            ("分页注入", "1' AND 1=1--", "返回数据篡改结果"),
        ]

        for payload_name, payload, expected in sqli_payloads:
            test_param = params[0]["name"] if params else "id"
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【安全-SQL注入】{api_name} - {payload_name}",
                "module": module,
                "feature": f"{method} {url}",
                "type": "安全",
                "sub_type": "SQL注入",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"在参数{test_param}中注入: {payload}",
                    f"发送{method}请求: {url}"
                ],
                "expected_result": expected,
                "test_tags": ["安全", "SQL注入", "高危"],
                "security_meta": {
                    "severity": "高危",
                    "payload": payload,
                    "type": "SQL注入"
                },
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # XSS
        xss_payloads = [
            ("弹窗脚本", "<script>alert('XSS')</script>", "执行JavaScript弹窗"),
            ("跳转链接", "<script>window.location='http://evil.com'</script>", "页面跳转至恶意地址"),
            ("img onerror", "<img src=x onerror=alert('XSS')>", "图片加载失败触发XSS"),
            ("HTML标签注入", "<b>XSS</b>", "HTML标签被解析执行"),
        ]

        for payload_name, payload, expected in xss_payloads:
            test_param = params[0]["name"] if params else "name"
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【安全-XSS】{api_name} - {payload_name}",
                "module": module,
                "feature": f"{method} {url}",
                "type": "安全",
                "sub_type": "XSS跨站脚本",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"在参数{test_param}中注入: {payload}",
                    f"发送{method}请求: {url}",
                    "检查响应内容是否包含注入脚本"
                ],
                "expected_result": expected,
                "test_tags": ["安全", "XSS", "高危"],
                "security_meta": {
                    "severity": "高危",
                    "payload": payload,
                    "type": "XSS跨站脚本"
                },
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # 越权访问
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【安全-越权】{api_name} - 水平越权(查询他人数据)",
            "module": module,
            "feature": f"{method} {url}",
            "type": "安全",
            "sub_type": "越权访问",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": [
                "使用当前用户Token",
                f"尝试查询其他用户数据: {url}/other_user_id",
                "检查是否返回了其他用户的数据"
            ],
            "expected_result": "返回403禁止访问，不返回其他用户数据",
            "test_tags": ["安全", "越权", "水平越权", "高危"],
            "security_meta": {
                "severity": "高危",
                "type": "水平越权"
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【安全-越权】{api_name} - 垂直越权(低权限访问高权限)",
            "module": module,
            "feature": f"{method} {url}",
            "type": "安全",
            "sub_type": "越权访问",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": [
                "使用普通用户Token",
                f"尝试访问管理员接口: {url}",
                "检查是否成功访问"
            ],
            "expected_result": "返回403禁止访问，低权限用户无法访问高权限接口",
            "test_tags": ["安全", "越权", "垂直越权", "高危"],
            "security_meta": {
                "severity": "高危",
                "type": "垂直越权"
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # 敏感信息泄露
        if api.get("is_sensitive"):
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【安全-信息泄露】{api_name} - 返回体敏感信息检查",
                "module": module,
                "feature": f"{method} {url}",
                "type": "安全",
                "sub_type": "敏感信息泄露",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"发送{method}请求: {url}",
                    "检查响应体是否包含明文敏感数据"
                ],
                "expected_result": "响应体中敏感数据已脱敏/加密，不返回明文密码/身份证等",
                "test_tags": ["安全", "信息泄露", "中危"],
                "security_meta": {
                    "severity": "中危",
                    "type": "敏感信息泄露"
                },
                "is_sensitive": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # CSRF
        cases.append({
            "id": str(uuid.uuid4()),
            "name": f"【安全-CSRF】{api_name} - 跨站伪造请求",
            "module": module,
            "feature": f"{method} {url}",
            "type": "安全",
            "sub_type": "CSRF",
            "priority": "高",
            "preconditions": base_precondition,
            "steps": [
                "构造跨站请求伪造(无CSRF Token)",
                f"从其他域名发送{method}请求: {url}",
                "检查请求是否被接受"
            ],
            "expected_result": "请求被拒绝或要求CSRF Token验证",
            "test_tags": ["安全", "CSRF", "高危"],
            "security_meta": {
                "severity": "高危",
                "type": "CSRF跨站伪造"
            },
            "is_sensitive": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # 路径遍历
        path_traversal_payloads = [
            ("目录穿越", "../../etc/passwd", "读取系统敏感文件"),
            ("Windows路径", "..\\..\\windows\\system32\\config", "读取Windows系统配置"),
            ("URL编码穿越", "%2e%2e%2f%2e%2e%2fetc%2fpasswd", "绕过过滤读取文件"),
        ]

        for payload_name, payload, expected in path_traversal_payloads:
            test_param = params[0]["name"] if params else "file_path"
            cases.append({
                "id": str(uuid.uuid4()),
                "name": f"【安全-路径遍历】{api_name} - {payload_name}",
                "module": module,
                "feature": f"{method} {url}",
                "type": "安全",
                "sub_type": "路径遍历",
                "priority": "高",
                "preconditions": base_precondition,
                "steps": [
                    f"在参数{test_param}中传入: {payload}",
                    f"发送{method}请求: {url}"
                ],
                "expected_result": expected,
                "test_tags": ["安全", "路径遍历", "高危"],
                "security_meta": {
                    "severity": "高危",
                    "payload": payload,
                    "type": "路径遍历"
                },
                "is_sensitive": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # 若接口涉及文件上传
        params_str = json.dumps(params, ensure_ascii=False).lower()
        if "file" in params_str or "upload" in url.lower():
            file_payloads = [
                ("脚本文件上传", "test.jsp", "上传可执行脚本文件"),
                ("文件后缀篡改", "test.jpg.php", "双后缀绕过检测"),
                ("路径伪装上传", "../../webshell.php", "路径穿越上传"),
            ]
            for payload_name, payload, expected in file_payloads:
                cases.append({
                    "id": str(uuid.uuid4()),
                    "name": f"【安全-文件上传】{api_name} - {payload_name}",
                    "module": module,
                    "feature": f"{method} {url}",
                    "type": "安全",
                    "sub_type": "文件上传漏洞",
                    "priority": "高",
                    "preconditions": base_precondition,
                    "steps": [
                        f"上传文件: {payload}",
                        f"发送{method}请求: {url}"
                    ],
                    "expected_result": expected,
                    "test_tags": ["安全", "文件上传", "高危"],
                    "security_meta": {
                        "severity": "高危",
                        "payload": payload,
                        "type": "文件上传漏洞"
                    },
                    "is_sensitive": False,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        return cases

    def _aggregate_features(self, api_definitions: list, all_cases: list) -> list:
        module_map = {}
        for case in all_cases:
            module = case.get("module", "未分类")
            if module not in module_map:
                module_map[module] = {"功能": 0, "性能": 0, "安全": 0}
            case_type = case.get("type", "功能")
            if case_type in module_map[module]:
                module_map[module][case_type] += 1

        features = []
        for module, counts in module_map.items():
            total = sum(counts.values())
            features.append({
                "name": module,
                "module": module,
                "description": f"API模块 - {module}",
                "casesCount": total,
                "functional_count": counts["功能"],
                "performance_count": counts["性能"],
                "security_count": counts["安全"],
                "coverage": 100
            })
        return features

    def _generate_risk_assessment(self, api_definitions: list, functional_cases: list,
                                    performance_cases: list, security_cases: list) -> dict:
        risks = []

        func_count = len(functional_cases)
        if func_count == 0:
            risks.append({"level": "中", "category": "功能缺陷", "description": "功能测试用例缺失，建议补充"})

        perf_count = len(performance_cases)
        if perf_count == 0:
            risks.append({"level": "高", "category": "性能瓶颈", "description": "未生成性能测试用例，存在性能风险"})

        high_severity_count = sum(1 for c in security_cases
                                   if c.get("security_meta", {}).get("severity") == "高危")
        if high_severity_count > 0:
            risks.append({
                "level": "高",
                "category": "安全高危漏洞",
                "description": f"发现{high_severity_count}个高危安全测试场景，需重点关注"
            })

        sensitive_apis = [a for a in api_definitions if a.get("is_sensitive")]
        if sensitive_apis:
            risks.append({
                "level": "中",
                "category": "敏感数据风险",
                "description": f"{len(sensitive_apis)}个接口涉及敏感数据传输，需确保加密传输和脱敏处理"
            })

        risk_level = "低"
        if any(r["level"] == "高" for r in risks):
            risk_level = "高"
        elif any(r["level"] == "中" for r in risks):
            risk_level = "中"

        return {
            "risk_level": risk_level,
            "risks": risks,
            "summary": f"共生成{func_count}条功能用例、{perf_count}条性能用例、{len(security_cases)}条安全用例",
            "api_count": len(api_definitions),
            "suggestions": [
                "建议优先执行高危安全用例",
                "敏感数据接口需重点验证加密传输",
                "性能压测建议在独立环境执行",
                "SQL注入/XSS测试需在测试环境执行"
            ]
        }

    def _generate_postman_collection(self, api_definitions: list) -> dict:
        items = []
        for api in api_definitions:
            request_data = {
                "name": api["name"],
                "request": {
                    "method": api["method"],
                    "url": {
                        "raw": f"{api.get('base_url', '')}{api['url']}",
                        "host": [api.get("base_url", "")] if api.get("base_url") else ["localhost"],
                        "path": [x for x in api["url"].split("/") if x]
                    },
                    "header": [
                        {"key": "Content-Type", "value": "application/json", "type": "text"},
                        {"key": "Authorization", "value": "Bearer {{token}}", "type": "text"}
                    ]
                }
            }

            if api["params"]:
                query_params = []
                path_params = []
                for p in api["params"]:
                    param_item = {
                        "key": p["name"],
                        "value": str(p.get("example", "")),
                        "type": "text",
                        "description": f"{p['type']}{' (必填)' if p['required'] else ''}"
                    }
                    if p["in"] == "query":
                        query_params.append(param_item)
                    elif p["in"] == "path":
                        path_params.append(param_item)

                if query_params:
                    request_data["request"]["url"]["query"] = query_params
                if path_params:
                    request_data["request"]["url"]["variable"] = path_params

            if api.get("request_body") and api["request_body"].get("example"):
                request_data["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(api["request_body"]["example"], ensure_ascii=False, indent=2),
                    "options": {
                        "raw": {"language": "json"}
                    }
                }

            responses = []
            for resp in api.get("responses", []):
                response_item = {
                    "name": f"Response {resp['code']}",
                    "status": resp["code"],
                    "code": int(resp["code"]),
                    "header": [],
                    "cookie": [],
                    "body": json.dumps(resp.get("example", {}), ensure_ascii=False, indent=2) if resp.get("example") else "",
                    "_postman_previewlanguage": "json"
                }
                responses.append(response_item)
            request_data["response"] = responses

            items.append(request_data)

        return {
            "info": {
                "name": "Swagger导入接口集合",
                "description": f"由Swagger文档自动生成，共{len(api_definitions)}个接口",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": items
        }

    def _generate_jmeter_template(self, api_definitions: list) -> str:
        test_plan = '<?xml version="1.0" encoding="UTF-8"?>\n'
        test_plan += '<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.5">\n'
        test_plan += '  <hashTree>\n'
        test_plan += '    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Swagger接口性能测试计划" enabled="true">\n'
        test_plan += '      <stringProp name="TestPlan.comments">由Swagger文档自动生成</stringProp>\n'
        test_plan += '      <boolProp name="TestPlan.functional_mode">false</boolProp>\n'
        test_plan += '      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>\n'
        test_plan += '    </TestPlan>\n'
        test_plan += '    <hashTree>\n'

        test_plan += '      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="10并发用户组" enabled="true">\n'
        test_plan += '        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>\n'
        test_plan += '        <elementProp name="ThreadGroup.main_controller" elementType="LoopController">\n'
        test_plan += '          <boolProp name="LoopController.continue_forever">false</boolProp>\n'
        test_plan += '          <intProp name="LoopController.loops">10</intProp>\n'
        test_plan += '        </elementProp>\n'
        test_plan += '        <stringProp name="ThreadGroup.num_threads">10</stringProp>\n'
        test_plan += '        <stringProp name="ThreadGroup.ramp_time">5</stringProp>\n'
        test_plan += '      </ThreadGroup>\n'
        test_plan += '      <hashTree>\n'

        for api in api_definitions:
            test_plan += f'        <HTTPSamplerProxy testname="{api["name"]}" enabled="true">\n'
            test_plan += f'          <stringProp name="HTTPSampler.domain">localhost</stringProp>\n'
            test_plan += f'          <stringProp name="HTTPSampler.port">8000</stringProp>\n'
            test_plan += f'          <stringProp name="HTTPSampler.protocol">http</stringProp>\n'
            test_plan += f'          <stringProp name="HTTPSampler.path">{api["url"]}</stringProp>\n'
            test_plan += f'          <stringProp name="HTTPSampler.method">{api["method"]}</stringProp>\n'
            test_plan += '          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>\n'
            test_plan += '          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>\n'
            test_plan += '        </HTTPSamplerProxy>\n'
            test_plan += '        <hashTree>\n'
            test_plan += '          <ResponseAssertion testname="响应断言" enabled="true">\n'
            test_plan += '            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>\n'
            test_plan += '            <boolProp name="Assertion.assume_success">false</boolProp>\n'
            test_plan += '            <intProp name="Assertion.test_strategy">1</intProp>\n'
            test_plan += '            <stringProp name="Assertion.custom_message"></stringProp>\n'
            test_plan += '            <stringProp name="Assertion.test_patterns">200,201,204</stringProp>\n'
            test_plan += '          </ResponseAssertion>\n'
            test_plan += '          <hashTree/>\n'
            test_plan += '        </hashTree>\n'
            test_plan += '      </hashTree>\n'

        test_plan += '    </hashTree>\n'
        test_plan += '  </hashTree>\n'
        test_plan += '</jmeterTestPlan>'
        return test_plan

    def _generate_pytest_script(self, api_definitions: list) -> str:
        script = '# Auto-generated pytest test script from Swagger\n'
        script += '# Generated by Swagger Test Generator\n'
        script += '# Usage: pytest swagger_tests.py -v\n\n'
        script += 'import pytest\n'
        script += 'import requests\n'
        script += 'import json\n'
        script += 'from faker import Faker\n\n'
        script += 'fake = Faker()\n\n'
        script += 'BASE_URL = "http://localhost:8000"\n'
        script += 'HEADERS = {\n'
        script += '    "Content-Type": "application/json",\n'
        script += '    "Authorization": "Bearer your_token_here"\n'
        script += '}\n\n\n'

        for i, api in enumerate(api_definitions):
            func_name = api["name"].lower().replace(" ", "_").replace("-", "_")
            if i > 0:
                script += '\n'

            script += f'class Test_{func_name.replace(" ", "_")}:\n'
            script += f'    """测试: {api["name"]}"""\n\n'
            script += f'    BASE_URL = BASE_URL\n'
            script += f'    ENDPOINT = "{api["url"]}"\n'
            script += f'    METHOD = "{api["method"]}"\n\n'

            # 正向测试
            script += f'    def test_normal_{func_name}(self):\n'
            script += f'        """正向正常请求测试"""\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        payload = self._build_normal_payload()\n'
            script += f'        response = getattr(requests, self.METHOD.lower())(\n'
            script += f'            url, json=payload, headers=HEADERS, timeout=30\n'
            script += f'        )\n'
            script += f'        assert response.status_code in [200, 201, 204], f"Expected 2xx, got {{response.status_code}}"\n'
            script += f'        print(f"Response: {{response.json()}}")\n\n'

            # 异常测试
            script += f'    def test_missing_required_param_{func_name}(self):\n'
            script += f'        """缺少必填参数测试"""\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        payload = self._build_normal_payload()\n'
            script += f'        if payload:\n'
            script += f'            key_to_remove = list(payload.keys())[0]\n'
            script += f'            del payload[key_to_remove]\n'
            script += f'        response = getattr(requests, self.METHOD.lower())(\n'
            script += f'            url, json=payload, headers=HEADERS, timeout=30\n'
            script += f'        )\n'
            script += f'        assert response.status_code == 400, f"Expected 400, got {{response.status_code}}"\n\n'

            # 边界值测试
            script += f'    def test_boundary_{func_name}(self):\n'
            script += f'        """边界值测试"""\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        payload = self._build_boundary_payload()\n'
            script += f'        response = getattr(requests, self.METHOD.lower())(\n'
            script += f'            url, json=payload, headers=HEADERS, timeout=30\n'
            script += f'        )\n'
            script += f'        assert response.status_code in [200, 201, 204, 400], f"Unexpected status {{response.status_code}}"\n\n'

            # 权限测试
            script += f'    def test_unauthorized_{func_name}(self):\n'
            script += f'        """未授权请求测试"""\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        headers = {{"Content-Type": "application/json"}}\n'
            script += f'        response = getattr(requests, self.METHOD.lower())(\n'
            script += f'            url, headers=headers, timeout=30\n'
            script += f'        )\n'
            script += f'        assert response.status_code == 401, f"Expected 401, got {{response.status_code}}"\n\n'

            # 性能测试
            script += f'    @pytest.mark.performance\n'
            script += f'    def test_performance_{func_name}(self):\n'
            script += f'        """性能测试 - 并发响应时间"""\n'
            script += f'        import time\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        start_time = time.time()\n'
            script += f'        for _ in range(100):\n'
            script += f'            response = getattr(requests, self.METHOD.lower())(\n'
            script += f'                url, headers=HEADERS, timeout=30\n'
            script += f'            )\n'
            script += f'        elapsed = time.time() - start_time\n'
            script += f'        avg_time = elapsed / 100\n'
            script += f'        assert avg_time < 1.0, f"Average response time {{avg_time:.3f}}s exceeds 1s threshold"\n'
            script += f'        print(f"Average response time: {{avg_time:.3f}}s")\n\n'

            # 安全测试
            script += f'    @pytest.mark.security\n'
            script += f'    def test_sql_injection_{func_name}(self):\n'
            script += f'        """SQL注入测试"""\n'
            script += f'        url = f"{{self.BASE_URL}}{{self.ENDPOINT}}"\n'
            script += f'        payload = self._build_normal_payload()\n'
            script += f'        if payload:\n'
            script += f'            first_key = list(payload.keys())[0]\n'
            script += f'            payload[first_key] = payload.get(first_key, "1") + "\' OR \'1\'=\'1"\n'
            script += f'        response = getattr(requests, self.METHOD.lower())(\n'
            script += f'            url, json=payload, headers=HEADERS, timeout=30\n'
            script += f'        )\n'
            script += f'        assert response.status_code not in [200, 201], f"SQL injection may have succeeded! Status: {{response.status_code}}"\n\n'

            # Helper methods
            script += f'    def _build_normal_payload(self):\n'
            if api.get("request_body") and api["request_body"].get("example"):
                body_example = json.dumps(api["request_body"]["example"], ensure_ascii=False, indent=8)
                script += f'        return {body_example}\n\n'
            else:
                script += f'        return {{}}\n\n'

            script += f'    def _build_boundary_payload(self):\n'
            if api.get("request_body") and api["request_body"].get("schema", {}).get("properties"):
                script += f'        payload = self._build_normal_payload()\n'
                script += f'        for key in payload:\n'
                script += f'            if isinstance(payload[key], str):\n'
                script += f'                payload[key] = "a" * 1000\n'
                script += f'            elif isinstance(payload[key], (int, float)):\n'
                script += f'                payload[key] = 99999999\n'
                script += f'        return payload\n\n'
            else:
                script += f'        return {{}}\n\n'

        return script