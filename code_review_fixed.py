#!/usr/bin/env python3
"""
Fixed version — all code review issues resolved.
"""

import os
import sqlite3
import logging
import bcrypt
from functools import wraps
from flask import Flask, request, jsonify, session

app = Flask(__name__)

# Fix 1: Secret from environment
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise ValueError("SECRET_KEY not configured")

logger = logging.getLogger(__name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_user_id():
    return session.get('user_id')


# Fix 2+3: Parameterised query, no password hash in response
@app.route('/api/users/<int:user_id>/profile', methods=['GET'])
@login_required
def get_profile(user_id):
    conn = sqlite3.connect('app.db')
    user = conn.execute(
        "SELECT id, username, email, created_at FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user[0],
        "username": user[1],
        "email": user[2],
        "created_at": user[3]
    })


# Fix 4+5: Auth check, authorization check, safe logging
@app.route('/api/users/<int:user_id>/profile', methods=['PUT'])
@login_required
def update_profile(user_id):
    current_user_id = get_current_user_id()
    if current_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.json
    email = data.get('email', '').strip()

    if not email or '@' not in email:
        return jsonify({"error": "Invalid email"}), 400

    conn = sqlite3.connect('app.db')
    conn.execute(
        "UPDATE users SET email=? WHERE id=?",
        (email, user_id)
    )
    conn.commit()
    conn.close()

    # Fix 5: Log only safe metadata
    logger.info(f"Profile updated: user_id={user_id}")
    return jsonify({"updated": True})


# Fix 6: Admin endpoint with proper auth
@app.route('/api/admin/users', methods=['GET'])
@login_required
def list_all_users():
    current_user_id = get_current_user_id()
    conn = sqlite3.connect('app.db')
    is_admin = conn.execute(
        "SELECT is_admin FROM users WHERE id=?",
        (current_user_id,)
    ).fetchone()

    if not is_admin or not is_admin[0]:
        return jsonify({"error": "Forbidden"}), 403

    users = conn.execute(
        "SELECT id, username, email, created_at FROM users"
    ).fetchall()
    conn.close()
    return jsonify({"users": users})


# Fix 7+8: Strong password policy, bcrypt hashing
@app.route('/api/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password(user_id):
    current_user_id = get_current_user_id()
    if current_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    new_password = request.json.get('password', '')

    if len(new_password) < 12:
        return jsonify({"error": "Password must be at least 12 characters"}), 400

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

    conn = sqlite3.connect('app.db')
    conn.execute(
        "UPDATE users SET password_hash=? WHERE id=?",
        (hashed, user_id)
    )
    conn.commit()
    conn.close()

    logger.info(f"Password reset: user_id={user_id}")
    return jsonify({"reset": True})


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    # Fix 9: debug=False
    app.run(debug=False)