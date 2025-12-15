# UniBus – Student Validation API

## Overview

Secondary microservice responsible for validating student eligibility for the UniBus service. This API applies deterministic validation rules, persists validation results, and exposes configuration endpoints.

**Service Name:** `unibus-student-validation-api`

## Features

- ✅ Student eligibility validation with configurable rules
- ✅ Persistent storage of validation results
- ✅ RESTful API with GET, POST, PUT, and DELETE operations
- ✅ SQLite database (easy to switch to PostgreSQL/MySQL)
- ✅ Docker support
- ✅ FastAPI with automatic OpenAPI documentation
- ✅ Simple, academic-friendly architecture

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (with SQLAlchemy ORM)
- **Language:** Python 3.11+
- **Container:** Docker

## Installation

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- Access to `unibus-network` Docker network (shared with other UniBus services)

### Option 1: Local Development

1. Clone the repository and navigate to the project directory:
```bash
cd unibus-validation-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python -m app.main
# or
uvicorn app.main:app --reload --port 8001
```

### Option 2: Docker

1. First, create the shared network (if it doesn't exist):
```bash
docker network create unibus-network
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Or build manually:
```bash
docker build -t unibus-validation-api .
docker run -p 8001:8001 --network unibus-network unibus-validation-api
```

## API Access

- **API Base URL:** http://localhost:8001
- **Interactive Docs:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Database

The service uses SQLite by default. The database is automatically created on first run with default validation rules.

### Tables

#### `student_validations`
Stores validation results for each student validation request.

| Field        | Type     | Description                  |
|--------------|----------|------------------------------|
| id           | Integer  | Auto-increment primary key   |
| email        | String   | Student email                |
| registration | String   | Student registration number  |
| is_valid     | Boolean  | Validation result            |
| reason       | String   | Reason for validation result |
| validated_at | DateTime | Timestamp of validation      |

#### `validation_rules`
Stores configuration for validation rules.

| Field     | Type    | Description                |
|-----------|---------|----------------------------|
| id        | Integer | Auto-increment primary key |
| rule_name | String  | Rule identifier            |
| enabled   | Boolean | Whether the rule is active |

## Validation Rules

The service implements two simple, configurable validation rules:

1. **institutional_email_check**: Email must contain `@aluno` OR end with `.edu.br`
2. **registration_length_check**: Registration number must be at least 6 characters

**Note:** All enabled rules must pass for a student to be considered valid.

## API Endpoints

### Health Check

#### `GET /health`
Simple health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

### Student Validation

#### `POST /validations/validate-student`
Main endpoint: Validates a student and stores the result.

**Request:**
```json
{
  "name": "João Silva",
  "email": "joao@aluno.ufrj.br",
  "registration": "202312345"
}
```

**Response:**
```json
{
  "is_valid": true,
  "reason": "Institutional email detected (@aluno)"
}
```

---

#### `GET /validations`
Returns all stored validation records (ordered by most recent).

**Response:**
```json
[
  {
    "id": 1,
    "email": "joao@aluno.ufrj.br",
    "registration": "202312345",
    "is_valid": true,
    "reason": "Institutional email detected (@aluno)",
    "validated_at": "2025-12-15T09:30:00"
  }
]
```

---

#### `GET /validations/{id}`
Returns a single validation record by ID.

**Response:**
```json
{
  "id": 1,
  "email": "joao@aluno.ufrj.br",
  "registration": "202312345",
  "is_valid": true,
  "reason": "Institutional email detected (@aluno)",
  "validated_at": "2025-12-15T09:30:00"
}
```

**Error (404):**
```json
{
  "detail": "Validation with id 999 not found"
}
```

---

#### `DELETE /validations/{id}`
Deletes a validation record by ID.

**Response:**
```json
{
  "message": "Validation deleted successfully"
}
```

**Error (404):**
```json
{
  "detail": "Validation with id 999 not found"
}
```

---

### Validation Rules Management

#### `GET /rules`
Returns all validation rules and their current status.

**Response:**
```json
[
  {
    "rule_name": "institutional_email_check",
    "enabled": true
  },
  {
    "rule_name": "registration_length_check",
    "enabled": true
  }
]
```

---

#### `PUT /rules/{rule_name}`
Enable or disable a validation rule.

**Available Rules:**
- `institutional_email_check`
- `registration_length_check`

**Request:**
```json
{
  "enabled": false
}
```

**Response:**
```json
{
  "rule_name": "institutional_email_check",
  "enabled": false
}
```

**Error (404):**
```json
{
  "detail": "Rule 'invalid_rule' not found"
}
```

---

## Integration with Core API

This service is designed to be consumed by the `unibus-core-api` during student registration.

### Network Configuration

Both services must be on the same Docker network (`unibus-network`) to communicate.

**Create the network:**
```bash
docker network create unibus-network
```

### Suggested Integration Flow:

1. User calls `POST /students` on `unibus-core-api`
2. Core API calls `POST /validations/validate-student` on this service (http://unibus-validation-api:8001)
3. If `is_valid = false`, Core API returns HTTP 400 to user
4. If `is_valid = true`, Core API persists the student and returns HTTP 201

### Example Integration Code (Python):

```python
import httpx

async def register_student(student_data):
    # Call validation service
    async with httpx.AsyncClient() as client:
        validation_response = await client.post(
            "http://unibus-validation-api:8001/validations/validate-student",
            json=student_data
        )
        validation_result = validation_response.json()
    
    # Check validation result
    if not validation_result["is_valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Student validation failed: {validation_result['reason']}"
        )
    
    # Proceed with student registration
    # ... save student to database ...
```

## Testing

### Manual Testing with curl

**Validate a student:**
```bash
curl -X POST http://localhost:8001/validations/validate-student \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@aluno.ufrj.br",
    "registration": "202312345"
  }'
