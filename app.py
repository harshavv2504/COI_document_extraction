import os
# Load environment variables from .env file before anything else
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
from modules.ocr_module import run_ocr
from modules.prompt_builder import build_prompt
from modules.openai_module import extract_json_from_md
from modules.pdf_generator import generate_pdf_from_json
import json
from datetime import datetime

app = Flask(__name__)

# --- CONFIG ---
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

OUTPUT_JSON_DIR = "extracted_json"
os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)

DOCUMENTS_DB = os.path.join(app.root_path, 'documents.json')

# --- DB HELPER FUNCTIONS ---
def read_documents_db():
    if not os.path.exists(DOCUMENTS_DB):
        with open(DOCUMENTS_DB, 'w') as f:
            json.dump([], f)
        return []
    with open(DOCUMENTS_DB, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_documents_db(data):
    with open(DOCUMENTS_DB, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            filename = secure_filename(file.filename)
            pdf_content = file.read()

            user_input = run_ocr(pdf_content)
            prompt = build_prompt()
            json_output = extract_json_from_md(prompt, user_input)

            output_filename = f"{os.path.splitext(filename)[0]}.json"
            output_filepath = os.path.join(OUTPUT_JSON_DIR, output_filename)
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(json_output)

            documents = read_documents_db()
            new_doc = {
                'filename': output_filename,
                'custom_name': request.form.get('custom_name'),
                'external_id': request.form.get('external_id'),
                'tenant_code': request.form.get('tenant_code'),
                'property_no': request.form.get('property_no'),
                'action': request.form.get('action'),
                'upload_date': datetime.utcnow().isoformat(),
                'status': 'uploaded'
            }
            documents.append(new_doc)
            write_documents_db(documents)

            return jsonify({'message': 'File processed successfully', 'filename': output_filename})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File processing failed'}), 500

@app.route('/get_documents', methods=['GET'])
def get_documents():
    documents = read_documents_db()
    return jsonify(sorted(documents, key=lambda x: x['upload_date'], reverse=True))

@app.route('/get_processed_files')
def get_processed_files():
    try:
        files = [f for f in os.listdir(OUTPUT_JSON_DIR) if f.endswith('.json')]
        return jsonify(sorted(files, reverse=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_json/<filename>')
def get_json(filename):
    return send_from_directory(directory=OUTPUT_JSON_DIR, path=filename)

@app.route('/download_json/<filename>')
def download_json(filename):
    if not os.path.exists(OUTPUT_JSON_DIR):
        return 'Directory not found', 404
    return send_from_directory(directory=OUTPUT_JSON_DIR, path=filename, as_attachment=True)

@app.route('/download_pdf/<filename>')
def download_pdf(filename):
    try:
        json_path = os.path.join(OUTPUT_JSON_DIR, filename)
        if not os.path.exists(json_path):
            return 'File not found', 404

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename) # Storing in uploads temporarily

        generate_pdf_from_json(data, pdf_path)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return str(e), 500

@app.route('/save_json/<filename>', methods=['POST'])
def save_json(filename):
    try:
        updated_data = request.get_json()
        filepath = os.path.join(OUTPUT_JSON_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=4)
        
        documents = read_documents_db()
        for doc in documents:
            if doc['filename'] == filename:
                doc['status'] = 'in_progress'
                break
        write_documents_db(documents)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mark_complete/<filename>', methods=['POST'])
def mark_complete(filename):
    try:
        documents = read_documents_db()
        for doc in documents:
            if doc['filename'] == filename:
                doc['status'] = 'verified'
                break
        write_documents_db(documents)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_document/<filename>', methods=['DELETE'])
def delete_document(filename):
    try:
        # Remove from the JSON file system
        filepath = os.path.join(OUTPUT_JSON_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Remove from the DB
        documents = read_documents_db()
        updated_documents = [doc for doc in documents if doc['filename'] != filename]
        write_documents_db(updated_documents)

        return jsonify({'message': f'Document {filename} deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
