from flask import Blueprint, request, jsonify, session
import webauthn
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from models.db import mysql
import base64
import os

webauthn_bp = Blueprint('webauthn', __name__)

RP_ID = "localhost"
RP_NAME = "Email System"
ORIGIN = "http://localhost:5000"


# ================= BASE64 =================
def b64url_decode(s: str) -> bytes:       
    s = s + '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


# =================================================
# TEST ROUTE (DEBUG)
# =================================================
@webauthn_bp.route('/test', methods=['GET'])
def test():
    return "WebAuthn working ✅"


# =================================================
# REGISTER - STEP 1
# =================================================
@webauthn_bp.route('/register/options', methods=['POST'])
def register_options():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username required'}), 400

    # 🔥 Check existing credentials (avoid duplicate)
    cur = mysql.connection.cursor()
    cur.execute("SELECT credential_id FROM webauthn_credentials WHERE username=%s", (username,))
    existing = cur.fetchall()
    cur.close()

    exclude_credentials = []
    for row in existing:
        exclude_credentials.append({
            "type": "public-key",
            "id": row[0]
        })

    user_id = os.urandom(16)

    options = webauthn.generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=user_id,
        user_name=username,
        user_display_name=username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_256],
    )

    session['challenge'] = b64url_encode(options.challenge)
    session['username'] = username

    return jsonify({
        "challenge": b64url_encode(options.challenge),
        "rp": {"name": RP_NAME, "id": RP_ID},
        "user": {
            "id": b64url_encode(user_id),
            "name": username,
            "displayName": username
        },
        "pubKeyCredParams": [{"alg": -7, "type": "public-key"}],
        "timeout": 60000,
        "attestation": "none",
        "authenticatorSelection": {
            "authenticatorAttachment": "platform",
            "userVerification": "required"
        },
        "excludeCredentials": exclude_credentials
    })


# =================================================
# REGISTER - STEP 2
# =================================================
@webauthn_bp.route('/register/verify', methods=['POST'])
def register_verify():

    if 'challenge' not in session or 'username' not in session:
        return jsonify({'error': 'Session expired'}), 400

    data = request.get_json()

    try:
        credential = webauthn.verify_registration_response(
            credential=data,
            expected_challenge=b64url_decode(session['challenge']),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            require_user_verification=True,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO webauthn_credentials 
        (username, credential_id, public_key, sign_count)
        VALUES (%s, %s, %s, %s)
    """, (
        session['username'],
        b64url_encode(credential.credential_id),
        b64url_encode(credential.credential_public_key),
        credential.sign_count
    ))
    mysql.connection.commit()
    cur.close()

    return jsonify({"status": "registered"})


# =================================================
# LOGIN - STEP 1
# =================================================
@webauthn_bp.route('/login/options', methods=['POST'])
def login_options():

    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username required'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT credential_id FROM webauthn_credentials WHERE username=%s", (username,))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return jsonify({'error': 'No fingerprint registered'}), 404

    allow_credentials = [{
        "type": "public-key",
        "id": row[0]
    } for row in rows]

    options = webauthn.generate_authentication_options(
        rp_id=RP_ID,
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    session['challenge'] = b64url_encode(options.challenge)
    session['username'] = username

    return jsonify({
        "challenge": b64url_encode(options.challenge),
        "rpId": RP_ID,
        "allowCredentials": allow_credentials,
        "timeout": 60000,
        "userVerification": "required"
    })


# =================================================
# LOGIN - STEP 2
# =================================================
@webauthn_bp.route('/login/verify', methods=['POST'])
def login_verify():

    if 'challenge' not in session or 'username' not in session:
        return jsonify({'error': 'Session expired'}), 400

    data = request.get_json()
    credential_id = data.get("id")

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT public_key, sign_count 
        FROM webauthn_credentials 
        WHERE credential_id=%s
    """, (credential_id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({'error': 'Credential not found'}), 404

    try:
        verification = webauthn.verify_authentication_response(
            credential=data,
            expected_challenge=b64url_decode(session['challenge']),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=b64url_decode(row[0]),
            credential_current_sign_count=row[1],
            require_user_verification=True,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # update sign count
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE webauthn_credentials 
        SET sign_count=%s 
        WHERE credential_id=%s
    """, (verification.new_sign_count, credential_id))
    mysql.connection.commit()
    cur.close()

    session['user'] = session['username']

    return jsonify({
    "status": "logged_in",
    "redirect": "/super_dashboard"   # ✅ correct route
})