
import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect("audit.db")

    def save_findings(self, findings):

        cursor = self.conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS findings(type TEXT, vendor TEXT, amount REAL)"
        )

        for f in findings:

            cursor.execute(
                "INSERT INTO findings(type,vendor,amount) VALUES(?,?,?)",
                (f.get("type"), f.get("vendor"), f.get("amount"))
            )

        self.conn.commit()
