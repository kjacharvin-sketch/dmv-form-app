from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file(os.path.join(os.getcwd(), 'dmv_app.html'))

@app.route('/generate', methods=['POST'])
def generate():
    return {"status": "working"}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
