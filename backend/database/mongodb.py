from pymongo import MongoClient
from datetime import datetime
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

def get_database():
    return db
