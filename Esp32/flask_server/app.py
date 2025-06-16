from flask import Flask, request, jsonify
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # load env variables

app = Flask(__name__)

LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")

def log_data(data):
    try:
        with open(LOG_FILE_PATH, 'a') as f:
            timestamped_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data': data
            }
            f.write(json.dumps(timestamped_data) + '\n')
    except Exception as e:
        print(f"Error saving data to log: {e}")

@app.route('/')
def index():
    return "Welcome to the ESP32 Temperature & Humidity Logger!"

@app.route('/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()

        print(f"Received data: {data}")

        if not data or 'humidity' not in data or 'temperature_c' not in data:
            return jsonify({'message': 'Invalid data received'}), 400

        log_data(data)

        return jsonify({
            'message': 'Data received',
            'received_data': data
        })

    except Exception as e:
        print(f"Error handling request: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(host='192.168.0.10', port=5001)
