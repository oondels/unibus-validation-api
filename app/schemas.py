from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class StudentValidationRequest(BaseModel):
    """Modelo de solicitação para validação de estudante"""
    name: str
    email: EmailStr
    registration: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "João Silva",
                "email": "joao@aluno.ufrj.br",
                "registration": "202312345"
            }
        }


class StudentValidationResponse(BaseModel):
    """Modelo de resposta para validação de estudante"""
    is_valid: bool
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "reason": "Institutional email detected"
            }
        }


class ValidationRecordResponse(BaseModel):
    """Modelo de resposta para registros de validação"""
    id: int
    email: str
    registration: str
    is_valid: bool
    reason: str
    validated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "joao@aluno.ufrj.br",
                "registration": "202312345",
                "is_valid": True,
                "reason": "Institutional email detected",
                "validated_at": "2025-12-15T09:30:00"
            }
        }


class ValidationRuleCreate(BaseModel):
    """Modelo de solicitação para criar uma nova regra de validação"""
    rule_name: str
    enabled: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "rule_name": "custom_rule_check",
                "enabled": True
            }
        }


class ValidationRuleUpdate(BaseModel):
    """Modelo de solicitação para atualizar regras de validação"""
    enabled: bool

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": False
            }
        }


class ValidationRuleResponse(BaseModel):
    """Modelo de resposta para regras de validação"""
    rule_name: str
    enabled: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "rule_name": "institutional_email_check",
                "enabled": True
            }
        }


class DeleteResponse(BaseModel):
    """Response model for delete operations"""
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Validation deleted successfully"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok"
            }
        }
