import os
import json

# This will simulate fingerprint verification

def generate_challenge():
    return os.urandom(32).hex()

def verify_fingerprint_response(data):
    """
    In real WebAuthn:
    - Verify signature
    - Verify challenge
    - Verify authenticator
    
    For project/demo:
    - Just check if response exists
    """
    if not data:
        return False
    
    # Simulate verification success
    return True