import qrcode
import os
import uuid

def generate_qr(document_id: str, base_url: str) -> str:
    """Genera un QR único y lo guarda en la carpeta assets/qrs"""
    qr_folder = "assets/qrs"
    os.makedirs(qr_folder, exist_ok=True)

    qr_filename = f"{document_id}.png"
    qr_path = os.path.join(qr_folder, qr_filename)

    qr_link = f"{base_url}?doc_id={document_id}"
    img = qrcode.make(qr_link)
    img.save(qr_path)

    return qr_path
