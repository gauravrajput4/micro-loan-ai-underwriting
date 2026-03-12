from fastapi import APIRouter
from database.mongodb import (
    loan_applications_collection,
    loan_predictions_collection,
    users_collection
)
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/admin-dashboard")
async def get_admin_dashboard():

    total_applications = loan_applications_collection.count_documents({})
    total_predictions = loan_predictions_collection.count_documents({})
    approved_loans = loan_predictions_collection.count_documents({"prediction": 1})
    rejected_loans = loan_predictions_collection.count_documents({"prediction": 0})

    approval_rate = (approved_loans / total_predictions * 100) if total_predictions > 0 else 0

    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_probability": {"$avg": "$probability"},
                "avg_credit_score": {"$avg": "$credit_score"}
            }
        }
    ]

    avg_stats = list(loan_predictions_collection.aggregate(pipeline))
    avg_credit_score = avg_stats[0]["avg_credit_score"] if avg_stats else 0

    recent_applications = list(
        loan_predictions_collection.find()
        .sort("created_at", -1)
        .limit(10)
    )

    for app in recent_applications:
        app["_id"] = str(app["_id"])

    status_distribution = {
        "approved": approved_loans,
        "rejected": rejected_loans
    }

    credit_ranges = [
        {"range": "300-550", "count": loan_predictions_collection.count_documents({"credit_score": {"$gte":300,"$lt":550}})},
        {"range": "550-650", "count": loan_predictions_collection.count_documents({"credit_score": {"$gte":550,"$lt":650}})},
        {"range": "650-750", "count": loan_predictions_collection.count_documents({"credit_score": {"$gte":650,"$lt":750}})},
        {"range": "750-850", "count": loan_predictions_collection.count_documents({"credit_score": {"$gte":750,"$lte":850}})}
    ]

    six_months_ago = datetime.utcnow() - timedelta(days=180)

    monthly_pipeline = [
        {"$match": {"created_at": {"$gte": six_months_ago}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "total": {"$sum": 1},
                "approved": {
                    "$sum": {"$cond": [{"$eq": ["$prediction", 1]}, 1, 0]}
                }
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]

    monthly_trends = list(loan_predictions_collection.aggregate(monthly_pipeline))

    return {
        "summary": {
            "total_applications": total_applications,
            "total_predictions": total_predictions,
            "approved_loans": approved_loans,
            "rejected_loans": rejected_loans,
            "approval_rate": round(approval_rate,2),
            "avg_credit_score": round(avg_credit_score,2)
        },
        "recent_applications": recent_applications,
        "status_distribution": status_distribution,
        "credit_score_distribution": credit_ranges,
        "monthly_trends": monthly_trends
    }

@router.get("/loan-applications")
async def get_all_applications():
    """Get all loan applications"""
    applications = list(
        loan_applications_collection.find()
        .sort("created_at", -1)
        .limit(100)
    )
    
    for app in applications:
        app["_id"] = str(app["_id"])
    
    return {"applications": applications}

@router.get("/metrics")
async def get_user_dashboard_metrics(email: str):

    # Latest prediction
    prediction = loan_predictions_collection.find_one(
        {"email": email},
        sort=[("created_at", -1)]
    )

    # Applications
    applications = list(
        loan_applications_collection.find({"email": email})
        .sort("created_at", -1)
        .limit(5)
    )

    for app in applications:
        app["_id"] = str(app["_id"])

    total_borrowed = 0
    next_payment = 0
    credit_score = 0
    status = "No Application"

    repayment_schedule = []

    if prediction:

        credit_score = prediction.get("credit_score", 0)

        decision = "Approved" if prediction.get("prediction") == 1 else "Rejected"

        status = decision

        emi_data = prediction.get("emi_data", {})

        if decision == "Approved":

            total_borrowed = prediction.get("requested_amount", 0)

            next_payment = emi_data.get("monthly_emi", 0)

            balance = total_borrowed

            months = ["Jan","Feb","Mar","Apr","May","Jun"]

            for m in months:

                balance -= next_payment

                if balance < 0:
                    balance = 0

                repayment_schedule.append({
                    "month": m,
                    "balance": round(balance,2)
                })

    return {
        "totalBorrowed": total_borrowed,
        "nextPayment": next_payment,
        "creditScore": credit_score,
        "recentStatus": status,
        "repaymentSchedule": repayment_schedule,
        "myApplications": applications
    }
