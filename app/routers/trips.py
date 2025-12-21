from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import ValidationRule
from app.schemas import (
    ValidationRuleCreate,
    ValidationRuleUpdate,
    ValidationRuleResponse,
    DeleteResponse
)

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("", response_model=List[ValidationRuleResponse])
async def get_all_rules(db: Session = Depends(get_db)):
    """
    Retorna todas as regras de validação e seu status atual.
    """
    rules = db.query(ValidationRule).all()
    return rules


@router.post("", response_model=ValidationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: ValidationRuleCreate,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova regra de validação.
    
    - **rule_name**: Nome identificador da regra (deve ser único)
    - **enabled**: Status inicial da regra (True ou False)
    """
    # Verificar se a regra já existe
    existing_rule = db.query(ValidationRule).filter(
        ValidationRule.rule_name == rule.rule_name
    ).first()
    
    if existing_rule:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Rule '{rule.rule_name}' already exists"
        )
    
    # Criar nova regra
    new_rule = ValidationRule(
        rule_name=rule.rule_name,
        enabled=rule.enabled
    )
    
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    return ValidationRuleResponse(
        rule_name=new_rule.rule_name,
        enabled=new_rule.enabled
    )


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


@router.delete("/{rule_name}", response_model=DeleteResponse)
async def delete_rule(
    rule_name: str,
    db: Session = Depends(get_db)
):
    """
    Remove uma regra de validação existente.
    
    - **rule_name**: Nome da regra a ser removida
    
    **Aviso**: Deletar regras padrão (institutional_email_check, registration_length_check) 
    pode afetar o funcionamento do sistema de validação.
    """
    rule = db.query(ValidationRule).filter(ValidationRule.rule_name == rule_name).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule '{rule_name}' not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return DeleteResponse(
        message=f"Rule '{rule_name}' deleted successfully"
    )
