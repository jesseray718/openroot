from flask import Flask, request, jsonify
import subprocess, os, json
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get('prompt', '')
    provider = data.get('provider', 'groq')
    
    # For now, just route to Groq
    groq_key = os.environ.get('GROQ_API_KEY')
    if not groq_key:
        return jsonify({'error': 'GROQ_API_KEY not set'}), 500
    
    result = subprocess.run([
        'python3', '-c', f'''
import os, sys
try:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": """{prompt}"""}]
    )
    print(resp.choices[0].message.content)
except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
'''], capture_output=True, text=True, env={**os.environ})
    
    return jsonify({
        'response': result.stdout.strip(),
        'errors': result.stderr.strip()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'alive',
        'provider': 'groq' if os.environ.get('GROQ_API_KEY') else 'no_keys'
    })

if __name__ == '__main__':
    print("Starting bridge on port 9999...")
    app.run(host='0.0.0.0', port=9999, debug=False)
