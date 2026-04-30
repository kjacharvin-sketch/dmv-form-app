from flask import Flask, send_file, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file(os.path.join(os.getcwd(), 'dmv_app.html'))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form.to_dict()

    print("FORM DATA:", data)  # shows in Render logs

    return jsonify({
        "success": True,
        "data": data
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
