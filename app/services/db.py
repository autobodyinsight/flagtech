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

conn = psycopg2.connect(dsn_with_ssl, cursor_factory=psycopg2.extras.RealDictCursor)