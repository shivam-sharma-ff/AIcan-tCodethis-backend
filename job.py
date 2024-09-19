import requests
import random
from collections import defaultdict
from metrics import analyze_performance, response_map, best_aa_requests,reset_metrics, trim_response_map # Import the new metrics
from datetime import datetime

# Configuration for AA and FIP IDs
AA_IDS = ['AA1', 'AA2', 'AA3']
FIP_IDS = ['fip1', 'fip2']
USER_ID = 'user123'  # Example user ID

# Configuration for epsilon-greedy
EPSILON = 0.1  # Probability of exploration

# Function to send initial requests
def send_requests_uniformly(user_id, fip_id):
    aa_id = select_aa_uniformly()  # New method to select AA uniformly
    
    response = requests.post('http://localhost:5000/api/callAA', json={
        'AAID': aa_id,
        'userID': user_id,  # Use external user_id
        'fipID': fip_id     # Use external fip_id
    })

    return response, aa_id  # Return the response

# New method to select AA uniformly
def select_aa_uniformly():
    return random.choice(AA_IDS)  # Uniformly select an AA from the list

# New method for epsilon-greedy selection of AA
def select_aa_epsilon_greedy(fip_id):
    if random.random() < EPSILON:
        return select_aa_uniformly()  # Explore: select randomly
    else:
        return best_aa_requests.get(fip_id, select_aa_uniformly())  # Fallback to uniform if no best AA

# Function to send requests to the best AA for a given FIP and user ID
def send_requests_to_best_aa(user_id, fip_id):
    best_aa = best_aa_requests.get(fip_id)
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

# New function for the third firing job
def third_firing_job(fip_id, user_id):
    final_success_count = 0
    total_final_requests = 0

    fip_id = random.choice(FIP_IDS)
    user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
    total_final_requests += 1
    best_aa = select_aa_epsilon_greedy(fip_id)  # Use epsilon-greedy selection

    response = requests.post('http://localhost:5000/api/callAA', json={
        'AAID': best_aa,
        'userID': user_id,
        'fipID': fip_id
    })
    return response, best_aa

# Execute the functions
if __name__ == '__main__':
    for _ in range(150):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, aa_id = send_requests_uniformly(user_id, fip_id)
        response_map.append({
            'AAID': aa_id,  # Assuming AAID is in the response
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
        # response_map = trim_response_map(10)
        # print(response_map)
    initial_success_count = sum(1 for data in response_map if data['status_code'] == 200)
    total_initial_requests = len(response_map)

    analyze_performance()  # Analyze performance and determine the best AA for each FIP
    print(best_aa_requests)

    final_success_count = 0
    total_final_requests = 0
    for _ in range(150):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        total_final_requests += 1
        final_success_count += send_requests_to_best_aa(user_id, fip_id)  # Send requests to the best AA for each FIP

    # Calculate success percentages
    initial_success_percentage = (initial_success_count / total_initial_requests) * 100 if total_initial_requests > 0 else 0
    final_success_percentage = (final_success_count / total_final_requests) * 100 if total_final_requests > 0 else 0

    # Calculate the difference
    success_difference = final_success_percentage - initial_success_percentage

    reset_metrics()
    for _ in range(300):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, best_aa = third_firing_job(fip_id, user_id)  # Call the new third firing job
        response_map.append({
            'AAID': aa_id,  # Assuming AAID is in the response
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
        analyze_performance()
    print(best_aa_requests)
    epsilon_success_count = sum(1 for data in response_map if data['status_code'] == 200)
    total_epsilon_requests = len(response_map)
    print("initial success %", (initial_success_percentage + final_success_percentage) / 2)
    print("third firing success %", (epsilon_success_count / total_epsilon_requests) * 100 if total_initial_requests > 0 else 0)    