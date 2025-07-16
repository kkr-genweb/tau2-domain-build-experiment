from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from tau2.domains.financial.utils import FINANCIAL_DB_PATH
from tau2.environment.db import DB

class Customer(BaseModel):
    customer_id: str = Field(description="Unique identifier for the customer")
    name: str = Field(description="Customer's name")
    address: str = Field(description="Customer's address")
    email: str = Field(description="Customer's email address")
    phone: str = Field(description="Customer's phone number")

class Account(BaseModel):
    account_id: str = Field(description="Unique identifier for the account")
    customer_id: str = Field(description="ID of the customer who owns the account")
    account_type: Literal["checking", "savings"] = Field(description="Type of account")
    balance: float = Field(description="Account balance")
    currency: str = Field(description="Currency of the account (e.g., USD, EUR)")

class SwiftMessage(BaseModel):
    message_id: str = Field(description="Unique identifier for the SWIFT message")
    sender_bic: str = Field(description="BIC of the sending financial institution")
    receiver_bic: str = Field(description="BIC of the receiving financial institution")
    message_type: str = Field(description="SWIFT message type (e.g., MT103)")
    content: str = Field(description="Content of the SWIFT message")

class Transaction(BaseModel):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    from_account_id: str = Field(description="ID of the account from which the transaction is made")
    to_account_id: str = Field(description="ID of the account to which the transaction is made")
    amount: float = Field(description="Transaction amount")
    currency: str = Field(description="Currency of the transaction")
    status: Literal["pending", "cleared", "rejected", "flagged"] = Field(description="Status of the transaction")
    swift_message_id: Optional[str] = Field(None, description="ID of the associated SWIFT message")
    fraud_score: Optional[float] = Field(None, description="Fraud score of the transaction")

class FinancialDB(DB):
    """Database of all customers, accounts, and transactions."""

    customers: Dict[str, Customer] = Field(
        description="Dictionary of all customers indexed by customer ID"
    )
    accounts: Dict[str, Account] = Field(
        description="Dictionary of all accounts indexed by account ID"
    )
    transactions: Dict[str, Transaction] = Field(
        description="Dictionary of all transactions indexed by transaction ID"
    )
    swift_messages: Dict[str, SwiftMessage] = Field(
        description="Dictionary of all SWIFT messages indexed by message ID"
    )

    def get_statistics(self) -> dict[str, Any]:
        """Get the statistics of the database."""
        num_customers = len(self.customers)
        num_accounts = len(self.accounts)
        num_transactions = len(self.transactions)
        num_swift_messages = len(self.swift_messages)
        return {
            "num_customers": num_customers,
            "num_accounts": num_accounts,
            "num_transactions": num_transactions,
            "num_swift_messages": num_swift_messages,
        }

def get_db():
    return FinancialDB.load(FINANCIAL_DB_PATH)
