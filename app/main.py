from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import engine
from app.database.base import Base
from app.api import predict, users, watchlist, history

# Create tables (only if database is configured)
if engine is not None:
    Base.metadata.create_all(bind=engine)
else:
    print("Warning: Database not configured - running without database support")

# Initialize app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router)
app.include_router(users.router)
app.include_router(watchlist.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {
        "message": "Stock Prediction API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
