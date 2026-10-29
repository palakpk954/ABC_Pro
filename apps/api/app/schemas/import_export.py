from typing import List, Optional

from pydantic import BaseModel


class CSVRowError(BaseModel):
    row_number: int
    field: Optional[str] = None
    value: Optional[str] = None
    error_message: str


class CSVImportSummary(BaseModel):
    entity_type: str  # employees, skills, projects, roles
    total_rows: int
    successful_rows: int
    failed_rows: int
    errors: List[CSVRowError] = []
    imported_ids: List[str] = []
