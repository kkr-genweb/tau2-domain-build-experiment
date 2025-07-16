import json
from typing import Optional

from tau2.data_model.tasks import Task
from tau2.domains.financial.data_model import FinancialDB
from tau2.domains.financial.tools import FinancialTools
from tau2.domains.financial.utils import (
    FINANCIAL_DB_PATH,
    FINANCIAL_POLICY_PATH,
    FINANCIAL_TASK_SET_PATH,
)
from tau2.environment.environment import Environment


def get_environment(
    db: Optional[FinancialDB] = None,
    solo_mode: bool = False,
) -> Environment:
    if solo_mode:
        raise ValueError("Financial domain does not support solo mode")
    if db is None:
        db = FinancialDB.load(FINANCIAL_DB_PATH)
    tools = FinancialTools(db)
    with open(FINANCIAL_POLICY_PATH, "r") as fp:
        policy = fp.read()
    return Environment(
        domain_name="financial",
        policy=policy,
        tools=tools,
    )


def get_tasks() -> list[Task]:
    with open(FINANCIAL_TASK_SET_PATH, "r") as fp:
        tasks = json.load(fp)
    return [Task.model_validate(task) for task in tasks]
