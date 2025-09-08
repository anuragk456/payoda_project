from fastapi import FastAPI, Depends, Request, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.decorator import cache

from auth import routes as auth_routes
from routers import record_router
from middlewares.auth_middleware import AuthMiddleware
from middlewares.logging_middleware import LoggingMiddleware
from utils.cache_utils import init_cache
from database import init_db
from utils.logger import logger
from auth.jwt_handler import get_current_username

from services.file_service import save_upload_file
from utils.parser_utils import extract_text_from_pdf
from services.llama_service import generate_questions_and_answers
from routers import qa_router

app = FastAPI(title="Auth + Records + Q&A API")

# -------------------- Middlewares --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# -------------------- Routers --------------------
app.include_router(auth_routes.router)
app.include_router(record_router.router)
app.include_router(qa_router.router)

# -------------------- Existing Endpoints --------------------
@app.get("/health", summary="Health check (no auth)")
async def health():
    return {"status": "ok"}


@app.get("/cached-data", summary="Authenticated cached data (2 minutes)")
@cache(expire=120)
async def cached_data(username: str = Depends(get_current_username)):
    import time
    return {"data": f"Hello, {username}", "timestamp": time.time()}


@app.get("/cached-data-scope", summary="Cached using scope auth (2 minutes)")
@cache(expire=120)
async def cached_data_scope(request: Request):
    username = request.scope.get("authenticated_user", "anonymous")
    import time
    return {"data": f"Hello (scope), {username}", "timestamp": time.time()}


# -------------------- New Q&A Endpoint --------------------
@app.post("/qa/generate", summary="Upload Resume + JD (PDFs) to generate interview Q&A")
async def generate_qa(resume: UploadFile, jd: UploadFile):
    """
    Upload Resume + Job Description (PDFs).
    Returns tailored interview Q&A using LLaMA (via Ollama).
    """
    try:
        resume_path = save_upload_file(resume)
        jd_path = save_upload_file(jd)

        resume_text = extract_text_from_pdf(resume_path)
        jd_text = extract_text_from_pdf(jd_path)

        qa_output = generate_questions_and_answers(jd_text, resume_text)
        return {"questions_and_answers": qa_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Startup --------------------
@app.on_event("startup")
async def on_startup():
    init_db()
    init_cache(app)
    logger.info("Application startup complete")
