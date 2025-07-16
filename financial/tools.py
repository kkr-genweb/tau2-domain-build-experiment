from typing import List, Optional
import uuid
import datetime

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

        # Update balances
        from_account.balance -= transaction.amount
        to_account.balance += transaction.amount

        # Update transaction status and timestamp
        transaction.status = "cleared"
        transaction.processed_at = datetime.datetime.now()
        
        # Update the accounts in the database
        self.db.accounts[transaction.from_account_id] = from_account
        self.db.accounts[transaction.to_account_id] = to_account
        
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

    @is_tool(ToolType.READ)
    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        """
        Get all accounts for a customer.

        Args:
            customer_id: The ID of the customer.

        Returns:
            List of accounts owned by the customer.
        """
        customer = self._get_customer(customer_id)
        accounts = []
        for account in self.db.accounts.values():
            if account.customer_id == customer_id:
                accounts.append(account)
        return accounts

    @is_tool(ToolType.READ)
    def get_account_transactions(self, account_id: str) -> List[Transaction]:
        """
        Get all transactions for an account.

        Args:
            account_id: The ID of the account.

        Returns:
            List of transactions involving the account.
        """
        account = self._get_account(account_id)
        transactions = []
        for transaction in self.db.transactions.values():
            if (transaction.from_account_id == account_id or 
                transaction.to_account_id == account_id):
                transactions.append(transaction)
        return transactions

    @is_tool(ToolType.WRITE)
    def create_swift_message(
        self, sender_bic: str, receiver_bic: str, message_type: str, content: str
    ) -> SwiftMessage:
        """
        Create a new SWIFT message.

        Args:
            sender_bic: BIC of the sending financial institution.
            receiver_bic: BIC of the receiving financial institution.
            message_type: SWIFT message type (e.g., MT103).
            content: Content of the SWIFT message.

        Returns:
            The created SWIFT message.
        """
        message_id = str(uuid.uuid4())
        swift_message = SwiftMessage(
            message_id=message_id,
            sender_bic=sender_bic,
            receiver_bic=receiver_bic,
            message_type=message_type,
            content=content,
        )
        
        self.db.swift_messages[message_id] = swift_message
        return swift_message

    @is_tool(ToolType.READ)
    def get_swift_message(self, message_id: str) -> SwiftMessage:
        """
        Get a SWIFT message by ID.

        Args:
            message_id: The ID of the SWIFT message.

        Returns:
            The SWIFT message.
        """
        if message_id not in self.db.swift_messages:
            raise ValueError(f"SWIFT message {message_id} not found")
        return self.db.swift_messages[message_id]

    @is_tool(ToolType.WRITE)
    def link_swift_message_to_transaction(
        self, transaction_id: str, message_id: str
    ) -> Transaction:
        """
        Link a SWIFT message to a transaction.

        Args:
            transaction_id: The ID of the transaction.
            message_id: The ID of the SWIFT message.

        Returns:
            The updated transaction.
        """
        transaction = self._get_transaction(transaction_id)
        swift_message = self.get_swift_message(message_id)
        
        transaction.swift_message_id = message_id
        return transaction

    @is_tool(ToolType.WRITE)
    def set_fraud_score(self, transaction_id: str, fraud_score: float) -> Transaction:
        """
        Set the fraud score for a transaction.

        Args:
            transaction_id: The ID of the transaction.
            fraud_score: The fraud score (0.0 to 1.0).

        Returns:
            The updated transaction.
        """
        if not 0.0 <= fraud_score <= 1.0:
            raise ValueError("Fraud score must be between 0.0 and 1.0")
        
        transaction = self._get_transaction(transaction_id)
        transaction.fraud_score = fraud_score
        return transaction
