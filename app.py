from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

OPENCELLID_URL = "https://us1.unwiredlabs.com/v2/process.php"
API_TOKEN = "pk.7dab36660f5c40b48a186d5cacc70785"

@app.route('/', methods=['GET'])
def health():
    return 'OK', 200
    
@app.route('/locate', methods=['POST'])
def locate():
    try:
        data = request.get_json()
        if not data or 'cellTowers' not in data:
            return jsonify({'error': 'Invalid or missing JSON'}), 400

        cell = data['cellTowers'][0]

        for radio_type in ['umts', 'lte', 'gsm']:
            payload = {
                'token': API_TOKEN,
                'radio': radio_type,
                'mcc': cell.get('mobileCountryCode'),
                'mnc': cell.get('mobileNetworkCode'),
                'lac': cell.get('locationAreaCode'),
                'cid': cell.get('cellId'),
                'address': 1
            }

            response = requests.post(OPENCELLID_URL, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            json_data = response.json()

            if json_data.get('status') == 'ok' and 'lat' in json_data and 'lon' in json_data:
                json_data['radio_used'] = radio_type
                return jsonify(json_data), 200

        return jsonify({'status': 'not_found', 'message': 'Cell not found in any radio type'}), 404

    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to reach OpenCelliD', 'details': str(e)}), 502
    except Exception as ex:
        return jsonify({'error': 'Internal server error', 'details': str(ex)}), 500



