import pytest
from tau2.domains.financial.data_model import (
    FinancialDB,
    Customer,
    Account,
    Transaction,
    SwiftMessage,
)
from tau2.domains.financial.tools import FinancialTools


class TestFinancialTools:
    def setup_method(self):
        """Set up test fixtures."""
        self.db = FinancialDB(
            customers={
                "cust_1": Customer(
                    customer_id="cust_1",
                    name="John Doe",
                    address="123 Main St",
                    email="john@example.com",
                    phone="555-0123",
                ),
                "cust_2": Customer(
                    customer_id="cust_2",
                    name="Jane Smith",
                    address="456 Oak Ave",
                    email="jane@example.com",
                    phone="555-0456",
                ),
            },
            accounts={
                "acc_1": Account(
                    account_id="acc_1",
                    customer_id="cust_1",
                    account_type="checking",
                    balance=1000.0,
                    currency="USD",
                ),
                "acc_2": Account(
                    account_id="acc_2",
                    customer_id="cust_2",
                    account_type="savings",
                    balance=500.0,
                    currency="USD",
                ),
            },
            transactions={},
            swift_messages={},
        )
        self.tools = FinancialTools(self.db)

    def test_get_customer_details(self):
        """Test getting customer details."""
        customer = self.tools.get_customer_details("cust_1")
        assert customer.customer_id == "cust_1"
        assert customer.name == "John Doe"
        assert customer.email == "john@example.com"

    def test_get_customer_details_not_found(self):
        """Test getting non-existent customer."""
        with pytest.raises(ValueError, match="Customer not_found not found"):
            self.tools.get_customer_details("not_found")

    def test_get_account_balance(self):
        """Test getting account balance."""
        balance = self.tools.get_account_balance("acc_1")
        assert balance == 1000.0

    def test_get_account_balance_not_found(self):
        """Test getting balance for non-existent account."""
        with pytest.raises(ValueError, match="Account not_found not found"):
            self.tools.get_account_balance("not_found")

    def test_create_transaction_success(self):
        """Test creating a valid transaction."""
        transaction = self.tools.create_transaction("acc_1", "acc_2", 100.0, "USD")
        assert transaction.from_account_id == "acc_1"
        assert transaction.to_account_id == "acc_2"
        assert transaction.amount == 100.0
        assert transaction.currency == "USD"
        assert transaction.status == "pending"
        assert transaction.transaction_id in self.db.transactions

    def test_create_transaction_insufficient_funds(self):
        """Test creating transaction with insufficient funds."""
        with pytest.raises(ValueError, match="Insufficient funds"):
            self.tools.create_transaction("acc_1", "acc_2", 2000.0, "USD")

    def test_create_transaction_invalid_from_account(self):
        """Test creating transaction with invalid from account."""
        with pytest.raises(ValueError, match="Account invalid not found"):
            self.tools.create_transaction("invalid", "acc_2", 100.0, "USD")

    def test_create_transaction_invalid_to_account(self):
        """Test creating transaction with invalid to account."""
        with pytest.raises(ValueError, match="Account invalid not found"):
            self.tools.create_transaction("acc_1", "invalid", 100.0, "USD")

    def test_clear_transaction_success(self):
        """Test clearing a pending transaction."""
        # Create a transaction first
        transaction = self.tools.create_transaction("acc_1", "acc_2", 100.0, "USD")
        
        # Store initial balances
        initial_from_balance = self.db.accounts["acc_1"].balance
        initial_to_balance = self.db.accounts["acc_2"].balance
        
        # Clear the transaction
        cleared_transaction = self.tools.clear_transaction(transaction.transaction_id)
        
        # Verify transaction status
        assert cleared_transaction.status == "cleared"
        
        # Verify balances were updated
        assert self.db.accounts["acc_1"].balance == initial_from_balance - 100.0
        assert self.db.accounts["acc_2"].balance == initial_to_balance + 100.0

    def test_clear_transaction_not_pending(self):
        """Test clearing a non-pending transaction."""
        # Create and clear a transaction
        transaction = self.tools.create_transaction("acc_1", "acc_2", 100.0, "USD")
        self.tools.clear_transaction(transaction.transaction_id)
        
        # Try to clear again
        with pytest.raises(ValueError, match="Transaction .* is not pending"):
            self.tools.clear_transaction(transaction.transaction_id)

    def test_clear_transaction_not_found(self):
        """Test clearing non-existent transaction."""
        with pytest.raises(ValueError, match="Transaction not_found not found"):
            self.tools.clear_transaction("not_found")

    def test_flag_transaction_for_fraud(self):
        """Test flagging a transaction for fraud."""
        # Create a transaction first
        transaction = self.tools.create_transaction("acc_1", "acc_2", 100.0, "USD")
        
        # Flag it for fraud
        flagged_transaction = self.tools.flag_transaction_for_fraud(
            transaction.transaction_id
        )
        
        # Verify status
        assert flagged_transaction.status == "flagged"

    def test_flag_transaction_for_fraud_not_found(self):
        """Test flagging non-existent transaction for fraud."""
        with pytest.raises(ValueError, match="Transaction not_found not found"):
            self.tools.flag_transaction_for_fraud("not_found")

    def test_get_transaction_status(self):
        """Test getting transaction status."""
        # Create a transaction
        transaction = self.tools.create_transaction("acc_1", "acc_2", 100.0, "USD")
        
        # Get status
        status = self.tools.get_transaction_status(transaction.transaction_id)
        assert status == "pending"
        
        # Clear and check again
        self.tools.clear_transaction(transaction.transaction_id)
        status = self.tools.get_transaction_status(transaction.transaction_id)
        assert status == "cleared"

    def test_get_transaction_status_not_found(self):
        """Test getting status for non-existent transaction."""
        with pytest.raises(ValueError, match="Transaction not_found not found"):
            self.tools.get_transaction_status("not_found")