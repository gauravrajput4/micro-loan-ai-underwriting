import pandas as pd
import numpy as np
import pdfplumber
import io
import re
from typing import Dict


class BankStatementAnalyzer:

    # -------------------------------
    # PDF ANALYSIS
    # -------------------------------

    def analyze_pdf(self, file_content: bytes) -> Dict:
        """Extract financial data from PDF bank statement"""

        text = ""

        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        transactions = self._extract_transactions(text)

        return self._calculate_metrics(transactions)

    # -------------------------------
    # CSV ANALYSIS
    # -------------------------------

    def analyze_csv(self, file_content: bytes) -> Dict:

        df = pd.read_csv(io.BytesIO(file_content))

        return self._calculate_metrics_from_df(df)

    # -------------------------------
    # EXCEL ANALYSIS
    # -------------------------------

    def analyze_excel(self, file_content: bytes) -> Dict:

        df = pd.read_excel(io.BytesIO(file_content))

        return self._calculate_metrics_from_df(df)

    # -------------------------------
    # EXTRACT TRANSACTIONS FROM PDF
    # -------------------------------

    def _extract_transactions(self, text: str):

        """
        Parse transactions from bank statement text

        Example row:
        12/03/2026 20.0 DR 3575.66
        """

        pattern = r'(\d{2}/\d{2}/\d{4})\s+(\d+\.\d+)\s+(DR|CR)\s+(\d+\.\d+)'

        matches = re.findall(pattern, text)

        transactions = []

        for date, amount, ttype, balance in matches:

            amount = float(amount)
            balance = float(balance)

            debit = 0
            credit = 0

            if ttype == "CR":
                credit = amount
            else:
                debit = amount

            transactions.append({
                "date": date,
                "debit": debit,
                "credit": credit,
                "balance": balance
            })

        return transactions

    # -------------------------------
    # CALCULATE METRICS FROM PDF DATA
    # -------------------------------

    def _calculate_metrics(self, transactions):

        if not transactions:
            return self._default_metrics()

        credits = [t["credit"] for t in transactions if t["credit"] > 0]
        debits = [t["debit"] for t in transactions if t["debit"] > 0]
        balances = [t["balance"] for t in transactions]

        avg_income = np.mean(credits) if credits else 0
        avg_expenses = np.mean(debits) if debits else 0
        avg_balance = np.mean(balances)

        savings_ratio = (
            (avg_income - avg_expenses) / avg_income
            if avg_income > 0 else 0
        )

        cash_flow_stability = 1 - (
            np.std(balances) / (np.mean(balances) + 1)
        )

        financial_stability_score = self._calculate_stability_score(
            savings_ratio,
            cash_flow_stability,
            avg_balance
        )

        return {
            "avg_monthly_balance": float(avg_balance),
            "avg_monthly_income": float(avg_income),
            "avg_monthly_expenses": float(avg_expenses),
            "savings_ratio": float(savings_ratio),
            "transaction_frequency": len(transactions),
            "cash_flow_stability": float(cash_flow_stability),
            "financial_stability_score": float(financial_stability_score)
        }

    # -------------------------------
    # CSV / EXCEL METRICS
    # -------------------------------

    def _calculate_metrics_from_df(self, df: pd.DataFrame):

        credits = df["Credit"].dropna() if "Credit" in df.columns else []
        debits = df["Debit"].dropna() if "Debit" in df.columns else []
        balance = df["Balance"].dropna() if "Balance" in df.columns else []

        avg_income = credits.mean() if len(credits) > 0 else 0
        avg_expenses = debits.mean() if len(debits) > 0 else 0
        avg_balance = balance.mean() if len(balance) > 0 else 0

        savings_ratio = (
            (avg_income - avg_expenses) / avg_income
            if avg_income > 0 else 0
        )

        transaction_frequency = len(df)

        cash_flow_stability = 1 - (
            balance.std() / (balance.mean() + 1)
        ) if len(balance) > 0 else 0

        financial_stability_score = self._calculate_stability_score(
            savings_ratio,
            cash_flow_stability,
            avg_balance
        )

        return {
            "avg_monthly_balance": float(avg_balance),
            "avg_monthly_income": float(avg_income),
            "avg_monthly_expenses": float(avg_expenses),
            "savings_ratio": float(savings_ratio),
            "transaction_frequency": int(transaction_frequency),
            "cash_flow_stability": float(cash_flow_stability),
            "financial_stability_score": float(financial_stability_score)
        }

    # -------------------------------
    # FINANCIAL STABILITY SCORE
    # -------------------------------

    def _calculate_stability_score(
        self,
        savings_ratio: float,
        cash_flow_stability: float,
        avg_balance: float
    ):

        score = (
            savings_ratio * 0.4 +
            cash_flow_stability * 0.3 +
            min(avg_balance / 100000, 1) * 0.3
        )

        return max(0, min(1, score))

    # -------------------------------
    # DEFAULT METRICS
    # -------------------------------

    def _default_metrics(self):

        return {
            "avg_monthly_balance": 0,
            "avg_monthly_income": 0,
            "avg_monthly_expenses": 0,
            "savings_ratio": 0,
            "transaction_frequency": 0,
            "cash_flow_stability": 0,
            "financial_stability_score": 0
        }

    # -------------------------------
    # MANUAL ENTRY
    # -------------------------------

    def analyze_manual_entry(self, data: Dict):

        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        savings = data.get("savings", 0)
        existing_loans = data.get("existing_loans", 0)
        account_balance = data.get("account_balance", 0)

        savings_ratio = (
            (monthly_income - monthly_expenses) / monthly_income
            if monthly_income > 0 else 0
        )
        # Ensure savings_ratio is non-negative
        savings_ratio = max(0, savings_ratio)

        cash_flow_stability = 0.7 if savings > monthly_expenses else 0.4

        financial_stability_score = self._calculate_stability_score(
            savings_ratio,
            cash_flow_stability,
            account_balance
        )

        # Estimate transaction frequency based on income and expenses
        # Higher income/expenses typically means more transactions
        estimated_transactions = min(100, max(20, int(monthly_expenses / 1000) + 30))

        return {
            "avg_monthly_balance": float(account_balance),
            "avg_monthly_income": float(monthly_income),
            "avg_monthly_expenses": float(monthly_expenses),
            "savings_ratio": float(savings_ratio),
            "transaction_frequency": estimated_transactions,
            "cash_flow_stability": float(cash_flow_stability),
            "financial_stability_score": float(financial_stability_score),
            "existing_loans": float(existing_loans),
            "savings": float(savings)
        }