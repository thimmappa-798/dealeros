# DealerOS - Multi-Tenant Reconciliation Platform



DealerOS is a full-stack reconciliation platform that compares financial records from two different systems, identifies discrepancies, and provides an organization-specific dashboard with natural-language Q&A.



The application supports multiple organizations using a shared database while enforcing tenant-level data isolation through PostgreSQL Row-Level Security (RLS).



## Features



- Import records from System A and System B CSV files.

- Normalize inconsistent record references before reconciliation.

- Detect missing records, duplicate entries, location mismatches, date mismatches, invalid amounts, and value mismatches.

- Provide actionable reconciliation exceptions with supporting evidence.

- Filter exceptions by reason code and location.

- Secure authentication using JWT stored in an HttpOnly cookie.

- Enforce multi-tenant isolation at the PostgreSQL database level.

- Ask natural-language questions about reconciliation data.

- Provide source citations for grounded Q&A responses.

- Refuse unsupported questions instead of generating unsupported answers.



## Technology Stack



### Backend

- Python

- FastAPI

- SQLAlchemy

- PostgreSQL

- Alembic

- Pydantic

- Pytest

- Ollama (Qwen 2.5 3B)



### Frontend

- React

- Vite

- JavaScript

- Axios

- React Router



## Project Structure



```text

dealeros/

â”‚

â”œâ”€â”€ backend/

â”‚   â”œâ”€â”€ app/

â”‚   â”‚   â”œâ”€â”€ data/

â”‚   â”‚   â”œâ”€â”€ models/

â”‚   â”‚   â”œâ”€â”€ routers/

â”‚   â”‚   â”œâ”€â”€ schemas/

â”‚   â”‚   â”œâ”€â”€ service/

â”‚   â”‚   â”œâ”€â”€ database.py

â”‚   â”‚   â”œâ”€â”€ dependencies.py

â”‚   â”‚   â””â”€â”€ main.py

â”‚   â”‚

â”‚   â”œâ”€â”€ migrations/

â”‚   â”œâ”€â”€ tests/

â”‚   â”œâ”€â”€ requirements.txt

â”‚   â”œâ”€â”€ import\_source\_records.py

â”‚   â”œâ”€â”€ seed\_organizations\_locations.py

â”‚   â”œâ”€â”€ seed\_demo\_users.py

â”‚   â”œâ”€â”€ run\_reconciliation.py

â”‚   â””â”€â”€ .env

â”‚

â”œâ”€â”€ frontend/

â”‚   â”œâ”€â”€ src/

â”‚   â”œâ”€â”€ public/

â”‚   â”œâ”€â”€ package.json

â”‚   â””â”€â”€ README.md

â”‚

â”œâ”€â”€ .gitignore

â”œâ”€â”€ README.md

â””â”€â”€ DECISIONS.md

```



## Architecture



The application follows a React frontend and FastAPI backend architecture.



1\. Users authenticate through the React application.

2\. FastAPI validates credentials and creates a JWT.

3\. The JWT is stored in an HttpOnly cookie.

4\. Backend dependencies validate the token and identify the organization.

5\. PostgreSQL receives the organization context for the current transaction.

6\. Row-Level Security restricts database access to that organization.

7\. The reconciliation service compares records and generates exceptions.

8\. The Q&A service uses Ollama to identify supported question intent and retrieves the actual answer from PostgreSQL.



## Multi-Tenant Security



DealerOS uses a shared PostgreSQL database with organization-level data isolation.



Tenant-owned tables contain an `organization\_id` column.



PostgreSQL Row-Level Security policies use the transaction-local setting:



```sql

SELECT set\_config('app.current\_org', '1', true);

```



The RLS policies enforce:



- `USING`: Controls which existing rows an organization can read or modify.

- `WITH CHECK`: Controls which rows an organization can insert or update.



A dedicated PostgreSQL application role, `dealeros\_app`, is used for normal application operations. It does not have superuser or RLS-bypass privileges.



A separate administrative connection is used for migrations and trusted administrative scripts.



## Prerequisites



Install the following before running the project:



- Python and pip

- Node.js and npm

- PostgreSQL

- Git

- Ollama



## Backend Setup



### 1. Navigate to the backend



```powershell

cd backend

```



### 2. Create and activate a virtual environment



```powershell

python -m venv venv

.\\venv\\Scripts\\Activate.ps1

```



### 3. Install dependencies



```powershell

pip install -r requirements.txt

```



### 4. Configure environment variables



Create a `.env` file inside the backend directory.



Use the following variable names and replace the placeholders with your own local configuration:



```env

ADMIN\_DATABASE\_URL=postgresql+psycopg://postgres:YOUR\_ADMIN\_PASSWORD@localhost:5432/dealeros

APP\_DATABASE\_URL=postgresql+psycopg://dealeros\_app:YOUR\_APP\_PASSWORD@localhost:5432/dealeros

JWT\_SECRET\_KEY=YOUR\_SECURE\_RANDOM\_SECRET

ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

```



Never commit `.env` or expose database passwords and JWT secrets.



### 5. Configure PostgreSQL roles and permissions



Create the `dealeros` database and a restricted application role.



The application role should have:



- LOGIN

- NOSUPERUSER

- NOBYPASSRLS

- NOCREATEDB

- NOCREATEROLE



Grant the application role the required database connection, schema, table, and sequence permissions.



