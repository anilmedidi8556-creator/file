import os
import hashlib
import threading
import time
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

directory = 'path_to_your_directory'
file_hashes = {}
changed_files = []

def compute_hash(filepath, algorithm='sha256'):
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def baseline_load():
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_hashes[filename] = compute_hash(filepath)

def monitor_changes():
    global changed_files
    while True:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                new_hash = compute_hash(filepath)
                if filename in file_hashes and new_hash != file_hashes[filename]:
                    changed_files.append(filename)
                file_hashes[filename] = new_hash
        time.sleep(10)

@app.route('/')
def index():
    return render_template('index.html', changed_files=changed_files)

@app.route('/scan', methods=['GET'])
def scan_files():
    result = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            h = compute_hash(filepath)
            changed = filename in changed_files
            result.append({'filename': filename, 'hash': h, 'changed': changed})
    return jsonify(result)

if __name__ == '__main__':
    baseline_load()
    t = threading.Thread(target=monitor_changes, daemon=True)
    t.start()
    app.run(debug=True)
