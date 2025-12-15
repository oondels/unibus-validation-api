from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import ValidationRule
from app.schemas import (
    ValidationRuleUpdate,
    ValidationRuleResponse
)

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("", response_model=List[ValidationRuleResponse])
async def get_all_rules(db: Session = Depends(get_db)):
    """
    Retorna todas as regras de validação e seu status atual.
    """
    rules = db.query(ValidationRule).all()
    return rules


@router.put("/{rule_name}", response_model=ValidationRuleResponse)
async def update_rule(
    rule_name: str,
    update: ValidationRuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Habilitar ou desabilitar uma regra de validação.
    
    Regras disponíveis:
    - institutional_email_check
    - registration_length_check
    """
    rule = db.query(ValidationRule).filter(ValidationRule.rule_name == rule_name).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule '{rule_name}' not found"
        )
    
    rule.enabled = update.enabled
    db.commit()
    db.refresh(rule)
    
    return ValidationRuleResponse(
        rule_name=rule.rule_name,
        enabled=rule.enabled
    )
