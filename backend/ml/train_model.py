import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    confusion_matrix, classification_report, roc_auc_score,
    precision_recall_curve
)
from sklearn.calibration import CalibratedClassifierCV
import pickle
import os

# Try to import SMOTE for handling class imbalance
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    print("Warning: imbalanced-learn not installed. Using class_weight instead of SMOTE.")


def calculate_stability_score(savings_ratio, cash_flow_stability, avg_balance):
    """
    Calculate financial stability score - MUST match prediction pipeline
    """
    score = (
        savings_ratio * 0.4 +
        cash_flow_stability * 0.3 +
        min(avg_balance / 100000, 1) * 0.3
    )
    return max(0, min(1, score))


def calculate_credit_score(savings_ratio, financial_stability, cash_flow_stability, 
                           avg_income, avg_expenses, payment_history=0.8):
    """
    Calculate credit score - MUST match prediction pipeline
    """
    income_expense_ratio = (avg_income - avg_expenses) / avg_income if avg_income > 0 else 0
    
    base_score = (
        payment_history * 0.35 +
        financial_stability * 0.30 +
        savings_ratio * 0.20 +
        cash_flow_stability * 0.10 +
        income_expense_ratio * 0.05
    )
    
    credit_score = int(300 + (base_score * 550))
    return max(300, min(850, credit_score))


def generate_training_data(n_samples=10000):
    """
    Generate synthetic loan application data with consistent feature engineering
    that matches the prediction pipeline.
    """
    np.random.seed(42)
    
    # Generate base financial data (simulating real user inputs)
    monthly_income = np.random.normal(45000, 20000, n_samples).clip(15000, 150000)
    monthly_expenses = np.random.normal(25000, 12000, n_samples).clip(8000, 80000)
    
    # Ensure expenses don't exceed income for most samples
    monthly_expenses = np.minimum(monthly_expenses, monthly_income * 0.95)
    
    savings = np.random.exponential(50000, n_samples).clip(0, 500000)
    existing_loans = np.random.exponential(30000, n_samples).clip(0, 300000)
    account_balance = np.random.normal(50000, 30000, n_samples).clip(5000, 200000)
    
    # Derived features - matching prediction pipeline exactly
    savings_ratio = (monthly_income - monthly_expenses) / monthly_income
    savings_ratio = np.clip(savings_ratio, 0, 1)
    
    # Cash flow stability - based on whether savings exceed expenses
    cash_flow_stability = np.where(savings > monthly_expenses, 0.7, 0.4)
    # Add some variation
    cash_flow_stability = cash_flow_stability + np.random.uniform(-0.1, 0.1, n_samples)
    cash_flow_stability = np.clip(cash_flow_stability, 0.3, 1.0)
    
    # Financial stability score - matching prediction pipeline
    financial_stability_score = np.array([
        calculate_stability_score(sr, cfs, bal) 
        for sr, cfs, bal in zip(savings_ratio, cash_flow_stability, account_balance)
    ])
    
    # Credit score - matching prediction pipeline
    credit_score = np.array([
        calculate_credit_score(sr, fs, cfs, inc, exp)
        for sr, fs, cfs, inc, exp in zip(
            savings_ratio, financial_stability_score, cash_flow_stability,
            monthly_income, monthly_expenses
        )
    ])
    
    # Transaction frequency - realistic range
    transaction_frequency = np.random.randint(15, 100, n_samples)
    
    # Create DataFrame
    df = pd.DataFrame({
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'savings_ratio': savings_ratio,
        'financial_stability_score': financial_stability_score,
        'cash_flow_stability': cash_flow_stability,
        'credit_score': credit_score,
        'existing_loans': existing_loans,
        'account_balance': account_balance,
        'transaction_frequency': transaction_frequency,
    })
    
    # Generate target variable with balanced criteria
    # Using a scoring system instead of strict AND conditions
    approval_score = (
        (df['savings_ratio'] * 25) +                          # 0-25 points
        (df['financial_stability_score'] * 25) +              # 0-25 points
        ((df['credit_score'] - 300) / 550 * 25) +            # 0-25 points
        (np.clip(df['monthly_income'] / 100000, 0, 1) * 15) + # 0-15 points
        (np.clip(1 - df['existing_loans'] / 200000, 0, 1) * 10)  # 0-10 points
    )
    
    # Normalize to 0-100
    approval_score = (approval_score / 100) * 100
    
    # Threshold at 45 points (creates ~50% approval rate)
    df['loan_approved'] = (approval_score >= 45).astype(int)
    
    # Add controlled noise (5%)
    noise_indices = np.random.choice(df.index, size=int(0.05 * n_samples), replace=False)
    df.loc[noise_indices, 'loan_approved'] = 1 - df.loc[noise_indices, 'loan_approved']
    
    return df


