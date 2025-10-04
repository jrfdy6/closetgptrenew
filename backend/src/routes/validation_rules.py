"""
API endpoints for managing validation rules.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ..core.validation_rules import validation_rules
from ..auth.auth_service import get_current_user_optional
from ..custom_types.profile import UserProfile
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class RuleUpdateRequest(BaseModel):
    rule_path: str
    new_value: Any
    user_id: Optional[str] = None

class MaterialRuleRequest(BaseModel):
    material: str
    max_temp_f: int
    min_temp_f: int

class ValidationRulesResponse(BaseModel):
    rules: Dict[str, Any]
    metadata: Dict[str, Any]

@(router.get("/validation-rules") if router else None)
async def get_validation_rules(current_user: Optional[UserProfile] = Depends(get_current_user_optional)) -> ValidationRulesResponse:
    """Get current validation rules."""
    try:
        rules = validation_rules.get_rules()
        return ValidationRulesResponse(
            rules=rules,
            metadata=(rules.get('metadata', {}) if rules else {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching validation rules: {str(e)}")

@router.post("/validation-rules/update")
async def update_validation_rule(
    request: RuleUpdateRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Update a specific validation rule."""
    try:
        success = validation_rules.update_rule(request.rule_path, request.new_value)
        
        if success:
            # Log the change
            user_id = current_user.id if current_user else "anonymous"
            validation_rules.log_rule_change(
                request.rule_path, 
                "previous_value", 
                request.new_value, 
                user_id
            )
            
            return {
                "success": True,
                "message": f"Rule {request.rule_path} updated successfully",
                "rule_path": request.rule_path,
                "new_value": request.new_value
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update rule")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating rule: {str(e)}")

@router.post("/validation-rules/material")
async def add_material_rule(
    request: MaterialRuleRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Add a new material climate rule."""
    try:
        success = validation_rules.add_material_rule(
            request.material, 
            request.max_temp_f, 
            request.min_temp_f
        )
        
        if success:
            # Log the change
            user_id = current_user.id if current_user else "anonymous"
            validation_rules.log_rule_change(
                f"material_climate_rules.{request.material}",
                None,
                {"max_temp_f": request.max_temp_f, "min_temp_f": request.min_temp_f},
                user_id
            )
            
            return {
                "success": True,
                "message": f"Material rule for {request.material} added successfully",
                "material": request.material,
                "max_temp_f": request.max_temp_f,
                "min_temp_f": request.min_temp_f
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add material rule")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding material rule: {str(e)}")

@router.delete("/validation-rules/material/{material}")
async def remove_material_rule(
    material: str,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Remove a material climate rule."""
    try:
        success = validation_rules.remove_material_rule(material)
        
        if success:
            # Log the change
            user_id = current_user.id if current_user else "anonymous"
            validation_rules.log_rule_change(
                f"material_climate_rules.{material}",
                None,
                None,
                user_id
            )
            
            return {
                "success": True,
                "message": f"Material rule for {material} removed successfully",
                "material": material
            }
        else:
            raise HTTPException(status_code=404, detail=f"Material rule for {material} not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing material rule: {str(e)}")

@(router.get("/validation-rules/history") if router else None)
async def get_rule_history(
    limit: int = 10,
    current_user: Optional[UserProfile] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """Get history of rule changes."""
    try:
        history = validation_rules.get_rule_history(limit)
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rule history: {str(e)}")

@router.post("/apply-fix")
async def apply_fix(
    fix_request: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Apply a fix suggestion to validation rules.
    
    Expected format:
    {
        "rule_type": "material_climate",
        "rule_path": "material_climate_rules.wool.max_temp_f",
        "current_value": 75,
        "suggested_value": 80,
        "reason": "Increase wool max temperature for warmer weather",
        "fixable": true
    }
    """
    try:
        # Validate fix request
        required_fields = ["rule_path", "suggested_value"]
        for field in required_fields:
            if field not in fix_request:
                return {
                    "success": False,
                    "error": f"Missing required field: {field}"
                }
        
        # Apply the fix
        user_id = current_user.id if current_user else "anonymous"
        success = validation_rules.apply_fix(fix_request, user_id)
        
        if success:
            return {
                "success": True,
                "message": f"Fix applied successfully: {fix_request['rule_path']} = {fix_request['suggested_value']}",
                "applied_fix": fix_request
            }
        else:
            return {
                "success": False,
                "error": "Failed to apply fix"
            }
            
    except Exception as e:
        logger.error(f"Error applying fix: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/generate-fix-suggestion")
async def generate_fix_suggestion(
    error_data: Dict[str, Any],
    current_user: UserProfile = Depends(get_current_user_optional)
):
    """
    Generate a fixable suggestion for a validation error.
    
    Expected format:
    {
        "error_type": "material_climate_mismatch",
        "error_details": {
            "material": "wool",
            "temperature": 80
        }
    }
    """
    try:
        error_type = (error_data.get("error_type") if error_data else None)
        error_details = (error_data.get("error_details", {}) if error_data else {})
        
        if not error_type:
            return {
                "success": False,
                "error": "Missing error_type"
            }
        
        # Generate fix suggestion
        suggestion = validation_rules.generate_fixable_suggestion(error_type, error_details)
        
        if suggestion:
            return {
                "success": True,
                "suggestion": suggestion
            }
        else:
            return {
                "success": False,
                "error": "No fixable suggestion available for this error type",
                "error_type": error_type
            }
            
    except Exception as e:
        logger.error(f"Error generating fix suggestion: {e}")
        return {
            "success": False,
            "error": str(e)
        }
