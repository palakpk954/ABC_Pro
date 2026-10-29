from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.skills import router as skills_router
from app.api.v1.employees import router as employees_router
from app.api.v1.projects import router as projects_router
from app.api.v1.plans import router as plans_router
from app.api.v1.imports import router as imports_router
from app.api.v1.audit import router as audit_router
from app.api.v1.jobs import router as jobs_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(skills_router)
api_router.include_router(employees_router)
api_router.include_router(projects_router)
api_router.include_router(plans_router)
api_router.include_router(imports_router)
api_router.include_router(audit_router)
api_router.include_router(jobs_router)
