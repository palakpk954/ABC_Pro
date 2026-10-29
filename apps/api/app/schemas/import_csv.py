from typing import List, Optional, Any
from pydantic import BaseModel


class RowValidationError(BaseModel):
    row_number: int
    field: str
    value: Optional[Any] = None
    error_message: str


class CSVImportResult(BaseModel):
    entity_type: str  # employees, skills, projects, roles
    total_rows: int
    imported_rows: int
    failed_rows: int
    errors: List[RowValidationError] = []
    message: str
