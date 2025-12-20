"""
Admin Scenarios Endpoints
Admin endpoints for managing market scenarios
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...dependencies import get_current_user, require_role
from ...db.session import get_db
from ...models.user import User
from ...models.market import MarketScenario
from ...services.scenario_manager import get_scenario_manager

router = APIRouter(tags=["admin-scenarios"])


# Request Models
class CreateScenarioRequest(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_type: str  # bull, bear, volatile, sideways
    config: dict = {}


class UpdateScenarioRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scenario_type: Optional[str] = None
    config: Optional[dict] = None


# Response Models
class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    scenario_type: str
    config: dict
    is_active: bool
    created_by: Optional[int]

    class Config:
        from_attributes = True


@router.post("/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    request: CreateScenarioRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Create a new market scenario"""
    try:
        # Validate scenario_type
        valid_types = ["bull", "bear", "volatile", "sideways"]
        if request.scenario_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scenario_type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate config
        if not isinstance(request.config, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Config must be a dictionary"
            )
        
        scenario = MarketScenario(
            name=request.name,
            description=request.description,
            scenario_type=request.scenario_type,
            config=request.config,
            created_by=user.id,
            is_active=False
        )
        
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scenario: {str(e)}"
        )


@router.get("/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(
    scenario_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get all market scenarios"""
    try:
        query = db.query(MarketScenario)
        
        if scenario_type:
            query = query.filter(MarketScenario.scenario_type == scenario_type)
        
        if is_active is not None:
            query = query.filter(MarketScenario.is_active == is_active)
        
        scenarios = query.order_by(MarketScenario.created_at.desc()).all()
        
        return scenarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scenarios: {str(e)}"
        )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get a specific scenario"""
    scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )
    
    return scenario


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: int,
    request: UpdateScenarioRequest,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Update a scenario"""
    try:
        scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )
        
        # Update fields
        update_data = request.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(scenario, key, value)
        
        db.commit()
        db.refresh(scenario)
        
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update scenario: {str(e)}"
        )


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Delete a scenario"""
    try:
        scenario = db.query(MarketScenario).filter_by(id=scenario_id).first()
        
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )
        
        # Don't allow deleting active scenario
        if scenario.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete active scenario. Deactivate it first."
            )
        
        db.delete(scenario)
        db.commit()
        
        return {"success": True, "message": "Scenario deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete scenario: {str(e)}"
        )


@router.post("/scenarios/{scenario_id}/activate")
async def activate_scenario(
    scenario_id: int,
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Activate a scenario"""
    try:
        manager = get_scenario_manager()
        scenario_data = manager.apply_scenario(scenario_id, db)
        
        return {
            "success": True,
            "message": f"Scenario '{scenario_data['name']}' activated",
            "scenario": scenario_data
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate scenario: {str(e)}"
        )


@router.post("/scenarios/deactivate")
async def deactivate_scenario(
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Deactivate current scenario"""
    try:
        manager = get_scenario_manager()
        manager.stop_scenario(db)
        
        return {
            "success": True,
            "message": "All scenarios deactivated"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate scenario: {str(e)}"
        )


@router.get("/scenarios/active/current")
async def get_active_scenario(
    user: User = Depends(require_role(["admin", "owner"])),
    db: Session = Depends(get_db)
):
    """Get currently active scenario"""
    try:
        manager = get_scenario_manager()
        active = manager.get_active_scenario(db)
        
        if active:
            return {
                "success": True,
                "scenario": active
            }
        else:
            return {
                "success": True,
                "scenario": None,
                "message": "No active scenario"
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active scenario: {str(e)}"
        )
