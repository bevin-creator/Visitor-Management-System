from app.routers.auth import get_password_hash, verify_password

#test password hashing
def test_password_hash_and_verify():
    password = "StrongPass123!"

    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


#wrong password test
def test_wrong_password_fails():
    password = "StrongPass123!"

    hashed = get_password_hash(password)

    assert verify_password("WrongPassword", hashed) is False