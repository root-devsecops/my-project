from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "1.0", "uptime": 999})

@app.route('/version')
def version():
    return jsonify({"version": "1.0.0"})

@app.route('/login', methods=['POST'])
def login():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)