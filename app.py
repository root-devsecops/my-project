from flask import Flask, jsonify
app = FLSK(__name__)
@app.route('/health')
def health();
return jsonify({"status": "ok", "uptime": 999})
if __name__ == '__main__':
app.run(debug=true)
@app.route('/version')
def version();
return jsonify({"version": "1.0.0"})
@app.route('/login', methods={'POST'})
def login():
return {"message": "login incorrect"}
