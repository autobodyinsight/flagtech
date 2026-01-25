import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://management_app_yj3h_user:VioUE4I0r3VgaBiNt920IbTXfbRT9dfc@dpg-d5qf43juibrs73c4q5o0-a.oregon-postgres.render.com/management_app_yj3h")

conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)