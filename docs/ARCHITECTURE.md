# System Architecture

**Last Updated:** March 22, 2026

---

## Overview

Python POS is a FastAPI-based GraphQL API for point-of-sale operations with comprehensive role-based access control (RBAC).

**Primary Use Cases:**
- Shift management with user assignments
- Product and inventory tracking
- Meter reading snapshots per shift
- Sales calculation and reporting
- Multi-user authentication and authorization

---

## Technology Stack

### Backend Framework
- **FastAPI** 0.128.0 - Modern Python web framework
- **Strawberry GraphQL** 0.283.3 - GraphQL library for Python
- **Python** 3.9+ - Programming language

### Database
- **PostgreSQL** - Primary database
- **SQLAlchemy** 2.0.46 - ORM for database operations
- **Alembic** 1.16.5 - Database migrations

### Authentication & Security
- **JWT** (python-jose) - Token-based authentication
- **Bcrypt** (passlib) - Password hashing
- **Custom RBAC** - Permission-based authorization

### Development & Deployment
- **Docker** - Containerization
- **docker-compose** - Multi-container orchestration
- **Uvicorn** - ASGI server

---

## Architecture Layers

### 1. API Layer (`app/main.py`)

**Responsibilities:**
- Initialize FastAPI application
- Register GraphQL router with custom context getter
- Handle HTTP requests/responses

**Key Components:**
```python
app = FastAPI()
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
```

**Context Getter:**
- Extracts JWT token from Authorization header
- Validates token and loads authenticated user
- Provides user to GraphQL resolvers via context

---

### 2. GraphQL Layer (`app/graphql/`)

**Organization:** Entity-based (not feature-based)

**Structure:**
```
app/graphql/
├── schema.py                 # Main GraphQL schema
├── mutations/
│   ├── __init__.py          # Aggregates all mutations
│   ├── auth.py              # Login, password reset
│   ├── user.py              # User CRUD
│   ├── product.py           # Product CRUD
│   ├── shift.py             # Start/end shift
│   └── {entity}.py          # One file per entity
└── queries/
    ├── __init__.py          # Aggregates all queries
    ├── auth.py              # me, myPermissions, myRoles
    ├── user.py              # Users list/single
    ├── product.py           # Products list/single
    └── {entity}.py          # One file per entity
```

**Benefits:**
- Files are 50-150 lines (manageable)
- Easy to locate entity-specific logic
- Reduces merge conflicts
- Consistent with models/schemas structure

---

### 3. Business Logic Layer (GraphQL Resolvers)

**Responsibilities:**
- Validate input parameters
- Check permissions via `require_permission()`
- Execute business logic
- Manage database transactions
- Return GraphQL types

**Pattern:**
```python
@strawberry.mutation
def create_product(self, info: strawberry.types.Info, name: str, ...) -> ProductType:
    # 1. Check permission
    user = require_permission(info, "CREATE_PRODUCT")
    
    # 2. Open database session
    db = SessionLocal()
    
    # 3. Validate business rules
    if not valid:
        db.close()
        raise ValueError("Error message")
    
    # 4. Execute operation
    product = ProductModel(name=name, created_by=user.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # 5. Convert to GraphQL type
    result = ProductType(...)
    
    # 6. Clean up and return
    db.close()
    return result
```

---

### 4. Data Layer (`app/models/`)

**Responsibilities:**
- Define database schema via SQLAlchemy ORM
- Define relationships between entities
- Provide database table structure

**Audit Trail Patterns:**

1. **No Audit** (User)
   - Just basic fields, no change tracking

2. **Soft Delete Only** (ProductTemplate, Permission, Role)
   - `deleted_at`, `deleted_by`
   - Records marked deleted but not removed

3. **Full Audit Trail** (Product, Shift, most entities)
   - `deleted_at`, `deleted_by`
   - `created_at`, `created_by`
   - `updated_at`, `updated_by`
   - Complete history of who did what when

**Example Full Audit Entity:**
```python
class Product(Base):
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Audit fields
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
```

---

### 5. Database Layer (PostgreSQL)

**Features:**
- ACID compliance
- Foreign key constraints
- Timezone-aware timestamps
- Numeric precision for money (15,6)
- Indexes on primary keys and unique fields

**Migration Management:**
- Alembic tracks schema changes
- Version control for database schema
- Automatic migration generation from model changes

---

## Authentication & Authorization Flow

