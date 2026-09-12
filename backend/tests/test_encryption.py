from app.services.encryption import encrypt_field, decrypt_field

def test_encrypt_decrypt_round_trip():
    plaintext = "+254700123456"

    ciphertext = encrypt_field(plaintext)

    assert ciphertext != plaintext
    assert decrypt_field(ciphertext) == plaintext