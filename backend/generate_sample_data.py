"""
Sample Data Generator for Testing
Run this to create test users and sample loan applications
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

# Sample users
SAMPLE_USERS = [
    {
        "email": "student1@example.com",
        "password": "test123",
        "full_name": "Alice Johnson",
        "user_type": "applicant",
        "phone": "1234567890"
    },
    {
        "email": "unemployed1@example.com",
        "password": "test123",
        "full_name": "Bob Smith",
        "user_type": "applicant",
        "phone": "0987654321"
    },
    {
        "email": "admin@example.com",
        "password": "admin123",
        "full_name": "Admin User",
        "user_type": "admin",
        "phone": "5555555555"
    }
]

# Sample loan applications (likely to be approved)
APPROVED_PROFILES = [
    {
        "loan_amount": 100000,
        "loan_purpose": "education",
        "employment_status": "student",
        "monthly_income": 40000,
        "monthly_expenses": 20000,
        "savings": 80000,
        "existing_loans": 0,
        "account_balance": 100000
    },
    {
        "loan_amount": 150000,
        "loan_purpose": "personal",
        "employment_status": "unemployed",
        "monthly_income": 35000,
        "monthly_expenses": 18000,
        "savings": 100000,
        "existing_loans": 0,
        "account_balance": 120000
    }
]

# Sample loan applications (likely to be rejected)
REJECTED_PROFILES = [
    {
        "loan_amount": 500000,
        "loan_purpose": "business",
        "employment_status": "unemployed",
        "monthly_income": 15000,
        "monthly_expenses": 14000,
        "savings": 5000,
        "existing_loans": 50000,
        "account_balance": 10000
    },
    {
        "loan_amount": 300000,
        "loan_purpose": "personal",
        "employment_status": "student",
        "monthly_income": 12000,
        "monthly_expenses": 11000,
        "savings": 3000,
        "existing_loans": 30000,
        "account_balance": 8000
    }
]

def register_users():
    """Register sample users"""
    print("📝 Registering sample users...")
    for user in SAMPLE_USERS:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user)
            if response.status_code == 200:
                print(f"✅ Registered: {user['email']}")
            else:
                print(f"⚠️  {user['email']}: {response.json().get('detail', 'Already exists')}")
        except Exception as e:
            print(f"❌ Error registering {user['email']}: {e}")

def login_user(email, password):
    """Login and get token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Login error: {e}")
    return None

def submit_loan_applications():
    """Submit sample loan applications"""
    print("\n💼 Submitting sample loan applications...")
    
    # Login as first user
    token = login_user(SAMPLE_USERS[0]["email"], SAMPLE_USERS[0]["password"])
    if not token:
        print("❌ Could not login. Please ensure backend is running.")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Submit approved profiles
    print("\n✅ Submitting likely-approved applications...")
    for i, profile in enumerate(APPROVED_PROFILES, 1):
        profile["email"] = SAMPLE_USERS[0]["email"]
        profile["full_name"] = SAMPLE_USERS[0]["full_name"]
        
        try:
            response = requests.post(
                f"{BASE_URL}/loan/predict-loan",
                json=profile,
                headers=headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  Application {i}: {result['decision'].upper()} "
                      f"(Credit Score: {result['credit_score']}, "
                      f"Probability: {result['probability']:.2%})")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Submit rejected profiles
    print("\n❌ Submitting likely-rejected applications...")
    for i, profile in enumerate(REJECTED_PROFILES, 1):
        profile["email"] = SAMPLE_USERS[1]["email"]
        profile["full_name"] = SAMPLE_USERS[1]["full_name"]
        
        # Login as second user
        token2 = login_user(SAMPLE_USERS[1]["email"], SAMPLE_USERS[1]["password"])
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        try:
            response = requests.post(
                f"{BASE_URL}/loan/predict-loan",
                json=profile,
                headers=headers2
            )
            if response.status_code == 200:
                result = response.json()
                print(f"  Application {i}: {result['decision'].upper()} "
                      f"(Credit Score: {result['credit_score']}, "
                      f"Probability: {result['probability']:.2%})")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_emi_calculator():
    """Test EMI calculator"""
    print("\n🧮 Testing EMI Calculator...")
    try:
        response = requests.post(f"{BASE_URL}/loan/calculate-emi", json={
            "principal": 100000,
            "annual_rate": 12.0,
            "tenure_months": 36
        })
        if response.status_code == 200:
            result = response.json()
            print(f"  Loan Amount: ₹{result['principal']:,.0f}")
            print(f"  Monthly EMI: ₹{result['monthly_emi']:,.2f}")
            print(f"  Total Interest: ₹{result['total_interest']:,.2f}")
            print(f"  Total Payment: ₹{result['total_payment']:,.2f}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🚀 AI Loan Underwriting System - Sample Data Generator")
    print("=" * 60)
    print("\n⚠️  Make sure the backend is running on http://localhost:8000\n")
    
    # Register users
    register_users()
    
    # Submit loan applications
    submit_loan_applications()
    
    # Test EMI calculator
    test_emi_calculator()
    
    print("\n" + "=" * 60)
    print("✅ Sample data generation complete!")
    print("=" * 60)
    print("\n📊 You can now:")
    print("  1. Login to frontend with any of the test users")
    print("  2. View admin dashboard (admin@example.com / admin123)")
    print("  3. Apply for more loans")
    print("\n🔑 Test Credentials:")
    for user in SAMPLE_USERS:
        print(f"  {user['email']} / {user['password']} ({user['user_type']})")
    print()

if __name__ == "__main__":
    main()
