from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

try:
    from routes import auth_routes, loan_routes, upload_routes, dashboard_routes
except ModuleNotFoundError:
    from .routes import auth_routes, loan_routes, upload_routes, dashboard_routes

app = FastAPI(title="AI Loan Underwriting System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(loan_routes.router, prefix="/api/loan", tags=["Loan"])
app.include_router(upload_routes.router, prefix="/api/upload", tags=["Upload"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {
        "message": "AI-Powered Personal Loan Underwriting System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
