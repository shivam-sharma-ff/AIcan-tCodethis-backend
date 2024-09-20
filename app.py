from flask import Flask, jsonify
import random
from flask import request
from job import AA_IDS, FIP_IDS, USER_ID
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Configuration for AA availability based on fipID
AA_AVAILABILITY = {
    'fip1': {
        'AA1': 0.95,
        'AA2': 0.2,
        'AA3': 0.85
    },
    'fip2': {
        'AA1': 0.40,
        'AA2': 0.75,
        'AA3': 0.94
    }
}
_balls = {}

def get_balls():
    return _balls
    
@app.route('/set_balls', methods=['POST'])
def set_balls():
    global _balls
    payload = request.json
    if payload is not None:
        _balls = payload
        return jsonify(_balls), 200
    else:
        return jsonify({"error": "Missing payload in request body"}), 400


@app.route('/get_balls', methods=['GET'])
def get_balls():
    global _balls
    current_balls = _balls.copy()  # Copy current balls to return
    _balls.clear()  # Clear the balls
    return jsonify(current_balls)  # Return the current balls as JSON


@app.route('/')
def hello_world():
    return jsonify({"message": "Hello, World!"})

@app.route('/api/callAA', methods=['POST'])
def call_aa():
    aa_id = request.json.get('AAID')
    user_id = request.json.get('userID')
    fip_id = request.json.get('fipID')

    if not aa_id or not user_id or not fip_id:
        return jsonify({"error": "Missing AAID, userID, or fipID"}), 400

    if fip_id not in AA_AVAILABILITY or aa_id not in AA_AVAILABILITY[fip_id]:
        return jsonify({"error": "Invalid AAID or fipID"}), 400

    # Check AA availability based on configuration
    if random.random() < AA_AVAILABILITY[fip_id][aa_id]:
        return jsonify({
            "message": f"AA {aa_id} is available for user {user_id} under fip {fip_id}",
            "status": "success"
        }), 200
    else:
        return jsonify({
            "message": f"AA {aa_id} is not available for user {user_id} under fip {fip_id}",
            "status": "failure"
        }), 500

@app.route('/api/callAA/finsense', methods=['POST'])
def call_aa_finsense():
    payload = request.json
    aa_id = payload['body']['aaId']
    user_id = payload['body']['userId']
    fip_id = payload['body']['fipId']

    if not aa_id or not user_id or not fip_id:
        return jsonify({"error": "Missing AAID, userID, or fipID"}), 400

    if fip_id not in AA_AVAILABILITY or aa_id not in AA_AVAILABILITY[fip_id]:
        return jsonify({"error": "Invalid AAID or fipID"}), 400
    
    global _balls
    balls = {aa_id: {fip_id: 1}}
    for aa in AA_IDS:
        for fip in FIP_IDS:
            if fip not in balls.get(aa, {}):
                balls.setdefault(aa, {}).setdefault(fip, 0)

    _balls = balls
    # Check AA availability based on configuration
    if random.random() < AA_AVAILABILITY[fip_id][aa_id]:
        return jsonify({
            "message": f"AA {aa_id} is available for user {user_id} under fip {fip_id}",
            "status": "success"
        }), 200
    else:
        return jsonify({
            "message": f"AA {aa_id} is not available for user {user_id} under fip {fip_id}",
            "status": "failure"
        }), 500
    
@app.route('/update_metadata', methods=['POST'])
def update_metadata():
    global AA_AVAILABILITY
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data format"}), 400
    
    # Update AA_AVAILABILITY with the received data
    new_aa_availability = {}
    for aa_id, fip_data in data.items():
        for fip_id, value in fip_data.items():
            if fip_id not in new_aa_availability:
                new_aa_availability[fip_id] = {}
            new_aa_availability[fip_id][aa_id] = value / 100  # Convert to probability
    
    AA_AVAILABILITY=(new_aa_availability)
    
    return jsonify({"message": "Metadata updated successfully" + str(AA_AVAILABILITY)})


if __name__ == '__main__':
    app.run(debug=True)
