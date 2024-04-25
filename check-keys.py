import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class FileEncryptor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Encryptor')

        self.file_label = QLabel('File Path:')
        self.file_input = QLineEdit()
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.encrypt_button = QPushButton('Encrypt')
        self.decrypt_button = QPushButton('Decrypt')

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.encrypt_button)
        layout.addWidget(self.decrypt_button)

        self.setLayout(layout)

        self.encrypt_button.clicked.connect(self.encrypt_file)
        self.decrypt_button.clicked.connect(self.decrypt_file)

    def derive_key(self, password):
        salt = b'salt_123'  # You should use a unique salt for each encryption
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256-bit key length for Fernet
            salt=salt,
            iterations=100000,  # Adjust as needed for security vs performance
        )
        key_bytes = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key_bytes)

    def encrypt_file(self):
        file_path = self.file_input.text()
        password = self.password_input.text()
        key = self.derive_key(password)

        cipher_suite = Fernet(key)

        with open(file_path, 'rb') as file:
            file_data = file.read()

        encrypted_data = cipher_suite.encrypt(file_data)

        encrypted_file_path = file_path + '.encrypted'
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

        QMessageBox.information(self, 'Encryption', f'File encrypted and saved as: {encrypted_file_path}')

    def decrypt_file(self):
        encrypted_file_path = self.file_input.text()
        password = self.password_input.text()
        key = self.derive_key(password)

        cipher_suite = Fernet(key)

        with open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()

        try:
            decrypted_data = cipher_suite.decrypt(encrypted_data)

            decrypted_file_path = encrypted_file_path.replace('.encrypted', '_decrypted')
            with open(decrypted_file_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)

            QMessageBox.information(self, 'Decryption', f'File decrypted and saved as: {decrypted_file_path}')
        except InvalidToken:
            QMessageBox.warning(self, 'Decryption Error', 'Invalid password or corrupted file.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileEncryptor()
    window.show()
    sys.exit(app.exec_())
