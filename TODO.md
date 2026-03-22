# TODO

**Last Updated:** March 22, 2026

---

## High Priority

### Security & Configuration
- [ ] Move database credentials to environment variables (.env file)
  - Remove hardcoded credentials from `alembic.ini`
  - Remove default credentials from `database.py`
  - Add `.env.example` template file
  - Document required environment variables in README

- [ ] Implement password requirements
  - Minimum length (8+ characters)
  - Complexity rules (uppercase, lowercase, number, special char)
  - Validation on user creation and password update

- [ ] Add rate limiting to authentication endpoints
  - Prevent brute-force attacks on login
  - Consider library: `slowapi` or middleware

### Testing
- [ ] Add unit tests for critical business logic
  - Shift start/end validation
  - Product slot reading calculations
  - Permission checking logic

- [ ] Add integration tests for GraphQL resolvers
  - Authentication flow (login, token validation)
  - RBAC permission checks
  - Entity CRUD operations

### API Enhancements
- [ ] Add pagination to list queries
  - products, users, shifts, etc.
  - Support cursor-based or offset-based pagination
  - Document pagination pattern in entity creation guide

- [ ] Improve error handling and error messages
  - Consistent error format across all resolvers
  - User-friendly messages (not raw database errors)
  - Proper HTTP status codes

---

## Medium Priority

### Features
- [ ] Add filtering and sorting to list queries
  - Filter by date range, status, created_by
  - Sort by any field (created_at, name, etc.)
  - Use Strawberry input types for complex filters

- [ ] Implement file upload for images
  - Product images
  - Meter reading photos (currently just URLs)
  - Consider S3 or local storage strategy

- [ ] Add search functionality
  - Full-text search on product names
  - Search shifts by date or users
  - Consider PostgreSQL full-text search or Elasticsearch

- [ ] Sales reporting and analytics
  - Daily/weekly/monthly sales summaries
  - Product performance metrics
  - Shift revenue calculations

### Developer Experience
- [ ] Add Swagger/OpenAPI documentation
  - Auto-generated from GraphQL schema
  - Alternative for teams not familiar with GraphQL

- [ ] Improve logging
  - Structured logging (JSON format)
  - Log levels (DEBUG, INFO, WARNING, ERROR)
  - Request ID tracking for debugging

- [ ] Add database seeding for development
  - Sample products, templates, shifts
  - Test users with different roles
  - Make it easy to reset dev database

---

## Low Priority (Future Enhancements)

### Scalability
- [ ] Add caching layer with Redis
  - Cache user permissions
  - Cache product templates
  - Cache JWT token validation results

- [ ] Implement DataLoader pattern for GraphQL
  - Batch and cache database queries
  - Reduce N+1 query problems
  - Improve query performance

### Advanced Features
- [ ] GraphQL subscriptions for real-time updates
  - Notify when shift is started/ended
  - Live product updates
  - Real-time notifications

- [ ] Multi-tenant support
  - Separate data per organization
  - Tenant-specific configurations
  - Admin dashboard for tenant management

- [ ] Mobile app optimization
  - GraphQL query batching
  - Optimize payload sizes
  - Offline support considerations

- [ ] Internationalization (i18n)
  - Multi-language support
  - Currency formatting
  - Date/time localization

### Monitoring & Observability
- [ ] Add Application Performance Monitoring (APM)
  - Track slow queries
  - Monitor endpoint performance
  - Alert on errors/anomalies

- [ ] Add health check endpoints
  - Database connectivity check
  - System status endpoint
  - Kubernetes readiness/liveness probes

---

## Technical Debt

- [ ] Refactor session management
  - Currently calling `SessionLocal()` in every resolver
  - Consider dependency injection or context-based session
  - Ensure proper session cleanup (try/finally blocks)

- [ ] Standardize error patterns
  - Create custom exception classes
  - Centralized error handling
  - Consistent error codes

- [ ] Add type hints to all functions
  - Some older code may be missing type hints
  - Run mypy for type checking
  - Improve IDE autocomplete

- [ ] Document all environment variables
  - Create comprehensive .env.example
  - Document required vs optional variables
  - Add validation on startup

---

## Completed ✅

### Authentication & Authorization (March 2026)
- ✅ JWT-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Permission-based authorization system
- ✅ 40+ granular permissions
- ✅ 4 default roles (Admin, Manager, Cashier, Viewer)
- ✅ Bootstrap admin user on first run
- ✅ Seed permissions system
- ✅ Password hashing with bcrypt
- ✅ Token expiration and validation
- ✅ React Native compatible (token-based, no cookies)

### Core Entities (March 2026)
- ✅ User, Permission, Role, UserRole, RolePermission
- ✅ Product, ProductTemplate, ProductSlot, ProductSlotReading
- ✅ Shift, ShiftTemplate, ShiftUser
- ✅ Full audit trail (created_at, created_by, updated_at, updated_by)
- ✅ Soft delete pattern (deleted_at, deleted_by)

### Documentation (March 2026)
- ✅ Reorganized /prompts folder with sequential numbering
- ✅ Created comprehensive entity reference guide
- ✅ Created entity creation step-by-step guide
- ✅ Extracted code templates for easy reuse
- ✅ Created .ai/ folder structure for AI tool configs
- ✅ Created system architecture documentation
- ✅ Added Postman collections for all entities

---

## Notes

**Priority Definitions:**
- **High Priority**: Security issues, critical bugs, blockers for production
- **Medium Priority**: Important features, developer experience improvements
- **Low Priority**: Nice-to-have features, future optimizations

**Before Moving to Production:**
1. Complete all high-priority security items
2. Add comprehensive test coverage
3. Review and secure all environment variables
4. Set up monitoring and logging
5. Perform security audit
6. Load testing

**For Development Workflow:** See `DEV_WORKFLOW.md`  
**For Architecture:** See `docs/ARCHITECTURE.md`  
**For Entity Creation:** See `prompts/02-entity-creation-guide.md`