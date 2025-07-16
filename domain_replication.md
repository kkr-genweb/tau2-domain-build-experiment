# Domain Replication File

This file serves as a template for creating new domains. It is based on the structure of the `airline` domain.

## Directory Structure

A new domain should have the following directory structure:

```
<domain_name>/
├── data_model.py
├── db.json (or db.toml for complex data)
├── environment.py
├── policy.md
├── policy_solo.md (optional - for solo mode support)
├── tasks.json
├── tools.py
├── utils.py
└── test_tools_<domain_name>.py (recommended)
```

**Note:** Some domains may have additional files like user-specific models, workflows, or manuals depending on complexity.

## File Contents

### `data_model.py`

This file defines the data structures and models for the domain using `pydantic`. It should contain models for all the key entities in the domain.

```python
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
import datetime  # Add if using date/time fields
import uuid  # Add if generating UUIDs
from enum import Enum  # Add if using enums

from pydantic import BaseModel, Field

from tau2.domains.<domain_name>.utils import <DOMAIN_NAME>_DB_PATH
from tau2.environment.db import DB

# Define your data models here, using pydantic.
# For example:

class Customer(BaseModel):
    customer_id: str = Field(description="Unique identifier for the customer")
    name: str = Field(description="Customer's name")
    # ... other customer fields

class Account(BaseModel):
    account_id: str = Field(description="Unique identifier for the account")
    customer_id: str = Field(description="ID of the customer who owns the account")
    balance: float = Field(description="Account balance")
    # ... other account fields

class Transaction(BaseModel):
    transaction_id: str = Field(description="Unique identifier for the transaction")
    account_id: str = Field(description="ID of the account for the transaction")
    amount: float = Field(description="Transaction amount")
    # ... other transaction fields

class <DomainName>DB(DB):
    """Database of all customers, accounts, and transactions."""

    # Choose Dict[str, Model] for indexed access or List[Model] for sequential access
    customers: Dict[str, Customer] = Field(
        description="Dictionary of all customers indexed by customer ID"
    )
    accounts: Dict[str, Account] = Field(
        description="Dictionary of all accounts indexed by account ID"
    )
    transactions: Dict[str, Transaction] = Field(
        description="Dictionary of all transactions indexed by transaction ID"
    )

    def get_statistics(self) -> dict[str, Any]:
        """Get the statistics of the database."""
        num_customers = len(self.customers)
        num_accounts = len(self.accounts)
        num_transactions = len(self.transactions)
        return {
            "num_customers": num_customers,
            "num_accounts": num_accounts,
            "num_transactions": num_transactions,
        }


def get_db():
    return <DomainName>DB.load(<DOMAIN_NAME>_DB_PATH)

```

### `tools.py`

This file implements the tools and functions that can be used to interact with the domain.

```python
from typing import List, Optional
import uuid  # Add if generating UUIDs

from tau2.domains.<domain_name>.data_model import (
    <DomainName>DB,
    Customer,
    Account,
    Transaction,
)
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool

class <DomainName>Tools(ToolKitBase):
    """All the tools for the <domain_name> domain."""

    db: <DomainName>DB

    def __init__(self, db: <DomainName>DB) -> None:
        super().__init__(db)

    # Helper methods for getting entities (recommended pattern)
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

    # Define your tools here.
    # For example:

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

    @is_tool(ToolType.WRITE)
    def create_transaction(
        self, account_id: str, amount: float
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            account_id: The ID of the account for the transaction.
            amount: The transaction amount.
            
        Returns:
            The created transaction.
        """
        # Validate account exists
        account = self._get_account(account_id)
        
        # Generate unique ID
        transaction_id = str(uuid.uuid4())
        
        # Create transaction
        transaction = Transaction(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            # ... other fields
        )
        
        # Store in database
        self.db.transactions[transaction_id] = transaction
        return transaction
```

### `policy.md`

This file defines the policies and rules for the domain.

