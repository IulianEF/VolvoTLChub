from flask import Blueprint, jsonify
from app.models import Repair
import time

performance_tests = Blueprint('performance_tests', __name__)

@performance_tests.route('/health_check')
def health_check():
    """
    Basic health check endpoint to ensure the application is running.
    """
    return jsonify({'status': 'OK', 'message': 'Application running smoothly!'}), 200

@performance_tests.route('/load_test')
def load_test():
    """
    Simulates load to test application performance under stress.
    """
    start_time = time.time()
    for _ in range(1000):
        _ = Repair.query.all()
    end_time = time.time()
    duration = end_time - start_time
    return jsonify({'status': 'Completed', 'duration_seconds': duration}), 200