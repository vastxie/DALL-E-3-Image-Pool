from flask import Flask, jsonify, request
import requests
import random
from qcloud_cos import CosConfig, CosS3Client
import datetime
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

secret_id = os.environ.get('COS_SECRET_ID')
secret_key = os.environ.get('COS_SECRET_KEY')
region = os.environ.get('COS_REGION')
bucket_name = os.environ.get('COS_BUCKET_NAME')
service_api_key = os.environ.get('SERVICE_API_KEY')

cos_config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
cos_client = CosS3Client(cos_config)

api_keys_file = 'api_keys.txt'

def get_random_key():
    with open(api_keys_file, 'r') as file:
        keys = [key.strip() for key in file.readlines() if key.strip()]
    return random.choice(keys) if keys else None

def remove_invalid_key(key_to_remove):
    with open(api_keys_file, 'r') as file:
        keys = [key.strip() for key in file.readlines() if key.strip() and key.strip() != key_to_remove]
    with open(api_keys_file, 'w') as file:
        for key in keys:
            file.write(key + "\n")

def fetch_image(url, json, headers):
    response = requests.post(url, json=json, headers=headers)
    return response.json(), response.status_code

def upload_to_cos(image_data, bucket, object_name):
    try:
        cos_client.put_object(
            Bucket=bucket,
            Body=image_data.getvalue(),
            Key=object_name,
        )
        return f'https://{bucket}.cos.accelerate.myqcloud.com/{object_name}'
    except Exception as e:
        return False

@app.route('/v1/images/generations', methods=['POST'])
def generate_image():
    auth_header = request.headers.get('Authorization')
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Bearer' or parts[1] != service_api_key:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'dall-e-3')
    n = data.get('n', 1)
    quality = data.get('quality', 'standard')
    size = data.get('size', '1024x1024')
    
    max_retries = 10
    attempts = 0

    while attempts < max_retries:
        api_key = get_random_key()
        if not api_key:
            return jsonify({'error': 'No available API keys'}), 500

        payload = {
            'prompt': prompt,
            'model': model,
            'n': n,
            'quality': quality,
            'size': size,
        }

        response_data, status_code = fetch_image('https://api.openai.com/v1/images/generations', payload, {'Authorization': f'Bearer {api_key}'})
        
        if status_code == 400:
            return jsonify({'error': response_data.get('error', {}).get('message', 'Content policy violation')}), 400

        if status_code == 200:
            image_url = response_data['data'][0]['url']
            image_response = requests.get(image_url)
            image_data = BytesIO(image_response.content)
        
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            object_name = f"images/{timestamp}.jpg"

            upload_url = upload_to_cos(image_data, bucket_name, object_name)
            if upload_url:
                response_data['data'][0]['url'] = upload_url
                return jsonify(response_data)
            else:
                return jsonify({'error': 'Failed to upload image to Tencent Cloud COS'}), 500

        if not (status_code == 429 and response_data.get('error', {}).get('code') == 'rate_limit_exceeded'):
            remove_invalid_key(api_key)
        attempts += 1
        if attempts >= max_retries:
            return jsonify({'error': 'All retries failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
