Part 1.1: Symmetric Encryption

The `-pbkdf2` option applies Password-Based Key Derivation Function 2, which securely turns a human-readable passphrase into a strong, fixed-length cryptographic encryption key using repeated hashing iterations. Passphrase-based encryption requires PBKDF2 to derive a key with sufficient entropy and resistance to brute-force or dictionary attacks, as raw user passphrases do not directly match the length or randomness required for symmetric encryption keys.

Part 1.2: Encrypt the Same File Twice

The checksums are different because OpenSSL automatically generates a unique random salt and Initialization Vector (IV) for every encryption operation, ensuring the resulting ciphertext is unique even when encrypting identical plaintext with the same passphrase. If it produced identical ciphertexts for identical plaintexts, an attacker observing network traffic could determine when identical messages were sent or perform frequency analysis, compromising confidentiality.

Part 1.3: Watching ECB Leak Information

1. Distinct block counts:
   - `pattern.ecb`: Produces 3 distinct blocks (2 unique ciphertext blocks corresponding to the 'A' and 'B' plaintexts, plus 1 padding block). The most common block repeats 24 times (from the two 12-block sequences of 'A's).
   - `pattern.cbc`: Produces 37 distinct blocks (36 blocks of plaintext plus 1 padding block), where every block appears exactly 1 time.

2. What ECB leaked and its value to an attacker:
   ECB mode leaked structural patterns and repetition within the underlying plaintext data without revealing the key itself. To an attacker, this allows pattern recognition, data classification, and structural analysis (e.g., identifying identical database records, repetitive headers, or image shapes), making it possible to deduce content context without breaking AES encryption directly.

3. Question to ask before believing database records are protected:
   "Which block cipher mode of operation (such as CBC, GCM, or CTR) is being used, and is a unique Initialization Vector (IV) applied per record?"

Part 2.2: Keyed Hashing

1. Why SHA-256 does not protect your colleague:
   Because both the file and the SHA-256 hash are sent over the same controlled channel without authentication, an attacker can modify the file and compute a new valid SHA-256 hash for the altered file. When the colleague recalculates the hash, it will match the attacker's forged hash, making the modification undetected.

2. What changes when using an HMAC instead:
   An HMAC relies on a shared secret key known only to the sender and recipient. Generating a valid HMAC tag requires knowledge of this key, so an attacker cannot produce a matching HMAC for a modified file without knowing the secret key.

3. What the attacker can and cannot do in each situation:
   - SHA-256:
     - Can: Intercept the transmission, modify the file, recompute a valid SHA-256 hash, and pass both to the victim without detection.
     - Cannot: Prevent the recipient from verifying the hash match (the match succeeds, but on forged data).
   - HMAC:
     - Can: Intercept, modify, or block the file and tag in transit.
     - Cannot: Forge a valid HMAC tag for the modified file without knowing the secret key, causing the recipient's verification to fail and detecting the tampering.

 Part 3.3: Fingerprints

1. Email verification check:
   - What it proves: It proves that whoever uploaded the public key has active control access over the specified email inbox at the time of verification.
   - What it does NOT prove: It does not prove the true real-world identity of the person owning the email account, nor does it guarantee that the key creator hasn't compromised or impersonated the owner's identity.

2. Out-of-band fingerprint verification procedure:
   - Procedure: Obtain the classmate's 40-character fingerprint through an out-of-band, trusted secondary channel (such as reading it aloud in person, over a verified phone/video call, or receiving it on a physically signed card). Then, run `gpg --fingerprint <classmate_email>` locally and verify that every character of the generated fingerprint matches the out-of-band fingerprint exactly.
   - Why it works: Cryptographic hash functions underlying GPG fingerprints make it computationally impossible to find a different key that produces the same 40-character fingerprint (collision resistance). Because the fingerprint is transmitted over an independent channel out of reach from the network attacker, the attacker cannot tamper with the fingerprint verification without being detected.

Part 4.2: Find the Hybrid Encryption