Apply the appropriate table and sequence grants after the initial schema migrations have created the tables.



Do not use the PostgreSQL superuser as the application's database connection.



### 6. Apply initial migrations



Run the migrations up to the reconciliation-exceptions migration first:



```powershell

python -m alembic upgrade 04b196484901

```



### 7. Seed organizations and locations



```powershell

python seed\_organizations\_locations.py

```



### 8. Import source records



```powershell

python import\_source\_records.py

```



### 9. Apply remaining migrations



```powershell

python -m alembic upgrade head

```



This enables Row-Level Security and installs the secure authentication database function.



### 10. Create demo users



```powershell

python seed\_demo\_users.py

```



The script prompts for passwords for the demo accounts. Passwords are hashed before being stored.



Demo account emails:



- `admin-a@dealeros.local` - ORG-A

- `admin-b@dealeros.local` - ORG-B



Use the passwords configured during user creation.



### 11. Run reconciliation



```powershell

python run\_reconciliation.py

```



The reconciliation process compares the source records and creates organization-specific exceptions.



### 12. Start the backend



```powershell

python -m uvicorn app.main:app --reload

```



Backend URL:



http://localhost:8000



Swagger API documentation:



http://localhost:8000/docs



## Frontend Setup



Open another terminal.



### 1. Navigate to frontend



```powershell

cd frontend

```



### 2. Install dependencies



```powershell

npm install

```



### 3. Start React



```powershell

npm run dev

```



Frontend URL:



http://localhost:5173



## AI-Powered Natural Language Q&A



DealerOS uses a locally running Ollama model (`qwen2.5:3b`) to identify the intent of a user's question.



The model does not generate database facts directly.



Instead:



1\. The model identifies a supported question intent.

2\. The backend validates the intent.

3\. The backend queries PostgreSQL using the authenticated organization's context.

4\. The answer is calculated from actual reconciliation records.

5\. Supporting exception identifiers and source references are returned.

6\. Unsupported questions are refused.



### Start Ollama



Install Ollama and download the model:



```powershell

ollama pull qwen2.5:3b

```



Start the Ollama service:



```powershell

ollama serve

```



Ollama API:



http://localhost:11434



### Q&A API



```http

POST /qa/ask

```



Example request:



```json

{

&#x20; "question": "How many value mismatches are there?"

}

```



The response includes:



- Answer

- Grounded status

- Supporting exception IDs

- Normalized source references

- Source record identifiers



The Q&A endpoint refuses unsupported questions instead of guessing.



## API Endpoints



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | API status |

| GET | `/health` | Health check |

| POST | `/auth/login` | Authenticate user |

| POST | `/auth/logout` | Logout user |

| GET | `/locations/` | Get organization locations |

| GET | `/exceptions/` | Get reconciliation exceptions |

| POST | `/qa/ask` | Ask reconciliation questions |



The exceptions endpoint supports optional filters:



- `reason\_code`

- `location\_id`



Protected endpoints require authentication.



## Running Tests



Activate the backend virtual environment and navigate to the backend directory.



Run:



```powershell

python -m pytest -v

```



The current automated tests cover:



- Requests without tenant context.

- Organization-level row visibility.

- Cross-organization insert rejection.

- Grounded Q&A responses and source citations.

- Unsupported-question refusal.

- Ollama connection failure handling.



## Security Considerations



- Use a dedicated restricted PostgreSQL application role.

- Enforce tenant isolation using PostgreSQL RLS.

- Store JWTs in HttpOnly cookies.

- Never expose password hashes or secrets through APIs.

- Keep `.env` outside version control.

- Configure secure cookies and appropriate CSRF protection before production deployment.

- Use HTTPS and `Secure=True` cookies in production.



## Future Improvements



- Expand automated reconciliation test coverage.

- Add stronger Q&A intent validation and broader question support.

- Add production-ready CSRF protection.

- Improve operational monitoring and logging.

- Add automated deployment pipelines.




## Docker Setup

### Prerequisites
- Docker Desktop
- Docker Compose
- Ollama running on the host machine (for AI Q&A)

### First-time setup

1. Create the root `.env` file with:
   - POSTGRES_PASSWORD
   - APP_DB_PASSWORD

2. Build and start all services:

   docker compose up --build -d

3. Apply initial database migrations:

   docker compose exec backend python -m alembic upgrade 04b196484901

4. Seed organizations and locations:

   docker compose exec backend python seed_organizations_locations.py

5. Import source records:

   docker compose exec backend python import_source_records.py

6. Apply remaining migrations and RLS policies:

   docker compose exec backend python -m alembic upgrade head

7. Create demo users:

   docker compose exec backend python seed_demo_users.py

8. Run reconciliation:

   docker compose exec backend python run_reconciliation.py

### Access the application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Normal startup

docker compose up -d

### Stop containers

docker compose down

### Rebuild after code changes

docker compose up --build -d

### Check container status

docker compose ps

### View logs

docker compose logs -f

### Important

- Keep `.env` files out of Git.
- Never commit passwords or secrets.
- Database data is stored in a persistent Docker volume.
- Do not use `docker compose down -v` unless you intentionally want to delete the database volume and its data.
- First-time database migrations and seed commands should not be repeated unnecessarily.

## Author



DealerOS - Full-Stack Engineering Take-Home Project.




