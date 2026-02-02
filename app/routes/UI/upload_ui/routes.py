"""Upload processing routes for PDF parsing and grid display."""

from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.services.extractor import extract_text_from_pdf
from app.services.parser import parse_estimate_text
from app.services.grid_processor import kmeans_1d as _kmeans_1d, group_rows as _group_rows
from app.services.db import get_conn
    if not domain:
        return {"labor": [], "refinish": [], "error": "Not authenticated"}
    cur = get_conn().cursor()

    # Get labor assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_labor, timestamp
        FROM labor_assignments
        WHERE ro = %s AND domain = %s
        ORDER BY timestamp DESC
    """, (ro, domain))
    labor_rows = cur.fetchall()

    labor = [
        {
            "tech": row["tech"],
            "vehicle": row["vehicle"],
            "assigned": row["assigned"],
            "unassigned": row["unassigned"],
            "additional": row["additional"],
            "total_labor": float(row["total_labor"]),
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
        }
        for row in labor_rows
    ]

    # Get refinish assignments
    cur.execute("""
        SELECT tech, vehicle, assigned, unassigned, additional, total_paint, timestamp
        FROM refinish_assignments
        WHERE ro = %s AND domain = %s
        ORDER BY timestamp DESC
    """, (ro, domain))
    paint_rows = cur.fetchall()

    refinish = [
        {
            "tech": row["tech"],
            "vehicle": row["vehicle"],
            "assigned": row["assigned"],
            "unassigned": row["unassigned"],
            "additional": row["additional"],
            "total_paint": float(row["total_paint"]),
            "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None
        }
        for row in paint_rows
    ]

    return {"labor": labor, "refinish": refinish}

