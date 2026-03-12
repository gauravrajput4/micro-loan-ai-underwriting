import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pickle

# Generate synthetic training data
def generate_training_data(n_samples=5000):
    """Generate synthetic loan application data"""
    np.random.seed(42)
    
    data = {
        'monthly_income': np.random.normal(35000, 15000, n_samples).clip(10000, 100000),
        'monthly_expenses': np.random.normal(20000, 10000, n_samples).clip(5000, 60000),
        'savings_ratio': np.random.uniform(0, 0.6, n_samples),
        'financial_stability_score': np.random.uniform(0.2, 1.0, n_samples),
        'cash_flow_stability': np.random.uniform(0.3, 1.0, n_samples),
        'credit_score': np.random.normal(680, 80, n_samples).clip(300, 850),
        'existing_loans': np.random.normal(50000, 30000, n_samples).clip(0, 200000),
        'account_balance': np.random.normal(40000, 25000, n_samples).clip(1000, 150000),
        'transaction_frequency': np.random.randint(20, 100, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable (loan approval)
    df['loan_approved'] = (
        (df['savings_ratio'] > 0.2) &
        (df['financial_stability_score'] > 0.5) &
        (df['credit_score'] > 600) &
        (df['monthly_income'] > 25000)
    ).astype(int)
    
    # Add some noise
    noise_indices = np.random.choice(df.index, size=int(0.1 * n_samples), replace=False)
    df.loc[noise_indices, 'loan_approved'] = 1 - df.loc[noise_indices, 'loan_approved']
    
    return df

def train_model():
    """Train Random Forest model for loan prediction"""
    print("Generating training data...")
    df = generate_training_data()
    
    # Features and target
    X = df.drop('loan_approved', axis=1)
    y = df['loan_approved']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    print("\n=== Model Performance ===")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    print(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n=== Feature Importance ===")
    print(feature_importance)
    
    # Save model and scaler
    print("\nSaving model and scaler...")
    with open('backend/ml/loan_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('backend/ml/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print("Model training complete!")
    return model, scaler

if __name__ == "__main__":
    train_model()
