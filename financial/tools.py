from typing import List, Optional
import uuid

from tau2.domains.financial.data_model import (
    FinancialDB,
    Customer,
    Account,
    Transaction,
    SwiftMessage,
)
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool

class FinancialTools(ToolKitBase):
    """All the tools for the financial domain."""

    db: FinancialDB

    def __init__(self, db: FinancialDB) -> None:
        super().__init__(db)

    def _get_customer(self, customer_id: str) -> Customer:
        """Get customer from database."""
        if customer_id not in self.db.customers:
            raise ValueError(f"Customer {customer_id} not found")
        return self.db.customers[customer_id]

    def _get_account(self, account_id: str) -> Account:
        """Get account from database."""
        if account_id not in self.db.accounts:
            raise ValueError(f"Account {account_id} not found")
        return self.db.accounts[account_id]

    def _get_transaction(self, transaction_id: str) -> Transaction:
        """Get transaction from database."""
        if transaction_id not in self.db.transactions:
            raise ValueError(f"Transaction {transaction_id} not found")
        return self.db.transactions[transaction_id]

    @is_tool(ToolType.READ)
    def get_customer_details(self, customer_id: str) -> Customer:
        """
        Get the details of a customer.

        Args:
            customer_id: The ID of the customer to get details for.

        Returns:
            The customer details.
        """
        return self._get_customer(customer_id)

    @is_tool(ToolType.READ)
    def get_account_balance(self, account_id: str) -> float:
        """
        Get the balance of an account.

        Args:
            account_id: The ID of the account to get the balance for.

        Returns:
            The account balance.
        """
        account = self._get_account(account_id)
        return account.balance

    @is_tool(ToolType.WRITE)
    def create_transaction(
        self, from_account_id: str, to_account_id: str, amount: float, currency: str
    ) -> Transaction:
        """
        Create a new transaction.

        Args:
            from_account_id: The ID of the account from which the transaction is made.
            to_account_id: The ID of the account to which the transaction is made.
            amount: The transaction amount.
            currency: The currency of the transaction.

        Returns:
            The created transaction.
        """
        from_account = self._get_account(from_account_id)
        to_account = self._get_account(to_account_id)

        if from_account.balance < amount:
            raise ValueError("Insufficient funds")

        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            transaction_id=transaction_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            currency=currency,
            status="pending",
        )

        self.db.transactions[transaction_id] = transaction
        return transaction

    @is_tool(ToolType.WRITE)
    def clear_transaction(self, transaction_id: str) -> Transaction:
        """
        Clear a transaction.

        Args:
            transaction_id: The ID of the transaction to clear.

        Returns:
            The cleared transaction.
        """
        transaction = self._get_transaction(transaction_id)
        if transaction.status != "pending":
            raise ValueError(f"Transaction {transaction_id} is not pending")

        from_account = self._get_account(transaction.from_account_id)
        to_account = self._get_account(transaction.to_account_id)

        from_account.balance -= transaction.amount
        to_account.balance += transaction.amount

        transaction.status = "cleared"
        return transaction

    @is_tool(ToolType.WRITE)
    def flag_transaction_for_fraud(self, transaction_id: str) -> Transaction:
        """
        Flag a transaction for fraud.

        Args:
            transaction_id: The ID of the transaction to flag.

        Returns:
            The flagged transaction.
        """
        transaction = self._get_transaction(transaction_id)
        transaction.status = "flagged"
        return transaction

    @is_tool(ToolType.READ)
    def get_transaction_status(self, transaction_id: str) -> str:
        """
        Get the status of a transaction.

        Args:
            transaction_id: The ID of the transaction to get the status for.

        Returns:
            The status of the transaction.
        """
        transaction = self._get_transaction(transaction_id)
        return transaction.status
