"""prd_update_schema"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_prd_update"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("request_approvals")
    op.drop_table("access_requests")
    op.drop_table("card_requests")
    op.drop_table("requests")
    op.drop_table("auth_tokens")
    op.drop_table("user_otp")
    op.drop_table("audit_logs")
    op.drop_table("users")

    op.create_table(
        "employees",
        sa.Column("med_id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("name_ar", sa.String(length=150), nullable=False),
        sa.Column("name_en", sa.String(length=150), nullable=False),
        sa.Column("job_title", sa.String(length=120), nullable=False),
        sa.Column("nationality_ar", sa.String(length=120), nullable=False),
        sa.Column("nationality_en", sa.String(length=120), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("department_name", sa.String(length=150), nullable=False),
        sa.Column("account_status", sa.Enum("ACTIVE", "SUSPENDED"), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("employee_id"),
    )
    op.create_index("idx_employees_department", "employees", ["department_id"])
    op.create_index("idx_employees_status", "employees", ["account_status"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("role_code", sa.String(length=50), nullable=False),
        sa.Column("role_name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("role_code"),
    )

    op.create_table(
        "employee_permissions",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("internal_email", sa.String(length=150), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.UniqueConstraint("employee_id"),
        sa.UniqueConstraint("internal_email"),
    )
    op.create_index("idx_emp_perm_role", "employee_permissions", ["role_id"])

    op.create_table(
        "areas",
        sa.Column("area_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("area_name", sa.String(length=150), nullable=False),
        sa.Column("status", sa.Enum("ACTIVE", "INACTIVE"), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_areas_status", "areas", ["status"])

    op.create_table(
        "card_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("submitted_by_employee_id", sa.String(length=50), nullable=True),
        sa.Column("request_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("request_type", sa.Enum("NEW", "RENEW", "REPLACE_LOST"), nullable=False),
        sa.Column("request_reason", sa.Text(), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("manager_employee_id", sa.String(length=50), nullable=True),
        sa.Column("manager_updated_at", sa.DateTime(), nullable=True),
        sa.Column("security_employee_id", sa.String(length=50), nullable=True),
        sa.Column("security_updated_at", sa.DateTime(), nullable=True),
        sa.Column("printing_employee_id", sa.String(length=50), nullable=True),
        sa.Column("printing_updated_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PENDING_MANAGER_APPROVAL",
                "REJECTED_BY_MANAGER",
                "PENDING_SECURITY_APPROVAL",
                "REJECTED_BY_SECURITY",
                "IN_PROCESS",
                "COMPLETED",
                "CANCELLED",
            ),
            nullable=False,
            server_default="PENDING_MANAGER_APPROVAL",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.ForeignKeyConstraint(["submitted_by_employee_id"], ["employees.employee_id"]),
    )
    op.create_index("idx_card_req_status", "card_requests", ["status"])
    op.create_index("idx_card_req_employee", "card_requests", ["employee_id"])
    op.create_index("idx_card_req_submitted_by", "card_requests", ["submitted_by_employee_id"])
    op.create_index("idx_card_req_dates", "card_requests", ["request_date"])

    op.create_table(
        "permit_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("submitted_by_employee_id", sa.String(length=50), nullable=True),
        sa.Column("request_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("request_reason", sa.Text(), nullable=True),
        sa.Column("manager_employee_id", sa.String(length=50), nullable=True),
        sa.Column("manager_updated_at", sa.DateTime(), nullable=True),
        sa.Column("security_employee_id", sa.String(length=50), nullable=True),
        sa.Column("security_updated_at", sa.DateTime(), nullable=True),
        sa.Column("printing_employee_id", sa.String(length=50), nullable=True),
        sa.Column("printing_updated_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "PENDING_MANAGER_APPROVAL",
                "REJECTED_BY_MANAGER",
                "PENDING_SECURITY_APPROVAL",
                "REJECTED_BY_SECURITY",
                "IN_PROCESS",
                "COMPLETED",
                "CANCELLED",
            ),
            nullable=False,
            server_default="PENDING_MANAGER_APPROVAL",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.employee_id"]),
        sa.ForeignKeyConstraint(["submitted_by_employee_id"], ["employees.employee_id"]),
    )
    op.create_index("idx_permit_req_status", "permit_requests", ["status"])
    op.create_index("idx_permit_req_employee", "permit_requests", ["employee_id"])
    op.create_index("idx_permit_req_submitted_by", "permit_requests", ["submitted_by_employee_id"])
    op.create_index("idx_permit_req_dates", "permit_requests", ["request_date"])

    op.create_table(
        "permit_request_areas",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("permit_request_id", sa.BigInteger(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["permit_request_id"], ["permit_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["area_id"], ["areas.area_id"]),
        sa.UniqueConstraint("permit_request_id", "area_id"),
    )

    op.create_table(
        "user_otp",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("internal_email", sa.String(length=150), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_user_otp_email", "user_otp", ["internal_email"])
    op.create_index("idx_user_otp_expires", "user_otp", ["expires_at"])

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("internal_email", sa.String(length=150), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_auth_tokens_email", "auth_tokens", ["internal_email"])
    op.create_index("idx_auth_tokens_expires", "auth_tokens", ["expires_at"])
    op.create_index("idx_auth_tokens_revoked", "auth_tokens", ["revoked"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("performed_by_email", sa.String(length=150), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_audit_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_created", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("auth_tokens")
    op.drop_table("user_otp")
    op.drop_table("permit_request_areas")
    op.drop_table("permit_requests")
    op.drop_table("card_requests")
    op.drop_table("areas")
    op.drop_table("employee_permissions")
    op.drop_table("roles")
    op.drop_table("employees")

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=True),
        sa.Column("role_code", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("employee_id"),
    )

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=True, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    op.create_table(
        "requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("request_type", sa.Enum("CARD", "ACCESS"), nullable=False),
        sa.Column("requester_name", sa.String(length=150), nullable=False),
        sa.Column("requester_employee_id", sa.String(length=50), nullable=False),
        sa.Column("requester_department", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_step", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "card_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("card_type", sa.String(length=50), nullable=False),
        sa.Column("job_title", sa.String(length=100), nullable=False),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "access_requests",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("access_area", sa.String(length=100), nullable=False),
        sa.Column("access_level", sa.String(length=50), nullable=False),
        sa.Column("access_from", sa.Date(), nullable=False),
        sa.Column("access_to", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "request_approvals",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("approver_id", sa.BigInteger(), nullable=False),
        sa.Column("role_code", sa.String(length=50), nullable=False),
        sa.Column("action", sa.Enum("APPROVED", "REJECTED"), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"]),
    )

    op.create_table(
        "user_otp",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("otp_code", sa.String(length=10), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=True, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("performed_by", sa.BigInteger(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
