from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db import get_db
from app.models import StudentValidation
from app.schemas import (
    StudentValidationRequest,
    StudentValidationResponse,
    ValidationRecordResponse,
    DeleteResponse
)
from app.services import ValidationService

router = APIRouter(prefix="/validations", tags=["Validations"])


@router.post("/validate-student", response_model=StudentValidationResponse)
async def validate_student(
    request: StudentValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal: Valida um estudante e armazena o resultado.
    
    Regras de validação (quando habilitadas):
    - Verificação de email institucional: email contém '@aluno' OU termina com '.edu.br'
    - Verificação de comprimento do registro: comprimento do registro >= 6 caracteres
    
    Todas as regras habilitadas devem passar para o estudante ser considerado válido.
    """
    # Realizar validação
    validation_service = ValidationService(db)
    is_valid, reason = validation_service.validate_student(
        email=request.email,
        registration=request.registration
    )
    
    # Store validation result
    validation_record = StudentValidation(
        email=request.email,
        registration=request.registration,
        is_valid=is_valid,
        reason=reason,
        validated_at=datetime.utcnow()
    )
    db.add(validation_record)
    db.commit()
    db.refresh(validation_record)
    
    return StudentValidationResponse(
        is_valid=is_valid,
        reason=reason
    )


@router.get("", response_model=List[ValidationRecordResponse])
async def get_all_validations(db: Session = Depends(get_db)):
    """
    Retorna todos os registros de validação armazenados.
    """
    validations = db.query(StudentValidation).order_by(StudentValidation.validated_at.desc()).all()
    return validations


@router.get("/{validation_id}", response_model=ValidationRecordResponse)
async def get_validation_by_id(validation_id: int, db: Session = Depends(get_db)):
    """
    Retorna um único registro de validação pelo ID.
    """
    validation = db.query(StudentValidation).filter(StudentValidation.id == validation_id).first()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with id {validation_id} not found"
        )
    
    return validation


@router.delete("/{validation_id}", response_model=DeleteResponse)
async def delete_validation(validation_id: int, db: Session = Depends(get_db)):
    """
    Deleta um registro de validação pelo ID.
    """
    validation = db.query(StudentValidation).filter(StudentValidation.id == validation_id).first()
    
    if not validation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation with id {validation_id} not found"
        )
    
    db.delete(validation)
    db.commit()
    
    return DeleteResponse(message="Validation deleted successfully")
