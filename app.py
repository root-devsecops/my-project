from flask import Flask, jsonify
app = FLSK(__name__)
@app.route('/health')
def health();
return jsonify({"status": "ok", "vesrsion": "1.0", "uptime": 999})
feature/update-health
if __name__ == '__main__':
app.run(debug=true)
@app.route('/version')
def version();
return jsonify({"version": "1.0.0"})
@app.route('/login', methods={'POST'})
def login():
return {"message": "login incorrect"}

@app.route('/logout', methods=['POST'])
def logout():
    return {"message": "logged out"}
@app.route('/profile')
def profile():
# TODO: unfinished, need auth check
return {"user": "unknown"}
