#!/usr/bin/env python3
"""Flask server for NY DMV Form Filler."""

import json
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory

# Add the fill_forms script
sys.path.insert(0, '/home/claude')
from fill_forms import fill_all_forms

app = Flask(__name__)
OUTPUT_DIR = '/mnt/user-data/outputs'
BASE_DIR = '/home/claude'

import os

@app.route('/')
def index():
    return send_file(os.path.join(os.getcwd(), 'dmv_app.html'))

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        results = fill_all_forms(data, BASE_DIR, OUTPUT_DIR)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    safe = os.path.basename(filename)
    return send_from_directory(OUTPUT_DIR, safe, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("NYS DMV Form Filler server starting on http://localhost:7860")
    app.run(host='0.0.0.0', port=7860, debug=False)
