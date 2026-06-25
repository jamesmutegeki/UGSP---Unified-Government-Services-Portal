from alembic import context
from sqlalchemy import create_engine

from app.models.schemas import Base

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url="sqlite:///./ugsp.db",
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = create_engine("sqlite:///./ugsp.db")
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
