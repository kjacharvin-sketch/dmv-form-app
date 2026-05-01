from flask import Flask, send_file, request, jsonify
import os

from fill_forms import fill_all_forms

app = Flask(__name__)

# Home page
from flask import send_from_directory

@app.route('/')
def index():
    return send_from_directory('.', 'dmv_app.html')

# Generate forms
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()  # ✅ FIXED

        print("FORM DATA:", data)

        output_files = fill_all_forms(data)

        return jsonify({
            "success": True,
            "files": output_files
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Download files
@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(os.getcwd(), 'outputs', filename),
        as_attachment=True
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
