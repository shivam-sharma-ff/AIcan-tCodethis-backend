import requests
import random
from datetime import datetime
from metrics import response_map, trim_response_map, analyze_performance, best_aa_requests  # Import necessary metrics
from job import AA_IDS, FIP_IDS, USER_ID, select_aa_uniformly

def send_requests_uniformly(user_id, fip_id):
    aa_id = select_aa_uniformly()  # New method to select AA uniformly
    
    response = requests.post('http://localhost:5000/api/callAA', json={
        'AAID': aa_id,
        'userID': user_id,  # Use external user_id
        'fipID': fip_id     # Use external fip_id
    })

    return response, aa_id  # Return the response

def send_requests_to_best_aa(user_id, fip_id):
    best_aa = best_aa_requests.get(fip_id)
    # print(best_aa_requests)
    if best_aa:
        success_count = 0

        response = requests.post('http://localhost:5000/api/callAA', json={
            'AAID': best_aa,
            'userID': user_id,
            'fipID': fip_id
        })
        if response.status_code == 200:
            success_count += 1

        return success_count
    else:
        return 0

if __name__ == '__main__':
    for _ in range(500):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, aa_id = send_requests_uniformly(user_id, fip_id)
        response_map.append({
            'AAID': aa_id,  # Assuming AAID is in the response
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
    initial_success_count = sum(1 for data in response_map if data['status_code'] == 200)
    total_initial_requests = len(response_map)

    print(initial_success_count/total_initial_requests*100)

    best_aa_requests = analyze_performance()

    final_success_count = 0
    total_final_requests = 0
    for _ in range(2000):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        total_final_requests += 1
        final_success_count += send_requests_to_best_aa(user_id, fip_id)  # Send requests to the best AA for each FIP

    print(final_success_count/total_final_requests*100)

    print((initial_success_count/total_initial_requests*100+final_success_count/total_final_requests*100)/2)