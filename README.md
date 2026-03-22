# Python POS - FastAPI GraphQL API

**A modern point-of-sale API with comprehensive authentication and role-based access control**

---

## Overview

Python POS is a production-ready FastAPI GraphQL API for point-of-sale operations, featuring:

- 🔐 **JWT Authentication** with Role-Based Access Control (RBAC)
- 📊 **GraphQL API** powered by Strawberry
- 🗄️ **PostgreSQL Database** with SQLAlchemy ORM
- 🔄 **Database Migrations** via Alembic
- 🐳 **Docker Support** for easy deployment
- 📝 **Full Audit Trails** on all entities
- 🛡️ **Permission-Based Authorization** (40+ granular permissions)

---

## Quick Start

### Using Docker (Recommended)
```bash
docker-compose up
```

### Local Development
```bash
# Setup (detailed instructions in DEV_WORKFLOW.md)
python -m venv python-pos-env-39
source python-pos-env-39/Scripts/activate  # Windows: python-pos-env-39\Scripts\activate
pip install -r requirements.txt

# Initialize database
alembic upgrade head
python -m app.auth.bootstrap_admin
python -m app.auth.seed_permissions

# Run server
uvicorn app.main:app --reload
```

**API Access:** http://localhost:8000/graphql

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin` (⚠️ change immediately!)

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.128.0 |
| GraphQL | Strawberry | 0.283.3 |
| Database | PostgreSQL | Latest |
| ORM | SQLAlchemy | 2.0.46 |
| Migrations | Alembic | 1.16.5 |
| Auth | JWT (python-jose) | Latest |
| Python | Python 3 | 3.9+ |

---

## Project Structure

```
python-pos/
├── app/                          # Application code
│   ├── main.py                   # FastAPI app entry point
│   ├── database.py               # Database connection
│   ├── context.py                # GraphQL context (auth)
│   ├── models/                   # SQLAlchemy models (12 entities)
│   ├── schemas/                  # Strawberry GraphQL types
│   ├── graphql/                  # GraphQL resolvers
│   │   ├── schema.py             # Main GraphQL schema
│   │   ├── mutations/            # Entity-specific mutations
│   │   └── queries/              # Entity-specific queries
│   └── auth/                     # Authentication & RBAC
│       ├── jwt.py                # JWT token handling
│       ├── permissions.py        # Permission checks
│       ├── bootstrap_admin.py    # Create first admin user
│       └── seed_permissions.py   # Seed permissions
├── alembic/                      # Database migrations
│   └── versions/                 # Migration files
├── docs/                         # Documentation
│   └── ARCHITECTURE.md           # System architecture
├── prompts/                      # AI assistant context
│   ├── 00-README.md              # Start here
│   ├── 01-entity-reference.md    # Entity documentation
│   ├── 02-entity-creation-guide.md  # How to create entities
│   ├── 03-auth-and-permissions.md   # Auth reference
│   └── templates/                # Code templates
├── testing/postman/              # API test collections
├── .ai/                          # AI tool configurations
├── docker-compose.yml            # Docker orchestration
├── requirements.txt              # Python dependencies
└── DEV_WORKFLOW.md               # Development guide

