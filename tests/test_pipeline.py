import duckdb
import pytest

from pipeline import run


@pytest.fixture
def database(tmp_path, monkeypatch):
    path = tmp_path / "test.duckdb"
    monkeypatch.setenv("RECON_DB", str(path))
    with duckdb.connect(str(path)) as db:
        db.execute("CREATE TABLE enr_loans AS SELECT 'L1' AS loan_id, 'C04' AS client_id")
    return path


def test_reference_fields_and_idempotency(database):
    run()
    with duckdb.connect(str(database)) as db:
        first = db.execute("SELECT * FROM rpt_loans").fetchall()
        assert first == [("L1", "C04", "Client 4", "RM04", "Private")]
        assert {c[0] for c in db.execute("SELECT * FROM client_ref").description} == {
            "client_id", "client_name", "rm_id", "segment",
            "effective_from", "effective_to", "is_current"}
    run()
    with duckdb.connect(str(database)) as db:
        assert db.execute("SELECT * FROM rpt_loans").fetchall() == first


def test_only_current_client_version(database):
    with duckdb.connect(str(database)) as db:
        db.execute("UPDATE enr_loans SET client_id = 'C01'")
    run()
    with duckdb.connect(str(database)) as db:
        assert db.execute("SELECT count(*) FROM client_ref WHERE client_id = 'C01'").fetchone()[0] == 2
        assert db.execute("SELECT loan_id, rm_id FROM rpt_loans").fetchall() == [("L1", "RM01")]


def test_empty_input(database):
    with duckdb.connect(str(database)) as db:
        db.execute("DELETE FROM enr_loans")
    run()
    with duckdb.connect(str(database)) as db:
        assert db.execute("SELECT count(*) FROM rpt_loans").fetchone()[0] == 0


def test_missing_upstream(database):
    with duckdb.connect(str(database)) as db:
        db.execute("DROP TABLE enr_loans")
    with pytest.raises(duckdb.CatalogException):
        run()
