# UniBus – API de Validação de Estudantes

## Visão Geral

Microserviço secundário responsável por validar a elegibilidade de estudantes para o serviço UniBus. Esta API aplica regras de validação determinísticas, persiste resultados de validação e expõe endpoints de configuração.

**Nome do Serviço:** `unibus-student-validation-api`

## Funcionalidades

- ✅ Validação de elegibilidade de estudantes com regras configuráveis
- ✅ Armazenamento persistente de resultados de validação
- ✅ API RESTful completa com operações GET, POST, PUT e DELETE
- ✅ CRUD completo de regras de validação (criar, ler, atualizar, deletar)
- ✅ Banco de dados SQLite (embarcado, sem necessidade de banco externo)
- ✅ Suporte Docker
- ✅ FastAPI com documentação OpenAPI automática
- ✅ Arquitetura simples e amigável para fins acadêmicos

## Stack Tecnológica

- **Framework:** FastAPI
- **Banco de Dados:** SQLite (embarcado, baseado em arquivo)
- **Linguagem:** Python 3.11+
- **Container:** Docker
- **ORM:** SQLAlchemy

## Instalação

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (para deploy containerizado)
- Acesso à rede Docker `unibus-network` (compartilhada com outros serviços UniBus)

**Nota:** Não é necessário servidor de banco de dados externo - SQLite é embarcado!

### Opção 1: Desenvolvimento Local

1. Clone o repositório e navegue até o diretório do projeto:
```bash
cd unibus-validation-api
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python -m app.main
# ou
uvicorn app.main:app --reload --port 8001
```

### Opção 2: Docker

1. Primeiro, crie a rede compartilhada (se ainda não existir):
```bash
docker network create unibus-network
```

2. Build e execute com Docker Compose:
```bash
docker-compose up -d
```

**Nota:** O arquivo do banco de dados SQLite é persistido em um volume Docker (`validation-db`), então os dados sobrevivem a reinicializações do container.

3. Ou faça o build manualmente:
```bash
docker build -t unibus-validation-api .
docker run -p 8001:8001 \
  --network unibus-network \
  -v validation-db:/app/data \
  unibus-validation-api
```

## Acesso à API

- **URL Base da API:** http://localhost:8001
- **Documentação Interativa:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Banco de Dados

O serviço usa **SQLite** como banco de dados - um banco de dados leve baseado em arquivo, perfeito para as necessidades deste microserviço. O banco de dados é criado automaticamente na primeira execução com as regras de validação padrão.

### Por que SQLite?

- ✅ **Armazenamento Independente:** Cada microserviço tem seu próprio banco de dados (boa prática de microserviços)
- ✅ **Deploy Simples:** Arquivo único, sem necessidade de servidor de banco de dados separado
- ✅ **Backup Fácil:** Basta copiar o arquivo do banco de dados
- ✅ **Suficiente para o Caso de Uso:** Baixo volume de registros de validação
- ✅ **Configuração Zero:** Funciona imediatamente

### Localização do Banco de Dados

- **Docker (Produção):** `/app/data/unibus_validation.db` (persistido via volume)
- **Desenvolvimento Local:** `./unibus_validation.db` (na raiz do projeto)

### Tabelas

#### `student_validations`
Armazena os resultados de validação para cada requisição de validação de estudante.

| Campo        | Tipo     | Descrição                        |
|--------------|----------|----------------------------------|
| id           | Integer  | Chave primária auto-incremento   |
| email        | String   | Email do estudante               |
| registration | String   | Número de matrícula do estudante |
| is_valid     | Boolean  | Resultado da validação           |
| reason       | String   | Razão do resultado da validação  |
| validated_at | DateTime | Timestamp da validação           |

#### `validation_rules`
Armazena a configuração das regras de validação.

| Campo     | Tipo    | Descrição                    |
|-----------|---------|------------------------------|
| id        | Integer | Chave primária auto-incremento |
| rule_name | String  | Identificador da regra       |
| enabled   | Boolean | Se a regra está ativa        |

## Regras de Validação

O serviço implementa duas regras de validação simples e configuráveis:

1. **institutional_email_check**: Email deve conter `@aluno` OU terminar com `.edu.br`
2. **registration_length_check**: Número de matrícula deve ter pelo menos 6 caracteres

**Nota:** Todas as regras habilitadas devem passar para que o estudante seja considerado válido.

## Endpoints da API

### Health Check

#### `GET /health`
Endpoint simples de verificação de saúde.

**Resposta:**
```json
{
  "status": "ok"
}
```

---

### Validação de Estudantes

#### `POST /validations/validate-student`
Endpoint principal: valida um estudante e armazena o resultado.

**Requisição:**
```json
{
  "name": "João Silva",
  "email": "joao@aluno.ufrj.br",
  "registration": "202312345"
}
```

**Resposta:**
```json
{
  "is_valid": true,
  "reason": "Institutional email detected (@aluno)"
}
```

---

#### `GET /validations`
Retorna todos os registros de validação armazenados (ordenados do mais recente).

**Resposta:**
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
Retorna um único registro de validação por ID.

**Resposta:**
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

**Erro (404):**
```json
{
  "detail": "Validation with id 999 not found"
}
```

---

#### `DELETE /validations/{id}`
Deleta um registro de validação por ID.

**Resposta:**
```json
{
  "message": "Validation deleted successfully"
}
```

**Erro (404):**
```json
{
  "detail": "Validation with id 999 not found"
}
```

---

### Gerenciamento de Regras de Validação