**Full architecture documentation:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
```

---

## Core Features

### Authentication & Authorization
- **JWT tokens** with 60-minute expiration
- **40+ granular permissions** (CREATE_USER, VIEW_PRODUCT, etc.)
- **4 default roles:** Admin, Manager, Cashier, Viewer
- **Permission-based access control** on every GraphQL operation
- **Bcrypt password hashing** for security

### Entities (12 Total)
- **User Management:** Users, Roles, Permissions
- **Product Management:** Products, Product Templates, Product Slots
- **Shift Management:** Shifts, Shift Templates, Shift Assignments
- **Inventory Tracking:** Product Slot Readings (meter snapshots)

### Data Integrity
- **Full Audit Trails:** created_at, created_by, updated_at, updated_by
- **Soft Delete:** Records marked as deleted, never removed
- **Foreign Key Constraints:** Enforced at database level
- **Transaction Safety:** ACID compliance via PostgreSQL

---

## Documentation

| Document | Purpose |
|----------|---------|
| [DEV_WORKFLOW.md](DEV_WORKFLOW.md) | **Setup, development, testing, deployment** |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and design |
| [prompts/00-README.md](prompts/00-README.md) | AI assistant entry point |
| [prompts/01-entity-reference.md](prompts/01-entity-reference.md) | Complete entity documentation |
| [prompts/02-entity-creation-guide.md](prompts/02-entity-creation-guide.md) | How to create new entities |
| [prompts/03-auth-and-permissions.md](prompts/03-auth-and-permissions.md) | Authentication & RBAC details |
| [TODO.md](TODO.md) | Current priorities and roadmap |

---

## API Testing

### GraphQL Playground
Open http://localhost:8000/graphql in your browser for interactive API exploration.

### Postman Collections
Pre-built API test collections in [testing/postman/](testing/postman/):
- Authentication and RBAC
- Product Management
- Shift Operations
- User Management
- And more...

### Example: Login and Query
```graphql
# 1. Login
mutation {
  login(username: "admin", password: "admin") {
    token
    user { id username }
  }
}

# 2. Use token in HTTP Headers:
# { "Authorization": "Bearer <your-token>" }

# 3. Query with authentication
query {
  products {
    id
    name
    costPrice
    sellingPrice
  }
}
```

**Recommended:** Use Postman collections in [testing/postman/](testing/postman/) for comprehensive API testing with auto-token management.

---

## Common Tasks

### Create a New Entity
See detailed guide: [prompts/02-entity-creation-guide.md](prompts/02-entity-creation-guide.md)

Quick steps:
1. Create model in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Apply migration: `alembic upgrade head`
4. Create GraphQL schema, mutations, queries
5. Add permissions and seed
6. Update documentation

### Database Migrations
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# View status
alembic current

# Rollback one version
alembic downgrade -1
```

**Full migration guide:** [DEV_WORKFLOW.md#database-migrations](DEV_WORKFLOW.md#database-migrations)

### Add New Permission
```bash
# 1. Edit app/auth/seed_permissions.py
# 2. Run seeding
python -m app.auth.seed_permissions
# 3. Use in resolvers: require_permission(info, "NEW_PERMISSION")
```

---

## Development Environment

**Python Version:** 3.9.13  
**Virtual Environment:** `python-pos-env-39`  
**Package Manager:** pip 22.0.4

**For complete setup instructions:** [DEV_WORKFLOW.md#initial-setup](DEV_WORKFLOW.md#initial-setup)

---

## Deployment

### Production Checklist
- [ ] Change default admin password
- [ ] Configure environment variables (.env)
- [ ] Set strong JWT_SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for production domains
- [ ] Set up database backups
- [ ] Configure monitoring and logging

**Detailed deployment guide:** [DEV_WORKFLOW.md#deployment](DEV_WORKFLOW.md#deployment)

---

## Architecture Highlights

### GraphQL Organization
- **Entity-based structure** (not feature-based)
- One file per entity for mutations and queries
- Keeps files small and maintainable (50-150 lines)
- Easy to locate and modify entity-specific logic

### Security Layers
1. **Network:** HTTPS/TLS encryption
2. **Authentication:** JWT token validation
3. **Authorization:** Permission-based access control
4. **Data Protection:** Bcrypt hashing, input validation, parameterized queries
5. **Audit:** Full trails of who did what when

### Scalability
- Stateless JWT design (horizontal scaling ready)
- Database connection pooling
- GraphQL field-level resolution (no over-fetching)

**Full architecture details:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## Contributing

When contributing to this project:
1. Follow the entity creation guide for consistency
2. Implement RBAC on all new operations
3. Add appropriate audit fields
4. Update documentation (mandatory)
5. Test with Postman collections

---

## Support & Resources

- **Issues:** Check [TODO.md](TODO.md) for known issues and planned features
- **Architecture Questions:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Development Help:** Refer to [DEV_WORKFLOW.md](DEV_WORKFLOW.md)
- **Entity Reference:** Check [prompts/01-entity-reference.md](prompts/01-entity-reference.md)

---

## License

This project is licensed under the MIT License.