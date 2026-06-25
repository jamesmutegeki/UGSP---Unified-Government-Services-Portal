"""Initial schema — services, applications, orders, payments, audit_logs

Revision ID: 001
Revises:
Create Date: 2026-06-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean


revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        Column("id", Integer, primary_key=True),
        Column("name", String(255), nullable=False),
        Column("description", Text),
        Column("ministry", String(255)),
        Column("category", String(50), default="citizen"),
        Column("fee", Float, default=0.0),
        Column("turnaround_days", Integer, default=5),
        Column("icon", String(50), default="document"),
        Column("requirements", JSON, default=list),
        Column("active", Boolean, default=True),
        Column("created_at", DateTime),
    )
    op.create_table(
        "applications",
        Column("id", Integer, primary_key=True),
        Column("user_nin", String(20), nullable=False),
        Column("service_id", Integer, nullable=False),
        Column("status", String(50), default="submitted"),
        Column("metadata_json", JSON, default=dict),
        Column("submitted_at", DateTime),
        Column("updated_at", DateTime),
    )
    op.create_index("ix_applications_user_nin", "applications", ["user_nin"])
    op.create_table(
        "orders",
        Column("id", Integer, primary_key=True),
        Column("user_nin", String(20), nullable=False),
        Column("service_id", Integer, nullable=False),
        Column("amount", Float, nullable=False),
        Column("payment_channel", String(50), default="mobile_money"),
        Column("status", String(50), default="pending"),
        Column("prn", String(50)),
        Column("created_at", DateTime),
    )
    op.create_index("ix_orders_prn", "orders", ["prn"], unique=True)
    op.create_table(
        "payments",
        Column("id", Integer, primary_key=True),
        Column("prn", String(50)),
        Column("amount", Float, nullable=False),
        Column("channel", String(50)),
        Column("transaction_id", String(100)),
        Column("status", String(50), default="pending"),
        Column("paid_at", DateTime, nullable=True),
    )
    op.create_table(
        "audit_logs",
        Column("id", Integer, primary_key=True),
        Column("request_id", String(64)),
        Column("method", String(10)),
        Column("path", String(500)),
        Column("user_nin", String(20), nullable=True),
        Column("ip_address", String(50)),
        Column("user_agent", String(500), nullable=True),
        Column("status_code", Integer, nullable=True),
        Column("timestamp", DateTime),
    )
    op.create_index("ix_audit_logs_request_id", "audit_logs", ["request_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("applications")
    op.drop_table("services")
