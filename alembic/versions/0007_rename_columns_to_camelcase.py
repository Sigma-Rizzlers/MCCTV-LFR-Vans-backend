"""Rename all snake_case columns to camelCase across every table.

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-16
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── api_van_requests ─────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN request_id TO "requestId"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN status TO "approvalStatus"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN mission_title TO "missionTitle"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN mission_place TO "missionPlace"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN pickup_date TO "pickupDate"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN return_date TO "returnDate"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN job_position TO "jobPosition"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN requester_phone TO "requesterPhone"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN requester_gender TO "requesterGender"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN submitter_username TO "submitterUsername"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN selfie_url TO "selfieUrl"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN support_file_name TO "supportFileName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN lodging_image_name TO "lodgingImageName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN breakfast_image_name TO "breakfastImageName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN lunch_image_name TO "lunchImageName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN dinner_image_name TO "dinnerImageName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN implementation_image_name TO "implementationImageName"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN form_data TO "formData"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN equipment_items TO "equipmentItems"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN admin_panel TO "adminPanel"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN is_deleted TO "isDeleted"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN approved_by TO "approvedBy"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN approval_note TO "approvalNote"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN approved_at TO "approvedAt"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN created_at TO "submittedAt"')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN updated_at TO "updatedAt"')

    # ── api_stops ────────────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_stops RENAME COLUMN van_request_id TO "vanRequestId"')
    op.execute('ALTER TABLE api_stops RENAME COLUMN place_name TO "placeName"')
    op.execute('ALTER TABLE api_stops RENAME COLUMN created_at TO "createdAt"')

    # ── api_van_request_participants ─────────────────────────────────────────
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN van_request_id TO "vanRequestId"')
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN participant_id TO "participantId"')
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN order_index TO "orderIndex"')

    # ── api_participants ─────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_participants RENAME COLUMN support_file_name TO "supportFileName"')
    op.execute('ALTER TABLE api_participants RENAME COLUMN is_deleted TO "isDeleted"')
    op.execute('ALTER TABLE api_participants RENAME COLUMN created_at TO "createdAt"')

    # ── api_users ────────────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_users RENAME COLUMN unit_name TO "unitName"')
    op.execute('ALTER TABLE api_users RENAME COLUMN is_active TO "isActive"')
    op.execute('ALTER TABLE api_users RENAME COLUMN created_at TO "createdAt"')

    # ── api_token_store ──────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_token_store RENAME COLUMN user_id TO "userId"')
    op.execute('ALTER TABLE api_token_store RENAME COLUMN created_at TO "createdAt"')

    # ── api_mission_admin_panels ─────────────────────────────────────────────
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN mission_code TO "missionCode"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN mission_title TO "missionTitle"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN mission_place TO "missionPlace"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN mission_time TO "missionTime"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN participant_count TO "participantCount"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN mission_via TO "missionVia"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN request_plan_file_name TO "requestPlanFileName"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN request_plan_file_key TO "requestPlanFileKey"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN request_plan_file_type TO "requestPlanFileType"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN is_active TO "isActive"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN saved_at TO "savedAt"')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN created_at TO "createdAt"')


def downgrade() -> None:
    # ── api_mission_admin_panels ─────────────────────────────────────────────
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "createdAt" TO created_at')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "savedAt" TO saved_at')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "isActive" TO is_active')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "requestPlanFileType" TO request_plan_file_type')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "requestPlanFileKey" TO request_plan_file_key')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "requestPlanFileName" TO request_plan_file_name')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "missionVia" TO mission_via')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "participantCount" TO participant_count')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "missionTime" TO mission_time')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "missionPlace" TO mission_place')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "missionTitle" TO mission_title')
    op.execute('ALTER TABLE api_mission_admin_panels RENAME COLUMN "missionCode" TO mission_code')

    # ── api_token_store ──────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_token_store RENAME COLUMN "createdAt" TO created_at')
    op.execute('ALTER TABLE api_token_store RENAME COLUMN "userId" TO user_id')

    # ── api_users ────────────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_users RENAME COLUMN "createdAt" TO created_at')
    op.execute('ALTER TABLE api_users RENAME COLUMN "isActive" TO is_active')
    op.execute('ALTER TABLE api_users RENAME COLUMN "unitName" TO unit_name')

    # ── api_participants ─────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_participants RENAME COLUMN "createdAt" TO created_at')
    op.execute('ALTER TABLE api_participants RENAME COLUMN "isDeleted" TO is_deleted')
    op.execute('ALTER TABLE api_participants RENAME COLUMN "supportFileName" TO support_file_name')

    # ── api_van_request_participants ─────────────────────────────────────────
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN "orderIndex" TO order_index')
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN "participantId" TO participant_id')
    op.execute('ALTER TABLE api_van_request_participants RENAME COLUMN "vanRequestId" TO van_request_id')

    # ── api_stops ────────────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_stops RENAME COLUMN "createdAt" TO created_at')
    op.execute('ALTER TABLE api_stops RENAME COLUMN "placeName" TO place_name')
    op.execute('ALTER TABLE api_stops RENAME COLUMN "vanRequestId" TO van_request_id')

    # ── api_van_requests ─────────────────────────────────────────────────────
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "updatedAt" TO updated_at')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "submittedAt" TO created_at')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "approvedAt" TO approved_at')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "approvalNote" TO approval_note')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "approvedBy" TO approved_by')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "isDeleted" TO is_deleted')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "adminPanel" TO admin_panel')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "equipmentItems" TO equipment_items')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "formData" TO form_data')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "implementationImageName" TO implementation_image_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "dinnerImageName" TO dinner_image_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "lunchImageName" TO lunch_image_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "breakfastImageName" TO breakfast_image_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "lodgingImageName" TO lodging_image_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "supportFileName" TO support_file_name')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "selfieUrl" TO selfie_url')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "submitterUsername" TO submitter_username')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "requesterGender" TO requester_gender')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "requesterPhone" TO requester_phone')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "jobPosition" TO job_position')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "returnDate" TO return_date')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "pickupDate" TO pickup_date')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "missionPlace" TO mission_place')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "missionTitle" TO mission_title')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "approvalStatus" TO status')
    op.execute('ALTER TABLE api_van_requests RENAME COLUMN "requestId" TO request_id')