1. What is contained in each packet:
   - `pubkey enc` packet: Contains the randomly generated symmetric session key, encrypted using the recipient's public RSA key.
   - Encrypted data packet: Contains the actual message payload, encrypted using a fast symmetric cipher (such as AES) using the session key.

2. Why GPG uses this approach instead of encrypting the entire message with RSA:
   Asymmetric encryption like RSA is computationally expensive and slow for large datasets, and it can only encrypt messages up to a limited size matching the key length. Using symmetric encryption for the message payload allows fast and efficient processing, while RSA is only needed to securely transmit the small symmetric session key.

3. Name of this construction:
   This construction is called Hybrid Encryption.

Part 4.3: Sign, Verify, and Break

1. Which key is used for signing: The sender's private key.
2. Which key is used for verifying: The sender's public key.
3. Which key is used for encryption: The recipient's public key.
4. Which key is used for decryption: The recipient's private key.
5. Security property provided by signing that encryption does not include: Non-repudiation (or authenticity), which proves the true identity of the origin sender and prevents them from denying that they authored and sent the message.

 Part 5 Written Answer

Ed25519 relies on elliptic curve cryptography, where solving the discrete logarithm problem requires exponentially more computational effort per bit than breaking RSA's integer factorization. As a result, a 256-bit Ed25519 key offers comparable cryptographic security (roughly 128 bits of security) to a 4096-bit RSA key while providing faster computations and a significantly smaller key size.

Part 7:

Defect 1: Use of Electronic Codebook (ECB) Mode   

What is wrong: The function uses AES.MODE_ECB without an Initialization Vector (IV).   

Attacker Exploit: ECB mode encrypts identical 16-byte blocks of plaintext into identical blocks of ciphertext. An attacker can analyze patterns in the ciphertext (e.g., identical headers or repetitive data blocks) to infer the file structure or contents without knowing the key. 

Defect 2: Unauthenticated Encryption (Lack of Integrity Verification)   

What is wrong: The encryption scheme lacks an authentication tag or Message Authentication Code (MAC).   

Attacker Exploit: An attacker can perform a bit-flipping attack by modifying ciphertext bytes in transit. When decrypted, the corrupted data will be processed without triggering any error or warning, leading to data corruption or padding oracle attacks.

Defect 3: Insecure Key Handling and Lack of KDF   

What is wrong: The function converts a user-supplied text string directly into a key via simple zero-padding (zfill(16)), rather than using a proper Key Derivation Function (KDF) with salt.   

Attacker Exploit: Simple string inputs lack cryptographic entropy. An attacker can perform a dictionary attack or brute-force search against weak passwords in seconds. 

Fixes:

1. Changed Cipher Mode to AES-GCM (Galois/Counter Mode)
What changed: Swapped AES.MODE_ECB for AES.MODE_GCM with a unique 12-byte nonce generated per encryption via get_random_bytes(12).

Why it changed: ECB mode processes identical plaintext blocks into identical ciphertext blocks, exposing structural patterns in data.

Security problem addressed: Fixes the loss of confidentiality / pattern leakage (violating Indistinguishability under Chosen Plaintext Attack).


2. Added Message Integrity and Authentication (AEAD)
What changed: Integrated AES-GCM's built-in 16-byte authentication tag (tag), which is computed during encryption (encrypt_and_digest) and verified during decryption (decrypt_and_verify).

Why it changed: Without authentication, ciphertext can be modified in transit without detection.

Security problem addressed: Fixes susceptibility to bit-flipping and ciphertext tampering (violating Indistinguishability under Chosen Ciphertext Attack - IND-CCA).

3. Implemented Key Derivation (PBKDF2) with Salt
What changed: Replaced string zero-padding (zfill(16)) with PBKDF2 key derivation using a cryptographically random 16-byte salt and 100,000 iterations.

Why it changed: Passwords have low entropy and simple zero-padding yields predictable, low-complexity keys vulnerable to dictionary attacks.

Security problem addressed: Fixes weak key generation and credential guessing attacks by enforcing high computational entropy.