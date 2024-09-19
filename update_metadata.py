from collections import defaultdict

# Dictionary to store responses
response_map = {}
best_aa_requests = {}

def analyze_performance():
    global best_aa_requests
    global response_map
    # Initialize or reset the global best_aa_requests

    performance_map = defaultdict(lambda: defaultdict(lambda: {'success': 0, 'total': 0}))

    # Analyze the response_map
    for request_id, data in response_map.items():
        aa_id = data['AAID']
        fip_id = data['fipID']
        status_code = data['status_code']

        performance_map[fip_id][aa_id]['total'] += 1
        if status_code == 200:
            performance_map[fip_id][aa_id]['success'] += 1

    # Determine the best-performing AA for each FIP
    for fip_id, aa_data in performance_map.items():
        best_aa = max(aa_data.items(), key=lambda item: item[1]['success'] / item[1]['total'] if item[1]['total'] > 0 else 0)
        best_aa_requests[fip_id] = best_aa[0]  # Store the best AA ID

def reset_metrics():
    global response_map
    global best_aa_requests
    response_map = {}  # Reset the response map
    best_aa_requests = {}  # Reset the best AA requests
