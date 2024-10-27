from flask import Flask, request, render_template, send_file, url_for
import qrcode
from io import BytesIO
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Folder to store uploaded files
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Generate QR Code
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    link = request.form.get('link')  # External link
    file = request.files.get('file')  # Uploaded file

    # Determine what the QR code should link to
    if link:
        # Generate a QR code for the external link
        data = link
    elif file:
        # Save the uploaded file and generate a link to it
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate a URL for the file
        data = url_for('uploaded_file', filename=filename, _external=True)
    else:
        return "Please provide either a link or a file to generate a QR code."

    # Create a QR code with the determined data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Send the QR code as a response
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)
