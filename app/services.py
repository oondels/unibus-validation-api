from sqlalchemy.orm import Session
from app.models import ValidationRule
from typing import List, Tuple


class ValidationService:
    def __init__(self, db: Session):
        self.db = db

    def get_enabled_rules(self) -> List[ValidationRule]:
        """Obter todas as regras de validação habilitadas"""
        return self.db.query(ValidationRule).filter(ValidationRule.enabled == True).all()

    def validate_institutional_email(self, email: str) -> Tuple[bool, str]:
        """
        Validar se o email é institucional
        Regra: email contém '@aluno' OU termina com '.edu.br'
        """
        email_lower = email.lower()
        
        if "@aluno" in email_lower:
            return True, "Institutional email detected (@aluno)"
        
        if email_lower.endswith(".edu.br"):
            return True, "Institutional email detected (.edu.br domain)"
        
        return False, "Email is not institutional (must contain @aluno or end with .edu.br)"

    def validate_registration_length(self, registration: str) -> Tuple[bool, str]:
        """
        Validar o comprimento do número de matrícula
        Regra: comprimento da matrícula >= 6 caracteres
        """
        if len(registration) >= 6:
            return True, "Registration number has valid length"
        
        return False, f"Registration number too short (minimum 6 characters, got {len(registration)})"

    def validate_student(self, email: str, registration: str) -> Tuple[bool, str]:
        """
        Validar estudante com base nas regras habilitadas
        Retorna: (é_válido, motivo)
        """
        enabled_rules = self.get_enabled_rules()
        
        if not enabled_rules:
            return False, "No validation rules are enabled"

        # Rastrear resultados da validação
        validation_results = []
        reasons = []

        for rule in enabled_rules:
            if rule.rule_name == "institutional_email_check":
                is_valid, reason = self.validate_institutional_email(email)
                validation_results.append(is_valid)
                reasons.append(reason)
            
            elif rule.rule_name == "registration_length_check":
                is_valid, reason = self.validate_registration_length(registration)
                validation_results.append(is_valid)
                reasons.append(reason)

        # Todas as regras habilitadas devem passar
        if all(validation_results):
            # Retornar o primeiro motivo de sucesso (priorizar validação de email)
            return True, reasons[0]
        else:
            # Retornar o primeiro motivo de falha
            for i, result in enumerate(validation_results):
                if not result:
                    return False, reasons[i]
            
            return False, "Validation failed"
