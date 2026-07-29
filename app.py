#!/usr/bin/env python3
"""
Flask app — DevSecOps M5 Lab
Vault integration for secrets management.
"""

import os
import logging
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)


def get_secret_from_vault(secret_path, field):
    """Fetch a secret from HashiCorp Vault."""
    vault_addr = os.environ.get('VAULT_ADDR', 'http://localhost:8200')
    vault_token = os.environ.get('VAULT_TOKEN')

    if not vault_token:
        return os.environ.get(field.upper())

    try:
        import hvac
        client = hvac.Client(url=vault_addr, token=vault_token)
        secret = client.secrets.kv.v2.read_secret_version(
            path=secret_path,
            mount_point='secret'
        )
        return secret['data']['data'].get(field)
    except Exception as e:
        logger.warning(f"Vault unavailable, falling back to env: {e}")
        return os.environ.get(field.upper())


app = Flask(__name__)
app.secret_key = get_secret_from_vault('flask-app', 'secret_key') or 'dev-fallback-key'


@app.route('/')
def index():
    return jsonify({"message": "Flask DevSecOps App", "version": "1.0"})


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Server'] = 'webserver'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; font-src 'self'; object-src 'none'; "
        "frame-ancestors 'none'"
    )
    return response


@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "1.0", "uptime": 999})


@app.route('/version')
def version():
    return jsonify({"version": "1.0.0"})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    logger.info(f"Login attempt: username={username} ip={request.remote_addr}")
    return jsonify({"message": "login endpoint"})


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "logged out"})


@app.route('/profile')
def profile():
    return jsonify({"user": "unknown"})


@app.route('/crash')
def crash():
    raise Exception("Intentional crash for demo")


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal error: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500
    if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', debug=debug_mode)  # nosec B104