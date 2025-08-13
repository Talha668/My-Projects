import random
import string

chars = " " + string.whitespace + string.punctuation + string.digits + string.ascii_letters
chars = list(chars)
key = chars.copy()

random.shuffle(key)

print(f"chars: {chars}")
print(f"key: {key}")

# Encryption

plain_text = input("Enter Message to Encrypt: ")
cipher_text = ""

for letter in plain_text:
    index = chars.index(letter)
    cipher_text += key[index]

print(f"Original Message: {plain_text}")
print(f"Encrypted Message: {cipher_text}")

# Decryption
cipher_text = input("\nEnter Message to Decrypt: ")
decrypted_text = ""
for letter in cipher_text:
    index = key.index(letter)
    decrypted_text += chars[index]

print(f"\nEncrypted Message: {cipher_text}")
print(f"Decrypted Message: {decrypted_text}")
