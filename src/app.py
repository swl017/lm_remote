from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests
import json
import os

app = Flask(__name__)

LM_STUDIO_URL = "http://localhost:1234"  # Adjust this to your LM Studio address

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json['prompt']
    
    def generate_stream():
        try:
            response = requests.post(f"{LM_STUDIO_URL}/v1/completions", 
                                     json={
                                         "prompt": prompt,
                                         "max_tokens": -1,  # Adjust as needed
                                         "stream": True
                                     },
                                     stream=True)
            
            yield f"data: {{\"debug\": \"Connected to LM Studio\"}}\n\n"
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # Remove the 'data: ' prefix if it exists
                    if decoded_line.startswith('data: '):
                        decoded_line = decoded_line[6:]
                    yield f"data: {decoded_line}\n\n"
                    app.logger.info(f"Sent line: {decoded_line}")
                else:
                    yield f"data: {{\"debug\": \"Empty line received\"}}\n\n"
            
            yield f"data: {{\"debug\": \"Stream ended\"}}\n\n"
        except requests.RequestException as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
            app.logger.error(f"Request error: {str(e)}")

    return Response(stream_with_context(generate_stream()), content_type='text/event-stream')

@app.route('/model_info', methods=['GET'])
def model_info():
    try:
        response = requests.get(f"{LM_STUDIO_URL}/v1/models")
        if response.status_code == 200:
            models = response.json()
            if models and len(models) > 0:
                return jsonify({"model_name": models[0].get("id", "Unknown")})
    except requests.RequestException as e:
        app.logger.error(f"Error fetching model info: {str(e)}")
    
    return jsonify({"model_name": "Unable to fetch model information"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)