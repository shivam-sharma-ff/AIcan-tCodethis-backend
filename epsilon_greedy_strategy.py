import requests
import random
from datetime import datetime
from metrics import response_map, trim_response_map, analyze_performance, best_aa_requests  # Import necessary metrics
from job import AA_IDS, FIP_IDS, USER_ID, select_aa_uniformly

EPSILON = 0.1  # Probability of exploration

# New method for epsilon-greedy selection of AA
def select_aa_epsilon_greedy(fip_id):
    if random.random() < EPSILON:
        return select_aa_uniformly()  # Explore: select randomly
    else:
        return best_aa_requests.get(fip_id, select_aa_uniformly())  # Fallback to uniform if no best AA

# New function for the third firing job
def third_firing_job(fip_id, user_id):
    best_aa = select_aa_epsilon_greedy(fip_id)  # Use epsilon-greedy selection

    response = requests.post('http://localhost:5000/api/callAA', json={
        'AAID': best_aa,
        'userID': user_id,
        'fipID': fip_id
    })
    return response, best_aa

# Execute the rolling strategy firing
if __name__ == '__main__':
    total_responses = 0
    successful_responses = 0
    FIRE_COUNT = 500
    PAST_SIZE = 50
    for _ in range(FIRE_COUNT):
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, best_aa = third_firing_job(fip_id, user_id)  # Call the new third firing job
        response_map.append({
            'AAID': best_aa,  # Assuming AAID is in the response
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
        total_responses += 1
        if response.status_code == 200:
            successful_responses += 1
        best_aa_requests = analyze_performance()
        response_map = trim_response_map(PAST_SIZE)
        print(best_aa_requests)
        print(response_map)
    final_success_percentage = (successful_responses / total_responses) * 100 if total_responses > 0 else 0
    print(f"Final Success Percentage: {final_success_percentage:.2f}%")