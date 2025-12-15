from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db import Base


class StudentValidation(Base):
    """Modelo para armazenar resultados de validação de estudantes"""
    __tablename__ = "student_validations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, index=True, nullable=False)
    registration = Column(String, index=True, nullable=False)
    is_valid = Column(Boolean, nullable=False)
    reason = Column(String, nullable=False)
    validated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ValidationRule(Base):
    """Modelo para armazenar a configuração das regras de validação"""
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rule_name = Column(String, unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=True, nullable=False)
