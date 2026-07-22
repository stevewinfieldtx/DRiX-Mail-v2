from sqlalchemy import event
from app.models import Email, EmailStatus

@event.listens_for(Email,"init",propagate=True)
def materialize_python_default(target,args,kwargs):
    # SQLAlchemy column defaults normally materialize on flush. Unit fakes do not
    # flush, so mirror the database behavior for pure state-machine tests.
    if "status" not in kwargs: target.status=EmailStatus.ready
