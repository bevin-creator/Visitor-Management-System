from sqlalchemy import inspect
from app.models.user import User

#database test
def test_database_tables_are_created(db_session):
    inspector = inspect(db_session.bind)

    tables = inspector.get_table_names()

    assert "users" in tables
    assert "visitors" in tables
    assert "visit_records" in tables
    assert "audit_logs" in tables

#test CRUD
def test_can_insert_and_read_user(db_session):
    user = User(
        username="testguard",
        email="testguard@example.com",
        hashed_password="fake-hash-for-db-test",
        full_name="Test Guard",
        role="guard",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()

    saved_user = (
        db_session.query(User)
        .filter(User.username == "testguard")
        .first()
    )

    assert saved_user is not None
    assert saved_user.username == "testguard"
    assert saved_user.role == "guard"


#verify test isolation
def test_database_starts_empty(db_session):
    user_count = db_session.query(User).count()

    assert user_count == 0