from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "loan_underwriting"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
loan_applications_collection = db["loan_applications"]
bank_statements_collection = db["bank_statements"]
loan_predictions_collection = db["loan_predictions"]
admin_metrics_collection = db["admin_metrics"]
kyc_documents_collection = db["kyc_documents"]
audit_logs_collection = db["audit_logs"]
refresh_tokens_collection = db["refresh_tokens"]
otp_codes_collection = db["otp_codes"]
password_reset_tokens_collection = db["password_reset_tokens"]
signup_verifications_collection = db["signup_verifications"]
model_registry_collection = db["model_registry"]
shadow_predictions_collection = db["shadow_predictions"]
monitoring_snapshots_collection = db["monitoring_snapshots"]
fairness_reports_collection = db["fairness_reports"]
retraining_jobs_collection = db["retraining_jobs"]

def get_database():
    return db
