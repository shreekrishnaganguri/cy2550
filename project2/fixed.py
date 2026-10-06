# fixed_crypto.py
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a strong 256-bit key from a password using PBKDF2-HMAC-SHA256."""
    return PBKDF2(password, salt, dkLen=32, count=100_000)

def encrypt_file(input_file_path: str, output_file_path: str, password: str):
    """Encrypts a file using AES-256-GCM (Authenticated Encryption)."""
    # Generate a random 16-byte salt and 12-byte nonce
    salt = get_random_bytes(16)
    nonce = get_random_bytes(12)
    
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    with open(input_file_path, 'rb') as f:
        data = f.read()
        
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    # Store salt (16B), nonce (12B), tag (16B), and ciphertext together
    with open(output_file_path, 'wb') as f:
        f.write(salt + nonce + tag + ciphertext)

def decrypt_file(input_file_path: str, output_file_path: str, password: str):
    """Decrypts a file and verifies its integrity using AES-GCM."""
    with open(input_file_path, 'rb') as f:
        salt = f.read(16)
        nonce = f.read(12)
        tag = f.read(16)
        ciphertext = f.read()
        
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    # Decrypt and verify authentication tag (raises ValueError if tampered)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    
    with open(output_file_path, 'wb') as f:
        f.write(plaintext)

if __name__ == "__main__":
    # Demonstration / Round-trip test
    original_text = "This is a secret document for CY2550."
    
    with open("test.txt", "w") as f:
        f.write(original_text)
        
    encrypt_file("test.txt", "test.enc", "MySecurePassword123")
    decrypt_file("test.enc", "test_decrypted.txt", "MySecurePassword123")
    
    with open("test_decrypted.txt", "r") as f:
        print("Decrypted successfully:", f.read() == original_text)