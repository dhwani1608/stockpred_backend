from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import engine
from app.database.base import Base
from app.api import predict, users, watchlist, history

# Create tables (only if database is configured)
if engine is not None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Table creation failed, attempting to drop and recreate: {e}")
        try:
            # Drop all tables and recreate (only safe for new deployments)
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            print("Successfully recreated database tables")
        except Exception as e2:
            print(f"Error: Could not recreate tables: {e2}")
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
@app.head("/")
def root():
    return {
        "message": "Stock Prediction API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
@app.head("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
