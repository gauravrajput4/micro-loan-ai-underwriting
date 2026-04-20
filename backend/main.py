from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    from routes import auth_routes, loan_routes, upload_routes, dashboard_routes, kyc_routes, workflow_routes, audit_routes, risk_routes, profile_routes
except ModuleNotFoundError:
    from .routes import auth_routes, loan_routes, upload_routes, dashboard_routes, kyc_routes, workflow_routes, audit_routes, risk_routes, profile_routes

app = FastAPI(title="AI Loan Underwriting System", version="1.0.0")

# Load environment variables from backend/.env when available.
if load_dotenv:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(current_dir, ".env"))
    load_dotenv(os.path.join(os.path.dirname(current_dir), ".env"))

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
app.include_router(profile_routes.router, prefix="/api/profile", tags=["Profile"])
app.include_router(loan_routes.router, prefix="/api/loan", tags=["Loan"])
app.include_router(upload_routes.router, prefix="/api/upload", tags=["Upload"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(kyc_routes.router, prefix="/api/kyc", tags=["KYC"])
app.include_router(workflow_routes.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(audit_routes.router, prefix="/api/audit", tags=["Audit"])
app.include_router(risk_routes.router, prefix="/api/risk", tags=["Risk"])

backend_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = os.path.join(backend_dir, "uploads")
os.makedirs(media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")

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
    # Use module path compatible with both script and package execution.
    app_target = "backend.main:app" if __package__ else "main:app"
    uvicorn.run(app_target, host="0.0.0.0", port=8000, reload=True)
