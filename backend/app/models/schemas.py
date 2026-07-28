from pydantic import BaseModel
from typing import List, Dict, Optional

class TestCase(BaseModel):
    id: str
    name: str
    type: str
    priority: str
    preconditions: str
    steps: List[str]
    expected_result: str
    status: str
    created_at: str

class CoverageReport(BaseModel):
    total_cases: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]
    coverage_rate: int
    uncovered_items: List[str]

class ExportFormat(BaseModel):
    format: str
    test_cases: List[TestCase]
    coverage: CoverageReport