from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from datetime import datetime

try:
    from services.bank_statement_analyzer import BankStatementAnalyzer
    from database.mongodb import bank_statements_collection
    from services.security import AuthUser, require_roles
except ModuleNotFoundError:
    from ..services.bank_statement_analyzer import BankStatementAnalyzer
    from ..database.mongodb import bank_statements_collection
    from ..services.security import AuthUser, require_roles

router = APIRouter()

@router.post("/upload-bank-statement")
async def upload_bank_statement(email: str = Form(...),
    file: UploadFile = File(...),
    current_user: AuthUser = Depends(require_roles("applicant", "student", "unemployed", "underwriter", "risk_manager", "admin"))):
    """Upload and analyze bank statement"""
    role = str(current_user.get("role", "")).lower()
    if role in {"applicant", "student", "unemployed"} and email.strip().lower() != current_user["email"]:
        raise HTTPException(status_code=403, detail="Cannot upload statement for another user")
    
    # Validate file type
    allowed_extensions = ['.pdf', '.csv', '.xlsx', '.xls']
    file_ext = '.' + file.filename.split('.')[-1].lower()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed: PDF, CSV, Excel")
    
    # Read file content
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    # Analyze based on file type
    analyzer = BankStatementAnalyzer()
    
    try:
        if file_ext == '.pdf':
            financial_data = analyzer.analyze_pdf(content)
        elif file_ext == '.csv':
            financial_data = analyzer.analyze_csv(content)
        else:  # Excel
            financial_data = analyzer.analyze_excel(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")
    
    # Save to database
    statement_doc = {
        "email": email,
        "filename": file.filename,
        "file_type": file_ext,
        "financial_data": financial_data,
        "uploaded_at": datetime.utcnow()
    }
    
    result = bank_statements_collection.insert_one(statement_doc)
    
    return {
        "message": "Bank statement analyzed successfully",
        "statement_id": str(result.inserted_id),
        "financial_data": financial_data
    }
