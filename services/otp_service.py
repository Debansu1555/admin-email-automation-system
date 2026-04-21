import pyotp

def generate_otp(secret):
    return pyotp.TOTP(secret, interval=300).now()

def verify_otp(secret, otp):
    return pyotp.TOTP(secret, interval=300).verify(otp)
