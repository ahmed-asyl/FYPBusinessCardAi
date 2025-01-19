import qrcode

# Create a QR code object
qr = qrcode.QRCode(version=1, box_size=10, border=5)

import vobject

# Assume vcard_object is your vCard object
vcard_object = vobject.vCard()
vcard_object.add('fn').value = 'CHRIS SALCEDO'
vcard_object.add('title').value = 'APPRENTICE'
adr = vcard_object.add('adr')
adr.type_param = 'WORK'
adr.value = vobject.vcard.Address(street="2675 EL CAMINO REAL", city="PALO ALTO", region="CA", code="94306", country="")
adr.value.street = "CHIPOTLE MEXICAN GRILL, INC. 2675 EL CAMINO REAL"
adr.value.city = "PALO ALTO"
adr.value.region = "CA"
adr.value.code = "94306"

# Convert the vCard object back to a string
vcard_string = vcard_object.serialize()

# Add the vCard data to the QR code object
qr.add_data(vcard_string)

# Make the QR code
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code image
img.save("qr_code_vcard.png")