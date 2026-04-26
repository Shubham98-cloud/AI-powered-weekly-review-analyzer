import sqlite3
import os
from datetime import datetime

class AuditStore:
    def __init__(self, db_path: str = None):
        # Use RAILWAY_VOLUME_MOUNT_PATH if available for persistent storage
        if not db_path:
            base_dir = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", ".")
            db_path = os.path.join(base_dir, "run_log.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS run_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product TEXT NOT NULL,
                    iso_week TEXT NOT NULL,
                    status TEXT NOT NULL,
                    delivered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(product, iso_week)
                )
            """)

    def is_delivered(self, product: str, iso_week: str) -> bool:
        """Checks if a report has already been delivered for this product and week."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM run_log WHERE product = ? AND iso_week = ? AND status = 'delivered'",
                (product, iso_week)
            )
            return cursor.fetchone() is not None

    def log_run(self, product: str, iso_week: str, status: str = "delivered"):
        """Logs a successful delivery."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO run_log (product, iso_week, status, delivered_at) VALUES (?, ?, ?, ?)",
                (product, iso_week, status, datetime.utcnow())
            )
