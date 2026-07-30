from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.database.session import get_session
from app.domain.budget_plan import BudgetPlanValidator
from app.domain.expense_validator import ExpenseValidator
from app.domain.installment_plan import InstallmentPlanBuilder
from app.domain.shared_expense import SharedExpenseSplitter
from app.events import EventBus, EventDispatcher, EventPublisher
from app.events.handlers import LoggingEventHandler, ProjectionRefreshHandler
from app.repositories.automation_repository import AutomationRepository
from app.repositories.budget_expense_repository import BudgetExpenseRepository
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.event_repository import EventRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.import_repository import ImportRepository
from app.repositories.financial_profile_repository import FinancialProfileRepository
from app.repositories.recurring_expense_repository import RecurringExpenseRepository
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.receivable_repository import ReceivableRepository
from app.repositories.report_repository import ReportRepository
from app.services.automation_service import AutomationService
from app.services.budget_service import BudgetService
from app.services.dashboard_service import DashboardService
from app.services.event_aware import (
    EventAwareBudgetService,
    EventAwareExpenseEditorService,
    EventAwareExpenseManagementService,
    EventAwareExpenseService,
    EventAwareImportService,
    EventAwareReceivableService,
)
from app.services.expense_editor_service import ExpenseEditorService
from app.services.expense_management_service import ExpenseManagementService
from app.services.expense_query_service import ExpenseQueryService
from app.services.expense_service import ExpenseService
from app.services.import_service import ImportService
from app.services.future_planning_service import FuturePlanningService
from app.services.recurring_expense_service import RecurringExpenseService
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
        self.financial_profile_repository = FinancialProfileRepository(session)
        self.recurring_expense_repository = RecurringExpenseRepository(session)
        self.automation_repository = AutomationRepository(session)
        self.event_repository = EventRepository(session)

        self.lookup_service = LookupService(
            category_repository=self.category_repository,
            payment_method_repository=self.payment_repository,
        )
        validator = ExpenseValidator()
        installment_builder = InstallmentPlanBuilder()
        shared_splitter = SharedExpenseSplitter()

        base_expense_service = ExpenseService(
            expense_repository=self.expense_repository,
            lookup_service=self.lookup_service,
            validator=validator,
            person_repository=self.person_repository,
            installment_builder=installment_builder,
            shared_splitter=shared_splitter,
        )
        base_editor_service = ExpenseEditorService(
            expense_repository=self.expense_repository,
            lookup_service=self.lookup_service,
            validator=validator,
            person_repository=self.person_repository,
            installment_builder=installment_builder,
            shared_splitter=shared_splitter,
        )
        base_management_service = ExpenseManagementService(
            expense_repository=self.expense_repository
        )
        base_receivable_service = ReceivableService(
            receivable_repository=self.receivable_repository,
            person_repository=self.person_repository,
        )
        base_budget_service = BudgetService(
            budget_repository=self.budget_repository,
            expense_repository=self.budget_expense_repository,
            validator=BudgetPlanValidator(),
        )
        self.report_service = ReportService(
            repository=self.report_repository
        )
        self.intelligence_service = IntelligenceService(
            repository=self.report_repository,
            report_service=self.report_service,
            budget_service=base_budget_service,
        )

        self.event_bus = EventBus()
        self.event_bus.subscribe("*", LoggingEventHandler())
        self.event_bus.subscribe_many(
            (
                "expense.created",
                "expense.updated",
                "expense.deleted",
                "receivable.settled",
                "receivable.reopened",
                "budget.updated",
                "import.completed",
            ),
            ProjectionRefreshHandler(
                budget_service=base_budget_service,
                report_service=self.report_service,
            ),
        )
        self.event_publisher = EventPublisher(
            repository=self.event_repository,
            bus=self.event_bus,
        )
        self.event_dispatcher = EventDispatcher(
            repository=self.event_repository,
            bus=self.event_bus,
        )

        self.expense_service = EventAwareExpenseService(
            base_expense_service,
            self.event_publisher,
        )
        self.expense_editor_service = EventAwareExpenseEditorService(
            base_editor_service,
            self.event_publisher,
        )
        self.expense_management_service = EventAwareExpenseManagementService(
            base_management_service,
            self.event_publisher,
        )
        self.expense_query_service = ExpenseQueryService(
            expense_repository=self.expense_repository
        )
        self.receivable_service = EventAwareReceivableService(
            base_receivable_service,
            self.event_publisher,
        )
        self.budget_service = EventAwareBudgetService(
            base_budget_service,
            self.event_publisher,
        )
        self.monthly_export_service = MonthlyExportService(
            report_repository=self.report_repository,
            receivable_repository=self.receivable_repository,
        )
        self.automation_service = AutomationService(
            repository=self.automation_repository,
            budget_service=self.budget_service,
        )
        self.recurring_expense_service = RecurringExpenseService(
            repository=self.recurring_expense_repository,
            profile_repository=self.financial_profile_repository,
        )
        self.future_planning_service = FuturePlanningService(
            budget_service=base_budget_service,
            recurring_repository=self.recurring_expense_repository,
        )

        base_import_service = ImportService(
            repository=self.import_repository,
            expense_service=self.expense_service,
            lookup_service=self.lookup_service,
        )
        self.import_service = EventAwareImportService(
            base_import_service,
            self.event_publisher,
        )

        self.dashboard_service = DashboardService(
            report_service=self.report_service,
            report_repository=self.report_repository,
            budget_service=self.budget_service,
            receivable_service=self.receivable_service,
            expense_management_service=self.expense_management_service,
            intelligence_service=self.intelligence_service,
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
