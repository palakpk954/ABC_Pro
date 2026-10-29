from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit,
    auth,
    dossier,
    employees,
    import_data,
    plans,
    projects,
    scenarios,
    skills,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dossier.router, prefix="/dossier", tags=["Living Talent Dossier"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(plans.router, prefix="/plans", tags=["Plans & Optimization"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios & What-If"])
api_router.include_router(import_data.router, prefix="/import", tags=["CSV Import"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Log"])