```

**Get all validations:**
```bash
curl http://localhost:8001/validations
```

**Disable a rule:**
```bash
curl -X PUT http://localhost:8001/rules/institutional_email_check \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

**Delete a validation:**
```bash
curl -X DELETE http://localhost:8001/validations/1
```

## Project Structure

```
unibus-validation-api/
├── app/
│   ├── __init__.py              # App initialization
│   ├── main.py                  # FastAPI application and startup
│   ├── db.py                    # Database configuration and session
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── services.py              # Business logic
│   ├── external.py              # External service integrations
│   └── routers/
│       ├── __init__.py          # Router initialization
│       ├── routes.py            # Health check routes
│       ├── students.py          # Student validation routes
│       └── trips.py             # Validation rules routes
├── Dockerfile                    # Docker image configuration
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Environment Variables

Create a `.env` file (see `.env.example`):

```env
DATABASE_URL=sqlite:///./unibus_validation.db
API_HOST=0.0.0.0
API_PORT=8001
```

## Why This Architecture Works Well

✅ **Clear separation of concerns** - Single responsibility (validation only)  
✅ **Independent persistence** - Own database and data model  
✅ **RESTful design** - Uses all major HTTP verbs (GET, POST, PUT, DELETE)  
✅ **Easy to demonstrate** - Simple rules that are easy to explain academically  
✅ **No external dependencies** - Completely self-contained  
✅ **Extensible** - Easy to add new validation rules or switch to real services  
✅ **Microservice-ready** - Can be deployed independently  
✅ **Academic-friendly** - Clear educational value for microservices learning

## Future Enhancements

- Integration with actual university registration systems
- More complex validation rules (e.g., check against enrollment database)
- Authentication and authorization
- Rate limiting
- Metrics and monitoring
- PostgreSQL/MySQL support for production
- Async validation with message queues

## License

MIT License - Academic use for PUC-Rio Sprint 3 Microservices MVP

---

**Author:** UniBus Development Team  
**Version:** 1.0.0  
**Last Updated:** December 15, 2025
