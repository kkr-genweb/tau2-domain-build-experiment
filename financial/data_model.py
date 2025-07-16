from typing import Annotated, Any, Dict, List, Literal, Optional, Union
import datetime

from pydantic import BaseModel, Field, validator

from tau2.domains.financial.utils import FINANCIAL_DB_PATH
from tau2.environment.db import DB

class Customer(BaseModel):
    customer_id: str = Field(description="Unique identifier for the customer")
    name: str = Field(description="Customer's name")
    address: str = Field(description="Customer's address")
    email: str = Field(description="Customer's email address")
    phone: str = Field(description="Customer's phone number")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Timestamp when customer was created"
    )
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class Account(BaseModel):
    account_id: str = Field(description="Unique identifier for the account")
    customer_id: str = Field(description="ID of the customer who owns the account")
    account_type: Literal["checking", "savings", "investment", "loan"] = Field(description="Type of account")
    balance: float = Field(description="Account balance")
    currency: str = Field(description="Currency of the account (e.g., USD, EUR)")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Timestamp when account was created"
    )
    status: Literal["active", "suspended", "closed"] = Field(
        default="active",
        description="Account status"
    )
    
    @validator('balance')
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v

class SwiftMessage(BaseModel):
    message_id: str = Field(description="Unique identifier for the SWIFT message")
    sender_bic: str = Field(description="BIC of the sending financial institution")
    receiver_bic: str = Field(description="BIC of the receiving financial institution")
    message_type: str = Field(description="SWIFT message type (e.g., MT103)")
    content: str = Field(description="Content of the SWIFT message")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Timestamp when SWIFT message was created"
    )
    processed: bool = Field(default=False, description="Whether the message has been processed")

class Transaction(BaseModel):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    from_account_id: str = Field(description="ID of the account from which the transaction is made")
    to_account_id: str = Field(description="ID of the account to which the transaction is made")
    amount: float = Field(description="Transaction amount")
    currency: str = Field(description="Currency of the transaction")
    status: Literal["pending", "cleared", "rejected", "flagged"] = Field(description="Status of the transaction")
    swift_message_id: Optional[str] = Field(None, description="ID of the associated SWIFT message")
    fraud_score: Optional[float] = Field(None, description="Fraud score of the transaction (0.0 to 1.0)")
    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.now,
        description="Timestamp when transaction was created"
    )
    processed_at: Optional[datetime.datetime] = Field(
        None,
        description="Timestamp when transaction was processed"
    )
    description: Optional[str] = Field(None, description="Transaction description")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Transaction amount must be positive')
        return v
    
    @validator('fraud_score')
    def validate_fraud_score(cls, v):
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError('Fraud score must be between 0.0 and 1.0')
        return v

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
