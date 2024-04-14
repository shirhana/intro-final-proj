from cryptography.fernet import Fernet
import os

# Generate a key from a password (you can also generate a random key and save it securely)
def generate_key(password):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(password.encode())
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key, encrypted_password

# Encrypt a file using the key
def encrypt_file(filename, key):
    with open(filename, "rb") as f:
        data = f.read()
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data)
    with open(f"encrypted_{filename}", "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)

# Decrypt a file using the key
def decrypt_file(filename, key):
    with open(filename, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    with open(f"decrypted_{filename}", "wb") as decrypted_file:
        decrypted_file.write(decrypted_data)

# Example usage
password = "mypassword"
key, encrypted_password = generate_key(password)

# Store the encrypted password securely, you will need it for decryption
print("Encrypted Password:", encrypted_password)

# Encrypt a file
encrypt_file("myfile.txt", key)

# Decrypt a file (make sure to use the correct key and encrypted password)
decrypt_file("encrypted_myfile.txt", key)