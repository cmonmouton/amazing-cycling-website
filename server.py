import jwt
from flask import Flask, request, send_file, abort, jsonify

app = Flask(__name__, static_url_path='/static')

available_pages = [
    "index.html",
    "gravel.html",
    "route.html",
    "vtt.html",
]


@app.get('/')
def render_page():
    page = request.args.get('page')
    if not page:
        return send_file('index.html')

    if page in available_pages:
        return send_file(page)

    abort(404, "Page not found")


@app.route('/robots.txt')
def robot_page():
    return send_file('robots.txt')


@app.route('/favicon.ico')
def ico_page():
    return send_file('favicon.ico')


@app.get('/backups/<zip_filename>')
def backup_page(zip_filename):
    if not zip_filename:
        abort(400, "Incorrect parameters")

    token = request.headers.get('Authorization')
    token = token.replace("Bearer ", "")
    if not token:
        abort(401, "Unauthenticated")

    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        if "role" not in decoded:
            return jsonify({'message': "Only an user with 'admin' role can access this page..."}), 403
        elif decoded.get("role") == "admin" and decoded.get("email", "").endswith("@slb.com"):
            try:
                if zip_filename not in ["09-16-2024_6sdf465s.zip", "08-16-2024_fdas65d4.zip",
                                        "07-16-2024_68sadf6d.zip"]:
                    raise FileNotFoundError("Incorrect file")
                return send_file(f"backups/{zip_filename}")
            except FileNotFoundError:
                abort(404, "Not found")
    except Exception:
        pass

    abort(403, "Unauthorized")


@app.get('/api/admin')
def admin_page():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'A bearer token is required'}), 401

    token = token.replace("Bearer ", "")
    try:
        decoded = jwt.decode(token, options={
            "verify_signature": False,
            "verify_exp": True
        })
        if "role" not in decoded or decoded.get("role", None) != "admin":
            return jsonify({'message': "Only an user with 'admin' role can access this page..."}), 403
        if "iss" not in decoded or decoded.get("iss", None) != "https://csi.slb.com/v2":
            return jsonify({'message': "Only a token issued by 'https://csi.slb.com/v2' are authorized"}), 403
        if decoded["role"] == "admin" and decoded["iss"] == "https://csi.slb.com/v2":
            # simple admin
            if "email" not in decoded:
                return jsonify({
                    'Monthly statistics': {
                        "total users count": "2 149 464",
                        "unique users ": "84 634",
                        "new subscribed users": "52 014",
                    },
                    "Backup configuration": "️⚠️ Information are restricted to users with an 'email' @slb.com ⚠️"
                })
            # super admin identified by email
            elif decoded["email"].endswith("@slb.com"):
                return jsonify({
                    'Monthly statistics': {
                        "total users count": "2 149 464",
                        "unique users ": "84 634",
                        "new subscribed users": "52 014",
                    },
                    "API_FLAG": "FLAG{UF!ndThe@piFlagz!}",
                    "Backup configuration": {
                        "Frequency": "monthly",
                        "Backup folders": [
                            "backups/07-16-2024_68sadf6d.zip",
                            "backups/08-16-2024_fdas65d4.zip",
                            "backups/09-16-2024_6sdf465s.zip",
                        ]
                    }
                })
    except jwt.ExpiredSignatureError:
        return "The provided token is expired", 401



if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5555)
