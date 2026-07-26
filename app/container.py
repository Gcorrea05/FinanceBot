from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.database.session import get_session
from app.domain.budget_plan import BudgetPlanValidator
from app.domain.expense_validator import ExpenseValidator
from app.domain.installment_plan import InstallmentPlanBuilder
from app.domain.shared_expense import SharedExpenseSplitter
from app.repositories.automation_repository import AutomationRepository
from app.repositories.budget_expense_repository import BudgetExpenseRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.import_repository import ImportRepository
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.receivable_repository import ReceivableRepository
from app.repositories.report_repository import ReportRepository
from app.services.automation_service import AutomationService
from app.services.budget_service import BudgetService
from app.services.expense_editor_service import ExpenseEditorService
from app.services.expense_management_service import ExpenseManagementService
from app.services.expense_query_service import ExpenseQueryService
from app.services.expense_service import ExpenseService
from app.services.import_service import ImportService
from app.services.intelligence_service import IntelligenceService
from app.services.lookup_service import LookupService
from app.services.monthly_export_service import MonthlyExportService
from app.services.receivable_service import ReceivableService
from app.services.report_service import ReportService


class Container:
    def __init__(self, session: Session):
        self.session = session
        self.expense_repository = ExpenseRepository(session)
        self.category_repository = CategoryRepository(session)
        self.payment_repository = PaymentMethodRepository(session)
        self.person_repository = PersonRepository(session)
        self.receivable_repository = ReceivableRepository(session)
        self.budget_repository = BudgetRepository(session)
        self.budget_expense_repository = BudgetExpenseRepository(session)
        self.report_repository = ReportRepository(session)
        self.import_repository = ImportRepository(session)
        self.automation_repository = AutomationRepository(session)

        self.lookup_service = LookupService(
            category_repository=self.category_repository,
            payment_method_repository=self.payment_repository,
        )
        self.expense_validator = ExpenseValidator()
        self.installment_builder = InstallmentPlanBuilder()
        self.shared_splitter = SharedExpenseSplitter()

        self.expense_service = ExpenseService(
            expense_repository=self.expense_repository,
            lookup_service=self.lookup_service,
            validator=self.expense_validator,
            person_repository=self.person_repository,
            installment_builder=self.installment_builder,
            shared_splitter=self.shared_splitter,
        )
        self.expense_editor_service = ExpenseEditorService(
            expense_repository=self.expense_repository,
            lookup_service=self.lookup_service,
            validator=self.expense_validator,
            person_repository=self.person_repository,
            installment_builder=self.installment_builder,
            shared_splitter=self.shared_splitter,
        )
        self.expense_query_service = ExpenseQueryService(expense_repository=self.expense_repository)
        self.expense_management_service = ExpenseManagementService(expense_repository=self.expense_repository)
        self.receivable_service = ReceivableService(
            receivable_repository=self.receivable_repository,
            person_repository=self.person_repository,
        )
        self.budget_service = BudgetService(
            budget_repository=self.budget_repository,
            expense_repository=self.budget_expense_repository,
            validator=BudgetPlanValidator(),
        )
        self.report_service = ReportService(repository=self.report_repository)
        self.monthly_export_service = MonthlyExportService(
            report_repository=self.report_repository,
            receivable_repository=self.receivable_repository,
        )
        self.automation_service = AutomationService(
            repository=self.automation_repository,
            budget_service=self.budget_service,
        )
        self.intelligence_service = IntelligenceService(
            repository=self.report_repository,
            report_service=self.report_service,
            budget_service=self.budget_service,
        )
        self.import_service = ImportService(
            repository=self.import_repository,
            expense_service=self.expense_service,
            lookup_service=self.lookup_service,
        )


@contextmanager
def container_context() -> Iterator[Container]:
    session = get_session()
    try:
        yield Container(session)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
