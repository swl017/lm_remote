from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

LM_STUDIO_URL = "http://localhost:1234"  # Adjust this to your LM Studio address

@app.route('/')
def index():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Template folder path: {app.template_folder}")
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Exception when rendering template: {str(e)}")
        return f"Error: {str(e)}"

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json['prompt']
    
    # Send request to LM Studio API
    response = requests.post(f"{LM_STUDIO_URL}/v1/completions", json={
        "prompt": prompt,
        "max_tokens": 100  # Adjust as needed
    })
    
    if response.status_code == 200:
        generated_text = response.json()['choices'][0]['text']
        return jsonify({'generated_text': generated_text})
    else:
        return jsonify({'error': 'Failed to generate text'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)