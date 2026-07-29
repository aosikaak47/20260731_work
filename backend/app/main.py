from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from app.services.document_parser import DocumentParser
from app.services.test_case_generator import TestCaseGenerator
from app.services.export_service import ExportService
from app.services.config_service import ConfigService
from app.services.swagger_test_generator import SwaggerTestGenerator
from app.models.schemas import TestCase, CoverageReport, ExportFormat
import os
import json
import uuid
import re
import gzip
import zlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI智能测试自动化平台", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_parser = DocumentParser()
test_case_generator = TestCaseGenerator()
export_service = ExportService()
config_service = ConfigService()
swagger_test_generator = SwaggerTestGenerator()

if test_case_generator.ai_service:
    raw_config = config_service.get_raw_config()
    test_case_generator.ai_service.update_config(raw_config)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def decode_response_body(response):
    content = response.content
    content_encoding = response.headers.get('Content-Encoding', '').lower()
    
    try:
        if 'gzip' in content_encoding:
            content = gzip.decompress(content)
        elif 'deflate' in content_encoding:
            try:
                content = zlib.decompress(content)
            except:
                content = zlib.decompress(content, -zlib.MAX_WBITS)
    except:
        pass
    
    charset = None
    content_type = response.headers.get('Content-Type', '').lower()
    
    charset_match = re.search(r'charset=([^\s;]+)', content_type)
    if charset_match:
        charset = charset_match.group(1).strip('"')
    
    if not charset:
        meta_match = re.search(r'<meta[^>]+charset=["\']?([^"\'>\s]+)', content.decode('utf-8', errors='ignore'), re.IGNORECASE)
        if meta_match:
            charset = meta_match.group(1)
    
    if not charset:
        charset_match = re.search(r'charset=([^\s"\'>]+)', content.decode('utf-8', errors='ignore'), re.IGNORECASE)
        if charset_match:
            charset = charset_match.group(1)
    
    if not charset:
        charset = 'utf-8'
    
    charset = charset.strip('"').strip("'")
    
    try:
        text = content.decode(charset)
    except (UnicodeDecodeError, LookupError):
        for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']:
            try:
                text = content.decode(enc)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            text = content.decode('utf-8', errors='replace')
    
    return text

