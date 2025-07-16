# Domain Replication File

This file serves as a template for creating new domains. It is based on the structure of the `airline` domain.

## Directory Structure

A new domain should have the following directory structure:

```
<domain_name>/
├── data_model.py
├── db.json
├── environment.py
├── policy.md
├── tasks.json
└── tools.py
```

## File Contents

### `data_model.py`

This file defines the data structures and models for the domain using `pydantic`. It should contain models for all the key entities in the domain.

```python
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

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

    # Define your tools here.
    # For example:

    @is_tool(ToolType.READ)
    def get_customer_details(self, customer_id: str) -> Customer:
        """Get the details of a customer."""
        if customer_id not in self.db.customers:
            raise ValueError(f"Customer {customer_id} not found")
        return self.db.customers[customer_id]

    @is_tool(ToolType.WRITE)
    def create_transaction(
        self, account_id: str, amount: float
    ) -> Transaction:
        """Create a new transaction."""
        # ... implementation for creating a transaction
        pass
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
<DOMAIN_NAME>_DB_PATH = <DOMAIN_NAME>_ROOT_PATH / "db.json"
<DOMAIN_NAME>_POLICY_PATH = <DOMAIN_NAME>_ROOT_PATH / "policy.md"
<DOMAIN_NAME>_TASK_SET_PATH = <DOMAIN_NAME>_ROOT_PATH / "tasks.json"

```
