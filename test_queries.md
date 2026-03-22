# GraphQL API Testing Guide

⚠️ **Note:** This API requires JWT authentication for all operations except `login`.

---

## Quick Start

### 1. Access GraphQL Playground
Open your browser: **http://localhost:8000/graphql**

### 2. Login to Get Token
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

### 3. Set Authorization Header
In GraphQL Playground, click "HTTP HEADERS" at the bottom and add:
```json
{
  "Authorization": "Bearer <paste-your-token-here>"
}
```

**Token expires in 60 minutes.** Re-login if you get authentication errors.

---

## Common Queries

### Authentication

**Check your permissions:**
```graphql
query {
  myPermissions {
    code
    name
    description
  }
}
```

**Get your user info:**
```graphql
query {
  me {
    id
    username
    email
  }
}
```

**Check your roles:**
```graphql
query {
  myRoles {
    id
    name
    code
  }
}
```

---

### User Management

**List all users** (requires VIEW_USER permission):
```graphql
query {
  users {
    id
    username
    email
  }
}
```

**Get single user:**
```graphql
query {
  user(userId: 1) {
    id
    username
    email
    createdAt
  }
}
```

**Create user** (requires CREATE_USER permission):
```graphql
mutation {
  createUser(
    username: "cashier1"
    email: "cashier1@example.com"
    password: "password123"
  ) {
    id
    username
    email
  }
}
```

**Update user** (requires UPDATE_USER permission):
```graphql
mutation {
  updateUser(
    userId: 2
    email: "newemail@example.com"
  ) {
    id
    username
    email
    updatedAt
    updatedBy
  }
}
```

**Delete user** (requires DELETE_USER permission):
```graphql
mutation {
  deleteUser(userId: 2) {
    id
    username
    deletedAt
    deletedBy
  }
}
```

---

### Product Management

**List products:**
```graphql
query {
  products {
    id
    name
    costPrice
    sellingPrice
    createdAt
  }
}
```

**Create product:**
```graphql
mutation {
  createProduct(
    productTemplateId: 1
    name: "Premium Gasoline"
    costPrice: 45.50
    sellingPrice: 52.00
  ) {
    id
    name
    costPrice
    sellingPrice
  }
}
```

---

### Shift Operations

**List active shifts:**
```graphql
query {
  shifts {
    id
    shiftDate
    status
    startedAt
    users {
      id
      username
    }
  }
}
```

**Start a shift:**
```graphql
mutation {
  startShift(
    shiftTemplateId: 1
    shiftDate: "2026-03-22"
    userIds: [1, 2]
    startReadings: [
      { productSlotId: 1, reading: 1000, imageUrl: "https://example.com/photo1.jpg" }
      { productSlotId: 2, reading: 2000, imageUrl: "https://example.com/photo2.jpg" }
    ]
  ) {
    id
    status
    startedAt
    startedBy
  }
}
```

**End a shift:**
```graphql
mutation {
  endShift(
    shiftId: 1
    endReadings: [
      { productSlotId: 1, reading: 1500, imageUrl: "https://example.com/photo3.jpg" }
      { productSlotId: 2, reading: 2300, imageUrl: "https://example.com/photo4.jpg" }
    ]
  ) {
    id
    status
    endedAt
    endedBy
  }
}
```

---

## Testing with Postman

**Recommended:** Use pre-built Postman collections in `testing/postman/`:

- `Authentication and RBAC.postman_collection.json`
- `Product.postman_collection.json`
- `Shift.postman_collection.json`
- `User.postman_collection.json`
- And more...

**Setup:**
1. Import collection into Postman
2. Set environment variable: `baseUrl = http://localhost:8000`
3. Run login request → token auto-saved
4. All other requests use saved token automatically

---

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(username: \"admin\", password: \"admin\") { token } }"
  }'
```

### Query with Authentication
```bash
# Replace <TOKEN> with actual token from login
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "query": "{ products { id name costPrice sellingPrice } }"
  }'
```

### Create Product
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "query": "mutation { createProduct(productTemplateId: 1, name: \"Test Product\", costPrice: 10.00, sellingPrice: 15.00) { id name } }"
  }'
```

---

## Common Errors

### "User is not authenticated"
- **Cause:** No token provided or invalid token
- **Solution:** Login again and set Authorization header

### "Could not validate credentials"
- **Cause:** Token expired (60min limit)
- **Solution:** Run login mutation to get new token

### "User does not have required permission: VIEW_PRODUCT"
- **Cause:** Your user/role lacks the required permission
- **Solution:** Admin must assign permission to your role

### "Cannot return null for non-nullable field"
- **Cause:** Required field not provided in mutation
- **Solution:** Check GraphQL schema for required fields

---

## Permission Requirements

**Common permissions needed for operations:**

| Operation | Required Permission |
|-----------|-------------------|
| Login | None (public) |
| View Products | VIEW_PRODUCT |
| Create Product | CREATE_PRODUCT |
| Update Product | UPDATE_PRODUCT |
| Delete Product | DELETE_PRODUCT |
| Start Shift | START_SHIFT |
| End Shift | END_SHIFT |
| View Users | VIEW_USER |
| Create User | CREATE_USER |

**Full permission list:** See [prompts/03-auth-and-permissions.md](prompts/03-auth-and-permissions.md)

---

## For More Information

- **Entity Reference:** [prompts/01-entity-reference.md](prompts/01-entity-reference.md)
- **Auth Details:** [prompts/03-auth-and-permissions.md](prompts/03-auth-and-permissions.md)
- **Development Guide:** [DEV_WORKFLOW.md](DEV_WORKFLOW.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
