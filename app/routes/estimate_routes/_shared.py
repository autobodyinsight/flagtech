import asyncio
import os
import json
import math
import re
import hashlib
import uuid
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, UploadFile, File, Request, Response
from fastapi.responses import JSONResponse

from app.services.extractor import load_pdf
from app.services.parser import parse_estimate_pdf
from app.models.estimate import EstimateResponse
from app.services.db import get_conn
from app.services.middleware import (
    SESSION_COOKIE_NAME,
    create_auth_session,
    get_authenticated_user,
    get_authenticated_user_email,
    get_user_domain,
    get_user_shop_uuid,
    revoke_auth_session,
)
from app.services.permissions import build_permission_snapshot

from app.routes.estimate_modules.db_schema import (
    _quote_ident,
    _ensure_shops_table,
    _sync_shop_id_bindings,
    _ensure_parts_vendors_table,
    _ensure_shop_settings_table,
    _ensure_shop_users_table,
    _ensure_chat_messages_table,
    _ensure_saved_estimates_table,
    _ensure_ro_payment_totals_table,
    _ensure_ro_payment_entries_table,
    _ensure_parts_orders_table,
    _ensure_parts_received_table,
    _ensure_ro_phases_table,
    _ensure_ro_notes_table,
    _ensure_ro_activity_log_table,
    _ensure_ro_assignments_table,
    _ensure_ro_line_assignments_table,
    _ensure_ro_flagout_lines_table,
    _ensure_techs_table,
    _ensure_archived_techs_table,
)
from app.routes.estimate_modules.shop_scope import (
    _resolve_first_active_shop_domain,
    _resolve_effective_shop_domain,
    _ensure_shop_id_columns_for_domain_tables,
    _ensure_shop_id_sync_triggers,
    _resolve_request_shop_id,
    _resolve_request_shop_uuid,
    _ensure_shop_isolation_infrastructure,
)
from app.routes.estimate_modules.auth_utils import (
    _resolve_request_user_email,
    _is_architect_email,
    _build_cookie_secure_flag,
    _resolve_internal_access_level,
    _request_is_architect,
    _resolve_setup_scope_domain,
)
from app.routes.estimate_modules.ro_utils import (
    _resolve_note_created_by,
    _resolve_request_user_display_name,
    _load_latest_repairs_for_ro,
    _upsert_ro_lines,
    _ensure_ro_line_assignments_for_ro,
    _get_scope_rows,
    _sum_assigned_hours,
)
from app.routes.estimate_modules.tech_utils import _is_manager_or_hr_role
from app.routes.estimate_modules.vendor_utils import _parse_part_description_and_number
from app.routes.estimate_modules.chat_utils import _resolve_current_user_row
from app.routes.estimate_modules.payments_utils import (
    _to_local_business_date,
    _parse_json_field,
    _parse_float_value,
)
from app.routes.estimate_modules.activity_log import _activity_to_datetime, _log_ro_activity
from app.routes.estimate_modules.parsing_utils import (
    _normalize_line_ids,
    _alpha_only_description,
    _serialize_datetime_for_client,
    _extract_line_number,
    _coerce_number,
    _build_unified_estimate_lines,
    _coerce_date,
    _weekday_days_from_hours,
    _add_weekdays,
    _calculate_ecd_date,
    _parse_owner_info,
    _sum_hours,
    _line_key,
    _normalize_repair_type,
)
