'''
ONLY EXPLOIT STRATEGY, BASED ON ROLLING PERFORMANCE
'''


import requests
import random
from metrics import response_map, trim_response_map, analyze_performance, best_aa_requests  # Import necessary metrics
from datetime import datetime
from job import AA_IDS, FIP_IDS, USER_ID, select_aa_uniformly

# Function to send requests to the best AA for a given FIP and user ID
def send_requests_to_best_aa(user_id, fip_id):
    print("best_aa_requests", best_aa_requests)
    best_aa = best_aa_requests.get(fip_id, select_aa_uniformly())
    response = requests.post('http://localhost:5000/api/callAA', json={
        'AAID': best_aa,
        'userID': user_id,
        'fipID': fip_id
    })
    return response, best_aa

# New function to calculate success percentage
def calculate_success_percentage(success_count, total_requests):
    return (success_count / total_requests) * 100 if total_requests > 0 else 0

# New function for rolling strategy-based firing
def rolling_strategy_firing(total_requests=500, keep_size=50):
    success_count = 0  # Initialize success count
    global response_map
    for _ in range(total_requests):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, best_aa = send_requests_to_best_aa(user_id, fip_id)

        # Count successful responses
        if response.status_code == 200:
            success_count += 1

        # Update response map
        response_map.append({
            'AAID': best_aa,
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
        response_map = trim_response_map(keep_size)  # Adjust size as needed
        best_aa_requests = analyze_performance()
        print("size response map", len(response_map))
        print(best_aa_requests)
    return success_count  # Return the success count

# Execute the rolling strategy firing
if __name__ == '__main__':
    total_requests = 500  # Store total requests for success percentage calculation
    keep_size = 100
    success_count = rolling_strategy_firing(total_requests, keep_size)  # Call the new rolling strategy function
    success_percentage = calculate_success_percentage(success_count, total_requests)  # Calculate success percentage
    print(f"Success Percentage: {success_percentage:.2f}%")  # Print success percentage
    print(best_aa_requests)