### Authentication (JWT)

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Server  │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  1. login(username, password)               │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                    2. Validate credentials   │
     │                       (bcrypt.verify)        │
     │                              │               │
     │                    3. Generate JWT token     │
     │                       (60min expiry)         │
     │                              │               │
     │  4. Return token + user info                 │
     │<─────────────────────────────────────────────┤
     │                                              │
     │  5. Store token                              │
     ├──┐                                           │
     │  │                                           │
     │<─┘                                           │
     │                                              │
     │  6. Subsequent requests with token           │
     │     Authorization: Bearer <token>            │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                    7. Validate token         │
     │                       (decode JWT)           │
     │                              │               │
     │                    8. Load user              │
     │                       (from database)        │
     │                              │               │
     │  9. Return protected data                    │
     │<─────────────────────────────────────────────┤
     │                                              │
```

**Token Structure:**
```json
{
  "sub": "username",
  "user_id": 1,
  "exp": 1742832000,
  "iat": 1742828400
}
```

**Configuration:**
- Algorithm: HS256
- Expiration: 60 minutes
- Secret: Environment variable (JWT_SECRET_KEY)

---

### Authorization (RBAC)

**Permission-Based Model** (not role-based):

```
User
  │
  ├──> UserRole ──> Role ──> RolePermission ──> Permission
  │       (many)    (code)        (many)          (code)
  │
  └──> Effective Permissions Set
