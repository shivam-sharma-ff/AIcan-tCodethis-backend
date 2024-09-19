import requests
import random
from collections import defaultdict
from metrics import analyze_performance, response_map, best_aa_requests,reset_metrics, trim_response_map # Import the new metrics
from datetime import datetime

# Configuration for AA and FIP IDs
AA_IDS = ['AA1', 'AA2', 'AA3']
FIP_IDS = ['fip1', 'fip2']
USER_ID = 'user123'  # Example user ID


def select_aa_uniformly():
    return random.choice(AA_IDS)  # Uniformly select an AA from the list