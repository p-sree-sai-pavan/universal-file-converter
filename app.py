import os
from flask import Flask, request, render_template, send_file, redirect, url_for
import uuid
from universal_file_converter import ConversionRegistry, FFmpegConverter, ImageMagickConverter, UnoconvConverter # Import necessary classes

app = Flask(__name__)

# --- Configuration ---
# Create directories for storing uploaded and converted files
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
# Ensure these directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Max upload size: 16 MB

# --- Initialize the Conversion Registry ---
# You can customize the plugins here if needed
registry = ConversionRegistry()
# You might want to dynamically get supported formats for the frontend
SUPPORTED_INPUT_FORMATS = sorted(list(registry.graph.keys()))
ALL_POSSIBLE_OUTPUT_FORMATS = sorted(list(set(fmt for sub_dict in registry.graph.values() for fmt in sub_dict.keys())))


# --- Routes ---

@app.route('/')
def index():
    """Renders the main upload form."""
    return render_template(
        'index.html',
        supported_input_formats=SUPPORTED_INPUT_FORMATS,
        all_possible_output_formats=ALL_POSSIBLE_OUTPUT_FORMATS
    )

@app.route('/convert', methods=['POST'])
def convert_file():
    """Handles file upload and conversion."""
    if 'file' not in request.files:
        return render_template('index.html', error="No file part in the request."), 400

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', error="No selected file."), 400

    # Get target extension from the form
    target_ext = request.form.get('target_extension')
    if not target_ext:
        return render_template('index.html', error="No target format selected."), 400

    original_filename = file.filename
    # Ensure filename is safe (basic sanitization)
    original_filename_base, original_ext_full = os.path.splitext(original_filename)
    original_ext = original_ext_full.lstrip('.').lower() # Get extension without dot

    # Create unique filenames to avoid conflicts and improve security
    unique_id = str(uuid.uuid4())
    infile_name = f"{unique_id}_input.{original_ext}"
    outfile_name = f"{unique_id}_output.{target_ext}"

    infile_path = os.path.join(app.config['UPLOAD_FOLDER'], infile_name)
    outfile_path = os.path.join(app.config['CONVERTED_FOLDER'], outfile_name)

    try:
        # Save the uploaded file
        file.save(infile_path)

        # Perform the conversion using your registry
        print(f"Attempting to convert {infile_path} to {outfile_path}")
        registry.convert(infile_path, outfile_path)
        print(f"Conversion successful to {outfile_path}")

        # Send the converted file back to the user for download
        # Use a more user-friendly download name
        download_name = f"{original_filename_base}_converted.{target_ext}"
        response = send_file(outfile_path, as_attachment=True, download_name=download_name)
        return response

    except Exception as e:
        print(f"Conversion error: {e}")
        return render_template('index.html', error=f"Conversion failed: {e}"), 500
    finally:
        # Clean up temporary files regardless of success or failure
        if os.path.exists(infile_path):
            os.remove(infile_path)
            print(f"Cleaned up {infile_path}")
        if os.path.exists(outfile_path):
            # For simplicity, remove after sending. For persistent storage, adjust.
            # send_file usually handles removal if it's the last use.
            pass # We rely on send_file to manage the file, or implement a background cleaner.
        print(f"File paths: infile={infile_path}, outfile={outfile_path}")

if __name__ == '__main__':
    # Run the Flask development server
    # In production, use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True) # debug=True enables auto-reloading and shows detailed errors