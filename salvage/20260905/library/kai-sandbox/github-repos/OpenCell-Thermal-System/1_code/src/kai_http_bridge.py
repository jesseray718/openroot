import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)
last_output = ""

@app.route('/press', methods=['POST'])
def press():
    global last_output
    cmd = request.json.get('cmd')
    if not cmd:
        return jsonify({"error":"no cmd"}),400
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        last_output = result.stdout + result.stderr
        return jsonify({"ok":True, "output":last_output})
    except Exception as e:
        last_output = str(e)
        return jsonify({"ok":False, "error":str(e)})

@app.route('/status')
def status():
    return jsonify({"output":last_output})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
