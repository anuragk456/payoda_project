# FastAPI Project with JWT Auth, Middleware, Caching, and CRUD

## 🔧 Setup

brew install python

python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn


Swagger:
    http://127.0.0.1:8000/docs


---

## Flow 

    /auth/login → returns JWT (20 min expiry).

    Middleware → checks JWT for every request except:

    /auth/login

    /health

    /docs

    /openapi.json

    /auth/me → shows user info if token valid.

    /cached-data → caches response for 2 minutes (same output even if called repeatedly).




# How it works (detailed explanation)

### 1) Authentication & JWT
- The `/auth/login` route accepts `username` and `password` as `application/x-www-form-urlencoded` (OAuth2 password form).
- `auth/jwt_handler.py` creates JWT tokens with claims:
  - `sub`: username
  - `exp`: expiry time (20 minutes)
  - `iat`: issued at
- `get_current_user` and `get_current_username` are standard FastAPI dependencies to validate tokens when used in path operations.

### 2) Global Authentication Middleware
- `middlewares/auth_middleware.AuthMiddleware` is an ASGI middleware that:
  - Skips public paths (login, health, docs, etc.).
  - Reads `Authorization: Bearer <token>` header.
  - Decodes & validates JWT using same `SECRET_KEY` + `ALGORITHM`.
  - Sets `scope["authenticated_user"] = username` so endpoints can read it.
  - Returns 401 for missing/invalid token before calling any endpoint.
- Advantage: you don’t need to annotate every route with dependencies; middleware enforces auth globally.
- You can still use `Depends(get_current_user)` in endpoints if you want more fine-grained checks or to get the Pydantic `User` object.

### 3) CORS middleware
- `fastapi.middleware.cors.CORSMiddleware` configured with permissive settings (allow all).
- For production, set `allow_origins` to your front-end domain(s).

### 4) Caching for authenticated responses
- `fastapi-cache2` provides `@cache(expire=N)` decorator.
- In our `/cached-data` route we pass `username: str = Depends(get_current_username)`. `fastapi-cache2` builds cache key using the **function arguments**, so different usernames lead to different cache entries → per-user cache.
- You can switch backend to Redis by setting `CACHE_BACKEND="redis"` and ensuring `REDIS_URL` is correct in `config.py`. Redis persists across restarts and works across multiple processes.

---

# How to test (step-by-step)

### 1) Start the server


pip install -r requirements.txt
uvicorn main:app --reload


auth:
    curl -X GET http://127.0.0.1:8000/auth/me

auth With invalid token:
    curl -X GET http://127.0.0.1:8000/auth/me -H "Authorization: Bearer fake_token"


login:
    curl -X POST "http://127.0.0.1:8000/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=anurag&password=password123"


caching:
    curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/cached-data
    # Second call (within 2 minutes) - same timestamp (from cache)
    curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/cached-data


Creating records:
    curl -X POST "http://127.0.0.1:8000/records/" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d '{"option_type":"opportunity","description":"test","status":"active"}'


List records:
    curl -H "Authorization: Bearer <TOKEN>" "http://127.0.0.1:8000/records/"


Get a record:
    curl -H "Authorization: Bearer <TOKEN>" "http://127.0.0.1:8000/records/1"


Update record:
    curl -X PUT "http://127.0.0.1:8000/records/1" -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d '{"description":"updated"}'


Delete:
    curl -X DELETE -H "Authorization: Bearer <TOKEN>" "http://127.0.0.1:8000/records/1"

---

#### Important things to Know: 

+ Middleware: JWT is validated globally → no need to put Depends(get_current_user) everywhere.

+ CORS: All cross-origin requests are handled.

+ Cache: Any endpoint decorated with @cache(expire=120) will store results for 2 minutes.


***Notes on middleware:***

+ It validates JWT and rejects requests without a valid Bearer token.

+ It skips public endpoints (you can add/remove paths in self.public_paths).

+ It stores username in scope["authenticated_user"] for downstream use — endpoints can also use dependency get_current_user if you prefer.


**Important notes in main.py:**

+ /cached-data uses the dependency get_current_username so the cache key includes username — resulting in a per-user cache.

+ /cached-data-scope demonstrates reading user from request.scope (set by middleware); fastapi-cache2 will include request in the key-building so caching may be global unless request contents differ — prefer explicit username dependency to guarantee per-user keys.


---

curl -X POST "http://127.0.0.1:8000/qa/generate" \
  -H "Authorization: Bearer <TOKAN>" \
  -F "resume=@S_Sangeetha.pdf" \
  -F "jd=@Data_Quality_Analyst.pdf"