from sqlalchemy import inspect


def test_database_tables_are_created(db_session):
    inspector = inspect(db_session.bind)

    tables = inspector.get_table_names()

    assert "users" in tables
    assert "visitors" in tables
    assert "visit_records" in tables
    assert "audit_logs" in tables