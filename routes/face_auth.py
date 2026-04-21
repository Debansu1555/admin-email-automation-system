from flask import Blueprint, request, redirect, session, render_template
from services.face_service import verify_face
from models.db import mysql
import json

face_bp = Blueprint('face', __name__)

@face_bp.route('/register-face', methods=['GET', 'POST'])
def register_face():

    if 'user' not in session:         # 🔒 Must be logged in to register face
        return redirect('/')

    if request.method == 'POST':       #🔹 Handle face registration
        file = request.files['image']
        email = session['user']

        from services.face_service import encode_face   # Get face encoding from uploaded image
        encoding = encode_face(file)

        if encoding is None:
            return "No face detected ❌"

        import json

        cur = mysql.connection.cursor()             # Store face encoding as JSON string in DB
        cur.execute(
            "UPDATE admins SET face_encoding=%s WHERE email=%s",
            (json.dumps(encoding.tolist()), email)
        )
        mysql.connection.commit()
        cur.close()

        return "Face Registered Successfully ✅"

    return render_template('register_face.html')      #render_template is used to render the HTML template for face registration

# ---------------- LOAD FACE LOGIN PAGE ---------------- #
@face_bp.route('/face-login', methods=['GET'])
def face_login():
    # 🔒 Session protection
    if 'temp_user' not in session:
        return redirect('/')

    return render_template('face_login.html')


# ---------------- VERIFY FACE ---------------- #
@face_bp.route('/verify-face', methods=['POST'])
def verify_face_route():

    if 'temp_user' not in session:
        return redirect('/')

    file = request.files['image']
    email = session['temp_user']

    cur = mysql.connection.cursor()
    cur.execute("SELECT face_encoding FROM admins WHERE email=%s", (email,))
    result = cur.fetchone()
    cur.close()

    if not result or not result[0]:
        return "Face not registered ❌"

    import json
    stored_encoding = json.loads(result[0])

    from services.face_service import verify_face

    if verify_face(file, stored_encoding):
        return redirect('/final-login')

    return "Face not matched ❌"