"""initial FastAPI schema — all api_* tables

Squashes the original per-feature migrations into one authoritative
initial state. Django tables (van_requests, participants, users, …)
coexist unchanged in the same schema under their original names.

Revision ID: 0001
Revises: —
Create Date: 2026-05-16
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_users (
            id          BIGSERIAL    PRIMARY KEY,
            username    VARCHAR(150) NOT NULL UNIQUE,
            password    VARCHAR(255) NOT NULL,
            role        VARCHAR(20)  NOT NULL DEFAULT 'user'
                CHECK (role IN ('user', 'admin', 'superadmin', 'sysmanager')),
            unit_name   VARCHAR(255) NOT NULL DEFAULT '',
            is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        )
    """)

    # ── token store ───────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_token_store (
            token       VARCHAR(64) NOT NULL PRIMARY KEY,
            user_id     BIGINT      NOT NULL
                REFERENCES api_users(id) ON DELETE CASCADE,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_api_token_store_user_id
        ON api_token_store (user_id)
    """)

    # ── van requests ──────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_van_requests (
            id                        BIGSERIAL    PRIMARY KEY,
            request_id                VARCHAR(50)  NOT NULL UNIQUE DEFAULT '',
            status                    VARCHAR(20)  NOT NULL DEFAULT 'pending',
            mission_title             VARCHAR(255) NOT NULL DEFAULT '',
            mission_place             VARCHAR(255) NOT NULL DEFAULT '',
            pickup_date               DATE,
            return_date               DATE,
            fullname                  VARCHAR(255) NOT NULL DEFAULT '',
            job_position              VARCHAR(255) NOT NULL DEFAULT '',
            requester_phone           VARCHAR(20)  NOT NULL DEFAULT '',
            requester_gender          VARCHAR(10)  NOT NULL DEFAULT '',
            submitter_username        VARCHAR(150) NOT NULL DEFAULT '',
            reason                    TEXT         NOT NULL DEFAULT '',
            selfie_url                TEXT         NOT NULL DEFAULT '',
            support_file_name         VARCHAR(255) NOT NULL DEFAULT '',
            lodging_image_name        VARCHAR(255) NOT NULL DEFAULT '',
            breakfast_image_name      VARCHAR(255) NOT NULL DEFAULT '',
            lunch_image_name          VARCHAR(255) NOT NULL DEFAULT '',
            dinner_image_name         VARCHAR(255) NOT NULL DEFAULT '',
            implementation_image_name VARCHAR(255) NOT NULL DEFAULT '',
            form_data                 JSON         NOT NULL DEFAULT '{}',
            members                   JSON         NOT NULL DEFAULT '[]',
            vehicles                  JSON         NOT NULL DEFAULT '[]',
            equipment_items           JSON         NOT NULL DEFAULT '[]',
            admin_panel               JSON         NOT NULL DEFAULT '{}',
            is_deleted                BOOLEAN      NOT NULL DEFAULT FALSE,
            approved_by               BIGINT REFERENCES api_users(id),
            approval_note             TEXT         NOT NULL DEFAULT '',
            approved_at               TIMESTAMP,
            created_at                TIMESTAMP    NOT NULL DEFAULT NOW(),
            updated_at                TIMESTAMP
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_api_van_requests_request_id
        ON api_van_requests (request_id)
    """)

    # ── participants ──────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_participants (
            id                BIGSERIAL    PRIMARY KEY,
            name              VARCHAR(255) NOT NULL,
            phone             VARCHAR(20)  NOT NULL DEFAULT '',
            gender            VARCHAR(10)  NOT NULL DEFAULT '',
            role              VARCHAR(100) NOT NULL DEFAULT '',
            support_file_name VARCHAR(255) NOT NULL DEFAULT '',
            is_deleted        BOOLEAN      NOT NULL DEFAULT FALSE,
            created_at        DATE         NOT NULL DEFAULT CURRENT_DATE
        )
    """)

    # ── van request participants ───────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_van_request_participants (
            id             BIGSERIAL PRIMARY KEY,
            van_request_id BIGINT    NOT NULL
                REFERENCES api_van_requests(id) ON DELETE CASCADE,
            participant_id BIGINT    NOT NULL
                REFERENCES api_participants(id) ON DELETE CASCADE,
            order_index    INTEGER   NOT NULL DEFAULT 0,
            UNIQUE (van_request_id, participant_id)
        )
    """)

    # ── stops ─────────────────────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_stops (
            id             BIGSERIAL    PRIMARY KEY,
            van_request_id BIGINT       NOT NULL
                REFERENCES api_van_requests(id) ON DELETE CASCADE,
            place_name     VARCHAR(255) NOT NULL DEFAULT '',
            notes          TEXT         NOT NULL DEFAULT '',
            "order"        INTEGER      NOT NULL DEFAULT 0,
            created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)

    # ── mission admin panels ───────────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS api_mission_admin_panels (
            id                     BIGSERIAL    PRIMARY KEY,
            mission_code           VARCHAR(50)  NOT NULL UNIQUE,
            mission_title          VARCHAR(255) NOT NULL DEFAULT '',
            mission_place          VARCHAR(255) NOT NULL DEFAULT '',
            mission_time           TIMESTAMP,
            participant_count      VARCHAR(50)  NOT NULL DEFAULT '',
            mission_via            VARCHAR(255) NOT NULL DEFAULT '',
            request_plan_file_name VARCHAR(255) NOT NULL DEFAULT '',
            request_plan_file_key  VARCHAR(255) NOT NULL DEFAULT '',
            request_plan_file_type VARCHAR(100) NOT NULL DEFAULT '',
            is_active              BOOLEAN      NOT NULL DEFAULT TRUE,
            saved_at               TIMESTAMP    NOT NULL DEFAULT NOW(),
            created_at             TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_api_mission_admin_panels_mission_code
        ON api_mission_admin_panels (mission_code)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS api_mission_admin_panels")
    op.execute("DROP TABLE IF EXISTS api_stops")
    op.execute("DROP TABLE IF EXISTS api_van_request_participants")
    op.execute("DROP TABLE IF EXISTS api_participants")
    op.execute("DROP TABLE IF EXISTS api_van_requests")
    op.execute("DROP TABLE IF EXISTS api_token_store")
    op.execute("DROP TABLE IF EXISTS api_users")
