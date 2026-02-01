# GraphQL API Testing Guide

## Access the GraphQL Playground
Open your browser and go to: **http://localhost:8000/graphql**

---

## Example Queries and Mutations

### 1. Get all users
```graphql
query {
  users {
    id
    username
    email
    firstName
    lastName
  }
}
```

### 2. Create a new user
```graphql
mutation {
  createUser(
    username: "johndoe"
    email: "john@example.com"
    firstName: "John"
    lastName: "Doe"
    hashedPassword: "hashed_password_here"
  ) {
    id
    username
    email
    firstName
    lastName
  }
}
```

### 3. Update a user
```graphql
mutation {
  updateUser(
    userId: 1
    firstName: "Jane"
    lastName: "Smith"
  ) {
    id
    username
    email
    firstName
    lastName
  }
}
```

### 4. Delete a user
```graphql
mutation {
  deleteUser(userId: 1) {
    id
    username
    email
    firstName
    lastName
  }
}
```

---

## Testing with cURL (Command Line)

### Check API is running
```bash
curl http://localhost:8000/
```

### Get all users
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ users { id username email firstName lastName } }"}'
```

### Create a user
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createUser(username: \"johndoe\", email: \"john@example.com\", firstName: \"John\", lastName: \"Doe\", hashedPassword: \"password123\") { id username email firstName lastName } }"}'
```

---

## Docker Commands

### View container logs
```bash
docker logs python-pos-web-1
```

### Restart the web container
```bash
docker restart python-pos-web-1
```

### Stop all containers
```bash
docker-compose down
```

### Start all containers
```bash
docker-compose up -d
```
