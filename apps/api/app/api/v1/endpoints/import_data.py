from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.import_export import CSVImportSummary
from app.services.import_service import import_csv_data

router = APIRouter()


@router.post("/csv/{entity_type}", response_model=CSVImportSummary)
async def import_csv(
    entity_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import and validate CSV data for employees, skills, projects, or roles."""
    valid_types = ["employees", "skills", "projects", "roles"]
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity type: {entity_type}. Must be one of {valid_types}",
        )

    content = await file.read()
    csv_text = content.decode("utf-8", errors="replace")

    summary = import_csv_data(
        entity_type=entity_type,
        csv_content=csv_text,
        org_id=current_user.org_id,
        db=db,
        user_id=current_user.id,
    )
    return summary