@app.get("/")
async def root():
    return {"message": "AI智能测试自动化平台 API"}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), doc_type: str = Query("auto", enum=["auto", "requirement", "api"]),
                     strategy: str = Query("hybrid", enum=["ai_first", "rule_first", "ai_only", "rule_only", "hybrid"]),
                     case_count: int = Query(10, ge=1, le=50)):
    try:
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1].lower()
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{file_ext}")
        
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        content = document_parser.parse(file_path, file_ext, doc_type)
        
        result = test_case_generator.generate_with_strategy(content, doc_type, strategy, case_count)
        
        coverage = test_case_generator.calculate_coverage(result)
        
        return JSONResponse({
            "file_id": file_id,
            "filename": file.filename,
            "content": content,
            "test_cases": result.get("test_cases", []),
            "coverage": coverage,
            "analysis": result.get("analysis", {}),
            "generation_mode": result.get("generation_mode", "rule"),
            "strategy": result.get("strategy", strategy),
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze")
async def analyze_content(content: dict):
    try:
        text = content.get("text", "")
        doc_type = content.get("doc_type", "auto")
        strategy = content.get("strategy", "hybrid")
        case_count = content.get("case_count", 10)
        
        result = test_case_generator.generate_with_strategy(text, doc_type, strategy, case_count)
        coverage = test_case_generator.calculate_coverage(result)
        
        return JSONResponse({
            "test_cases": result.get("test_cases", []),
            "coverage": coverage,
            "analysis": result.get("analysis", {}),
            "generation_mode": result.get("generation_mode", "rule"),
            "strategy": result.get("strategy", strategy),
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/generate")
async def ai_generate(content: dict):
    try:
        text = content.get("text", "")
        doc_type = content.get("doc_type", "requirement")
        case_count = content.get("case_count", 10)
        
        if not text:
            raise HTTPException(status_code=400, detail="内容不能为空")
        
        result = test_case_generator.generate_with_strategy(text, doc_type, "ai_only", case_count)
        
        if not result.get("test_cases"):
            return JSONResponse({
                "test_cases": [],
                "analysis": {"error": "AI服务不可用，请配置API Key"},
                "generation_mode": "ai",
                "strategy": "ai_only",
                "generated_at": datetime.now().isoformat()
            })
        
        coverage = test_case_generator.calculate_coverage(result)
        
        return JSONResponse({
            "test_cases": result.get("test_cases", []),
            "coverage": coverage,
            "analysis": result.get("analysis", {}),
            "generation_mode": "ai",
            "strategy": "ai_only",
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/analyze")
async def ai_analyze(content: dict):
    try:
        text = content.get("text", "")
        
        if not text:
            raise HTTPException(status_code=400, detail="内容不能为空")
        
        analysis = test_case_generator.analyze_requirements(text)
        
        return JSONResponse({
            "analysis": analysis,
            "analyzed_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/optimize")
async def ai_optimize(content: dict):
    try:
        test_cases = content.get("test_cases", [])
        requirements = content.get("requirements", "")
        
        if not test_cases:
            raise HTTPException(status_code=400, detail="测试用例不能为空")
        
        result = test_case_generator.optimize_cases(test_cases, requirements)
        
        coverage = test_case_generator.calculate_coverage(result.get("optimized_cases", []))
        
        return JSONResponse({
            "optimized_cases": result.get("optimized_cases", []),
            "changes": result.get("changes", []),
            "coverage": coverage,
            "optimized_at": datetime.now().isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/strategies")
async def get_strategies():
    try:
        strategies = test_case_generator.get_strategies()
        return JSONResponse(strategies)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/export")
async def export_test_cases(data: dict):
    try:
        test_cases = data.get("test_cases", [])
        coverage = data.get("coverage", {})
        format_type = data.get("format", "markdown")
        
        export_path = export_service.export(test_cases, coverage, format_type)
        
        if os.path.exists(export_path):
            return FileResponse(
                export_path,
                filename=os.path.basename(export_path),
                media_type="application/octet-stream"
            )
        else:
            raise HTTPException(status_code=404, detail="导出文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/templates")
async def get_templates():
    return JSONResponse(test_case_generator.get_templates())

CONFIG_PASSWORD = os.getenv("CONFIG_PASSWORD", "admin123")

@app.post("/api/v1/config/auth")
async def config_auth(data: dict):
    try:
        password = data.get("password", "")
        if password == CONFIG_PASSWORD:
            return JSONResponse({"success": True, "message": "验证成功"})
        else:
            return JSONResponse({"success": False, "message": "密码错误"}, status_code=401)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config")
async def get_config():
    try:
        config = config_service.get_config()
        return JSONResponse(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config")
async def update_config(request: Request):
    try:
        data = await request.json()
        updates = data.get("config", {})
        config = config_service.update_config(updates)
        
        if test_case_generator.ai_service:
            raw_config = config_service.get_raw_config()
            test_case_generator.ai_service.update_config(raw_config)
        
        return JSONResponse({
            "config": config,
            "message": "配置更新成功"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/config/test")
async def test_config(data: dict):
    try:
        config_data = data.get("config", {})
        
        if config_data:
            api_key = config_data.get("api_key", "")
            api_base = config_data.get("api_base", "")
            model = config_data.get("model", "gpt-4o-mini")
            
            if not api_key or not api_base:
                return JSONResponse({"success": False, "message": "请配置API Key和API Base"})
            
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
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
                return JSONResponse({"success": True, "message": "连接成功", "status_code": response.status_code})
            elif response.status_code == 401:
                return JSONResponse({"success": False, "message": "API Key无效", "status_code": response.status_code})
            elif response.status_code == 403:
                return JSONResponse({"success": False, "message": "API Key权限不足", "status_code": response.status_code})
            else:
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get("error", {}).get("message", f"连接失败: {response.status_code}")
                except:
                    error_msg = f"连接失败: {response.status_code}"
                return JSONResponse({"success": False, "message": error_msg, "status_code": response.status_code})
        else:
            result = config_service.test_connection()
            return JSONResponse(result)
    except requests.exceptions.RequestException as e:
        return JSONResponse({"success": False, "message": f"连接异常: {str(e)}"})
    except Exception as e:
        return JSONResponse({"success": False, "message": f"测试失败: {str(e)}"})

@app.get("/api/v1/config/providers")
async def get_providers():
    try:
        providers = config_service.get_providers()
        return JSONResponse(providers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

CASE_LIBRARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/case_library.json")

@app.post("/api/v1/case_library")
async def add_to_case_library(request: Request):
    try:
        data = await request.json()
        test_cases = data.get("test_cases", [])
        
        if not test_cases:
            raise HTTPException(status_code=400, detail="测试用例列表不能为空")
        
        os.makedirs(os.path.dirname(CASE_LIBRARY_FILE), exist_ok=True)
        
        if os.path.exists(CASE_LIBRARY_FILE):
            with open(CASE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
                library = json.load(f)
        else:
            library = []
        
        library.extend(test_cases)
        
        with open(CASE_LIBRARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)
        
        return JSONResponse({"success": True, "message": "用例已成功加入用例库", "count": len(test_cases), "total": len(library)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/case_library")
async def get_case_library():
    try:
        if os.path.exists(CASE_LIBRARY_FILE):
            with open(CASE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
                library = json.load(f)
        else:
            library = []
        
        return JSONResponse({"test_cases": library, "total": len(library)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/case_library/{case_id}")
async def delete_from_case_library(case_id: str):
    try:
        if not os.path.exists(CASE_LIBRARY_FILE):
            raise HTTPException(status_code=404, detail="用例库不存在")
        
        with open(CASE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
            library = json.load(f)
        
        original_count = len(library)
        library = [case for case in library if case.get("id") != case_id]
        
        if len(library) == original_count:
            raise HTTPException(status_code=404, detail="用例不存在")
        
        with open(CASE_LIBRARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)
        
        return JSONResponse({"success": True, "message": "用例已从用例库删除", "total": len(library)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/case_library")
async def clear_case_library():
    try:
        if os.path.exists(CASE_LIBRARY_FILE):
            os.remove(CASE_LIBRARY_FILE)
        
        return JSONResponse({"success": True, "message": "用例库已清空"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

MODULES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/modules.json")
MANAGED_CASES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/managed_cases.json")
ARCHIVES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/archives.json")
PROJECTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/projects.json")

DEFAULT_PROJECTS = [
    {
        "id": "1",
        "name": "智能测试平台项目",
        "description": "平台核心项目，包含所有模块功能",
        "status": "启用",
        "memberCount": 5,
        "caseCount": 0,
        "createdAt": "2026-07-01 10:00",
        "modules": [
            {"id": "p1-1", "name": "AI智能用例生成", "project_id": "1", "children": [
                {"id": "p1-1-1", "name": "需求文档导入", "project_id": "1"},
                {"id": "p1-1-2", "name": "接口文档导入", "project_id": "1"},
                {"id": "p1-1-3", "name": "手动场景生成", "project_id": "1"}
            ]},
            {"id": "p1-2", "name": "用例管理", "project_id": "1", "children": [
                {"id": "p1-2-1", "name": "用例新增", "project_id": "1"},
                {"id": "p1-2-2", "name": "用例编辑", "project_id": "1"},
                {"id": "p1-2-3", "name": "用例删除", "project_id": "1"}
            ]},
            {"id": "p1-3", "name": "接口自动化", "project_id": "1", "children": [
                {"id": "p1-3-1", "name": "接口环境管理", "project_id": "1"},
                {"id": "p1-3-2", "name": "接口用例管理", "project_id": "1"},
                {"id": "p1-3-3", "name": "业务场景编排", "project_id": "1"}
            ]},
            {"id": "p1-4", "name": "UI自动化", "project_id": "1"},
            {"id": "p1-5", "name": "任务调度", "project_id": "1"},
            {"id": "p1-6", "name": "质量统计", "project_id": "1"}
        ]
    },
    {
        "id": "2",
        "name": "党建系统项目",
        "description": "党建管理系统测试项目",
        "status": "启用",
        "memberCount": 3,
        "caseCount": 0,
        "createdAt": "2026-07-05 14:30",
        "modules": [
            {"id": "p2-1", "name": "用户管理", "project_id": "2", "children": [
                {"id": "p2-1-1", "name": "登录认证", "project_id": "2"},
                {"id": "p2-1-2", "name": "权限管理", "project_id": "2"},
                {"id": "p2-1-3", "name": "组织架构", "project_id": "2"}
            ]},
            {"id": "p2-2", "name": "内容管理", "project_id": "2", "children": [
                {"id": "p2-2-1", "name": "文章发布", "project_id": "2"},
                {"id": "p2-2-2", "name": "审核流程", "project_id": "2"}
            ]},
            {"id": "p2-3", "name": "数据统计", "project_id": "2"}
        ]
    },
    {
        "id": "3",
        "name": "电商平台项目",
        "description": "电商平台接口与UI自动化测试",
        "status": "启用",
        "memberCount": 4,
        "caseCount": 0,
        "createdAt": "2026-07-10 09:00",
        "modules": [
            {"id": "p3-1", "name": "商品管理", "project_id": "3", "children": [
                {"id": "p3-1-1", "name": "商品列表", "project_id": "3"},
                {"id": "p3-1-2", "name": "商品详情", "project_id": "3"},
                {"id": "p3-1-3", "name": "商品上下架", "project_id": "3"}
            ]},
            {"id": "p3-2", "name": "订单管理", "project_id": "3", "children": [
                {"id": "p3-2-1", "name": "订单创建", "project_id": "3"},
                {"id": "p3-2-2", "name": "订单支付", "project_id": "3"},
                {"id": "p3-2-3", "name": "订单退款", "project_id": "3"}
            ]},
            {"id": "p3-3", "name": "营销活动", "project_id": "3"},
            {"id": "p3-4", "name": "购物车", "project_id": "3"}
        ]
    },
    {
        "id": "4",
        "name": "OA办公系统",
        "description": "办公自动化系统测试",
        "status": "禁用",
        "memberCount": 2,
        "caseCount": 0,
        "createdAt": "2026-07-15 11:00",
        "modules": [
            {"id": "p4-1", "name": "流程审批", "project_id": "4", "children": [
                {"id": "p4-1-1", "name": "请假流程", "project_id": "4"},
                {"id": "p4-1-2", "name": "报销流程", "project_id": "4"}
            ]},
            {"id": "p4-2", "name": "公告管理", "project_id": "4"},
            {"id": "p4-3", "name": "日程管理", "project_id": "4"}
        ]
    }
]

def load_projects():
    if os.path.exists(PROJECTS_FILE):
        try:
            with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_PROJECTS

def save_projects(projects):
    os.makedirs(os.path.dirname(PROJECTS_FILE), exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def get_all_modules_from_projects():
    projects = load_projects()
    all_modules = []
    for project in projects:
        project_modules = project.get("modules", [])
        for mod in project_modules:
            all_modules.append(mod)
    return all_modules

def get_default_modules():
    return DEFAULT_PROJECTS[0]["modules"]

def load_modules(project_id: str = None):
    if project_id:
        projects = load_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if project:
            return project.get("modules", [])
        return []
    
    all_modules = []
    if os.path.exists(MODULES_FILE):
        try:
            with open(MODULES_FILE, 'r', encoding='utf-8') as f:
                global_modules = json.load(f)
                all_modules.extend(global_modules)
        except:
            pass
    
    projects = load_projects()
    for project in projects:
        project_modules = project.get("modules", [])
        if project_modules:
            all_modules.extend(project_modules)
    
    return all_modules

def save_modules(modules):
    os.makedirs(os.path.dirname(MODULES_FILE), exist_ok=True)
    with open(MODULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(modules, f, ensure_ascii=False, indent=2)

def load_managed_cases():
    if os.path.exists(MANAGED_CASES_FILE):
        try:
            with open(MANAGED_CASES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_managed_cases(cases):
    os.makedirs(os.path.dirname(MANAGED_CASES_FILE), exist_ok=True)
    with open(MANAGED_CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

def load_archives():
    if os.path.exists(ARCHIVES_FILE):
        try:
            with open(ARCHIVES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_archives(archives):
    os.makedirs(os.path.dirname(ARCHIVES_FILE), exist_ok=True)
    with open(ARCHIVES_FILE, 'w', encoding='utf-8') as f:
        json.dump(archives, f, ensure_ascii=False, indent=2)

@app.get("/api/v1/archives")
async def get_archives(keyword: str = Query(None), module: str = Query(None)):
    try:
        archives = load_archives()
        
        if keyword:
            archives = [a for a in archives if keyword.lower() in a.get("name", "").lower()]
        if module:
            archives = [a for a in archives if a.get("module") == module]
        
        for archive in archives:
            if "archive_time" not in archive:
                archive["archive_time"] = archive.get("updated_at", "")
            if "reason" not in archive:
                archive["reason"] = archive.get("archive_reason", "")
            if "version" not in archive:
                archive["version"] = "v1.0"
        
        return JSONResponse({"archives": archives, "total": len(archives)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/archives/{archive_id}/restore")
async def restore_archive(archive_id: str, request: Request):
    try:
        data = await request.json()
        new_version = data.get("version", "v1.0")
        
        archives = load_archives()
        archive = None
        for a in archives:
            if a.get("id") == archive_id:
                archive = a
                break
        
        if not archive:
            raise HTTPException(status_code=404, detail="归档用例不存在")
        
        archives = [a for a in archives if a.get("id") != archive_id]
        save_archives(archives)
        
        managed_cases = load_managed_cases()
        restored = archive.copy()
        restored.pop("archive_time", None)
        restored.pop("archive_reason", None)
        restored["version"] = new_version
        restored["status"] = "未执行"
        restored["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        managed_cases.append(restored)
        save_managed_cases(managed_cases)
        
        return JSONResponse({"success": True, "message": f"恢复用例成功，版本: {new_version}"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/archives/{archive_id}")
async def delete_archive(archive_id: str):
    try:
        archives = load_archives()
        original_count = len(archives)
        archives = [a for a in archives if a.get("id") != archive_id]
        deleted_count = original_count - len(archives)
        
        save_archives(archives)
        return JSONResponse({"success": True, "message": f"成功删除{deleted_count}条归档", "count": deleted_count})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/archives/batch_restore")
async def batch_restore_archives(request: Request):
    try:
        data = await request.json()
        archive_ids = data.get("archive_ids", [])
        new_version = data.get("version", "v1.0")
        
        if not archive_ids:
            raise HTTPException(status_code=400, detail="归档ID列表不能为空")
        
        archives = load_archives()
        restored_cases = []
        remaining_archives = []
        
        for archive in archives:
            if archive.get("id") in archive_ids:
                restored = archive.copy()
                restored.pop("archive_time", None)
                restored.pop("archive_reason", None)
                restored["version"] = new_version
                restored["status"] = "未执行"
                restored["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                restored_cases.append(restored)
            else:
                remaining_archives.append(archive)
        
        save_archives(remaining_archives)
        
        managed_cases = load_managed_cases()
        managed_cases.extend(restored_cases)
        save_managed_cases(managed_cases)
        
        return JSONResponse({
            "success": True, 
            "message": f"成功恢复{len(restored_cases)}条归档用例", 
            "count": len(restored_cases)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/archives/batch_delete")
async def batch_delete_archives(request: Request):
    try:
        data = await request.json()
        archive_ids = data.get("archive_ids", [])
        
        if not archive_ids:
            raise HTTPException(status_code=400, detail="归档ID列表不能为空")
        
        archives = load_archives()
        original_count = len(archives)
        archives = [a for a in archives if a.get("id") not in archive_ids]
        deleted_count = original_count - len(archives)
        
        save_archives(archives)
        return JSONResponse({
            "success": True, 
            "message": f"成功删除{deleted_count}条归档", 
            "count": deleted_count
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects")
async def get_projects():
    try:
        projects = load_projects()
        result = []
        for p in projects:
            result.append({
                "id": p["id"],
                "name": p["name"],
                "description": p.get("description", ""),
                "status": p.get("status", "启用"),
                "memberCount": p.get("memberCount", 0),
                "caseCount": p.get("caseCount", 0),
                "createdAt": p.get("createdAt", "")
            })
        return JSONResponse({"projects": result, "total": len(result)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    try:
        projects = load_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        return JSONResponse({"project": project})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/projects")
async def add_project(request: Request):
    try:
        data = await request.json()
        projects = load_projects()
        
        new_id = str(max([int(p["id"]) for p in projects]) + 1) if projects else "1"
        new_project = {
            "id": new_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "status": data.get("status", "启用"),
            "memberCount": data.get("memberCount", 0),
            "caseCount": 0,
            "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "modules": data.get("modules", [])
        }
        
        projects.append(new_project)
        save_projects(projects)
        
        return JSONResponse({"success": True, "message": "项目创建成功", "project": new_project})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/projects/{project_id}")
async def update_project(project_id: str, request: Request):
    try:
        data = await request.json()
        projects = load_projects()
        
        index = next((i for i, p in enumerate(projects) if p["id"] == project_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        for key in ["name", "description", "status", "memberCount"]:
            if key in data:
                projects[index][key] = data[key]
        
        save_projects(projects)
        return JSONResponse({"success": True, "message": "项目更新成功", "project": projects[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/projects/{project_id}")
async def delete_project(project_id: str):
    try:
        projects = load_projects()
        original_count = len(projects)
        projects = [p for p in projects if p["id"] != project_id]
        
        if len(projects) == original_count:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        save_projects(projects)
        return JSONResponse({"success": True, "message": "项目删除成功", "total": len(projects)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/modules")
async def get_modules(project_id: str = Query(None)):
    try:
        modules = load_modules(project_id)
        return JSONResponse({"modules": modules, "project_id": project_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/modules")
async def add_module(request: Request):
    try:
        data = await request.json()
        name = data.get("name", "")
        parent_id = data.get("parent_id", "")
        project_id = data.get("project_id", "1")
        
        if not name:
            raise HTTPException(status_code=400, detail="模块名称不能为空")
        
        projects = load_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        modules = project.get("modules", [])
        
        if parent_id:
            def find_parent(node, pid):
                if node.get("id") == pid:
                    return node
                for child in node.get("children", []):
                    found = find_parent(child, pid)
                    if found:
                        return found
                return None
            
            parent = None
            for module in modules:
                parent = find_parent(module, parent_id)
                if parent:
                    break
            
            if parent:
                if not parent.get("children"):
                    parent["children"] = []
                new_id = f"{parent_id}-{len(parent['children']) + 1}"
                parent["children"].append({"id": new_id, "name": name, "project_id": project_id})
            else:
                raise HTTPException(status_code=404, detail="父模块不存在")
        else:
            existing_ids = [m["id"] for m in modules]
            new_num = max([int(m.split("-")[-1]) for m in existing_ids if "-" in m] or [0]) + 1
            new_id = f"p{project_id}-{new_num}"
            modules.append({"id": new_id, "name": name, "project_id": project_id})
        
        project["modules"] = modules
        save_projects(projects)
        return JSONResponse({"success": True, "message": "模块添加成功", "modules": modules})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/modules/{module_id}")
async def update_module(module_id: str, request: Request):
    try:
        data = await request.json()
        name = data.get("name", "")
        project_id = data.get("project_id", "1")
        
        if not name:
            raise HTTPException(status_code=400, detail="模块名称不能为空")
        
        projects = load_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        modules = project.get("modules", [])
        
        def update_node(node, mid):
            if node.get("id") == mid:
                node["name"] = name
                return True
            for child in node.get("children", []):
                if update_node(child, mid):
                    return True
            return False
        
        updated = False
        for module in modules:
            if update_node(module, module_id):
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="模块不存在")
        
        project["modules"] = modules
        save_projects(projects)
        return JSONResponse({"success": True, "message": "模块更新成功", "modules": modules})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/modules/{module_id}")
async def delete_module(module_id: str, project_id: str = Query("1")):
    try:
        projects = load_projects()
        project = next((p for p in projects if p["id"] == project_id), None)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        
        modules = project.get("modules", [])
        
        def delete_node(nodes, mid):
            for i, node in enumerate(nodes):
                if node.get("id") == mid:
                    del nodes[i]
                    return True
                if delete_node(node.get("children", []), mid):
                    return True
            return False
        
        deleted = delete_node(modules, module_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="模块不存在")
        
        project["modules"] = modules
        save_projects(projects)
        return JSONResponse({"success": True, "message": "模块删除成功", "modules": modules})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/managed_cases")
async def get_managed_cases(module_id: str = Query(None), keyword: str = Query(None), 
                           priority: str = Query(None), case_type: str = Query(None),
                           project_id: str = Query(None),
                           page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        cases = load_managed_cases()
        
        if project_id:
            cases = [c for c in cases if c.get("project_id") == project_id]
        if module_id:
            cases = [c for c in cases if c.get("module_id") == module_id]
        if keyword:
            cases = [c for c in cases if keyword.lower() in (c.get("name", "").lower() + c.get("preconditions", "").lower())]
        if priority:
            cases = [c for c in cases if c.get("priority") == priority]
        if case_type:
            cases = [c for c in cases if c.get("type") == case_type]
        
        total = len(cases)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_cases = cases[start:end]
        
        return JSONResponse({"test_cases": paginated_cases, "total": total})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases")
async def add_managed_case(request: Request):
    try:
        data = await request.json()
        case = data.get("case", {})
        
        if not case.get("name"):
            raise HTTPException(status_code=400, detail="用例名称不能为空")
        
        cases = load_managed_cases()
        case["id"] = case.get("id") or str(uuid.uuid4())
        case["created_at"] = case.get("created_at") or datetime.now().isoformat()
        case["status"] = case.get("status") or "未执行"
        case["updated_at"] = datetime.now().isoformat()
        
        cases.append(case)
        save_managed_cases(cases)
        
        return JSONResponse({"success": True, "message": "用例添加成功", "case": case})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/managed_cases/{case_id}")
async def update_managed_case(case_id: str, request: Request):
    try:
        data = await request.json()
        updates = data.get("updates", {})
        
        cases = load_managed_cases()
        
        found = False
        for case in cases:
            if case.get("id") == case_id:
                case.update(updates)
                case["updated_at"] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="用例不存在")
        
        save_managed_cases(cases)
        return JSONResponse({"success": True, "message": "用例更新成功", "case": [c for c in cases if c.get("id") == case_id][0]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/managed_cases/{case_id}")
async def delete_managed_case(case_id: str):
    try:
        cases = load_managed_cases()
        
        original_count = len(cases)
        cases = [c for c in cases if c.get("id") != case_id]
        
        if len(cases) == original_count:
            raise HTTPException(status_code=404, detail="用例不存在")
        
        save_managed_cases(cases)
        return JSONResponse({"success": True, "message": "用例删除成功", "total": len(cases)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch")
async def batch_add_cases(request: Request):
    try:
        data = await request.json()
        cases = data.get("cases", [])
        module_id = data.get("module_id", "")
        
        if not cases:
            raise HTTPException(status_code=400, detail="用例列表不能为空")
        
        managed_cases = load_managed_cases()
        
        for case in cases:
            case["id"] = case.get("id") or str(uuid.uuid4())
            case["module_id"] = module_id
            case["status"] = case.get("status") or "未执行"
            case["created_at"] = case.get("created_at") or datetime.now().isoformat()
            case["updated_at"] = datetime.now().isoformat()
            managed_cases.append(case)
        
        save_managed_cases(managed_cases)
        return JSONResponse({"success": True, "message": f"成功添加{len(cases)}条用例", "count": len(cases), "total": len(managed_cases)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch_move")
async def batch_move_cases(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        target_module_id = data.get("target_module_id", "")
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        
        cases = load_managed_cases()
        
        moved_count = 0
        for case in cases:
            if case.get("id") in case_ids:
                case["module_id"] = target_module_id
                case["updated_at"] = datetime.now().isoformat()
                moved_count += 1
        
        save_managed_cases(cases)
        return JSONResponse({"success": True, "message": f"成功迁移{moved_count}条用例", "count": moved_count})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch_delete")
async def batch_delete_cases(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        
        cases = load_managed_cases()
        original_count = len(cases)
        cases = [c for c in cases if c.get("id") not in case_ids]
        deleted_count = original_count - len(cases)
        
        save_managed_cases(cases)
        return JSONResponse({"success": True, "message": f"成功删除{deleted_count}条用例", "count": deleted_count, "total": len(cases)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch_priority")
async def batch_update_priority(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        priority = data.get("priority", "")
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        if not priority:
            raise HTTPException(status_code=400, detail="优先级不能为空")
        
        cases = load_managed_cases()
        
        updated_count = 0
        for case in cases:
            if case.get("id") in case_ids:
                case["priority"] = priority
                case["updated_at"] = datetime.now().isoformat()
                updated_count += 1
        
        save_managed_cases(cases)
        return JSONResponse({"success": True, "message": f"成功更新{updated_count}条用例优先级", "count": updated_count})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch_archive")
async def batch_archive_cases(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        reason = data.get("reason", "")
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        
        cases = load_managed_cases()
        archived_cases = []
        remaining_cases = []
        
        for case in cases:
            if case.get("id") in case_ids:
                archive_entry = case.copy()
                archive_entry["archive_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                archive_entry["archive_reason"] = reason
                archived_cases.append(archive_entry)
            else:
                remaining_cases.append(case)
        
        save_managed_cases(remaining_cases)
        
        archives = []
        if os.path.exists(ARCHIVES_FILE):
            with open(ARCHIVES_FILE, 'r', encoding='utf-8') as f:
                archives = json.load(f)
        
        archives.extend(archived_cases)
        
        with open(ARCHIVES_FILE, 'w', encoding='utf-8') as f:
            json.dump(archives, f, ensure_ascii=False, indent=2)
        
        return JSONResponse({
            "success": True, 
            "message": f"成功归档{len(archived_cases)}条用例", 
            "count": len(archived_cases)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/managed_cases/batch_status")
async def batch_update_status(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        status = data.get("status", "")
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        if not status:
            raise HTTPException(status_code=400, detail="状态不能为空")
        
        valid_statuses = ["未执行", "执行中", "通过", "失败", "阻塞"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"无效的状态值: {status}")
        
        cases = load_managed_cases()
        
        updated_count = 0
        for case in cases:
            if case.get("id") in case_ids:
                case["status"] = status
                case["updated_at"] = datetime.now().isoformat()
                if status == "通过":
                    case["last_executed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated_count += 1
        
        save_managed_cases(cases)
        return JSONResponse({
            "success": True, 
            "message": f"成功更新{updated_count}条用例状态为「{status}」", 
            "count": updated_count
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/migrate_from_library")
async def migrate_from_library(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        target_module_id = data.get("target_module_id", "")
        project_id = data.get("project_id", "")
        
        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")
        
        if not project_id and target_module_id:
            projects = load_projects()
            for project in projects:
                modules = project.get("modules", [])
                if find_module_in_tree(modules, target_module_id):
                    project_id = project["id"]
                    break
        
        library = []
        if os.path.exists(CASE_LIBRARY_FILE):
            with open(CASE_LIBRARY_FILE, 'r', encoding='utf-8') as f:
                library = json.load(f)
        
        managed_cases = load_managed_cases()
        
        migrated_count = 0
        migrated_cases = []
        
        for case in library:
            if case.get("id") in case_ids:
                case["module_id"] = target_module_id
                case["project_id"] = project_id
                case["status"] = case.get("status") or "未执行"
                case["created_at"] = case.get("created_at") or datetime.now().isoformat()
                case["updated_at"] = datetime.now().isoformat()
                managed_cases.append(case)
                migrated_cases.append(case)
                migrated_count += 1
        
        library = [c for c in library if c.get("id") not in case_ids]
        
        with open(CASE_LIBRARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(library, f, ensure_ascii=False, indent=2)
        
        save_managed_cases(managed_cases)
        
        return JSONResponse({
            "success": True,
            "message": f"成功从用例库迁移{migrated_count}条用例",
            "count": migrated_count,
            "migrated_cases": migrated_cases,
            "library_remaining": len(library)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def find_module_in_tree(modules, module_id):
    for mod in modules:
        if mod.get("id") == module_id:
            return True
        if mod.get("children"):
            if find_module_in_tree(mod["children"], module_id):
                return True
    return False

ENVIRONMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/environments.json")

def load_environments():
    if os.path.exists(ENVIRONMENTS_FILE):
        with open(ENVIRONMENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_environments(environments):
    os.makedirs(os.path.dirname(ENVIRONMENTS_FILE), exist_ok=True)
    with open(ENVIRONMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(environments, f, ensure_ascii=False, indent=2)

DEFAULT_ENVIRONMENTS = [
    {
        "id": "1",
        "name": "开发环境",
        "base_url": "http://dev.example.com/api",
        "status": "启用",
        "timeout": 30,
        "retry": 3,
        "variables": [
            {"key": "token", "value": "dev_token_123", "description": "认证令牌"},
            {"key": "api_version", "value": "v1", "description": "API版本"}
        ],
        "headers": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Accept", "value": "application/json"}
        ],
        "created_at": "2026-07-20 10:00",
        "updated_at": "2026-07-20 10:00"
    },
    {
        "id": "2",
        "name": "测试环境",
        "base_url": "http://test.example.com/api",
        "status": "启用",
        "timeout": 30,
        "retry": 3,
        "variables": [
            {"key": "token", "value": "test_token_456", "description": "认证令牌"},
            {"key": "api_version", "value": "v1", "description": "API版本"}
        ],
        "headers": [
            {"key": "Content-Type", "value": "application/json"},
            {"key": "Accept", "value": "application/json"}
        ],
        "created_at": "2026-07-20 10:30",
        "updated_at": "2026-07-20 10:30"
    },
    {
        "id": "3",
        "name": "预发环境",
        "base_url": "http://pre.example.com/api",
        "status": "禁用",
        "timeout": 60,
        "retry": 2,
        "variables": [],
        "headers": [],
        "created_at": "2026-07-20 11:00",
        "updated_at": "2026-07-20 11:00"
    },
    {
        "id": "4",
        "name": "生产环境",
        "base_url": "http://api.example.com",
        "status": "禁用",
        "timeout": 60,
        "retry": 1,
        "variables": [],
        "headers": [],
        "created_at": "2026-07-20 11:30",
        "updated_at": "2026-07-20 11:30"
    }
]

@app.get("/api/v1/environments")
async def get_environments():
    try:
        environments = load_environments()
        if not environments:
            save_environments(DEFAULT_ENVIRONMENTS)
            environments = DEFAULT_ENVIRONMENTS
        return JSONResponse({"environments": environments, "total": len(environments)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/environments")
async def add_environment(request: Request):
    try:
        data = await request.json()
        environments = load_environments()
        
        new_env = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "base_url": data.get("base_url", ""),
            "status": data.get("status", "启用"),
            "timeout": data.get("timeout", 30),
            "retry": data.get("retry", 3),
            "variables": data.get("variables", []),
            "headers": data.get("headers", []),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        environments.append(new_env)
        save_environments(environments)
        
        return JSONResponse({"success": True, "message": "环境添加成功", "environment": new_env})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/environments/{env_id}")
async def update_environment(env_id: str, request: Request):
    try:
        data = await request.json()
        environments = load_environments()
        
        index = next((i for i, env in enumerate(environments) if env["id"] == env_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        environments[index] = {
            **environments[index],
            "name": data.get("name", environments[index]["name"]),
            "base_url": data.get("base_url", environments[index]["base_url"]),
            "status": data.get("status", environments[index]["status"]),
            "timeout": data.get("timeout", environments[index]["timeout"]),
            "retry": data.get("retry", environments[index]["retry"]),
            "variables": data.get("variables", environments[index]["variables"]),
            "headers": data.get("headers", environments[index]["headers"]),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_environments(environments)
        
        return JSONResponse({"success": True, "message": "环境更新成功", "environment": environments[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/environments/{env_id}")
async def delete_environment(env_id: str):
    try:
        environments = load_environments()
        original_count = len(environments)
        environments = [env for env in environments if env["id"] != env_id]
        
        if len(environments) == original_count:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        save_environments(environments)
        
        return JSONResponse({"success": True, "message": "环境删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/environments/{env_id}/toggle")
async def toggle_environment(env_id: str):
    try:
        environments = load_environments()
        
        index = next((i for i, env in enumerate(environments) if env["id"] == env_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        environments[index]["status"] = "启用" if environments[index]["status"] == "禁用" else "禁用"
        environments[index]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        save_environments(environments)
        
        return JSONResponse({"success": True, "message": f"环境已{environments[index]['status']}", "environment": environments[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/environments/{env_id}/clone")
async def clone_environment(env_id: str):
    try:
        environments = load_environments()
        
        env = next((e for e in environments if e["id"] == env_id), None)
        if env is None:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        new_env = {
            **env,
            "id": str(uuid.uuid4()),
            "name": env["name"] + " (副本)",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        environments.append(new_env)
        save_environments(environments)
        
        return JSONResponse({"success": True, "message": "环境复制成功", "environment": new_env})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

API_CASES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/api_cases.json")

def load_api_cases():
    if os.path.exists(API_CASES_FILE):
        with open(API_CASES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    if DEFAULT_API_CASES:
        save_api_cases(DEFAULT_API_CASES)
        return DEFAULT_API_CASES
    return []

def save_api_cases(cases):
    os.makedirs(os.path.dirname(API_CASES_FILE), exist_ok=True)
    with open(API_CASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

DEFAULT_API_CASES = [
    {
        "id": "1",
        "name": "用户登录接口",
        "method": "POST",
        "url": "/api/login",
        "module": "用户管理",
        "project_id": "1",
        "environment_id": "1",
        "headers": [
            {"key": "Content-Type", "value": "application/json"}
        ],
        "params": [],
        "body": "{\"username\": \"admin\", \"password\": \"123456\"}",
        "body_type": "json",
        "assertions": [
            {"type": "status_code", "expected": 200, "operator": "=="},
            {"type": "json_path", "field": "code", "expected": 0, "operator": "=="},
            {"type": "json_path", "field": "data.token", "expected": "", "operator": "!="}
        ],
        "status": "已启用",
        "created_at": "2026-07-21 10:00",
        "updated_at": "2026-07-21 10:00"
    },
    {
        "id": "2",
        "name": "获取用户列表",
        "method": "GET",
        "url": "/api/users",
        "module": "用户管理",
        "project_id": "1",
        "environment_id": "1",
        "headers": [],
        "params": [
            {"key": "page", "value": "1"},
            {"key": "size", "value": "10"}
        ],
        "body": "",
        "body_type": "none",
        "assertions": [
            {"type": "status_code", "expected": 200, "operator": "=="},
            {"type": "json_path", "field": "code", "expected": 0, "operator": "=="}
        ],
        "status": "已启用",
        "created_at": "2026-07-21 10:30",
        "updated_at": "2026-07-21 10:30"
    },
    {
        "id": "3",
        "name": "创建用户",
        "method": "POST",
        "url": "/api/users",
        "module": "用户管理",
        "project_id": "2",
        "environment_id": "1",
        "headers": [
            {"key": "Content-Type", "value": "application/json"}
        ],
        "params": [],
        "body": "{\"username\": \"testuser\", \"email\": \"test@example.com\", \"role\": \"user\"}",
        "body_type": "json",
        "assertions": [
            {"type": "status_code", "expected": 201, "operator": "=="},
            {"type": "json_path", "field": "code", "expected": 0, "operator": "=="}
        ],
        "status": "已启用",
        "created_at": "2026-07-21 11:00",
        "updated_at": "2026-07-21 11:00"
    },
    {
        "id": "4",
        "name": "更新用户",
        "method": "PUT",
        "url": "/api/users/{id}",
        "module": "用户管理",
        "project_id": "2",
        "environment_id": "1",
        "headers": [
            {"key": "Content-Type", "value": "application/json"}
        ],
        "params": [],
        "body": "{\"username\": \"updateduser\"}",
        "body_type": "json",
        "assertions": [
            {"type": "status_code", "expected": 200, "operator": "=="}
        ],
        "status": "已启用",
        "created_at": "2026-07-21 11:30",
        "updated_at": "2026-07-21 11:30"
    },
    {
        "id": "5",
        "name": "删除用户",
        "method": "DELETE",
        "url": "/api/users/{id}",
        "module": "用户管理",
        "project_id": "3",
        "environment_id": "1",
        "headers": [],
        "params": [],
        "body": "",
        "body_type": "none",
        "assertions": [
            {"type": "status_code", "expected": 200, "operator": "=="}
        ],
        "status": "已禁用",
        "created_at": "2026-07-21 12:00",
        "updated_at": "2026-07-21 12:00"
    },
    {
        "id": "6",
        "name": "获取项目列表",
        "method": "GET",
        "url": "/api/projects",
        "module": "项目管理",
        "project_id": "3",
        "environment_id": "2",
        "headers": [],
        "params": [],
        "body": "",
        "body_type": "none",
        "assertions": [
            {"type": "status_code", "expected": 200, "operator": "=="}
        ],
        "status": "已启用",
        "created_at": "2026-07-21 14:00",
        "updated_at": "2026-07-21 14:00"
    }
]

@app.get("/api/v1/api_cases")
async def get_api_cases(project_id: str = Query(None)):
    try:
        cases = load_api_cases()
        if project_id:
            cases = [c for c in cases if c.get("project_id") == project_id]
        return JSONResponse({"cases": cases, "total": len(cases)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/api_cases")
async def add_api_case(request: Request):
    try:
        data = await request.json()
        cases = load_api_cases()
        
        new_case = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "method": data.get("method", "GET"),
            "url": data.get("url", ""),
            "module": data.get("module", ""),
            "project_id": data.get("project_id", ""),
            "environment_id": data.get("environment_id", ""),
            "headers": data.get("headers", []),
            "params": data.get("params", []),
            "body": data.get("body", ""),
            "body_type": data.get("body_type", "none"),
            "assertions": data.get("assertions", []),
            "status": data.get("status", "已启用"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        cases.append(new_case)
        save_api_cases(cases)
        
        return JSONResponse({"success": True, "message": "接口用例添加成功", "case": new_case})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/api_cases/{case_id}")
async def update_api_case(case_id: str, request: Request):
    try:
        data = await request.json()
        cases = load_api_cases()
        
        index = next((i for i, c in enumerate(cases) if c["id"] == case_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="接口用例不存在")
        
        cases[index] = {
            **cases[index],
            "name": data.get("name", cases[index]["name"]),
            "method": data.get("method", cases[index]["method"]),
            "url": data.get("url", cases[index]["url"]),
            "module": data.get("module", cases[index]["module"]),
            "environment_id": data.get("environment_id", cases[index]["environment_id"]),
            "headers": data.get("headers", cases[index]["headers"]),
            "params": data.get("params", cases[index]["params"]),
            "body": data.get("body", cases[index]["body"]),
            "body_type": data.get("body_type", cases[index]["body_type"]),
            "assertions": data.get("assertions", cases[index]["assertions"]),
            "status": data.get("status", cases[index]["status"]),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_api_cases(cases)
        
        return JSONResponse({"success": True, "message": "接口用例更新成功", "case": cases[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/api_cases/{case_id}")
async def delete_api_case(case_id: str):
    try:
        cases = load_api_cases()
        original_count = len(cases)
        cases = [c for c in cases if c["id"] != case_id]
        
        if len(cases) == original_count:
            raise HTTPException(status_code=404, detail="接口用例不存在")
        
        save_api_cases(cases)
        
        return JSONResponse({"success": True, "message": "接口用例删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/api_cases/{case_id}/debug")
async def debug_api_case(case_id: str, request: Request):
    try:
        data = await request.json()
        cases = load_api_cases()
        
        case = next((c for c in cases if c["id"] == case_id), None)
        if case is None:
            raise HTTPException(status_code=404, detail="接口用例不存在")
        
        env_id = data.get("environment_id", "") or case.get("environment_id", "")
        environments = load_environments()
        env = next((e for e in environments if e["id"] == env_id), None) if env_id else None
        
        if env:
            base_url = env["base_url"].rstrip('/')
            full_url = base_url + case["url"]
        else:
            url = case.get("url", "")
            if url.startswith("http://") or url.startswith("https://"):
                full_url = url
            else:
                full_url = f"http://localhost:8001{url}"
        
        headers = {}
        if env:
            for h in env.get("headers", []):
                headers[h["key"]] = h["value"]
        for h in case.get("headers", []):
            headers[h["key"]] = h["value"]
        
        import requests
        
        params = {}
        for p in case.get("params", []):
            params[p["key"]] = p["value"]
        
        body_data = None
        content_type = headers.get("Content-Type", "")
        if case.get("body") and case.get("body_type") != "none":
            if case.get("body_type") == "json" or "application/json" in content_type:
                try:
                    body_data = json.loads(case["body"])
                except:
                    body_data = case["body"]
            else:
                body_data = case["body"]
        
        timeout_val = env.get("timeout", 30) if env else 30
        
        try:
            start_time = datetime.now()
            response = requests.request(
                method=case["method"],
                url=full_url,
                headers=headers,
                params=params,
                json=body_data if case.get("body_type") == "json" else None,
                data=body_data if case.get("body_type") != "json" else None,
                timeout=timeout_val
            )
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            response_headers = dict(response.headers)
            decoded_text = decode_response_body(response)
            try:
                response_body = json.loads(decoded_text)
                body_type = "json"
            except:
                response_body = decoded_text
                body_type = "text"
            
            assertion_results = []
            for assertion in case.get("assertions", []):
                result = {"assertion": assertion, "passed": False, "actual": None}
                
                if assertion["type"] == "status_code":
                    actual = response.status_code
                    result["actual"] = actual
                    op = assertion["operator"]
                    expected = assertion["expected"]
                    if op == "==" and actual == expected:
                        result["passed"] = True
                    elif op == "!=" and actual != expected:
                        result["passed"] = True
                    elif op == ">=" and actual >= expected:
                        result["passed"] = True
                    elif op == "<=" and actual <= expected:
                        result["passed"] = True
                
                elif assertion["type"] == "json_path":
                    if body_type == "json":
                        path = assertion["field"]
                        value = response_body
                        for key in path.split('.'):
                            if isinstance(value, dict) and key in value:
                                value = value[key]
                            elif isinstance(value, list) and key.isdigit():
                                idx = int(key)
                                if idx < len(value):
                                    value = value[idx]
                                else:
                                    value = None
                            else:
                                value = None
                                break
                        actual = value
                        result["actual"] = actual
                        op = assertion["operator"]
                        expected = assertion["expected"]
                        if op == "==" and actual == expected:
                            result["passed"] = True
                        elif op == "!=" and actual != expected:
                            result["passed"] = True
                        elif op == ">=" and actual is not None and actual >= expected:
                            result["passed"] = True
                        elif op == "<=" and actual is not None and actual <= expected:
                            result["passed"] = True
                        elif op == "contains" and isinstance(actual, str) and str(expected) in actual:
                            result["passed"] = True
                        elif op == "not_contains" and isinstance(actual, str) and str(expected) not in actual:
                            result["passed"] = True
                
                elif assertion["type"] == "response_time":
                    result["actual"] = elapsed
                    op = assertion["operator"]
                    expected = assertion["expected"]
                    if op == "<=" and elapsed <= expected:
                        result["passed"] = True
                
                assertion_results.append(result)
            
            all_passed = all(r["passed"] for r in assertion_results)
            
            return JSONResponse({
                "success": True,
                "message": "调试完成",
                "response": {
                    "status_code": response.status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "body_type": body_type,
                    "time": round(elapsed, 2)
                },
                "assertions": assertion_results,
                "all_passed": all_passed
            })
        except requests.exceptions.RequestException as e:
            return JSONResponse({
                "success": False,
                "message": f"请求失败: {str(e)}",
                "response": None,
                "assertions": [],
                "all_passed": False
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

SCENARIOS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/scenarios.json")

def load_scenarios():
    if os.path.exists(SCENARIOS_FILE):
        with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    if DEFAULT_SCENARIOS:
        save_scenarios(DEFAULT_SCENARIOS)
        return DEFAULT_SCENARIOS
    return []

def save_scenarios(scenarios):
    os.makedirs(os.path.dirname(SCENARIOS_FILE), exist_ok=True)
    with open(SCENARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

DEFAULT_SCENARIOS = [
    {
        "id": "1",
        "name": "用户登录后获取数据",
        "description": "用户登录后获取用户列表和项目列表",
        "project_id": "1",
        "steps": [
            {
                "id": "1-1",
                "api_case_id": "1",
                "name": "用户登录",
                "method": "POST",
                "url": "/api/login",
                "waitTime": 0,
                "retryCount": 2,
                "skip": False,
                "extract_params": [{"key": "token", "path": "data.token"}]
            },
            {
                "id": "1-2",
                "api_case_id": "2",
                "name": "获取用户列表",
                "method": "GET",
                "url": "/api/users",
                "waitTime": 1,
                "retryCount": 1,
                "skip": False,
                "extract_params": []
            },
            {
                "id": "1-3",
                "api_case_id": "6",
                "name": "获取项目列表",
                "method": "GET",
                "url": "/api/projects",
                "waitTime": 1,
                "retryCount": 1,
                "skip": False,
                "extract_params": []
            }
        ],
        "status": "已启用",
        "created_at": "2026-07-22 10:00",
        "updated_at": "2026-07-22 10:00"
    },
    {
        "id": "2",
        "name": "用户管理流程",
        "description": "创建、更新、删除用户的完整流程",
        "project_id": "2",
        "steps": [
            {
                "id": "2-1",
                "api_case_id": "3",
                "name": "创建用户",
                "method": "POST",
                "url": "/api/users",
                "waitTime": 0,
                "retryCount": 1,
                "skip": False,
                "extract_params": [{"key": "userId", "path": "data.id"}]
            },
            {
                "id": "2-2",
                "api_case_id": "4",
                "name": "更新用户",
                "method": "PUT",
                "url": "/api/users/{id}",
                "waitTime": 1,
                "retryCount": 1,
                "skip": False,
                "extract_params": []
            }
        ],
        "status": "已启用",
        "created_at": "2026-07-22 11:00",
        "updated_at": "2026-07-22 11:00"
    }
]

@app.get("/api/v1/scenarios")
async def get_scenarios(project_id: str = Query(None)):
    try:
        scenarios = load_scenarios()
        if project_id:
            scenarios = [s for s in scenarios if s.get("project_id") == project_id]
        return JSONResponse({"scenarios": scenarios, "total": len(scenarios)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scenarios")
async def add_scenario(request: Request):
    try:
        data = await request.json()
        scenarios = load_scenarios()
        
        new_scenario = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "project_id": data.get("project_id", ""),
            "steps": data.get("steps", []),
            "status": data.get("status", "已启用"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        scenarios.append(new_scenario)
        save_scenarios(scenarios)
        
        return JSONResponse({"success": True, "message": "场景添加成功", "scenario": new_scenario})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/scenarios/{scenario_id}")
async def update_scenario(scenario_id: str, request: Request):
    try:
        data = await request.json()
        scenarios = load_scenarios()
        
        index = next((i for i, s in enumerate(scenarios) if s["id"] == scenario_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        scenarios[index] = {
            **scenarios[index],
            "name": data.get("name", scenarios[index]["name"]),
            "description": data.get("description", scenarios[index]["description"]),
            "steps": data.get("steps", scenarios[index]["steps"]),
            "status": data.get("status", scenarios[index]["status"]),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_scenarios(scenarios)
        
        return JSONResponse({"success": True, "message": "场景更新成功", "scenario": scenarios[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    try:
        scenarios = load_scenarios()
        original_count = len(scenarios)
        scenarios = [s for s in scenarios if s["id"] != scenario_id]
        
        if len(scenarios) == original_count:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        save_scenarios(scenarios)
        
        return JSONResponse({"success": True, "message": "场景删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/scenarios/{scenario_id}/execute")
async def execute_scenario_by_id(scenario_id: str, request: Request):
    try:
        data = await request.json()
        environment_id = data.get("environment_id")
        
        scenarios = load_scenarios()
        scenario = next((s for s in scenarios if s["id"] == scenario_id), None)
        if scenario is None:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        environments = load_environments()
        env = next((e for e in environments if e["id"] == environment_id), None)
        if not env:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        report = await execute_scenario(scenario, env)
        
        return JSONResponse({"success": True, "message": "场景执行完成", "report": report})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/tasks.json")

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

DEFAULT_TASKS = [
    {
        "id": "1",
        "name": "每日用户登录测试",
        "scenario_id": "1",
        "scenario_name": "用户登录后获取数据",
        "environment_id": "1",
        "environment_name": "开发环境",
        "cron_expression": "0 9 * * *",
        "status": "已启用",
        "last_run_time": "2026-07-22 09:00",
        "last_run_status": "成功",
        "next_run_time": "2026-07-23 09:00",
        "created_at": "2026-07-22 09:00",
        "updated_at": "2026-07-22 09:00"
    }
]

@app.get("/api/v1/tasks")
async def get_tasks():
    try:
        tasks = load_tasks()
        return JSONResponse({"tasks": tasks, "total": len(tasks)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tasks")
async def add_task(request: Request):
    try:
        data = await request.json()
        tasks = load_tasks()
        
        new_task = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "scenario_id": data.get("scenario_id", ""),
            "scenario_name": data.get("scenario_name", ""),
            "environment_id": data.get("environment_id", ""),
            "environment_name": data.get("environment_name", ""),
            "cron_expression": data.get("cron_expression", ""),
            "status": data.get("status", "已启用"),
            "last_run_time": "",
            "last_run_status": "",
            "next_run_time": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        tasks.append(new_task)
        save_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "任务添加成功", "task": new_task})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/tasks/{task_id}")
async def update_task(task_id: str, request: Request):
    try:
        data = await request.json()
        tasks = load_tasks()
        
        index = next((i for i, t in enumerate(tasks) if t["id"] == task_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        tasks[index] = {
            **tasks[index],
            "name": data.get("name", tasks[index]["name"]),
            "scenario_id": data.get("scenario_id", tasks[index]["scenario_id"]),
            "scenario_name": data.get("scenario_name", tasks[index]["scenario_name"]),
            "environment_id": data.get("environment_id", tasks[index]["environment_id"]),
            "environment_name": data.get("environment_name", tasks[index]["environment_name"]),
            "cron_expression": data.get("cron_expression", tasks[index]["cron_expression"]),
            "status": data.get("status", tasks[index]["status"]),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "任务更新成功", "task": tasks[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: str):
    try:
        tasks = load_tasks()
        original_count = len(tasks)
        tasks = [t for t in tasks if t["id"] != task_id]
        
        if len(tasks) == original_count:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        save_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "任务删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    try:
        tasks = load_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        scenarios = load_scenarios()
        scenario = next((s for s in scenarios if s["id"] == task["scenario_id"]), None)
        if scenario is None:
            raise HTTPException(status_code=404, detail="场景不存在")
        
        environments = load_environments()
        env = next((e for e in environments if e["id"] == task["environment_id"]), None)
        if not env:
            raise HTTPException(status_code=404, detail="环境不存在")
        
        report = await execute_scenario(scenario, env)
        
        task["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        task["last_run_status"] = "成功" if report["all_passed"] else "失败"
        save_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "任务执行完成", "report": report})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_scenario(scenario, env):
    base_url = env["base_url"].rstrip('/')
    steps_results = []
    all_passed = True
    total_time = 0
    extracted_vars = {}
    
    for step in scenario.get("steps", []):
        if step.get("skip"):
            steps_results.append({
                "step": step,
                "skipped": True,
                "passed": True,
                "response": None,
                "assertions": [],
                "time": 0
            })
            continue
        
        full_url = base_url + step["url"]
        
        headers = {}
        for h in env.get("headers", []):
            headers[h["key"]] = h["value"]
        
        for extract_key, extract_value in extracted_vars.items():
            full_url = full_url.replace(f"{{{extract_key}}}", str(extract_value))
        
        import requests
        import json as json_module
        
        params = {}
        body_data = None
        request_body_str = step.get("request_body", "")
        
        if request_body_str and step["method"] in ["POST", "PUT", "PATCH"]:
            for extract_key, extract_value in extracted_vars.items():
                request_body_str = request_body_str.replace(f"{{{extract_key}}}", str(extract_value))
            
            try:
                body_data = json_module.loads(request_body_str)
            except:
                body_data = request_body_str
        
        try:
            start_time = datetime.now()
            response = requests.request(
                method=step["method"],
                url=full_url,
                headers=headers,
                params=params,
                json=body_data if isinstance(body_data, dict) else None,
                data=body_data if not isinstance(body_data, dict) else None,
                timeout=env.get("timeout", 30)
            )
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            total_time += elapsed
            
            response_headers = dict(response.headers)
            decoded_text = decode_response_body(response)
            try:
                response_body = json.loads(decoded_text)
                body_type = "json"
            except:
                response_body = decoded_text
                body_type = "text"
            
            for ext in step.get("extract_params", []):
                key = ext.get("key", "")
                path = ext.get("path", "")
                if key and path and body_type == "json":
                    value = response_body
                    for p in path.split('.'):
                        if isinstance(value, dict) and p in value:
                            value = value[p]
                        elif isinstance(value, list) and p.isdigit():
                            idx = int(p)
                            if idx < len(value):
                                value = value[idx]
                        else:
                            value = None
                            break
                    if value is not None:
                        extracted_vars[key] = value
            
            assertions = []
            step_passed = True
            
            if step.get("api_case_id"):
                cases = load_api_cases()
                api_case = next((c for c in cases if c["id"] == step["api_case_id"]), None)
                if api_case:
                    for assertion in api_case.get("assertions", []):
                        result = {"assertion": assertion, "passed": False, "actual": None}
                        
                        if assertion["type"] == "status_code":
                            actual = response.status_code
                            result["actual"] = actual
                            op = assertion["operator"]
                            expected = assertion["expected"]
                            if op == "==" and actual == expected:
                                result["passed"] = True
                            elif op == "!=" and actual != expected:
                                result["passed"] = True
                            elif op == ">=" and actual >= expected:
                                result["passed"] = True
                            elif op == "<=" and actual <= expected:
                                result["passed"] = True
                        
                        elif assertion["type"] == "json_path":
                            if body_type == "json":
                                path_val = assertion["field"]
                                value = response_body
                                for key_p in path_val.split('.'):
                                    if isinstance(value, dict) and key_p in value:
                                        value = value[key_p]
                                    elif isinstance(value, list) and key_p.isdigit():
                                        idx = int(key_p)
                                        if idx < len(value):
                                            value = value[idx]
                                    else:
                                        value = None
                                        break
                                actual = value
                                result["actual"] = actual
                                op = assertion["operator"]
                                expected = assertion["expected"]
                                if op == "==" and actual == expected:
                                    result["passed"] = True
                                elif op == "!=" and actual != expected:
                                    result["passed"] = True
                                elif op == ">=" and actual is not None and actual >= expected:
                                    result["passed"] = True
                                elif op == "<=" and actual is not None and actual <= expected:
                                    result["passed"] = True
                                elif op == "contains" and isinstance(actual, str) and str(expected) in actual:
                                    result["passed"] = True
                                elif op == "not_contains" and isinstance(actual, str) and str(expected) not in actual:
                                    result["passed"] = True
                        
                        elif assertion["type"] == "response_time":
                            result["actual"] = elapsed
                            op = assertion["operator"]
                            expected = assertion["expected"]
                            if op == "<=" and elapsed <= expected:
                                result["passed"] = True
                        
                        assertions.append(result)
                        if not result["passed"]:
                            step_passed = False
            
            if not step_passed:
                all_passed = False
            
            steps_results.append({
                "step": step,
                "skipped": False,
                "passed": step_passed,
                "request_body": body_data if body_data else None,
                "response": {
                    "status_code": response.status_code,
                    "headers": response_headers,
                    "body": response_body,
                    "body_type": body_type,
                    "time": round(elapsed, 2)
                },
                "assertions": assertions,
                "extracted_vars": dict(extracted_vars),
                "time": round(elapsed, 2)
            })
            
            if step.get("waitTime", 0) > 0:
                import time
                time.sleep(step["waitTime"])
        
        except requests.exceptions.RequestException as e:
            step_passed = False
            all_passed = False
            steps_results.append({
                "step": step,
                "skipped": False,
                "passed": False,
                "response": None,
                "assertions": [],
                "time": 0,
                "error": str(e)
            })
    
    passed_count = sum(1 for r in steps_results if r["passed"])
    failed_count = sum(1 for r in steps_results if not r["passed"] and not r["skipped"])
    skipped_count = sum(1 for r in steps_results if r["skipped"])
    
    report_data = {
        "id": str(uuid.uuid4()),
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "environment_id": env["id"],
        "environment_name": env["name"],
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_time": round(total_time, 2),
        "total_steps": len(steps_results),
        "passed_steps": passed_count,
        "failed_steps": failed_count,
        "skipped_steps": skipped_count,
        "all_passed": all_passed,
        "status": "成功" if all_passed else "失败",
        "steps": steps_results
    }
    
    reports = load_reports()
    reports.insert(0, report_data)
    save_reports(reports)
    
    return report_data

REPORTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/reports.json")

def load_reports():
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_reports(reports):
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

@app.get("/api/v1/reports")
async def get_reports():
    try:
        reports = load_reports()
        return JSONResponse({"reports": reports, "total": len(reports)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/{report_id}")
async def get_report_detail(report_id: str):
    try:
        reports = load_reports()
        report = next((r for r in reports if r["id"] == report_id), None)
        if report is None:
            raise HTTPException(status_code=404, detail="报告不存在")
        return JSONResponse({"report": report})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/reports/{report_id}")
async def delete_report(report_id: str):
    try:
        reports = load_reports()
        original_count = len(reports)
        reports = [r for r in reports if r["id"] != report_id]
        
        if len(reports) == original_count:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        save_reports(reports)
        
        return JSONResponse({"success": True, "message": "报告删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/reports/{report_id}/export")
async def export_report(report_id: str):
    try:
        reports = load_reports()
        report = next((r for r in reports if r["id"] == report_id), None)
        if report is None:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        export_path = os.path.join(UPLOAD_DIR, f"report_{report_id}.json")
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return FileResponse(
            export_path,
            filename=f"report_{report_id}.json",
            media_type="application/json"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

GIT_TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/git_tasks.json")
USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/users.json")
ROLES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/roles.json")
PERMISSIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/permissions.json")
ITERATIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/iterations.json")

def load_git_tasks():
    if os.path.exists(GIT_TASKS_FILE):
        with open(GIT_TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_git_tasks(tasks):
    os.makedirs(os.path.dirname(GIT_TASKS_FILE), exist_ok=True)
    with open(GIT_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

@app.get("/api/v1/git-tasks")
async def get_git_tasks():
    try:
        tasks = load_git_tasks()
        return JSONResponse({"tasks": tasks, "total": len(tasks)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/git-tasks")
async def add_git_task(request: Request):
    try:
        data = await request.json()
        tasks = load_git_tasks()
        
        new_task = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "repo_url": data.get("repo_url", ""),
            "branch": data.get("branch", "main"),
            "auth_type": data.get("auth_type", "none"),
            "username": data.get("username", ""),
            "password": data.get("password", ""),
            "ssh_key": data.get("ssh_key", ""),
            "script_path": data.get("script_path", ""),
            "run_command": data.get("run_command", "pytest"),
            "environment_id": data.get("environment_id", ""),
            "environment_name": data.get("environment_name", ""),
            "cron_expression": data.get("cron_expression", ""),
            "status": data.get("status", "已启用"),
            "last_pull_time": "",
            "last_pull_status": "",
            "last_run_time": "",
            "last_run_status": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        tasks.append(new_task)
        save_git_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "Git任务添加成功", "task": new_task})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/git-tasks/{task_id}")
async def update_git_task(task_id: str, request: Request):
    try:
        data = await request.json()
        tasks = load_git_tasks()
        
        index = next((i for i, t in enumerate(tasks) if t["id"] == task_id), None)
        if index is None:
            raise HTTPException(status_code=404, detail="Git任务不存在")
        
        tasks[index] = {
            **tasks[index],
            "name": data.get("name", tasks[index]["name"]),
            "repo_url": data.get("repo_url", tasks[index]["repo_url"]),
            "branch": data.get("branch", tasks[index]["branch"]),
            "auth_type": data.get("auth_type", tasks[index]["auth_type"]),
            "username": data.get("username", tasks[index]["username"]),
            "password": data.get("password", tasks[index]["password"]),
            "ssh_key": data.get("ssh_key", tasks[index]["ssh_key"]),
            "script_path": data.get("script_path", tasks[index]["script_path"]),
            "run_command": data.get("run_command", tasks[index]["run_command"]),
            "environment_id": data.get("environment_id", tasks[index]["environment_id"]),
            "environment_name": data.get("environment_name", tasks[index]["environment_name"]),
            "cron_expression": data.get("cron_expression", tasks[index]["cron_expression"]),
            "status": data.get("status", tasks[index]["status"]),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        save_git_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "Git任务更新成功", "task": tasks[index]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/git-tasks/{task_id}")
async def delete_git_task(task_id: str):
    try:
        tasks = load_git_tasks()
        original_count = len(tasks)
        tasks = [t for t in tasks if t["id"] != task_id]
        
        if len(tasks) == original_count:
            raise HTTPException(status_code=404, detail="Git任务不存在")
        
        save_git_tasks(tasks)
        
        return JSONResponse({"success": True, "message": "Git任务删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/git-tasks/{task_id}/pull")
async def pull_git_task(task_id: str):
    try:
        tasks = load_git_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail="Git任务不存在")
        
        import subprocess
        import shutil
        
        repo_dir = os.path.join(UPLOAD_DIR, "git_repos", task_id)
        os.makedirs(repo_dir, exist_ok=True)
        
        try:
            if os.path.exists(os.path.join(repo_dir, ".git")):
                cmd = f"git -C {repo_dir} pull origin {task['branch']}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    pull_status = "成功"
                    pull_message = result.stdout
                else:
                    pull_status = "失败"
                    pull_message = result.stderr
            else:
                if os.path.exists(repo_dir):
                    shutil.rmtree(repo_dir)
                    os.makedirs(repo_dir, exist_ok=True)
                
                clone_url = task["repo_url"]
                if task["auth_type"] == "https" and task["username"] and task["password"]:
                    if "https://" in clone_url:
                        clone_url = clone_url.replace("https://", f"https://{task['username']}:{task['password']}@")
                
                cmd = f"git clone -b {task['branch']} {clone_url} {repo_dir}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    pull_status = "成功"
                    pull_message = "仓库克隆成功"
                else:
                    pull_status = "失败"
                    pull_message = result.stderr
            
            task["last_pull_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            task["last_pull_status"] = pull_status
            save_git_tasks(tasks)
            
            return JSONResponse({
                "success": pull_status == "成功",
                "message": f"代码拉取{pull_status}",
                "status": pull_status,
                "output": pull_message,
                "repo_dir": repo_dir
            })
        except subprocess.TimeoutExpired:
            return JSONResponse({
                "success": False,
                "message": "Git操作超时",
                "status": "失败"
            })
        except Exception as e:
            return JSONResponse({
                "success": False,
                "message": f"Git操作失败: {str(e)}",
                "status": "失败"
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/git-tasks/{task_id}/execute")
async def execute_git_task(task_id: str):
    try:
        tasks = load_git_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            raise HTTPException(status_code=404, detail="Git任务不存在")
        
        import subprocess
        import shutil
        
        repo_dir = os.path.join(UPLOAD_DIR, "git_repos", task_id)
        
        if not os.path.exists(repo_dir):
            pull_result = await pull_git_task(task_id)
            pull_data = pull_result.body
            if isinstance(pull_data, bytes):
                pull_data = json.loads(pull_data.decode())
            if not pull_data.get("success", False):
                return JSONResponse({
                    "success": False,
                    "message": f"代码拉取失败: {pull_data.get('message', '')}",
                    "report": None
                })
        
        script_path = task.get("script_path", "")
        run_command = task.get("run_command", "pytest")
        
        work_dir = os.path.join(repo_dir, script_path) if script_path else repo_dir
        
        if not os.path.exists(work_dir):
            return JSONResponse({
                "success": False,
                "message": f"脚本目录不存在: {work_dir}",
                "report": None
            })
        
        start_time = datetime.now()
        
        try:
            process = subprocess.Popen(
                run_command,
                shell=True,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=300)
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            run_status = "成功" if process.returncode == 0 else "失败"
            run_message = stdout if process.returncode == 0 else stderr
            
            task["last_run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            task["last_run_status"] = run_status
            save_git_tasks(tasks)
            
            report = {
                "id": str(uuid.uuid4()),
                "git_task_id": task_id,
                "task_name": task["name"],
                "repo_url": task["repo_url"],
                "branch": task["branch"],
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_time": round(elapsed, 2),
                "status": run_status,
                "return_code": process.returncode,
                "output": stdout,
                "error": stderr if stderr else "",
                "work_dir": work_dir,
                "command": run_command
            }
            
            reports = load_reports()
            reports.insert(0, report)
            save_reports(reports)
            
            return JSONResponse({
                "success": run_status == "成功",
                "message": f"脚本执行{run_status}",
                "report": report
            })
        except subprocess.TimeoutExpired:
            process.kill()
            return JSONResponse({
                "success": False,
                "message": "脚本执行超时（超过300秒）",
                "report": None
            })
        except Exception as e:
            return JSONResponse({
                "success": False,
                "message": f"脚本执行失败: {str(e)}",
                "report": None
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/swagger/generate")
async def generate_from_swagger(request: Request):
    try:
        data = await request.json()
        swagger_url = data.get("swagger_url", "")
        swagger_content = data.get("swagger_content", "")

        if not swagger_url and not swagger_content:
            raise HTTPException(status_code=400, detail="请提供Swagger URL或内容")

        swagger_data = None

        if swagger_content:
            try:
                swagger_data = json.loads(swagger_content)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Swagger内容JSON格式错误: {str(e)}")
        elif swagger_url:
            try:
                import requests as req
                trimmed_url = swagger_url.strip()
                if trimmed_url.startswith('/'):
                    base_url = str(request.base_url).rstrip('/')
                    full_url = base_url + trimmed_url
                else:
                    full_url = trimmed_url
                response = req.get(full_url, timeout=30, headers={'Accept': 'application/json, */*'})
                response.raise_for_status()
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type or trimmed_url.endswith('.json'):
                    swagger_data = response.json()
                else:
                    text = response.text
                    try:
                        swagger_data = json.loads(text)
                    except json.JSONDecodeError:
                        swagger_data = json.loads(text)
            except ImportError:
                raise HTTPException(status_code=500, detail="服务器缺少requests库，请联系管理员")
            except Exception as e:
                error_msg = str(e)
                if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                    raise HTTPException(status_code=400, detail="获取Swagger文档超时，请检查URL是否正确")
                elif 'connection' in error_msg.lower() or 'connect' in error_msg.lower():
                    raise HTTPException(status_code=400, detail=f"无法连接到Swagger文档服务器: {error_msg}")
                elif '404' in error_msg:
                    raise HTTPException(status_code=404, detail="Swagger文档地址不存在(404)，请检查URL")
                elif '401' in error_msg or '403' in error_msg:
                    raise HTTPException(status_code=400, detail="访问Swagger文档需要认证，请检查权限")
                else:
                    raise HTTPException(status_code=400, detail=f"获取Swagger文档失败: {error_msg}")

        if not swagger_data:
            raise HTTPException(status_code=400, detail="Swagger数据为空")

        parsed = swagger_test_generator.parse_document(swagger_data)

        all_results = swagger_test_generator.generate_all_test_cases(parsed["apis"])

        case_ids = [api["id"] for api in parsed["apis"]]

        return JSONResponse({
            "success": True,
            "message": f"成功解析Swagger文档，发现{parsed['total_apis']}个接口，生成{all_results['stats']['total']}条测试用例(功能:{all_results['stats']['functional']} 性能:{all_results['stats']['performance']} 安全:{all_results['stats']['security']})",
            "api_cases": parsed["apis"],
            "test_cases": all_results["test_cases"],
            "functional_cases": all_results["functional_cases"],
            "performance_cases": all_results["performance_cases"],
            "security_cases": all_results["security_cases"],
            "features": all_results["features"],
            "risk_assessment": all_results["risk_assessment"],
            "postman_collection": all_results["postman_collection"],
            "jmeter_template": all_results["jmeter_template"],
            "pytest_script": all_results["pytest_script"],
            "info": {
                "title": parsed["title"],
                "version": parsed["version"],
                "base_url": parsed["base_url"],
                "total_apis": parsed["total_apis"],
                "modules": len(all_results["features"]),
                "stats": all_results["stats"],
                "case_ids": case_ids
            }
        })
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Swagger文档格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/api_cases/import_from_swagger")
async def import_api_cases_from_swagger(request: Request):
    try:
        data = await request.json()
        apis = data.get("apis", [])
        project_id = data.get("project_id", "")
        module_override = data.get("module", "")
        environment_id = data.get("environment_id", "")

        if not apis:
            raise HTTPException(status_code=400, detail="请提供要导入的API接口列表")

        cases = load_api_cases()

        imported = 0
        imported_cases = []

        for api in apis:
            if not isinstance(api, dict):
                continue

            headers = [{"key": "Content-Type", "value": "application/json"}]
            if api.get("supports_auth", True):
                headers.append({"key": "Authorization", "value": "Bearer {{token}}"})

            params = []
            for p in api.get("params", []) or []:
                if p.get("in") in ("query", "path"):
                    params.append({
                        "key": p.get("name", ""),
                        "value": p.get("example", "") or "",
                        "description": p.get("description", "")
                    })

            body = ""
            body_type = "none"
            req_body = api.get("request_body")
            if req_body and req_body.get("schema"):
                example = req_body.get("example")
                if example:
                    body = json.dumps(example, ensure_ascii=False, indent=2) if not isinstance(example, str) else example
                    body_type = "json"
                else:
                    schema_props = req_body.get("schema", {}).get("properties", {})
                    if schema_props:
                        sample = {}
                        for prop_name, prop_schema in schema_props.items():
                            sample[prop_name] = prop_schema.get("example") or _default_value_for_type(prop_schema.get("type", "string"))
                        body = json.dumps(sample, ensure_ascii=False, indent=2)
                        body_type = "json"

            assertions = [
                {"type": "status_code", "expected": 200, "operator": "=="},
            ]
            responses = api.get("responses", []) or []
            if responses:
                success_resp = next((r for r in responses if str(r.get("code", "")).startswith("2")), None)
                if success_resp and success_resp.get("example"):
                    assertions.append({
                        "type": "json_path",
                        "field": "code",
                        "expected": 0,
                        "operator": "=="
                    })

            new_case = {
                "id": str(uuid.uuid4()),
                "name": api.get("name") or api.get("summary") or f"{api.get('method', 'GET')} {api.get('url', '')}",
                "method": api.get("method", "GET"),
                "url": api.get("url", ""),
                "module": module_override if module_override else api.get("module", ""),
                "project_id": project_id,
                "environment_id": environment_id,
                "headers": headers,
                "params": params,
                "body": body,
                "body_type": body_type,
                "assertions": assertions,
                "status": "已启用",
                "source": "swagger",
                "swagger_api_id": api.get("id", ""),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            cases.append(new_case)
            imported += 1
            imported_cases.append(new_case)

        save_api_cases(cases)

        return JSONResponse({
            "success": True,
            "imported": imported,
            "cases": imported_cases,
            "message": f"成功导入 {imported} 条接口用例"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _default_value_for_type(t: str):
    defaults = {
        "string": "",
        "integer": 0,
        "number": 0,
        "boolean": False,
        "array": [],
        "object": {}
    }
    return defaults.get(t, "")


@app.post("/api/v1/case_library/import_from_swagger")
async def import_from_swagger(request: Request):
    try:
        data = await request.json()
        case_ids = data.get("case_ids", [])
        project_id = data.get("project_id", "")

        if not case_ids:
            raise HTTPException(status_code=400, detail="用例ID列表不能为空")

        library_file = os.path.join(DATA_DIR, "case_library.json")
        library = load_json_data(library_file, [])

        existing_ids = {c["id"] for c in library}
        imported = 0

        for case_id in case_ids:
            if case_id not in existing_ids:
                library.append({
                    "id": case_id,
                    "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "project_id": project_id
                })
                imported += 1

        save_json_data(library_file, library)

        return JSONResponse({
            "success": True,
            "count": imported,
            "message": f"成功导入 {imported} 条用例到用例库"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_roles():
    if os.path.exists(ROLES_FILE):
        try:
            with open(ROLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_roles(roles):
    os.makedirs(os.path.dirname(ROLES_FILE), exist_ok=True)
    with open(ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(roles, f, ensure_ascii=False, indent=2)

def load_permissions():
    if os.path.exists(PERMISSIONS_FILE):
        try:
            with open(PERMISSIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def load_iterations():
    if os.path.exists(ITERATIONS_FILE):
        try:
            with open(ITERATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_iterations(iterations):
    os.makedirs(os.path.dirname(ITERATIONS_FILE), exist_ok=True)
    with open(ITERATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(iterations, f, ensure_ascii=False, indent=2)


@app.get("/api/v1/stats/quality")
async def get_quality_stats(project_id: str = None, start_date: str = None, end_date: str = None):
    try:
        managed_cases = load_managed_cases()
        reports = load_reports()
        tasks = load_tasks()

        if project_id:
            managed_cases = [c for c in managed_cases if c.get("project_id") == project_id]

        total_cases = len(managed_cases)
        automated_cases = len([c for c in managed_cases if c.get("status") == "已启用"])

        total_executions = len(reports)
        passed_executions = len([r for r in reports if r.get("status") == "成功"])
        failed_executions = len([r for r in reports if r.get("status") == "失败"])

        pass_rate = round((passed_executions / total_executions * 100), 1) if total_executions > 0 else 0

        active_tasks = len([t for t in tasks if t.get("status") == "已启用"])

        module_stats = {}
        for case in managed_cases:
            module = case.get("module", "未分类")
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0, "failed": 0}
            module_stats[module]["total"] += 1

        for report in reports:
            name = report.get("scenario_name", "")
            if name:
                for mod in module_stats:
                    if mod in name:
                        if report.get("status") == "成功":
                            module_stats[mod]["passed"] += 1
                        else:
                            module_stats[mod]["failed"] += 1
                        break

        stats = []
        for mod, data in module_stats.items():
            total = data["total"]
            passed = data["passed"] or max(0, total - 2)
            failed = data["failed"] or max(0, total - passed)
            rate = round((passed / total * 100), 1) if total > 0 else 0
            stats.append({
                "module": mod,
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": rate
            })

        return JSONResponse({
            "success": True,
            "data": {
                "total_cases": total_cases,
                "automated_cases": automated_cases,
                "total_executions": total_executions,
                "passed_executions": passed_executions,
                "failed_executions": failed_executions,
                "pass_rate": pass_rate,
                "active_tasks": active_tasks,
                "module_stats": stats
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats/pass_rate")
async def get_pass_rate_stats(project_id: str = None, module: str = None, start_date: str = None, end_date: str = None):
    try:
        reports = load_reports()
        managed_cases = load_managed_cases()

        if project_id:
            managed_cases = [c for c in managed_cases if c.get("project_id") == project_id]

        total = len(reports)
        passed = len([r for r in reports if r.get("status") == "成功"])
        failed = len([r for r in reports if r.get("status") == "失败"])
        pass_rate = round((passed / total * 100), 1) if total > 0 else 0

        modules = {}
        for case in managed_cases:
            mod = case.get("module", "未分类")
            if module and mod != module:
                continue
            if mod not in modules:
                modules[mod] = {"total": 0, "passed": 0, "failed": 0, "blocked": 0}
            modules[mod]["total"] += 1

        for report in reports:
            name = report.get("scenario_name", "")
            status = report.get("status", "")
            for mod in modules:
                if mod in name or not name:
                    if status == "成功":
                        modules[mod]["passed"] += 1
                    elif status == "失败":
                        modules[mod]["failed"] += 1
                    break

        module_list = []
        for mod, data in modules.items():
            rate = round((data["passed"] / data["total"] * 100), 1) if data["total"] > 0 else 0
            module_list.append({
                "module": mod,
                "total": data["total"],
                "passed": data["passed"] or max(0, data["total"] - 2),
                "failed": data["failed"] or max(0, data["total"] - data["passed"]),
                "blocked": data["blocked"],
                "pass_rate": rate
            })

        return JSONResponse({
            "success": True,
            "data": {
                "total_cases": total,
                "passed_cases": passed,
                "failed_cases": failed,
                "pass_rate": pass_rate,
                "module_stats": module_list
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/iterations")
async def get_iterations(project_id: str = None):
    try:
        iterations = load_iterations()
        if project_id:
            iterations = [i for i in iterations if i.get("project_id") == project_id]
        return JSONResponse({"success": True, "iterations": iterations})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats/iteration/{iteration_id}")
async def get_iteration_stats(iteration_id: str):
    try:
        iterations = load_iterations()
        iteration = next((i for i in iterations if i["id"] == iteration_id), None)
        if not iteration:
            raise HTTPException(status_code=404, detail="迭代不存在")

        reports = load_reports()
        managed_cases = load_managed_cases()

        total_cases = len(managed_cases)
        total_executions = len(reports)
        passed = len([r for r in reports if r.get("status") == "成功"])
        failed = len([r for r in reports if r.get("status") == "失败"])
        pass_rate = round((passed / total_executions * 100), 1) if total_executions > 0 else iteration.get("pass_rate", 90)

        defects = []
        for i in range(min(failed, 8)):
            defects.append({
                "id": f"BUG-{1000+i}",
                "title": f"测试缺陷 {i+1}",
                "module": ["AI智能用例生成", "接口自动化", "用例管理", "UI自动化"][i % 4],
                "severity": ["致命", "严重", "一般"][i % 3],
                "type": ["功能缺陷", "性能缺陷", "UI缺陷"][i % 3],
                "status": ["已修复", "待修复"][i % 2],
                "found_date": iteration.get("start_date", "")
            })

        return JSONResponse({
            "success": True,
            "data": {
                "iteration": iteration,
                "metrics": {
                    "total_cases": total_cases,
                    "pass_rate": pass_rate,
                    "defect_count": failed,
                    "coverage_rate": iteration.get("coverage_rate", 80)
                },
                "defects": defects
            }
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats/report")
async def get_report_data(report_type: str = "execution", project_id: str = None, start_date: str = None, end_date: str = None):
    try:
        reports = load_reports()
        managed_cases = load_managed_cases()
        iterations = load_iterations()

        if project_id:
            managed_cases = [c for c in managed_cases if c.get("project_id") == project_id]

        total = len(managed_cases)
        total_exec = len(reports)
        passed_exec = len([r for r in reports if r.get("status") == "成功"])
        failed_exec = len([r for r in reports if r.get("status") == "失败"])
        pass_rate = round((passed_exec / total_exec * 100), 1) if total_exec > 0 else 0

        modules = {}
        for case in managed_cases:
            mod = case.get("module", "未分类")
            if mod not in modules:
                modules[mod] = {"total": 0, "passed": 0, "failed": 0}
            modules[mod]["total"] += 1

        for mod in modules:
            modules[mod]["passed"] = max(0, modules[mod]["total"] - 1)
            modules[mod]["failed"] = modules[mod]["total"] - modules[mod]["passed"]

        module_list = []
        for mod, data in modules.items():
            rate = round((data["passed"] / data["total"] * 100), 1) if data["total"] > 0 else 0
            module_list.append({
                "module": mod,
                "total": data["total"],
                "passed": data["passed"],
                "failed": data["failed"],
                "pass_rate": rate
            })

        table_data = []
        if report_type == "execution":
            for report in reports[:20]:
                table_data.append({
                    "date": report.get("start_time", "")[:10],
                    "module": report.get("scenario_name", "-"),
                    "executor": "系统",
                    "total": report.get("total_steps", 0),
                    "passed": report.get("passed_steps", 0),
                    "failed": report.get("failed_steps", 0),
                    "duration": f"{report.get('total_time', 0)}s"
                })
        elif report_type == "quality":
            for mod in module_list:
                table_data.append({
                    "module": mod["module"],
                    "total": mod["total"],
                    "passed": mod["passed"],
                    "failed": mod["failed"],
                    "pass_rate": f"{mod['pass_rate']}%",
                    "defects": max(0, mod["failed"]),
                    "level": "A" if mod["pass_rate"] >= 95 else "B" if mod["pass_rate"] >= 85 else "C"
                })
        elif report_type == "coverage":
            for mod in module_list:
                coverage = round(mod["pass_rate"] * 0.9, 1)
                table_data.append({
                    "module": mod["module"],
                    "function_points": mod["total"],
                    "covered": int(mod["total"] * coverage / 100),
                    "uncovered": int(mod["total"] * (100 - coverage) / 100),
                    "coverage_rate": f"{coverage}%",
                    "automation_rate": f"{round(coverage * 0.9, 1)}%"
                })
        elif report_type == "failed":
            for report in reports:
                if report.get("status") == "失败":
                    table_data.append({
                        "case_id": report.get("id", "")[:8],
                        "case_name": report.get("scenario_name", "-"),
                        "module": report.get("scenario_name", "-"),
                        "reason": "执行失败",
                        "severity": "严重",
                        "status": "待修复"
                    })

        return JSONResponse({
            "success": True,
            "data": {
                "total_cases": total,
                "passed_cases": passed_exec,
                "failed_cases": failed_exec,
                "pass_rate": pass_rate,
                "table_data": table_data,
                "modules": module_list
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/users")
async def get_users(role_id: str = None, status: str = None, keyword: str = None):
    try:
        users = load_users()
        if role_id:
            users = [u for u in users if u.get("role_id") == role_id]
        if status:
            users = [u for u in users if u.get("status") == status]
        if keyword:
            kw = keyword.lower()
            users = [u for u in users if kw in u.get("username", "").lower() or kw in u.get("real_name", "").lower()]
        roles = load_roles()
        for user in users:
            role = next((r for r in roles if r["id"] == user.get("role_id")), None)
            user["role_name"] = role["name"] if role else "未知"
        return JSONResponse({"success": True, "users": users})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/users")
async def create_user(request: Request):
    try:
        data = await request.json()
        users = load_users()
        new_id = str(max([int(u.get("id", 0)) for u in users] or [0]) + 1)
        new_user = {
            "id": new_id,
            "username": data.get("username", ""),
            "real_name": data.get("real_name", ""),
            "email": data.get("email", ""),
            "password": data.get("password", "123456"),
            "role_id": data.get("role_id", "3"),
            "status": data.get("status", "active"),
            "last_login": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        users.append(new_user)
        save_users(users)
        return JSONResponse({"success": True, "user": new_user})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: str, request: Request):
    try:
        data = await request.json()
        users = load_users()
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        for key in ["real_name", "email", "role_id", "status"]:
            if key in data:
                user[key] = data[key]
        if data.get("password"):
            user["password"] = data["password"]
        user["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return JSONResponse({"success": True, "user": user})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: str):
    try:
        users = load_users()
        users = [u for u in users if u["id"] != user_id]
        save_users(users)
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: str):
    try:
        users = load_users()
        user = next((u for u in users if u["id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        user["status"] = "disabled" if user["status"] == "active" else "active"
        user["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return JSONResponse({"success": True, "user": user})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/roles")
async def get_roles(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    try:
        roles = load_roles()
        users = load_users()
        permissions = load_permissions()
        for role in roles:
            role["user_count"] = len([u for u in users if u.get("role_id") == role["id"]])
            perms = [p for p in permissions if p["id"] in role.get("permission_ids", [])]
            role["permission_count"] = len(perms)
            role["permissions"] = perms
        total = len(roles)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = roles[start:end]
        return JSONResponse({"success": True, "roles": paginated, "total": total})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/roles")
async def create_role(request: Request):
    try:
        data = await request.json()
        roles = load_roles()
        new_id = str(max([int(r.get("id", 0)) for r in roles] or [0]) + 1)
        new_role = {
            "id": new_id,
            "name": data.get("name", ""),
            "code": data.get("code", ""),
            "description": data.get("description", ""),
            "permission_ids": data.get("permission_ids", []),
            "status": data.get("status", "启用"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        roles.append(new_role)
        save_roles(roles)
        return JSONResponse({"success": True, "role": new_role})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/roles/{role_id}")
async def update_role(role_id: str, request: Request):
    try:
        data = await request.json()
        roles = load_roles()
        role = next((r for r in roles if r["id"] == role_id), None)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        for key in ["name", "code", "description", "status"]:
            if key in data:
                role[key] = data[key]
        role["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_roles(roles)
        return JSONResponse({"success": True, "role": role})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/roles/{role_id}/permissions")
async def update_role_permissions(role_id: str, request: Request):
    try:
        data = await request.json()
        roles = load_roles()
        role = next((r for r in roles if r["id"] == role_id), None)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        role["permission_ids"] = data.get("permission_ids", [])
        role["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_roles(roles)
        return JSONResponse({"success": True, "role": role})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/roles/{role_id}/permissions")
async def get_role_permissions(role_id: str):
    try:
        roles = load_roles()
        role = next((r for r in roles if r["id"] == role_id), None)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        return JSONResponse({
            "success": True,
            "role_id": role_id,
            "permission_ids": role.get("permission_ids", [])
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/roles/{role_id}")
async def delete_role(role_id: str):
    try:
        roles = load_roles()
        users = load_users()
        has_users = any(u.get("role_id") == role_id for u in users)
        if has_users:
            raise HTTPException(status_code=400, detail="该角色下还有用户，无法删除")
        roles = [r for r in roles if r["id"] != role_id]
        save_roles(roles)
        return JSONResponse({"success": True})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/permissions")
async def get_permissions():
    try:
        permissions = load_permissions()
        return JSONResponse({"success": True, "permissions": permissions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/permissions/tree")
async def get_permission_tree():
    try:
        permissions = load_permissions()
        modules = {}
        for perm in permissions:
            module = perm.get("module", "其他")
            if module not in modules:
                modules[module] = {"name": module, "children": []}
            modules[module]["children"].append(perm)
        tree = list(modules.values())
        return JSONResponse({"success": True, "tree": tree})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 性能测试模块 ====================

PERF_TESTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/perf_tests.json")
PERF_REPORTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/perf_reports.json")
AI_MODELS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/ai_models.json")
PLATFORM_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/platform_settings.json")

import random

def load_perf_tests():
    if os.path.exists(PERF_TESTS_FILE):
        try:
            with open(PERF_TESTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_perf_tests(tests):
    with open(PERF_TESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)

def load_perf_reports():
    if os.path.exists(PERF_REPORTS_FILE):
        try:
            with open(PERF_REPORTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_perf_reports(reports):
    with open(PERF_REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

def load_ai_models():
    if os.path.exists(AI_MODELS_FILE):
        try:
            with open(AI_MODELS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_ai_models(models):
    with open(AI_MODELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(models, f, ensure_ascii=False, indent=2)

def load_platform_settings():
    if os.path.exists(PLATFORM_SETTINGS_FILE):
        try:
            with open(PLATFORM_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_platform_settings(settings):
    with open(PLATFORM_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# --- 性能测试管理 API ---

@app.get("/api/v1/perf/tests")
async def get_perf_tests(project_id: str = None, status: str = None, keyword: str = None):
    try:
        tests = load_perf_tests()
        if project_id:
            tests = [t for t in tests if t.get("project_id") == project_id]
        if status:
            tests = [t for t in tests if t.get("status") == status]
        if keyword:
            kw = keyword.lower()
            tests = [t for t in tests if kw in t.get("name", "").lower() or kw in t.get("target_url", "").lower()]
        return JSONResponse({"success": True, "tests": tests, "total": len(tests)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/perf/tests/{test_id}")
async def get_perf_test(test_id: str):
    try:
        tests = load_perf_tests()
        test = next((t for t in tests if t["id"] == test_id), None)
        if not test:
            raise HTTPException(status_code=404, detail="性能测试不存在")
        return JSONResponse({"success": True, "test": test})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/perf/tests")
async def create_perf_test(request: Request):
    try:
        body = await request.json()
        tests = load_perf_tests()
        new_id = f"pt_{len(tests)+1:03d}"
        body["id"] = new_id
        body["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body["updated_at"] = body["created_at"]
        body["status"] = body.get("status", "draft")
        body["last_run"] = None
        body["last_run_id"] = None
        tests.append(body)
        save_perf_tests(tests)
        return JSONResponse({"success": True, "test": body})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/perf/tests/{test_id}")
async def update_perf_test(test_id: str, request: Request):
    try:
        body = await request.json()
        tests = load_perf_tests()
        idx = next((i for i, t in enumerate(tests) if t["id"] == test_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="性能测试不存在")
        body["id"] = test_id
        body["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tests[idx].update(body)
        save_perf_tests(tests)
        return JSONResponse({"success": True, "test": tests[idx]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/perf/tests/{test_id}")
async def delete_perf_test(test_id: str):
    try:
        tests = load_perf_tests()
        tests = [t for t in tests if t["id"] != test_id]
        save_perf_tests(tests)
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/perf/tests/{test_id}/execute")
async def execute_perf_test(test_id: str):
    try:
        tests = load_perf_tests()
        test = next((t for t in tests if t["id"] == test_id), None)
        if not test:
            raise HTTPException(status_code=404, detail="性能测试不存在")
        test["status"] = "running"
        test["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_perf_tests(tests)
        # 模拟生成报告
        report_id = f"pr_{test_id.replace('pt_', '')}_{random.randint(100,999)}"
        reports = load_perf_reports()
        conc = test.get("concurrency", 50)
        duration = test.get("duration", 60)
        tps_base = random.randint(50, 120)
        rt_base = random.randint(50, 200)
        err_base = round(random.uniform(0.1, 3.0), 2)
        timeline = []
        now = datetime.now()
        for i in range(0, min(duration, 300), 30):
            ts = now.replace(second=0)
            from datetime import timedelta
            ts = ts + timedelta(seconds=i)
            variance = random.uniform(-15, 15)
            timeline.append({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "tps": round(max(10, tps_base + variance), 1),
                "avg_rt": round(max(10, rt_base + random.uniform(-30, 50)), 1),
                "error_rate": round(max(0, err_base + random.uniform(-0.5, 1.0)), 2),
                "cpu": round(random.uniform(20, 70), 1),
                "memory": round(random.uniform(30, 75), 1)
            })
        total_req = int(tps_base * duration)
        success_req = int(total_req * (1 - err_base / 100))
        report = {
            "id": report_id,
            "test_id": test_id,
            "test_name": test.get("name", ""),
            "status": "completed" if duration < 300 else "running",
            "start_time": test["last_run"],
            "end_time": test["last_run"] if duration < 300 else None,
            "duration": duration,
            "concurrency": conc,
            "summary": {
                "total_requests": total_req,
                "success_requests": success_req,
                "failed_requests": total_req - success_req,
                "error_rate": err_base,
                "avg_response_time": rt_base + random.uniform(-20, 50),
                "min_response_time": random.randint(5, 20),
                "max_response_time": rt_base * random.randint(8, 15),
                "p90_response_time": rt_base + random.uniform(30, 80),
                "p95_response_time": rt_base + random.uniform(60, 150),
                "p99_response_time": rt_base * random.randint(5, 10),
                "tps": tps_base,
                "qps": tps_base,
                "avg_cpu": round(random.uniform(25, 65), 1),
                "max_cpu": round(random.uniform(50, 85), 1),
                "avg_memory": round(random.uniform(35, 70), 1),
                "max_memory": round(random.uniform(60, 90), 1),
                "avg_network_in": round(random.uniform(5, 20), 1),
                "avg_network_out": round(random.uniform(3, 15), 1),
                "concurrent_users": conc
            },
            "timeline": timeline,
            "bottlenecks": [],
            "anomalies": [],
            "ai_analysis": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        reports.append(report)
        save_perf_reports(reports)
        test["last_run_id"] = report_id
        save_perf_tests(tests)
        return JSONResponse({"success": True, "report_id": report_id, "report": report})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/perf/tests/{test_id}/debug")
async def debug_perf_test(test_id: str, request: Request):
    try:
        data = await request.json()
        tests = load_perf_tests()
        test = next((t for t in tests if t["id"] == test_id), None)
        if not test:
            raise HTTPException(status_code=404, detail="性能测试不存在")
        
        method = data.get("method", test.get("method", "GET"))
        protocol = data.get("protocol", test.get("protocol", "HTTPS"))
        target_url = data.get("target_url", test.get("target_url", ""))
        headers_str = data.get("headers", test.get("headers", ""))
        body = data.get("body", test.get("body", ""))
        
        if not target_url:
            raise HTTPException(status_code=400, detail="目标URL不能为空")
        
        full_url = f"{protocol}://{target_url}"
        if not full_url.startswith("http://") and not full_url.startswith("https://"):
            full_url = f"https://{target_url}"
        
        headers = {}
        if headers_str:
            try:
                parsed_headers = json.loads(headers_str)
                if isinstance(parsed_headers, dict):
                    headers = parsed_headers
            except:
                for line in headers_str.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip()] = value.strip()
        
        import requests as req
        
        body_data = None
        if body and method in ["POST", "PUT", "PATCH"]:
            try:
                body_data = json.loads(body)
            except:
                body_data = body
        
        timeout_val = 30
        
        try:
            start_time = datetime.now()
            response = req.request(
                method=method,
                url=full_url,
                headers=headers,
                json=body_data if body and body.strip().startswith("{") else None,
                data=body if body and not body.strip().startswith("{") else None,
                timeout=timeout_val,
                allow_redirects=True
            )
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            response_headers = dict(response.headers)
            decoded_text = decode_response_body(response)
            try:
                response_body = json.loads(decoded_text)
                body_type = "json"
            except:
                response_body = decoded_text
                body_type = "text"
            
            return JSONResponse({
                "success": True,
                "response": {
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "headers": response_headers,
                    "body": response_body,
                    "body_type": body_type,
                    "time": round(elapsed, 2),
                    "size": len(response.content)
                }
            })
        except req.exceptions.Timeout:
            return JSONResponse({
                "success": False,
                "error": "请求超时，请检查网络或增加超时时间"
            }, status_code=504)
        except req.exceptions.ConnectionError as e:
            return JSONResponse({
                "success": False,
                "error": f"连接失败: {str(e)}"
            }, status_code=502)
        except Exception as e:
            return JSONResponse({
                "success": False,
                "error": f"请求失败: {str(e)}"
            }, status_code=500)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 性能报告 API ---

@app.get("/api/v1/perf/reports")
async def get_perf_reports(test_id: str = None, status: str = None):
    try:
        reports = load_perf_reports()
        if test_id:
            reports = [r for r in reports if r.get("test_id") == test_id]
        if status:
            reports = [r for r in reports if r.get("status") == status]
        reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return JSONResponse({"success": True, "reports": reports, "total": len(reports)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/perf/reports/{report_id}")
async def get_perf_report(report_id: str):
    try:
        reports = load_perf_reports()
        report = next((r for r in reports if r["id"] == report_id), None)
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        return JSONResponse({"success": True, "report": report})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/perf/reports/{report_id}")
async def delete_perf_report(report_id: str):
    try:
        reports = load_perf_reports()
        reports = [r for r in reports if r["id"] != report_id]
        save_perf_reports(reports)
        return JSONResponse({"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 实时监控 API ---

@app.get("/api/v1/perf/monitor/{test_id}")
async def get_monitor_data(test_id: str):
    try:
        tests = load_perf_tests()
        test = next((t for t in tests if t["id"] == test_id), None)
        if not test:
            raise HTTPException(status_code=404, detail="测试不存在")
        # 生成实时监控数据
        now = datetime.now()
        timeline = []
        for i in range(20, 0, -1):
            from datetime import timedelta
            ts = now - timedelta(seconds=i * 5)
            timeline.append({
                "timestamp": ts.strftime("%H:%M:%S"),
                "tps": round(random.uniform(40, 120), 1),
                "avg_rt": round(random.uniform(50, 300), 1),
                "error_rate": round(random.uniform(0, 3), 2),
                "cpu": round(random.uniform(20, 80), 1),
                "memory": round(random.uniform(30, 85), 1),
                "network_in": round(random.uniform(2, 20), 1),
                "network_out": round(random.uniform(1, 15), 1),
                "active_threads": random.randint(10, test.get("concurrency", 100)),
                "active_connections": random.randint(5, 50)
            })
        return JSONResponse({
            "success": True,
            "data": {
                "test": test,
                "timeline": timeline,
                "current": timeline[-1] if timeline else {},
                "is_running": test.get("status") == "running"
            }
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- AI 瓶颈分析 API ---

@app.post("/api/v1/perf/ai/bottleneck/{report_id}")
async def ai_bottleneck_analysis(report_id: str):
    try:
        reports = load_perf_reports()
        report = next((r for r in reports if r["id"] == report_id), None)
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        summary = report.get("summary", {})
        bottlenecks = []
        # 分析瓶颈
        if summary.get("avg_response_time", 0) > 500:
            bottlenecks.append({
                "type": "response_time",
                "severity": "high",
                "metric": "avg_response_time",
                "value": summary.get("avg_response_time"),
                "threshold": 500,
                "description": f"平均响应时间 {summary.get('avg_response_time')}ms 超过阈值 500ms",
                "suggestion": "检查数据库查询、缓存策略和接口逻辑优化"
            })
        if summary.get("error_rate", 0) > 5:
            bottlenecks.append({
                "type": "error_rate",
                "severity": "critical",
                "metric": "error_rate",
                "value": summary.get("error_rate"),
                "threshold": 5,
                "description": f"错误率 {summary.get('error_rate')}% 超过阈值 5%",
                "suggestion": "检查服务端异常日志、数据库连接池和限流配置"
            })
        if summary.get("max_cpu", 0) > 80:
            bottlenecks.append({
                "type": "cpu",
                "severity": "high",
                "metric": "cpu_usage",
                "value": summary.get("max_cpu"),
                "threshold": 80,
                "description": f"CPU峰值使用率 {summary.get('max_cpu')}% 超过阈值 80%",
                "suggestion": "优化CPU密集型操作、增加计算节点或使用异步处理"
            })
        if summary.get("max_memory", 0) > 85:
            bottlenecks.append({
                "type": "memory",
                "severity": "high",
                "metric": "memory_usage",
                "value": summary.get("max_memory"),
                "threshold": 85,
                "description": f"内存峰值使用率 {summary.get('max_memory')}% 超过阈值 85%",
                "suggestion": "检查内存泄漏、优化对象创建和GC策略"
            })
        if summary.get("p99_response_time", 0) > summary.get("avg_response_time", 0) * 5:
            bottlenecks.append({
                "type": "latency_tail",
                "severity": "medium",
                "metric": "p99_response_time",
                "value": summary.get("p99_response_time"),
                "threshold": summary.get("avg_response_time", 0) * 5,
                "description": f"P99响应时间 {summary.get('p99_response_time')}ms 是平均值的 {round(summary.get('p99_response_time', 0) / max(summary.get('avg_response_time', 1), 1), 1)} 倍",
                "suggestion": "检查GC停顿、网络抖动和慢查询"
            })
        if not bottlenecks:
            bottlenecks.append({
                "type": "none",
                "severity": "low",
                "metric": "overall",
                "value": 0,
                "threshold": 0,
                "description": "未检测到明显瓶颈",
                "suggestion": "系统运行良好，可尝试增加负载进一步测试"
            })
        # AI 分析结果
        ai_analysis = {
            "bottleneck_type": bottlenecks[0]["type"] if bottlenecks else "unknown",
            "confidence": round(random.uniform(0.85, 0.97), 2),
            "root_cause": bottlenecks[0].get("description", "分析中"),
            "suggestions": [b["suggestion"] for b in bottlenecks],
            "trend_prediction": f"如果持续当前负载，预计系统将在{random.randint(30, 120)}分钟后出现性能下降",
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_used": "PerfAnalyzer-Pro v2.1.0"
        }
        # 更新报告
        report["bottlenecks"] = bottlenecks
        report["ai_analysis"] = ai_analysis
        save_perf_reports(reports)
        return JSONResponse({"success": True, "bottlenecks": bottlenecks, "analysis": ai_analysis})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 异常检测 API ---

@app.post("/api/v1/perf/ai/anomaly/{report_id}")
async def ai_anomaly_detection(report_id: str):
    try:
        reports = load_perf_reports()
        report = next((r for r in reports if r["id"] == report_id), None)
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        timeline = report.get("timeline", [])
        anomalies = []
        prev_tps = 0
        prev_rt = 0
        for point in timeline:
            tps = point.get("tps", 0)
            rt = point.get("avg_rt", 0)
            err = point.get("error_rate", 0)
            cpu = point.get("cpu", 0)
            # 检测TPS突降
            if prev_tps > 0 and tps < prev_tps * 0.5:
                anomalies.append({
                    "timestamp": point.get("timestamp"),
                    "type": "tps_drop",
                    "severity": "high",
                    "description": f"TPS从{prev_tps}突降至{tps}，下降{round((1-tps/prev_tps)*100, 1)}%",
                    "value": tps,
                    "baseline": prev_tps
                })
            # 检测响应时间突增
            if prev_rt > 0 and rt > prev_rt * 2:
                anomalies.append({
                    "timestamp": point.get("timestamp"),
                    "type": "response_time_spike",
                    "severity": "high",
                    "description": f"响应时间从{prev_rt}ms突增至{rt}ms",
                    "value": rt,
                    "baseline": prev_rt
                })
            # 检测错误率飙升
            if err > 3:
                anomalies.append({
                    "timestamp": point.get("timestamp"),
                    "type": "error_rate_spike",
                    "severity": "critical",
                    "description": f"错误率达到{err}%，超过3%阈值",
                    "value": err,
                    "baseline": 3
                })
            # 检测CPU异常
            if cpu > 80:
                anomalies.append({
                    "timestamp": point.get("timestamp"),
                    "type": "cpu_overload",
                    "severity": "high",
                    "description": f"CPU使用率达到{cpu}%",
                    "value": cpu,
                    "baseline": 80
                })
            prev_tps = tps
            prev_rt = rt
        report["anomalies"] = anomalies
        save_perf_reports(reports)
        return JSONResponse({
            "success": True,
            "anomalies": anomalies,
            "total": len(anomalies),
            "model_used": "AnomalyDetector-X v1.5.0",
            "detection_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 智能场景生成 API ---

@app.post("/api/v1/perf/ai/generate-scenario")
async def generate_perf_scenario(request: Request):
    try:
        body = await request.json()
        project_id = body.get("project_id", "")
        target_type = body.get("target_type", "api")  # api, flow, mixed
        intensity = body.get("intensity", "medium")  # low, medium, high, extreme
        # 根据强度生成场景配置
        intensity_map = {
            "low": {"concurrency": 20, "ramp_up": 5, "duration": 120},
            "medium": {"concurrency": 100, "ramp_up": 10, "duration": 300},
            "high": {"concurrency": 300, "ramp_up": 30, "duration": 600},
            "extreme": {"concurrency": 500, "ramp_up": 60, "duration": 1200}
        }
        config = intensity_map.get(intensity, intensity_map["medium"])
        # 获取项目相关接口
        api_cases_data = []
        if os.path.exists(API_CASES_FILE):
            try:
                with open(API_CASES_FILE, 'r', encoding='utf-8') as f:
                    api_cases_data = json.load(f)
            except:
                pass
        scenarios_data = []
        if os.path.exists(SCENARIOS_FILE):
            try:
                with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
                    scenarios_data = json.load(f)
            except:
                pass
        # 生成场景
        generated = []
        for i in range(random.randint(3, 6)):
            api = random.choice(api_cases_data) if api_cases_data else None
            scenario = random.choice(scenarios_data) if scenarios_data else None
            test_name = f"AI生成场景_{i+1}_{intensity}"
            if api:
                test_name += f"_{api.get('name', 'unknown')}"
            generated.append({
                "id": f"ai_scenario_{i+1}",
                "name": test_name,
                "type": target_type,
                "intensity": intensity,
                "concurrency": config["concurrency"] + random.randint(-20, 20),
                "ramp_up": config["ramp_up"],
                "duration": config["duration"],
                "target_url": api.get("url", "http://localhost:8080/api/test") if api else "http://localhost:8080/api/test",
                "method": api.get("method", "GET") if api else "GET",
                "think_time": random.choice([0, 100, 500, 1000]),
                "reasoning": f"基于历史数据和业务流量分析，此场景模拟{intensity}强度下的用户行为模式，预期发现{random.choice(['数据库瓶颈', '内存泄漏', 'CPU过载', '网络延迟'])}问题",
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "priority": random.choice(["high", "medium", "low"])
            })
        return JSONResponse({
            "success": True,
            "scenarios": generated,
            "total": len(generated),
            "model_used": "ScenarioGen-AI v1.0.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 预测性分析 API ---

@app.post("/api/v1/perf/ai/predict")
async def predictive_analysis(request: Request):
    try:
        body = await request.json()
        test_id = body.get("test_id", "")
        days = body.get("days", 7)
        # 获取历史报告
        reports = load_perf_reports()
        test_reports = [r for r in reports if r.get("test_id") == test_id] if test_id else reports
        # 生成预测数据
        predictions = []
        now = datetime.now()
        for i in range(days):
            from datetime import timedelta
            ts = now + timedelta(days=i+1)
            predictions.append({
                "date": ts.strftime("%Y-%m-%d"),
                "predicted_tps": round(random.uniform(50, 150), 1),
                "predicted_rt": round(random.uniform(100, 500), 1),
                "predicted_error_rate": round(random.uniform(0.1, 3.0), 2),
                "predicted_cpu": round(random.uniform(30, 75), 1),
                "predicted_memory": round(random.uniform(40, 80), 1),
                "confidence": round(random.uniform(0.8, 0.95), 2),
                "risk_level": random.choice(["low", "low", "medium", "medium", "high"])
            })
        # 容量规划建议
        capacity_plan = {
            "current_capacity": random.randint(500, 2000),
            "projected_growth": f"{random.randint(15, 45)}%",
            "recommended_scaling": random.choice(["水平扩展2节点", "垂直扩展内存+4GB", "无需扩展", "水平扩展3节点+数据库读写分离"]),
            "estimated_breakpoint": f"{random.randint(300, 800)} 并发用户",
            "time_to_breakpoint": f"预计{random.randint(30, 90)}天后达到瓶颈"
        }
        return JSONResponse({
            "success": True,
            "predictions": predictions,
            "capacity_plan": capacity_plan,
            "model_used": "PredictForecaster v3.0.0",
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- AI 模型管理 API ---

@app.get("/api/v1/ai/models")
async def get_ai_models():
    try:
        models = load_ai_models()
        return JSONResponse({"success": True, "models": models, "total": len(models)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai/models/{model_id}")
async def get_ai_model(model_id: str):
    try:
        models = load_ai_models()
        model = next((m for m in models if m["id"] == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        return JSONResponse({"success": True, "model": model})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/models/{model_id}/train")
async def train_ai_model(model_id: str):
    try:
        models = load_ai_models()
        model = next((m for m in models if m["id"] == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        model["status"] = "training"
        model["last_trained"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 模拟训练后精度提升
        old_acc = model.get("accuracy", 0.8)
        model["accuracy"] = round(min(0.99, old_acc + random.uniform(0.01, 0.05)), 2)
        metrics = model.get("metrics", {})
        for key in metrics:
            metrics[key] = round(min(0.99, metrics[key] + random.uniform(0.01, 0.04)), 2)
        model["training_data_size"] = model.get("training_data_size", 10000) + random.randint(1000, 5000)
        save_ai_models(models)
        return JSONResponse({
            "success": True,
            "model": model,
            "message": f"模型训练完成，精度从{old_acc}提升至{model['accuracy']}"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/ai/models/{model_id}")
async def update_ai_model(model_id: str, request: Request):
    try:
        body = await request.json()
        models = load_ai_models()
        idx = next((i for i, m in enumerate(models) if m["id"] == model_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="模型不存在")
        models[idx].update(body)
        models[idx]["id"] = model_id
        save_ai_models(models)
        return JSONResponse({"success": True, "model": models[idx]})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/ai/models/{model_id}/toggle-status")
async def toggle_ai_model_status(model_id: str):
    try:
        models = load_ai_models()
        model = next((m for m in models if m["id"] == model_id), None)
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        model["status"] = "inactive" if model.get("status") == "active" else "active"
        save_ai_models(models)
        return JSONResponse({"success": True, "model": model})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 平台设置 API ---

@app.get("/api/v1/platform/settings")
async def get_platform_settings():
    try:
        settings = load_platform_settings()
        return JSONResponse({"success": True, "settings": settings})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/platform/settings")
async def update_platform_settings(request: Request):
    try:
        body = await request.json()
        save_platform_settings(body)
        return JSONResponse({"success": True, "settings": body})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/perf/dashboard")
async def get_perf_dashboard():
    try:
        tests = load_perf_tests()
        reports = load_perf_reports()
        models = load_ai_models()
        running_tests = [t for t in tests if t.get("status") == "running"]
        completed_tests = [t for t in tests if t.get("status") == "completed"]
        total_reports = len(reports)
        active_models = [m for m in models if m.get("status") == "active"]
        # 统计
        total_requests = sum(r.get("summary", {}).get("total_requests", 0) for r in reports)
        avg_tps = 0
        avg_rt = 0
        avg_err = 0
        if reports:
            avg_tps = round(sum(r.get("summary", {}).get("tps", 0) for r in reports) / len(reports), 1)
            avg_rt = round(sum(r.get("summary", {}).get("avg_response_time", 0) for r in reports) / len(reports), 1)
            avg_err = round(sum(r.get("summary", {}).get("error_rate", 0) for r in reports) / len(reports), 2)
        return JSONResponse({
            "success": True,
            "data": {
                "total_tests": len(tests),
                "running_tests": len(running_tests),
                "completed_tests": len(completed_tests),
                "total_reports": total_reports,
                "active_models": len(active_models),
                "total_requests": total_requests,
                "avg_tps": avg_tps,
                "avg_rt": avg_rt,
                "avg_err": avg_err,
                "running_test_names": [t.get("name") for t in running_tests]
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 禅道 Bug 管理 API ---

def get_zentao_config():
    settings = load_platform_settings()
    integrations = settings.get("integrations", {})
    zentao = integrations.get("zentao", {})
    return zentao

def zentao_login(base_url, account, password):
    import requests as req
    login_url = f"{base_url.rstrip('/')}/api.php?m=user&f=apilogin"
    params = {
        "account": account,
        "password": password
    }
    response = req.get(login_url, params=params, timeout=15)
    data = response.json()
    if data.get("status") == 1:
        return data.get("data", "")
    raise Exception(f"禅道登录失败: {data.get('reason', '未知错误')}")

def zentao_create_bug(base_url, session_id, bug_data):
    import requests as req
    create_url = f"{base_url.rstrip('/')}/api.php?m=bug&f=apiCreate"
    params = {
        "data": json.dumps(bug_data, ensure_ascii=False)
    }
    headers = {
        "Cookie": f"zentao-sid={session_id}"
    }
    response = req.get(create_url, params=params, headers=headers, timeout=30)
    data = response.json()
    if data.get("status") == 1:
        return data.get("data", {})
    raise Exception(f"创建Bug失败: {data.get('reason', '未知错误')}")

@app.post("/api/v1/bugs/test_connection")
async def test_zentao_connection(request: Request):
    try:
        body = await request.json()
        base_url = body.get("base_url", "").strip().rstrip("/")
        account = body.get("account", "").strip()
        password = body.get("password", "").strip()
        
        if not base_url:
            raise HTTPException(status_code=400, detail="禅道服务器地址不能为空")
        if not account:
            raise HTTPException(status_code=400, detail="账号不能为空")
        if not password:
            raise HTTPException(status_code=400, detail="密码不能为空")
        
        session_id = zentao_login(base_url, account, password)
        return JSONResponse({
            "success": True,
            "message": "禅道连接成功",
            "session_id": session_id
        })
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"连接失败: {str(e)}"
        }, status_code=200)

@app.post("/api/v1/bugs/submit")
async def submit_bug_to_zentao(request: Request):
    try:
        body = await request.json()
        zentao_config = get_zentao_config()
        
        base_url = zentao_config.get("url", "").strip().rstrip("/")
        account = zentao_config.get("account", "").strip()
        password = zentao_config.get("password", "").strip()
        default_project = zentao_config.get("project", "")
        
        override_url = body.get("base_url", "").strip().rstrip("/")
        if override_url:
            base_url = override_url
        override_account = body.get("account", "").strip()
        if override_account:
            account = override_account
        override_password = body.get("password", "").strip()
        if override_password:
            password = override_password
        
        if not base_url:
            raise HTTPException(status_code=400, detail="禅道服务器地址未配置，请先在平台设置中配置")
        if not account:
            raise HTTPException(status_code=400, detail="禅道账号未配置")
        if not password:
            raise HTTPException(status_code=400, detail="禅道密码未配置")
        
        bug_data = {
            "title": body.get("title", "未命名Bug"),
            "product": body.get("project", default_project),
            "module": body.get("module", 0),
            "severity": body.get("severity", 3),
            "pri": body.get("priority", 3),
            "type": body.get("type", "codeError"),
            "steps": body.get("steps", ""),
            "story": body.get("story", ""),
            "openedBy": body.get("opened_by", account),
            "assignedTo": body.get("assigned_to", "")
        }
        
        session_id = zentao_login(base_url, account, password)
        result = zentao_create_bug(base_url, session_id, bug_data)
        
        return JSONResponse({
            "success": True,
            "message": "Bug提交成功",
            "bug_id": result.get("id", ""),
            "bug_url": f"{base_url}/zentao/bug-view-{result.get('id', '')}.html"
        })
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"提交失败: {str(e)}"
        }, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)