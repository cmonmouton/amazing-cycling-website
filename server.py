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





if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5555)
