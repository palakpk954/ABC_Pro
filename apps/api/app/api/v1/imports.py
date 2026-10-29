from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_org_id
from app.models import User
from app.schemas.import_csv import CSVImportResult
from app.services.import_service import (
    import_skills_csv,
    import_employees_csv,
    import_projects_csv,
)
from app.services.audit import log_audit_event

router = APIRouter(prefix="/imports", tags=["Imports"])


@router.post("/csv", response_model=CSVImportResult)
async def import_csv_data(
    file: UploadFile = File(...),
    entity_type: str = Query(..., description="Entity type: skills, employees, projects"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Imports CSV records with strict row-level validation and detailed error reporting."""
    content_bytes = await file.read()
    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content_bytes.decode("latin-1")

    entity_lower = entity_type.lower().strip()
    if entity_lower == "skills":
        result = import_skills_csv(db=db, org_id=current_user.org_id, content=content_str)
    elif entity_lower == "employees":
        result = import_employees_csv(db=db, org_id=current_user.org_id, content=content_str)
    elif entity_lower == "projects":
        result = import_projects_csv(db=db, org_id=current_user.org_id, content=content_str)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported entity_type '{entity_type}'. Must be one of: skills, employees, projects",
        )

    log_audit_event(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="import_csv",
        entity_type=entity_lower,
        entity_id=file.filename or entity_lower,
        after_state={
            "total_rows": result.total_rows,
            "imported_rows": result.imported_rows,
            "failed_rows": result.failed_rows,
        },
    )
    db.commit()

    return result
