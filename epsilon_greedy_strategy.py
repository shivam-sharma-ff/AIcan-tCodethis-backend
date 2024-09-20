import requests
import random
from datetime import datetime
from metrics import response_map, trim_response_map, analyze_performance, best_aa_requests  # Import necessary metrics
from job import AA_IDS, FIP_IDS, USER_ID, select_aa_uniformly
import time

    # Function to introduce delay
def introduce_delay():
    time.sleep(0.01) 
EPSILON = 0.1  # Probability of exploration

collate_balls = {}

def set_balls(balls):
    response = requests.post('http://localhost:5000/set_balls', json=balls)
    return response  # Return the response from the API

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
    FIRE_COUNT = 2000
    PAST_SIZE = 200
    # 100 milliseconds delay
    drop_payload = []
    for i in range(FIRE_COUNT):
        introduce_delay()
        fip_id = random.choice(FIP_IDS)
        user_id = random.choice(USER_ID)  # Ensure USER_ID is a list for random.choice
        response, best_aa = third_firing_job(fip_id, user_id)  # Call the new third firing job
        response_map.append({
            'AAID': best_aa,  # Assuming AAID is in the response
            'fipID': fip_id,
            'status_code': response.status_code,
            'timestamp': datetime.now()
        })
        balls = {best_aa: {fip_id:1}}
        for aa in AA_IDS:
            for fip in FIP_IDS:
                if fip not in balls.get(aa, {}):
                    balls.setdefault(aa, {}).setdefault(fip, 0)
                    
        if not collate_balls:
            collate_balls = balls
        else:
            for aa, fip_data in balls.items():
                for fip, count in fip_data.items():
                    collate_balls.setdefault(aa, {}).setdefault(fip, 0)
                    collate_balls[aa][fip] += count

        total_responses += 1
        if response.status_code == 200:
            successful_responses += 1

        if (i+1) % 100 == 0:
            set_balls(collate_balls)  # Set balls only when count is 100
            collate_balls = {}  # Reset collate_balls
            drop_payload.append({
                "requests": total_responses,
                "drop": total_responses - successful_responses
            })
            drop_payload_send = {
                "epsilon_greedy_strategy": drop_payload,
            }
            requests.post('http://localhost:5000/update_metrics', json=drop_payload_send)

        best_aa_requests = analyze_performance()
        response_map = trim_response_map(PAST_SIZE)
        # print(best_aa_requests)
        # print(response_map)
    final_success_percentage = (successful_responses / total_responses) * 100 if total_responses > 0 else 0
    print(f"Final Success Percentage: {final_success_percentage:.2f}%")