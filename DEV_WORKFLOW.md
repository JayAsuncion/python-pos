# Development Workflow

**Last Updated:** March 22, 2026

---

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Running the Application](#running-the-application)
3. [Creating a New Entity](#creating-a-new-entity)
4. [Database Migrations](#database-migrations)
5. [Permission Management](#permission-management)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Deployment](#deployment)

---

## Initial Setup

### Prerequisites
- Python 3.9 or higher
- PostgreSQL (or use Docker)
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd python-pos
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv python-pos-env-39
python-pos-env-39\Scripts\activate

# Linux/Mac
python3 -m venv python-pos-env-39
source python-pos-env-39/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file (currently using hardcoded values in `database.py`):
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/python_pos

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Setup Database

**Option A: Using Docker**
```bash
docker-compose up -d postgres
```

**Option B: Local PostgreSQL**
1. Install PostgreSQL
2. Create database: `CREATE DATABASE python_pos;`
3. Update connection string in `database.py` or `.env`

### 6. Run Migrations
```bash
alembic upgrade head
```

### 7. Bootstrap Admin User
```bash
python -m app.auth.bootstrap_admin
```
**Default credentials:**
- Username: `admin`
- Password: `admin` (change immediately!)

### 8. Seed Permissions
```bash
python -m app.auth.seed_permissions
```

---

## Running the Application

### Development Server
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker Compose
docker-compose up
```

### Access Points
- **GraphQL Playground:** http://localhost:8000/graphql
- **API Endpoint:** http://localhost:8000/graphql (POST)

### First Login
1. Open GraphQL Playground
2. Run login mutation:
```graphql
mutation {
  login(username: "admin", password: "admin") {
    token
    user {
      id
      username
    }
    requiresPasswordReset
  }
}
```
3. Copy the token
4. Add to HTTP Headers for authenticated requests:
```json
{
  "Authorization": "Bearer <your-token-here>"
}
```

---

## Creating a New Entity

**For detailed step-by-step guide, see:** [prompts/02-entity-creation-guide.md](prompts/02-entity-creation-guide.md)

**Quick Reference:**

### 1. Create Model
Create `app/models/{entity}.py`:
```python
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class MyEntity(Base):
    __tablename__ = "my_entity"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Full audit trail
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
```

### 2. Import Model for Migration Discovery
**In `alembic/env.py`:**
```python
from app.models.my_entity import MyEntity
```

**In `app/models/__init__.py` (optional but recommended):**
```python
from app.models.my_entity import MyEntity
```

### 3. Generate and Apply Migration
```bash
alembic revision --autogenerate -m "create my_entity table"
alembic upgrade head
```

### 4. Create GraphQL Schema
Create `app/schemas/{entity}.py`:
```python
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class MyEntityType:
    id: int
    name: str
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
```

### 5. Create Mutations
Create `app/graphql/mutations/{entity}.py`:
```python
import strawberry
from app.auth.permissions import require_permission
from app.database import SessionLocal
from app.models import MyEntity
from app.schemas.my_entity import MyEntityType

@strawberry.type  
class MyEntityMutations:
    @strawberry.mutation
    def create_my_entity(self, info: strawberry.types.Info, name: str) -> MyEntityType:
        user = require_permission(info, "CREATE_MY_ENTITY")
        db = SessionLocal()
        
        entity = MyEntity(name=name, created_by=user.id)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        
        result = MyEntityType(
            id=entity.id,
            name=entity.name,
            created_at=entity.created_at,
            created_by=entity.created_by
        )
        db.close()
        return result
```

Update `app/graphql/mutations/__init__.py`:
```python
from app.graphql.mutations.my_entity import MyEntityMutations

@strawberry.type
class Mutation(
    # ... other mutations ...
    MyEntityMutations,
):
    pass
```

### 6. Create Queries
Create `app/graphql/queries/{entity}.py`:
```python
import strawberry
from typing import List
from app.auth.permissions import require_permission
from app.database import SessionLocal
from app.models import MyEntity
from app.schemas.my_entity import MyEntityType

@strawberry.type
class MyEntityQueries:
    @strawberry.field
    def my_entities(self, info: strawberry.types.Info) -> List[MyEntityType]:
        require_permission(info, "VIEW_MY_ENTITY")
        db = SessionLocal()
        
        entities = db.query(MyEntity).filter(MyEntity.deleted_at == None).all()
        result = [MyEntityType(id=e.id, name=e.name) for e in entities]
        
        db.close()
        return result
```

Update `app/graphql/queries/__init__.py`:
```python
from app.graphql.queries.my_entity import MyEntityQueries

@strawberry.type
class Query(
    # ... other queries ...
    MyEntityQueries,
):
    pass
```

### 7. Add Permissions and Seed
**In `app/auth/seed_permissions.py`:**
```python
permissions_data = [
    # ... existing permissions ...
    
    # MyEntity permissions
    {"code": "CREATE_MY_ENTITY", "name": "Create My Entity", "description": "..."},
    {"code": "VIEW_MY_ENTITY", "name": "View My Entity", "description": "..."},
    {"code": "UPDATE_MY_ENTITY", "name": "Update My Entity", "description": "..."},
    {"code": "DELETE_MY_ENTITY", "name": "Delete My Entity", "description": "..."},
]
```

Run seeding:
```bash
python -m app.auth.seed_permissions
```

### 8. Update Documentation
**MANDATORY:** Update [prompts/01-entity-reference.md](prompts/01-entity-reference.md) with:
- Entity description
- Fields documentation
- Relationships
- Business rules

---

## Database Migrations

### Check Current Migration Status
```bash
alembic current
```

### Create New Migration
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for data migrations)
alembic revision -m "description of changes"
```

### Review Generated Migration
**ALWAYS review before applying:**
1. Open `alembic/versions/{hash}_{description}.py`
2. Check `upgrade()` function
3. Check `downgrade()` function
4. Verify column types, constraints, defaults

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific version
alembic upgrade <revision_id>
```

### Rollback Migrations
```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade all
alembic downgrade base
```

### View Migration History
```bash
alembic history

# Verbose output
alembic history --verbose
```

### Common Issues
**Issue:** Alembic doesn't detect model changes
- **Solution:** Ensure model is imported in `alembic/env.py`

**Issue:** Migration conflicts
- **Solution:** Merge migration branches or manually resolve conflicts in migration files

**Issue:** Can't downgrade migration
- **Solution:** Implement proper `downgrade()` function or revert manually

---

## Permission Management

### View All Permissions
```graphql
query {
  permissions {
    id
    code
    name
    description
  }
}
```

### Add New Permission
1. Edit `app/auth/seed_permissions.py`
2. Add to `permissions_data` list
3. Run: `python -m app.auth.seed_permissions`
4. Assign to roles via GraphQL or seed file

### Assign Permission to Role
```graphql
mutation {
  createRolePermission(roleId: 1, permissionId: 42) {
    id
    roleId
    permissionId
  }
}
```

### Check User Permissions
```graphql
query {
  myPermissions {
    code
    name
  }
}
```

### Permission Naming Convention
**Pattern:** `{ACTION}_{ENTITY}`

**Actions:**
- `CREATE` - Create new records
- `VIEW` - Read/query records
- `UPDATE` - Modify existing records
- `DELETE` - Soft delete records

**Examples:**
- `CREATE_PRODUCT`
- `VIEW_SHIFT`
- `UPDATE_USER`
- `DELETE_PRODUCT_TEMPLATE`

---

## Testing

### Recommended: Testing with Postman

**Why Postman?**
- ✅ Executable test collections (no copy/paste errors)
- ✅ Auto token management (login once, use everywhere)
- ✅ Environment variables for easy switching (dev/staging/prod)
- ✅ Request history and organization
- ✅ Built-in assertions and tests

**Available Collections** (in `testing/postman/`):
- `Authentication and RBAC.postman_collection.json` - Login, permissions, roles
- `User.postman_collection.json` - User CRUD operations
- `Product.postman_collection.json` - Product management
- `Product Template.postman_collection.json` - Product templates
- `Product Slot.postman_collection.json` - Slot management
- `Shift.postman_collection.json` - Shift operations (start/end)
- `ShiftTemplate.postman_collection.json` - Shift templates
- `ShiftUser.postman_collection.json` - Shift assignments
- `ProductSlotReading.postman_collection.json` - Meter readings

**Setup Instructions:**

1. **Import Collections**
   - Open Postman
   - Click "Import" button
   - Select all JSON files from `testing/postman/`
   - Collections appear in left sidebar

2. **Configure Environment**
   - Click "Environments" in left sidebar
   - Create new environment: "Local Dev"
   - Add variable:
     - `baseUrl` = `http://localhost:8000`
     - `accessToken` = (leave empty, auto-populated by login)
   - Select "Local Dev" from dropdown in top-right

3. **Authenticate**
   - Open "Authentication and RBAC" collection
   - Run "Login" request
   - Token automatically saved to `{{accessToken}}` variable
   - All other requests use this token automatically

4. **Test Workflows**
   - Browse collections by entity
   - Edit variables in request to test different scenarios
   - View responses and test results

**Example Workflow:**
```
1. Authentication and RBAC → Login (saves token)
2. Authentication and RBAC → Me (verifies token works)
3. User → Get All Users (test permission)
4. Product → Create Product (test entity creation)
5. Shift → Start Shift (test complex operation)
```

**Token Management:**
- Token expires in 60 minutes
- If you get authentication errors, re-run Login request
- Token is stored in environment variable `{{accessToken}}`
- All requests automatically include: `Authorization: Bearer {{accessToken}}`

---

### Alternative: GraphQL Playground

**For quick ad-hoc queries:**

1. Start development server: `uvicorn app.main:app --reload`
2. Open browser: http://localhost:8000/graphql
3. Login to get token:
   ```graphql
   mutation {
     login(username: "admin", password: "admin") {
       token
       user { id username }
     }
   }
   ```
4. Copy token from response
5. Click "HTTP HEADERS" at bottom
6. Add header:
   ```json
   {
     "Authorization": "Bearer <paste-token-here>"
   }
   ```
7. Run queries/mutations

**When to use GraphQL Playground:**
- Testing new queries during development
- Exploring schema (click "DOCS" on right)
- Quick one-off queries
- Schema introspection

**When to use Postman:**
- Regression testing
- Sharing tests with team
- Automated test runs
- Testing multiple environments

---

### Testing with cURL (CI/CD)

**For automation and scripting:**

```bash
# Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation{login(username:\"admin\",password:\"admin\"){token}}"}' \
  | jq -r '.data.login.token')

# Use token in subsequent requests
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"{products{id name costPrice sellingPrice}}"}'
```

**Useful for:**
- CI/CD pipeline integration
- Automated testing scripts
- Health checks
- Smoke tests after deployment

---

### Unit Testing (Future)

**TODO:** Add pytest and test coverage

```bash
# Install testing dependencies
pip install pytest pytest-cov pytest-asyncio

# Run tests
pytest

# With coverage report
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/test_auth.py -v
```

**Recommended test structure:**
```
tests/
├── conftest.py           # Fixtures and shared config
├── test_auth.py          # Authentication tests
├── test_permissions.py   # RBAC tests
├── test_user.py          # User mutations/queries
├── test_product.py       # Product operations
└── test_shift.py         # Shift workflows
```

---

## Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server`
- **Check:** PostgreSQL is running
- **Docker:** `docker-compose up postgres`
- **Local:** Check PostgreSQL service status

**Error:** `FATAL: database "python_pos" does not exist`
- **Solution:** Create database: `CREATE DATABASE python_pos;`

**Error:** `password authentication failed`
- **Solution:** Check credentials in `database.py` or `.env`

### Migration Issues

**Error:** `Can't locate revision identified by 'xxxx'`
- **Solution:** Database and migration files out of sync
- **Fix:** `alembic stamp head` (careful, this marks current state without running migrations)

**Error:** `Target database is not up to date`
- **Solution:** Run `alembic upgrade head`

### Authentication Issues

**Error:** `Could not validate credentials`
- **Check:** Token is in Authorization header: `Bearer <token>`
- **Check:** Token hasn't expired (60min default)
- **Solution:** Login again to get fresh token

**Error:** `User does not have required permission: ACTION_ENTITY`
- **Check:** User has required role
- **Check:** Role has required permission
- **Solution:** Assign permission to user's role

### GraphQL Errors

**Error:** `User is not authenticated`
- **Solution:** Add Authorization header with valid JWT token

**Error:** `Field 'xyz' doesn't exist on type 'ABC'`
- **Solution:** Check schema definition, field might be renamed or removed

**Error:** `Cannot return null for non-nullable field`
- **Solution:** Ensure resolver returns required fields or make field optional

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`
- **Solution:** Run from project root, not from subdirectory
- **Solution:** Activate virtual environment

**Error:** `ImportError: cannot import name 'X'`
- **Solution:** Check circular imports
- **Solution:** Verify model/schema is properly exported in `__init__.py`

---

## Deployment

### Pre-Deployment Checklist

- [ ] All migrations applied and tested
- [ ] Environment variables configured (.env)
- [ ] Secret key changed from default
- [ ] Admin password changed from default
- [ ] Database backups configured
- [ ] HTTPS/TLS certificate obtained
- [ ] CORS settings configured for production domains
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Monitoring/alerting set up

### Docker Production Build

**Update `Dockerfile` for production:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Don't run as root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t python-pos:latest .
docker run -d -p 8000:8000 --env-file .env python-pos:latest
```

### Environment Variables (Production)

**Required:**
```env
DATABASE_URL=postgresql://user:password@db-host:5432/python_pos
JWT_SECRET_KEY=<generate-strong-random-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Optional:**
```env
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
LOG_LEVEL=INFO
SENTRY_DSN=<your-sentry-dsn>
```

### Reverse Proxy (Nginx Example)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Backup

**PostgreSQL backup:**
```bash
# Backup
pg_dump -U user -d python_pos > backup_$(date +%Y%m%d).sql

# Restore
psql -U user -d python_pos < backup_20260322.sql
```

### Health Checks

**TODO:** Implement health check endpoint
```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

---

## Related Documentation

- **Entity Reference:** [prompts/01-entity-reference.md](prompts/01-entity-reference.md)
- **Entity Creation Guide:** [prompts/02-entity-creation-guide.md](prompts/02-entity-creation-guide.md)
- **Auth & Permissions:** [prompts/03-auth-and-permissions.md](prompts/03-auth-and-permissions.md)
- **Code Templates:** [prompts/templates/entity-template.md](prompts/templates/entity-template.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Current TODO:** [TODO.md](TODO.md)

---

**For questions or issues not covered here, check the documentation files above or reach out to the development team.**
