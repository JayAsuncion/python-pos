# FastAPI GraphQL App

This project is a skeleton web API built using the FastAPI framework, configured to run on Strawberry GraphQL, and utilizes SQLAlchemy as the ORM. It is designed to run with Uvicorn and is containerized using Docker.

## Project Structure

```
python-pos-fastapi-graphql-app
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── user.py
│   └── graphql
│       ├── __init__.py
│       ├── schema.py
│       ├── mutations/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   ├── product.py
│       │   └── ... (entity-specific mutations)
│       └── queries/
│           ├── __init__.py
│           ├── user.py
│           ├── product.py
│           └── ... (entity-specific queries)
├── alembic
│   ├── versions
│   └── env.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd fastapi-graphql-app
   ```

2. **Build the Docker image:**
   ```
   docker build -t fastapi-graphql-app .
   ```

3. **Run the application using Docker Compose:**
   ```
   docker-compose up
   ```

4. **Access the API:**
   The API will be available at `http://localhost:8000/graphql`.

## Usage Guidelines

- The application uses SQLAlchemy for ORM, and you can define your database models in the `app/models` directory.
- GraphQL queries and mutations are organized by entity in the `app/graphql` directory:
  - Each entity has its own mutations file in `app/graphql/mutations/{entity}.py`
  - Each entity has its own queries file in `app/graphql/queries/{entity}.py`
  - Mutations and queries are aggregated via class inheritance in `__init__.py` files
  - This structure keeps files maintainable (50-150 lines each) and easy to navigate
- Pydantic schemas for data validation and serialization can be found in the `app/schemas` directory.

## Dependencies

The project requires the following Python packages, which are listed in `requirements.txt`:

- FastAPI
- Strawberry GraphQL
- SQLAlchemy
- Uvicorn

## Local Setup Versions
1. Load virtual env
```
source python-pos-env-39/Scripts/activate
```

2. Python
```
python --version
# Python 3.9.13
```

3. PIP
```
pip --version
# pip 22.0.4 from E:\Git-Repos\python-pos\python-pos-env-39\lib\site-packages\pip (python 3.9)
# (python-pos-env-39)
```

## License

This project is licensed under the MIT License.