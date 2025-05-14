from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, auth, rules
from .config import settings

app = FastAPI(
    title="MageChat API",
    description="A chat application with Model Context Protocol (MCP) for AI safety and alignment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper tags and descriptions
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    rules.router,
    prefix="/rules",
    tags=["Rules"],
    responses={404: {"description": "Not found"}}
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to MageChat API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 