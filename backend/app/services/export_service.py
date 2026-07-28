import os
import json
import csv
from datetime import datetime
from typing import List, Dict
from openpyxl import Workbook

class ExportService:
    def __init__(self):
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)

    def export(self, test_cases: List[Dict], coverage: Dict, format_type: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "markdown":
            return self._export_markdown(test_cases, coverage, timestamp)
        elif format_type == "json":
            return self._export_json(test_cases, coverage, timestamp)
        elif format_type == "csv":
            return self._export_csv(test_cases, timestamp)
        elif format_type == "excel":
            return self._export_excel(test_cases, coverage, timestamp)
        else:
            return self._export_markdown(test_cases, coverage, timestamp)

    def _export_markdown(self, test_cases: List[Dict], coverage: Dict, timestamp: str) -> str:
        filename = f"test_cases_{timestamp}.md"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# 测试用例文档\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 覆盖率统计\n\n")
            f.write(f"- 测试用例总数: {coverage.get('total_cases', 0)}\n")
            f.write(f"- 覆盖率: {coverage.get('coverage_rate', 0)}%\n\n")
            
            f.write("### 按类型分布\n\n")
            for case_type, count in coverage.get("by_type", {}).items():
                f.write(f"- {case_type}: {count}条\n")
            
            f.write("\n### 按优先级分布\n\n")
            for priority, count in coverage.get("by_priority", {}).items():
                f.write(f"- {priority}: {count}条\n")
            
            f.write("\n## 测试用例列表\n\n")
            
            for i, case in enumerate(test_cases, 1):
                f.write(f"### {i}. {case.get('name', '')}\n\n")
                f.write(f"- **类型**: {case.get('type', '')}\n")
                f.write(f"- **优先级**: {case.get('priority', '')}\n")
                f.write(f"- **前置条件**: {case.get('preconditions', '')}\n")
                f.write(f"- **执行步骤**: \n")
                for j, step in enumerate(case.get('steps', []), 1):
                    f.write(f"  {j}. {step}\n")
                f.write(f"- **预期结果**: {case.get('expected_result', '')}\n")
                f.write(f"- **状态**: {case.get('status', '')}\n\n")
        
        return filepath

    def _export_json(self, test_cases: List[Dict], coverage: Dict, timestamp: str) -> str:
        filename = f"test_cases_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "coverage": coverage,
            "test_cases": test_cases
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath

    def _export_csv(self, test_cases: List[Dict], timestamp: str) -> str:
        filename = f"test_cases_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "用例名称", "类型", "优先级", "前置条件", "执行步骤", "预期结果", "状态"])
            
            for i, case in enumerate(test_cases, 1):
                steps = "\n".join(case.get('steps', []))
                writer.writerow([
                    i,
                    case.get('name', ''),
                    case.get('type', ''),
                    case.get('priority', ''),
                    case.get('preconditions', ''),
                    steps,
                    case.get('expected_result', ''),
                    case.get('status', '')
                ])
        
        return filepath

    def _export_excel(self, test_cases: List[Dict], coverage: Dict, timestamp: str) -> str:
        filename = f"test_cases_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        wb = Workbook()
        
        ws_cases = wb.active
        ws_cases.title = "测试用例"
        ws_cases.append(["序号", "用例名称", "类型", "优先级", "前置条件", "执行步骤", "预期结果", "状态"])
        
        for i, case in enumerate(test_cases, 1):
            steps = "\n".join(case.get('steps', []))
            ws_cases.append([
                i,
                case.get('name', ''),
                case.get('type', ''),
                case.get('priority', ''),
                case.get('preconditions', ''),
                steps,
                case.get('expected_result', ''),
                case.get('status', '')
            ])
        
        ws_coverage = wb.create_sheet("覆盖率统计")
        ws_coverage.append(["指标", "数值"])
        ws_coverage.append(["测试用例总数", coverage.get('total_cases', 0)])
        ws_coverage.append(["覆盖率", f"{coverage.get('coverage_rate', 0)}%"])
        ws_coverage.append(["功能用例数", coverage.get('by_type', {}).get('功能', 0)])
        ws_coverage.append(["异常用例数", coverage.get('by_type', {}).get('异常', 0)])
        ws_coverage.append(["边界用例数", coverage.get('by_type', {}).get('边界', 0)])
        ws_coverage.append(["安全用例数", coverage.get('by_type', {}).get('安全', 0)])
        ws_coverage.append(["高优先级", coverage.get('by_priority', {}).get('高', 0)])
        ws_coverage.append(["中优先级", coverage.get('by_priority', {}).get('中', 0)])
        ws_coverage.append(["低优先级", coverage.get('by_priority', {}).get('低', 0)])
        
        wb.save(filepath)
        
        return filepath