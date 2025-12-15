from fastapi import FastAPI
from app.db import init_db
from app.routers import routes, students, trips

# Initialize FastAPI app
app = FastAPI(
    title="UniBus Student Validation API",
    description="Secondary service responsible for validating student eligibility for UniBus service",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    """Inicia o banco de dados na inicialização"""
    init_db()
    print("✅ Database initialized successfully")


# Include routers
app.include_router(routes.router)
app.include_router(students.router)
app.include_router(trips.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
