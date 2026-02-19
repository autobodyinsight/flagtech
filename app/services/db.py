# Utility to fetch closed ROs and summary metrics
def get_closed_ros_and_summary():
	conn = get_conn()
	cur = conn.cursor()
	# Example query: adjust table/column names as needed
	cur.execute('''
		SELECT ro_number, vehicle, tech, parts, insurance, customer, in_date, picked_up, hours, total, status, gp_percent, gp_dollar, type
		FROM repair_orders
		WHERE status = 'closed'
	''')
	rows = cur.fetchall()
	# Calculate summary metrics
	summary = {
		'RO\'S': {'sales': 0, 'gp_percent': 0, 'gp_dollar': 0, 'count': 0},
		'PARTS': {'sales': 0, 'gp_percent': 0, 'gp_dollar': 0, 'count': 0},
		'LABOR': {'sales': 0, 'gp_percent': 0, 'gp_dollar': 0, 'count': 0},
	}
	for row in rows:
		# Example aggregation logic, adjust as needed
		summary["RO'S"]['sales'] += row.get('total', 0) or 0
		summary["RO'S"]['gp_percent'] += row.get('gp_percent', 0) or 0
		summary["RO'S"]['gp_dollar'] += row.get('gp_dollar', 0) or 0
		summary["RO'S"]['count'] += 1
		if row.get('type') == 'parts':
			summary['PARTS']['sales'] += row.get('parts', 0) or 0
			summary['PARTS']['gp_percent'] += row.get('gp_percent', 0) or 0
			summary['PARTS']['gp_dollar'] += row.get('gp_dollar', 0) or 0
			summary['PARTS']['count'] += 1
		if row.get('type') == 'labor':
			summary['LABOR']['sales'] += row.get('labor', 0) or 0
			summary['LABOR']['gp_percent'] += row.get('gp_percent', 0) or 0
			summary['LABOR']['gp_dollar'] += row.get('gp_dollar', 0) or 0
			summary['LABOR']['count'] += 1
	# Average GP %
	for k in summary:
		if summary[k]['count']:
			summary[k]['gp_percent'] = round(summary[k]['gp_percent'] / summary[k]['count'], 2)
	cur.close()
	return rows, summary
import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql://management_app_yj3h_user:VioUE4I0r3VgaBiNt920IbTXfbRT9dfc@dpg-d5qf43juibrs73c4q5o0-a.oregon-postgres.render.com/management_app_yj3h",
)


def _ensure_sslmode(dsn: str) -> str:
	"""Ensure the DSN has sslmode=require appended."""
	parsed = urlsplit(dsn)
	query = dict(parse_qsl(parsed.query, keep_blank_values=True))
	if "sslmode" not in query:
		query["sslmode"] = "require"
	rebuilt = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
	return rebuilt


dsn_with_ssl = _ensure_sslmode(DATABASE_URL)

conn = None


def get_conn():
	"""Return a live DB connection, reconnecting if needed."""
	global conn
	if conn is None or conn.closed:
		conn = psycopg2.connect(dsn_with_ssl, cursor_factory=psycopg2.extras.RealDictCursor)
		conn.autocommit = True
	return conn

def close_repair_order(ro_number):
    """Set status='closed' for the given RO number in repair_orders table."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE repair_orders
        SET status = 'closed'
        WHERE ro_number = %s
    """, (ro_number,))
    cur.close()

def set_picked_up_date(ro_number, picked_up):
    """Set picked_up date for the given RO number in repair_orders table."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE repair_orders
        SET picked_up = %s
        WHERE ro_number = %s
    """, (picked_up, ro_number))
    cur.close()