def find_optimal_threshold(model, X_test, y_test):
    """
    Find the optimal classification threshold using precision-recall curve
    """
    y_proba = model.predict_proba(X_test)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
    
    # Find threshold that maximizes F1 score
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores[:-1])  # Last element doesn't have a threshold
    optimal_threshold = thresholds[best_idx]
    
    return optimal_threshold, f1_scores[best_idx]


def train_model():
    """Train an improved Random Forest model for loan prediction"""
    print("=" * 60)
    print("MICRO LOAN ML MODEL TRAINING")
    print("=" * 60)
    
    print("\n[1/6] Generating training data...")
    df = generate_training_data(n_samples=10000)
    
    # Show class distribution
    class_dist = df['loan_approved'].value_counts()
    print(f"\nClass Distribution:")
    print(f"  Rejected (0): {class_dist[0]} ({class_dist[0]/len(df)*100:.1f}%)")
    print(f"  Approved (1): {class_dist[1]} ({class_dist[1]/len(df)*100:.1f}%)")
    
    # Features and target
    feature_names = [
        'monthly_income', 'monthly_expenses', 'savings_ratio',
        'financial_stability_score', 'cash_flow_stability', 'credit_score',
        'existing_loans', 'account_balance', 'transaction_frequency'
    ]
    X = df[feature_names]
    y = df['loan_approved']
    
    # Train-test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n[2/6] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Handle class imbalance
    print(f"\n[3/6] Handling class imbalance...")
    if SMOTE_AVAILABLE:
        smote = SMOTE(random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)
        print(f"  Applied SMOTE: {len(y_train)} -> {len(y_train_resampled)} samples")
    else:
        X_train_resampled, y_train_resampled = X_train_scaled, y_train
        print("  Using class_weight='balanced' instead of SMOTE")
    
    # Train Random Forest with balanced class weights
    print(f"\n[4/6] Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced' if not SMOTE_AVAILABLE else None,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_resampled, y_train_resampled)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_resampled, y_train_resampled, cv=5, scoring='f1')
    print(f"  Cross-validation F1 scores: {cv_scores}")
    print(f"  Mean CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    # Find optimal threshold
    print(f"\n[5/6] Finding optimal classification threshold...")
    optimal_threshold, best_f1 = find_optimal_threshold(model, X_test_scaled, y_test)
    print(f"  Optimal threshold: {optimal_threshold:.4f}")
    print(f"  F1 at optimal threshold: {best_f1:.4f}")
    
    # Evaluate with default threshold (0.5)
    print(f"\n[6/6] Model Evaluation")
    print("-" * 40)
    
    y_pred_default = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred_optimal = (y_proba >= optimal_threshold).astype(int)
    
    print("\n=== Default Threshold (0.5) ===")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_default):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_default):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred_default):.4f}")
    print(f"F1 Score:  {f1_score(y_test, y_pred_default):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, y_proba):.4f}")
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred_default))
    
    print(f"\n=== Optimal Threshold ({optimal_threshold:.3f}) ===")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred_optimal):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_optimal):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred_optimal):.4f}")
    print(f"F1 Score:  {f1_score(y_test, y_pred_optimal):.4f}")
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred_optimal))
    
    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred_optimal, target_names=['Rejected', 'Approved']))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n=== Feature Importance ===")
    print(feature_importance.to_string(index=False))
    
    # Save model, scaler, and threshold
    print("\n" + "=" * 60)
    print("Saving model artifacts...")
    
    # Determine correct path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'loan_model.pkl')
    scaler_path = os.path.join(script_dir, 'scaler.pkl')
    config_path = os.path.join(script_dir, 'model_config.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  Model saved to: {model_path}")
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"  Scaler saved to: {scaler_path}")
    
    # Save configuration including optimal threshold
    config = {
        'optimal_threshold': optimal_threshold,
        'feature_names': feature_names,
        'class_distribution': {
            'rejected': int(class_dist[0]),
            'approved': int(class_dist[1])
        }
    }
    with open(config_path, 'wb') as f:
        pickle.dump(config, f)
    print(f"  Config saved to: {config_path}")
    
    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETE!")
    print("=" * 60)
    
    return model, scaler, optimal_threshold


if __name__ == "__main__":
    train_model()