```markdown
# <DomainName> Agent Policy

As a <domain_name> agent, you can help users with...

## Domain Basic

### Customer
...

### Account
...

### Transaction
...
```

### `db.json`

This file contains the database for the domain in JSON format.

```json
{
  "customers": {},
  "accounts": {},
  "transactions": {}
}
```

### `tasks.json`

This file contains a set of tasks for the domain in JSON format.

```json
[
  {
    "task_id": "<domain_name>-0",
    "goal": "...",
    "user_dialogue": [
      {
        "role": "user",
        "content": "..."
      }
    ]
  }
]
```

### `environment.py`

This file creates and configures the domain's environment.

```python
import json
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.<domain_name>.data_model import <DomainName>DB
from tau2.domains.<domain_name>.tools import <DomainName>Tools
from tau2.domains.<domain_name>.utils import (
    <DOMAIN_NAME>_DB_PATH,
    <DOMAIN_NAME>_POLICY_PATH,
    <DOMAIN_NAME>_TASK_SET_PATH,
)
from tau2.environment.environment import Environment


def get_environment(
    db: Optional[<DomainName>DB] = None,
    solo_mode: bool = False,
) -> Environment:
    if solo_mode:
        raise ValueError("<DomainName> domain does not support solo mode")
    if db is None:
        db = <DomainName>DB.load(<DOMAIN_NAME>_DB_PATH)
    tools = <DomainName>Tools(db)
    with open(<DOMAIN_NAME>_POLICY_PATH, "r") as fp:
        policy = fp.read()
    return Environment(
        domain_name="<domain_name>",
        policy=policy,
        tools=tools,
    )


def get_tasks() -> list[Task]:
    with open(<DOMAIN_NAME>_TASK_SET_PATH, "r") as fp:
        tasks = json.load(fp)
    return [Task.model_validate(task) for task in tasks]

```

### `utils.py`

This file contains utility functions and constants for the domain.

```python
from pathlib import Path

<DOMAIN_NAME>_ROOT_PATH = Path(__file__).parent
<DOMAIN_NAME>_DB_PATH = <DOMAIN_NAME>_ROOT_PATH / "db.json"  # or "db.toml" for complex data
<DOMAIN_NAME>_POLICY_PATH = <DOMAIN_NAME>_ROOT_PATH / "policy.md"
<DOMAIN_NAME>_TASK_SET_PATH = <DOMAIN_NAME>_ROOT_PATH / "tasks.json"

```

## Testing

### `test_tools_<domain_name>.py`

This file contains unit tests for the domain tools (recommended for quality assurance).

```python
import pytest
from tau2.domains.<domain_name>.data_model import <DomainName>DB, Customer, Account, Transaction
from tau2.domains.<domain_name>.tools import <DomainName>Tools

class Test<DomainName>Tools:
    def setup_method(self):
        """Set up test fixtures."""
        self.db = <DomainName>DB(
            customers={
                "cust_1": Customer(
                    customer_id="cust_1",
                    name="Test Customer",
                    # ... other fields
                )
            },
            accounts={
                "acc_1": Account(
                    account_id="acc_1",
                    customer_id="cust_1",
                    balance=1000.0,
                    # ... other fields
                )
            },
            transactions={}
        )
        self.tools = <DomainName>Tools(self.db)

    def test_get_customer_details(self):
        """Test getting customer details."""
        customer = self.tools.get_customer_details("cust_1")
        assert customer.customer_id == "cust_1"
        assert customer.name == "Test Customer"

    def test_get_customer_details_not_found(self):
        """Test getting non-existent customer."""
        with pytest.raises(ValueError, match="Customer not_found not found"):
            self.tools.get_customer_details("not_found")

    def test_create_transaction(self):
        """Test creating a transaction."""
        transaction = self.tools.create_transaction("acc_1", 100.0)
        assert transaction.account_id == "acc_1"
        assert transaction.amount == 100.0
        assert transaction.transaction_id in self.db.transactions

```
