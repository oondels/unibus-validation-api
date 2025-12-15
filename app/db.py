from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unibus_validation.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência para obter a sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados e cria regras de validação padrão"""
    from app.models import ValidationRule
    
    Base.metadata.create_all(bind=engine)
    
    # Cria regras de validação padrão se não existirem
    db = SessionLocal()
    try:
        existing_rules = db.query(ValidationRule).count()
        if existing_rules == 0:
            default_rules = [
                ValidationRule(rule_name="institutional_email_check", enabled=True),
                ValidationRule(rule_name="registration_length_check", enabled=True)
            ]
            db.add_all(default_rules)
            db.commit()
            print("✅ Default validation rules created successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