```

**Permission Check Process:**
1. Extract JWT token from request
2. Decode token → get user_id
3. Load user from database
4. Query: User → UserRole → Role → RolePermission → Permission
5. Build set of permission codes
6. Check if required permission exists
7. Allow/deny operation

**Implementation:**
```python
# In every protected resolver:
user = require_permission(info, "CREATE_PRODUCT")
# Raises ValueError if:
# - No token provided
# - Invalid/expired token  
# - User doesn't have CREATE_PRODUCT permission
```

**Benefits:**
- Fine-grained access control
- Flexible role composition
- Easy to add/remove permissions
- Audit trail of permission changes
- No code changes needed for new permissions

---

## Data Flow Examples

### Example 1: Start Shift

**User Action:** Cashier starts morning shift

**Flow:**
```
1. Client sends startShift mutation with:
   - shift_template_id
   - shift_date
   - user_ids (who's working)
   - start readings & photos for all slots

2. Server validates JWT token
   ├─> Decodes token
   ├─> Loads user
   └─> Context contains authenticated user

3. Resolver checks permission
   └─> require_permission(info, "START_SHIFT")
       ├─> Traverses User → UserRole → Role → RolePermission → Permission
       └─> Verifies user has START_SHIFT permission

4. Business validation
   ├─> No active shift exists for this template
   ├─> All product slots have assigned products
   └─> Start reading photos provided

5. Database operations (transactional)
   ├─> Create Shift record (status: "active", started_by: user.id)
   ├─> Create ShiftUser records (one per selected user)
   └─> Create ProductSlotReading records (one per slot)
       ├─> Snapshot: product_id, cost_price, selling_price
       ├─> Record: start_reading, start_reading_image_url
       └─> Leave NULL: end_reading, end_reading_image_url

6. Return shift data to client
```

**Created Records:**
- 1 Shift
- N ShiftUser (N = number of workers)
- M ProductSlotReading (M = number of product slots)

---

### Example 2: Query Products

**User Action:** Manager views product list

**Flow:**
```
1. Client sends products query with token in header

2. Context getter extracts token, loads user

3. Resolver checks permission
   └─> require_permission(info, "VIEW_PRODUCT")

4. Database query
   └─> SELECT * FROM product WHERE deleted_at IS NULL

5. Convert to GraphQL types
   └─> Map ProductModel → ProductType (for each record)

6. Return list to client
```

**Note:** Soft-deleted products are filtered out automatically.

---

## Deployment Architecture

### Development Setup

```
┌──────────────────────────────────────────┐
│ Docker Compose                           │
│                                          │
│  ┌────────────────┐   ┌──────────────┐  │
│  │   FastAPI      │   │  PostgreSQL  │  │
│  │   Container    │──>│  Container   │  │
│  │  (port 8000)   │   │  (port 5432) │  │
│  └────────────────┘   └──────────────┘  │
│         │                                │
│         │ GraphQL Playground             │
│         v                                │
│  http://localhost:8000/graphql          │
└──────────────────────────────────────────┘
         │
         v
┌────────────────────┐
│  Postman / Client  │
│  (GraphQL requests)│
└────────────────────┘
```

### Production Considerations

**Recommended:**
- Load balancer (nginx/traefik) in front of FastAPI
- PostgreSQL cluster or managed database (RDS/Cloud SQL)
- Redis for caching (optional)
- Separate secrets management (AWS Secrets Manager, Vault)
- Horizontal scaling of FastAPI containers
- Database connection pooling (already configured in SQLAlchemy)

---

## Security Architecture

### Security Layers

```
Layer 1: Network
  └─> HTTPS/TLS encryption

Layer 2: Authentication
  └─> JWT token validation

Layer 3: Authorization
  └─> Permission-based access control

Layer 4: Data Protection
  ├─> Bcrypt password hashing
  ├─> Input validation
  └─> Parameterized queries (SQL injection prevention)

Layer 5: Audit
  ├─> Full audit trails (who/when)
  └─> Soft delete (data preservation)
```

### Password Security

**Hashing:**
- Algorithm: bcrypt (via passlib)
- Salt: Automatically generated per password
- Rounds: Default (sufficient for production)

**Legacy Detection:**
- Login checks if password is plaintext vs hashed
- Flags `requiresPasswordReset: true` for plaintext
- Forces user to reset before normal operations

**Best Practices:**
- Never return passwords in API responses
- Never log passwords (even hashed)
- Constant-time comparison (via bcrypt.verify)
- Minimum password requirements (implementation TBD)

---

## Scalability Considerations

### Current Architecture Supports:

**Stateless Design:**
- JWT tokens (no server-side session storage)
- Any FastAPI instance can handle any request
- Easy horizontal scaling

**Database Connection Pooling:**
- SQLAlchemy manages connection pool
- Configurable pool size
- Connection reuse

**GraphQL Efficiency:**
- Field-level resolution (no over-fetching)
- Single endpoint (no route management)
- Batch query support (client-side)

### Bottlenecks to Monitor:

1. **Database Connections**
   - Solution: Increase pool size, add read replicas

2. **JWT Token Validation**
   - Solution: Add Redis cache for token validation

3. **Permission Lookups**
   - Solution: Cache user permissions for session duration

4. **Large Product Catalogs**
   - Solution: Add pagination, implement DataLoader pattern

---

## Entity Summary

**Total Entities:** 12

### Master Data (Configuration)
- User - System users
- Permission - Access control permissions
- Role - Permission groups
- ProductTemplate - Product prototypes
- ShiftTemplate - Shift schedules

### Operational (Transactional)
- Product - Actual products with pricing
- ProductSlot - Physical locations
- Shift - Shift instances
- ProductSlotReading - Meter readings

### Junction (Many-to-Many)
- UserRole - User ↔ Role assignments
- RolePermission - Role ↔ Permission grants
- ShiftUser - Shift ↔ User assignments

**For detailed entity documentation, see:** `prompts/01-entity-reference.md`

---

## Development Workflow

### Entity Creation
1. Read existing entity documentation
2. Create model, schema, mutations, queries
3. Implement RBAC on all resolvers
4. Add permissions and seed
5. Generate and apply migration
6. **Update documentation** (mandatory)
7. Test with authentication

**Detailed guide:** `prompts/02-entity-creation-guide.md`

### Database Changes
1. Modify SQLAlchemy models
2. Generate migration: `alembic revision --autogenerate`
3. Review generated migration
4. Apply: `alembic upgrade head`
5. Update documentation if schema changed

### Adding Permissions
1. Add to `app/auth/seed_permissions.py`
2. Run: `python -m app.auth.seed_permissions`
3. Assign to roles (via seed file or GraphQL)
4. Use in resolvers: `require_permission(info, "NEW_PERMISSION")`

---

## Monitoring & Observability

**Current Implementation:**
- FastAPI logs (stdout)
- Database query logs (SQLAlchemy echo mode)
- GraphQL errors (Strawberry default)

**Recommended Additions:**
- Structured logging (JSON format)
- Application Performance Monitoring (APM)
- Database query performance tracking
- Authentication failure monitoring
- Permission denial tracking

---

## API Documentation

**GraphQL Introspection:**
- Built-in schema documentation
- Available at `/graphql` playground
- Auto-generated from Strawberry types

**Postman Collections:**
- Located in `testing/postman/`
- One collection per entity
- Includes authentication examples

**For permission requirements:** See `prompts/03-auth-and-permissions.md`

---

## Future Enhancements

**Potential Improvements:**
1. GraphQL subscriptions for real-time updates
2. File upload for product images (S3 integration)
3. Advanced reporting and analytics
4. Multi-tenant support
5. Mobile app API optimization
6. Caching layer (Redis)
7. Rate limiting
8. API versioning

---

## Related Documentation

- **Entity Reference:** `prompts/01-entity-reference.md` - All entities, relationships, business rules
- **Entity Creation:** `prompts/02-entity-creation-guide.md` - How to create new entities
- **Auth & Permissions:** `prompts/03-auth-and-permissions.md` - Authentication and authorization details
- **Development Workflow:** `DEV_WORKFLOW.md` - How to run, develop, deploy
- **API Examples:** `testing/postman/` - Postman collection examples

---

**For questions about architecture decisions or design patterns, refer to this document or ask the development team.**
