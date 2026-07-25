from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "ok", "service": "UNE Protocol"})

@app.route('/api/v1/resolve/<entity_id>')
def resolve(entity_id):
    return jsonify({
        "entity_id": entity_id,
        "type": "thermal" if "h003" in entity_id.lower() else "general",
        "acre_staked": 1240,
        "popw_score": 87.5,
        "attributes": {"thermal_capture_kwh_m2": 12.91, "validated": True}
    })

@app.route('/api/v1/conflict/<entity_id>')
def conflict(entity_id):
    return jsonify({
        "entity_id": entity_id,
        "has_conflict": False,
        "conflict_score": 0.0,
        "resolution": "clean"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
