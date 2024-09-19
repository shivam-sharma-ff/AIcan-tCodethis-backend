from flask import Flask, jsonify
import random
from flask import request

app = Flask(__name__)

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
    
@app.route('/update_metadata', methods=['POST'])
def update_metadata():
    global AA_AVAILABILITY
    data = request.json
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data format"}), 400
    
    # Update AA_AVAILABILITY with the received data
    new_aa_availability = {}
    for fip_data, aa_id in data.items():
        for aa_id, value in aa_id.items():
            if fip_data not in new_aa_availability:
                new_aa_availability[fip_data] = {}
            new_aa_availability[fip_data][aa_id] = value / 100  # Convert to probability
    
    AA_AVAILABILITY = new_aa_availability
    
    return jsonify({"message": "Metadata updated successfully" + str(AA_AVAILABILITY)})


if __name__ == '__main__':
    app.run(debug=True)