#### `GET /rules`
Retorna todas as regras de validação e seus status atuais.

**Resposta:**
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

#### `POST /rules`
Cria uma nova regra de validação.

**Requisição:**
```json
{
  "rule_name": "custom_rule_check",
  "enabled": true
}
```

**Resposta (201 Created):**
```json
{
  "rule_name": "custom_rule_check",
  "enabled": true
}
```

**Erro (409 Conflict):**
```json
{
  "detail": "Rule 'custom_rule_check' already exists"
}
```

---

#### `PUT /rules/{rule_name}`
Habilita ou desabilita uma regra de validação.

**Regras Disponíveis:**
- `institutional_email_check`
- `registration_length_check`

**Requisição:**
```json
{
  "enabled": false
}
```

**Resposta:**
```json
{
  "rule_name": "institutional_email_check",
  "enabled": false
}
```

**Erro (404):**
```json
{
  "detail": "Rule 'invalid_rule' not found"
}
```

---

#### `DELETE /rules/{rule_name}`
Remove uma regra de validação existente.

**Resposta:**
```json
{
  "message": "Rule 'custom_rule_check' deleted successfully"
}
```

**Erro (404):**
```json
{
  "detail": "Rule 'invalid_rule' not found"
}
```

**Aviso:** Deletar regras padrão (`institutional_email_check`, `registration_length_check`) pode afetar o funcionamento do sistema de validação.

---

## Integração com a API Core

Este serviço foi projetado para ser consumido pela `unibus-core-api` durante o cadastro de estudantes.

### Configuração de Rede

Ambos os serviços devem estar na mesma rede Docker (`unibus-network`) para se comunicarem.

**Criar a rede:**
```bash
docker network create unibus-network
```

### Fluxo de Integração Sugerido:

1. Usuário chama `POST /students` na `unibus-core-api`
2. API Core chama `POST /validations/validate-student` neste serviço (http://unibus-validation-api:8001)
3. Se `is_valid = false`, API Core retorna HTTP 400 ao usuário
4. Se `is_valid = true`, API Core persiste o estudante e retorna HTTP 201

### Exemplo de Código de Integração (Python):

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

## Testes

### Testes Manuais com curl

**Validar um estudante:**
```bash
curl -X POST http://localhost:8001/validations/validate-student \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@aluno.ufrj.br",
    "registration": "202312345"
  }'
```

**Obter todas as validações:**
```bash
curl http://localhost:8001/validations
```

**Desabilitar uma regra:**
```bash
curl -X PUT http://localhost:8001/rules/institutional_email_check \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

**Criar uma nova regra:**
```bash
curl -X POST http://localhost:8001/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "custom_rule_check",
    "enabled": true
  }'
```

**Deletar uma regra:**
```bash
curl -X DELETE http://localhost:8001/rules/custom_rule_check
```

**Deletar uma validação:**
```bash
curl -X DELETE http://localhost:8001/validations/1
```

## Estrutura do Projeto

```
unibus-validation-api/
├── app/
│   ├── __init__.py              # Inicialização do app
│   ├── main.py                  # Aplicação FastAPI e startup
│   ├── db.py                    # Configuração do banco de dados e sessão
│   ├── models.py                # Modelos SQLAlchemy
│   ├── schemas.py               # Schemas Pydantic
│   ├── services.py              # Lógica de negócio
│   ├── external.py              # Integrações com serviços externos
│   └── routers/
│       ├── __init__.py          # Inicialização dos routers
│       ├── routes.py            # Rotas de health check
│       ├── students.py          # Rotas de validação de estudantes
│       └── validation.py        # Rotas de regras de validação
├── Dockerfile                    # Configuração da imagem Docker
├── docker-compose.yml            # Configuração do Docker Compose
├── requirements.txt              # Dependências Python
├── .env.example                  # Template de variáveis de ambiente
├── .gitignore                    # Regras do Git ignore
└── README.md                     # Este arquivo
```

## Variáveis de Ambiente

Crie um arquivo `.env` (veja `.env.example`):

```env
DATABASE_URL=sqlite:///./data/unibus_validation.db
API_HOST=0.0.0.0
API_PORT=8001
```

## Por Que Esta Arquitetura Funciona Bem

✅ **Separação clara de responsabilidades** - Responsabilidade única (apenas validação)  
✅ **Persistência independente** - Banco de dados e modelo de dados próprios  
✅ **Design RESTful** - Usa todos os principais verbos HTTP (GET, POST, PUT, DELETE)  
✅ **Fácil de demonstrar** - Regras simples que são fáceis de explicar academicamente  
✅ **Sem dependências externas** - Completamente auto-contido  
✅ **Extensível** - Fácil adicionar novas regras de validação ou trocar por serviços reais  
✅ **Pronto para microsserviços** - Pode ser implantado independentemente  
✅ **Amigável para fins acadêmicos** - Valor educacional claro para aprendizado de microsserviços

## Melhorias Futuras

- Integração com sistemas reais de registro universitário
- Regras de validação mais complexas (ex: verificar contra banco de matrículas)
- Autenticação e autorização
- Rate limiting
- Métricas e monitoramento
- Suporte a PostgreSQL/MySQL para produção
- Validação assíncrona com filas de mensagens

## Licença

Licença MIT - Uso acadêmico para MVP de Microsserviços Sprint 3 PUC-Rio

---

**Autor:** Equipe de Desenvolvimento UniBus  
**Versão:** 1.0.0  
**Última Atualização:** 15 de dezembro de 2025
