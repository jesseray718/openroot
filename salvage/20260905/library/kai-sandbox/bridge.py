from flask import Flask, request, jsonify
import os
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get('prompt', '')
    try:
        from groq import Groq
        client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({'response': resp.choices[0].message.content, 'error': None})
    except Exception as e:
        return jsonify({'response': None, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({
        'status': 'alive',
        'key_present': bool(os.environ.get('GROQ_API_KEY'))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False, use_reloader=False)
