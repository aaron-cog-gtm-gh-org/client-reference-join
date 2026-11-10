from pathlib import Path

from db import connect

ROOT = Path(__file__).resolve().parent


def run():
    with connect() as db:
        db.execute("""
            CREATE OR REPLACE TABLE client_ref AS
            SELECT * FROM read_csv_auto(?)
        """, [str(ROOT / "data/client_ref.csv")])
        db.execute("""
            CREATE OR REPLACE TABLE rpt_loans AS
            SELECT e.*, c.client_name, c.rm_id, c.segment
            FROM enr_loans e
            JOIN client_ref c ON e.client_id = c.client_id
        """)


if __name__ == "__main__":
    run()
