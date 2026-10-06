# ai_crypto.py
from Crypto.Cipher import AES

def encrypt_file(input_file_path, output_file_path, key_string):
    # Pad key to 16 bytes
    key = key_string.zfill(16).encode('utf-8')
    
    # Insecure ECB mode setup
    cipher = AES.new(key, AES.MODE_ECB)
    
    with open(input_file_path, 'rb') as f:
        data = f.read()
        
    # PKCS7 Padding
    pad_len = 16 - (len(data) % 16)
    padded_data = data + bytes([pad_len] * pad_len)
    
    encrypted_data = cipher.encrypt(padded_data)
    
    with open(output_file_path, 'wb') as f:
        f.write(encrypted_data)