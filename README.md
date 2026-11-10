# client-reference-join
Reads: enr_loans and owned data/client_ref.csv (SCD2 history).
Writes: client_ref and rpt_loans.
Owns: Client data reference history and reporting join.
Run: pip install -r requirements.txt; make run; make test. Shared DB: $RECON_DB (default ~/lending-demo/lending.duckdb); tables are replaced on each run.
