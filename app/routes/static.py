from flask import Blueprint, send_from_directory, current_app
import os

bp = Blueprint('static', __name__)

@bp.route("/")
def serve_index():
    return send_from_directory(current_app.static_folder, 'index.html')

@bp.route("/dashboard.html")
def serve_dashboard():
    return send_from_directory(current_app.static_folder, 'dashboard.html')

@bp.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(current_app.static_folder, path)

@bp.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'js'), filename)

@bp.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'css'), filename)

@bp.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'images'), filename)

@bp.route("/templates/<path:filename>")
def serve_templates(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'templates'), filename)
