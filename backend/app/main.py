
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import locations
from app.routers.qa import router as qa_router

app = FastAPI(title="DealerOS API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.routers.auth import router as auth_router
from app.routers.exceptions import router as exceptions_router


app.include_router(auth_router)
app.include_router(exceptions_router)
app.include_router(qa_router)
app.include_router(locations.router)
@app.get("/")
def home():
    return {
        "message": "DealerOS API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
