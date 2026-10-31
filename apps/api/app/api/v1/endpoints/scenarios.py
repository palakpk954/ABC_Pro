from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.plan import Plan, Scenario
from app.models.user import User
from app.schemas.scenario import (
    NaturalScenarioSimulateRequest,
    NaturalScenarioSimulateResponse,
    ScenarioCreateRequest,
    ScenarioResponse,
)
from app.services.cognitive_advisor import CognitiveAdvisorService
from app.services.scenario_service import create_and_run_scenario

router = APIRouter()


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
def create_scenario(
    req: ScenarioCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run a what-if scenario against a base plan and compute mathematical diffs."""
    try:
        scenario = create_and_run_scenario(
            org_id=current_user.org_id,
            db=db,
            req=req,
            user_id=current_user.id,
        )
        return scenario
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/simulate-prompt", response_model=NaturalScenarioSimulateResponse)
def simulate_natural_scenario(
    req: NaturalScenarioSimulateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulates a What-If operational scenario from a natural language prompt.
    Synthesizes executive recommendation from Alex, computes metric diffs,
    and identifies impacted engineers and mitigations.
    """
    base_plan = (
        db.query(Plan)
        .filter(Plan.id == req.base_plan_id, Plan.org_id == current_user.org_id)
        .first()
    )
    if not base_plan:
        raise HTTPException(status_code=404, detail="Base plan not found")

    return CognitiveAdvisorService.simulate_natural_scenario(
        base_plan=base_plan,
        prompt=req.prompt,
        db=db,
    )


@router.get("", response_model=List[ScenarioResponse])
def list_scenarios(
    base_plan_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List scenarios created for a plan or organization."""
    query = db.query(Scenario).filter(Scenario.org_id == current_user.org_id)
    if base_plan_id:
        query = query.filter(Scenario.base_plan_id == base_plan_id)
    return query.order_by(Scenario.created_at.desc()).all()


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch scenario results and side-by-side diff."""
    scenario = (
        db.query(Scenario)
        .filter(Scenario.id == scenario_id, Scenario.org_id == current_user.org_id)
        .first()
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario
