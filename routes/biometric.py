from flask import Blueprint, request, session, redirect, render_template, jsonify
import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    PublicKeyCredentialDescriptor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from models.db import mysql
import base64                                    

biometric_bp = Blueprint('biometric', __name__)      # Blueprint for biometric routes (fingerprint + WebAuthn)

# ─────────────────────────────────────────────────────────────
#  CONFIG  — must match browser address bar exactly
# ─────────────────────────────────────────────────────────────
RP_ID   = "localhost"
RP_NAME = "Email System"
ORIGIN  = "http://localhost:5000"


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def b64url_encode(b: bytes) -> str:                  # base64url encode without padding for storing binary data in MySQL
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()  


def b64url_decode(s: str) -> bytes:
    s = s.replace('-', '+').replace('_', '/')
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.b64decode(s)


# ─────────────────────────────────────────────────────────────
#  PAGE ROUTES
# ─────────────────────────────────────────────────────────────

@biometric_bp.route('/fingerprint-login', methods=['GET'])
def fingerprint_login():
    if 'temp_user' not in session:
        return redirect('/')
    return render_template('fingerprint_login.html')


@biometric_bp.route('/fingerprint-register', methods=['GET'])
def fingerprint_register():
    # Must be logged in as admin to register fingerprint
    if 'user' not in session:
        return redirect('/')
    return render_template('fingerprint_register.html')


# =====================================================
# REGISTER — Step 1: generate options
# =====================================================

@biometric_bp.route('/webauthn/register-begin', methods=['POST'])
def register_begin():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    email = session['user']

    options = webauthn.generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_name=email,
        user_display_name=email,
        # PLATFORM = Windows Hello / Touch ID only (no USB keys)
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_256],
    )

    # Save challenge in session
    session['webauthn_reg_challenge'] = b64url_encode(options.challenge)

    return jsonify({
        'challenge': b64url_encode(options.challenge),
        'rp': {
            'id':   options.rp.id,
            'name': options.rp.name,
        },
        'user': {
            'id':          b64url_encode(options.user.id),
            'name':        options.user.name,
            'displayName': options.user.display_name,
        },
        'pubKeyCredParams': [
            {'type': 'public-key', 'alg': -7}
        ],
        'authenticatorSelection': {
            'authenticatorAttachment': 'platform',
            'userVerification':        'required',
        },
        'timeout':     60000,
        'attestation': 'none',
    })


# =====================================================
# REGISTER — Step 2: verify & save into admins table
# =====================================================

@biometric_bp.route('/webauthn/register-complete', methods=['POST'])
def register_complete():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    challenge_b64 = session.get('webauthn_reg_challenge')
    if not challenge_b64:
        return jsonify({'error': 'Session expired — please try again'}), 400

    data = request.get_json()

    try:
        credential = webauthn.verify_registration_response(
            credential=data,
            expected_challenge=b64url_decode(challenge_b64),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            require_user_verification=True,
        )
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 400

    email          = session['user']
    credential_id  = b64url_encode(credential.credential_id)
    public_key     = b64url_encode(credential.credential_public_key)

    # Save into the existing admins table columns
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE admins
            SET webauthn_credential_id = %s,
                webauthn_public_key    = %s
            WHERE email = %s
        """, (credential_id, public_key, email))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        return jsonify({'error': f'DB error: {str(e)}'}), 500

    session.pop('webauthn_reg_challenge', None)
    return jsonify({'status': 'registered'})


# =====================================================
# LOGIN — Step 1: generate challenge
# =====================================================

@biometric_bp.route('/webauthn/login-begin', methods=['POST'])
def login_begin():
    if 'temp_user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    email = session['temp_user']

    # Fetch stored credential from admins table
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT webauthn_credential_id
            FROM admins
            WHERE email = %s
        """, (email,))
        result = cur.fetchone()
        cur.close()
    except Exception as e:
        return jsonify({'error': f'DB error: {str(e)}'}), 500

    if not result or not result[0]:
        return jsonify({'error': 'Fingerprint not registered for this account'}), 400

    credential_id_b64 = result[0]

    allow_credentials = [
        PublicKeyCredentialDescriptor(id=b64url_decode(credential_id_b64))
    ]

    options = webauthn.generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=allow_credentials,
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    session['webauthn_auth_challenge']   = b64url_encode(options.challenge)
    session['webauthn_auth_credential']  = credential_id_b64   # store for verify step

    return jsonify({
        'challenge': b64url_encode(options.challenge),
        'allowCredentials': [
            {'type': 'public-key', 'id': credential_id_b64}
        ],
        'userVerification': 'required',
        'rpId':    RP_ID,
        'timeout': 60000,
    })


# =====================================================
# LOGIN — Step 2: verify assertion → log user in
# =====================================================

@biometric_bp.route('/webauthn/login-complete', methods=['POST'])
def login_complete():
    if 'temp_user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    challenge_b64     = session.get('webauthn_auth_challenge')
    credential_id_b64 = session.get('webauthn_auth_credential')

    if not challenge_b64 or not credential_id_b64:
        return jsonify({'error': 'Session expired — please try again'}), 400

    email = session['temp_user']

    # Fetch public key from admins table
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT webauthn_public_key
            FROM admins
            WHERE email = %s
        """, (email,))
        result = cur.fetchone()
        cur.close()
    except Exception as e:
        return jsonify({'error': f'DB error: {str(e)}'}), 500

    if not result or not result[0]:
        return jsonify({'error': 'No public key found — please register fingerprint first'}), 400

    public_key_bytes = b64url_decode(result[0])
    data             = request.get_json()

    # Verify the signed assertion from Windows Hello
    try:
        verification = webauthn.verify_authentication_response(
            credential=data,
            expected_challenge=b64url_decode(challenge_b64),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=0,   # admins table has no sign_count column
            require_user_verification=True,
        )
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 400

    # Clean up session and log the user in
    session.pop('webauthn_auth_challenge',  None)
    session.pop('webauthn_auth_credential', None)
    temp_user = session.pop('temp_user', None)
    session['user'] = temp_user

    return jsonify({
        'status':   'success',
        'redirect': '/final-login'
    })