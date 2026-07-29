from app.database.foreign_keys import install_sqlite_foreign_keys
from app.database.models.automation import AutomationDelivery, AutomationSettings
from app.database.models.budget import Budget
from app.database.models.category import Category
from app.database.models.domain_event import DomainEventRecord
from app.database.models.expense import Expense
from app.database.models.expense_installment import ExpenseInstallment
from app.database.models.expense_person import ExpensePerson
from app.database.models.import_batch import ImportBatch, ImportRow
from app.database.models.import_job import ImportJob
from app.database.models.payment_method import PaymentMethod
from app.database.models.person import Person

install_sqlite_foreign_keys()

__all__ = [
    "AutomationDelivery",
    "AutomationSettings",
    "Budget",
    "Category",
    "DomainEventRecord",
    "Expense",
    "ExpenseInstallment",
    "ExpensePerson",
    "ImportBatch",
    "ImportJob",
    "ImportRow",
    "PaymentMethod",
    "Person",
]
