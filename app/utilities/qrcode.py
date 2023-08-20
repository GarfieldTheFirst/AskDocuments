from qrcode import QRCode, constants
from qrcode.image import svg


def get_qr_code(data):
    qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_L,
            box_size=40,
            border=4,
        )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white",
                        image_factory=svg.SvgImage)
    return img
