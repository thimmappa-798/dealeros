# DealerOS - Technical Decisions



## 1. PostgreSQL Row-Level Security (RLS)



**Decision:** Use PostgreSQL RLS to enforce tenant isolation at the database level.



**Reason:** Application-level filters alone are not sufficient. A forgotten filter or raw SQL query could expose another organization's records. RLS provides an additional database-level security boundary.



## 2. Separate Database Roles



**Decision:** Use a restricted `dealeros\_app` role for application requests and a separate admin connection for trusted administrative operations.



**Reason:** PostgreSQL superusers can bypass RLS. The application must connect using a role without superuser or `BYPASSRLS` privileges.



## 3. Transaction-Local Tenant Context



**Decision:** Set the current organization using PostgreSQL `set\_config('app.current\_org', ..., true)`.



**Reason:** The third argument makes the setting transaction-local. This prevents tenant context from remaining on a pooled database connection after its transaction ends.



## 4. Shared Database Architecture



**Decision:** Store multiple organizations in the same PostgreSQL database using an `organization\_id` column.



**Reason:** This keeps the architecture simpler to operate while RLS enforces data isolation.



## 5. Record Reference Normalization



**Decision:** Trim whitespace, convert references to uppercase, remove spaces and hyphens, and add the `REC` prefix to numeric-only references.



**Reason:** The two source systems may represent the same reference differently. Normalization helps identify matching records.



## 6. Decimal-Based Financial Comparisons



**Decision:** Use Python `Decimal` for financial values instead of floating-point arithmetic.



**Reason:** Decimal arithmetic avoids common floating-point precision problems when comparing financial amounts. Raw source values are also preserved where needed for invalid-value investigation.



## 7. Duplicate Detection



**Decision:** Identify duplicate entries without automatically treating every multiple-entry reference as a duplicate.



**Reason:** Multiple entries can be legitimate split payments. Their combined value must be considered before raising an exception.



## 8. Local LLM for Question Classification



**Decision:** Use Ollama with the `qwen2.5:3b` model to classify supported natural-language questions.



**Reason:** This avoids requiring a paid external LLM API. The LLM identifies question intent, while deterministic database queries calculate the answer.



## 9. Grounded Answers and Citations



**Decision:** Generate answers from database results and return source record identifiers as citations.



**Reason:** The LLM must not invent financial numbers. Unsupported questions are refused when they cannot be answered using the available reconciliation data.



## 10. JWT Authentication with HttpOnly Cookies



**Decision:** Store the JWT in an HttpOnly cookie rather than exposing it to frontend JavaScript.



**Reason:** HttpOnly cookies reduce the risk of token theft through JavaScript access. SameSite is configured as Lax. Production deployment should also enable Secure cookies over HTTPS and implement appropriate CSRF protection.



## 11. Frontend and Backend Separation



**Decision:** Use React with Vite for the frontend and FastAPI for backend APIs.



**Reason:** This separates the user interface from business logic and allows each layer to evolve independently.



## 12. Automated Testing



**Decision:** Add automated tests for tenant isolation and grounded Q&A behavior.



**Reason:** Tenant isolation is a critical security requirement. Tests verify that missing tenant context does not expose data, cross-tenant inserts are blocked, and unsupported questions are refused.



## 13. AI-Assisted Development



AI tools were used as development assistance during implementation, debugging, and documentation. The application also uses a local Ollama model at runtime for question-intent classification. Database queries and answer calculations remain deterministic.



