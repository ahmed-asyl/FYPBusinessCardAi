from flask import Flask, request, jsonify, send_file
from Extractor import analyze_business_card, business_card_confidence
from flask_cors import CORS
import vobject
import qrcode
import os
import time

app = Flask(__name__)
CORS(app)

@app.route('/analyze_document', methods=['POST'])
def analyze_document_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Read the image file
    byte_data = file.read()

    # Extract contact details using Azure Form Recognizer (implemented in extractor.py)
    contact_details = analyze_business_card(byte_data)

    # get confidence data
    contact_confidence = business_card_confidence(byte_data)

    # Create VCF file
    qr_url = create_vcard_qr(contact_details)


    # Return QR code path and contact details as JSON
    return jsonify({
        "contact_details": contact_details,
        "contact_confidence": contact_confidence,
        "qr_code_url": qr_url
    })


def create_vcard_qr(contact_details):
    # Create a vCard object
    vcard = vobject.vCard()

    vcard.add('fn').value = contact_details['full_name']

    if 'company' in contact_details:
        org = vcard.add('org')
        org.value = [contact_details['company']]

    if 'position' in contact_details:
        title = vcard.add('title')
        title.value = contact_details['position']

    if 'phone' in contact_details:
        tel = vcard.add('tel')
        tel.value = contact_details['phone']
        tel.type_param = 'WORK'

    if 'phone_1' in contact_details:
        tel = vcard.add('tel')
        tel.value = contact_details['phone_1']
        tel.type_param = 'WORK'

    if 'phone_2' in contact_details:
        tel = vcard.add('tel')
        tel.value = contact_details['phone_2']
        tel.type_param = 'HOME'

    if 'email' in contact_details:
        email = vcard.add('email')
        email.value = contact_details['email']
        email.type_param = 'INTERNET'

    if 'address' in contact_details:
        adr = vcard.add('adr')
        adr.value = vobject.vcard.Address(
            street=contact_details['address'],
            city='',
            region='',
            code='',
            country=''
        )
        adr.type_param = 'WORK'

    # Serialize the vCard into a string
    vcard_data = vcard.serialize()

    # Extract the full name (FN) from the vCard data
    try:
        name_line = next(line for line in vcard_data.splitlines() if line.startswith("FN:"))
        full_name = name_line.replace("FN:", "").strip().replace(" ", "_")
    except StopIteration:
        # Fallback in case FN is not found
        full_name = "contact"

    # Generate a unique filename using the name and the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    qr_filename = f"{full_name}_vcard_qr_{timestamp}.png"

    # Create a QR code from the vCard data
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard_data)  # Add the vCard data to the QR code
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a file with a dynamic name
    save_path = os.path.join('static', 'qr_codes', qr_filename)
    img.save(save_path)

    qr_url = f'/static/qr_codes/{qr_filename}'

    return qr_url


if __name__ == '__main__':
    app.run(debug=True)
