import streamlit as st
from services.supabase_client import supabase
from PIL import Image
import io
import urllib.parse as urlparse
import requests
import cv2
import numpy as np

# ==============================================
# ⚙️ CONFIGURACIÓN INICIAL
# ==============================================
st.set_page_config(page_title="Ver documento", page_icon="🎧", layout="centered")

# ==============================================
# 🎨 ESTILOS PERSONALIZADOS
# ==============================================
st.markdown("""
<style>
    .block-container {
        max-width: 800px;
        margin: auto;
        padding-top: 1rem;
    }

    .stButton>button {
        background-color: #28A745;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #218838;
        transform: scale(1.03);
    }

    h1, h2, h3 {
        text-align: center;
    }

    .footer {
        text-align: center;
        color: gray;
        font-size: 14px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================
# 🧩 FUNCIONES PRINCIPALES
# ==============================================

def obtener_documento(doc_id: str):
    """Obtiene un documento desde Supabase por su ID."""
    try:
        doc = supabase.table("media_documents").select("*").eq("id", doc_id).execute()
        return doc.data[0] if doc.data else None
    except Exception as e:
        st.error(f"❌ Error al obtener el documento: {e}")
        return None


def mostrar_documento(doc):
    """Muestra el documento multimedia según su tipo."""
    st.subheader(doc["title"])
    st.write(doc["description"] or "Sin descripción disponible.")

    try:
        if doc["media_type"] == "image":
            st.image(doc["media_url"], caption="📷 Imagen cargada")
        elif doc["media_type"] == "video":
            st.video(doc["media_url"])
        elif doc["media_type"] == "audio":
            st.audio(doc["media_url"])
        else:
            st.warning("⚠️ Tipo de archivo no soportado.")
    except Exception as e:
        st.error(f"⚠️ No se pudo abrir el archivo multimedia: {e}")


def procesar_imagen_qr(uploaded_qr):
    """Lee una imagen de QR usando OpenCV."""
    try:
        file_bytes = np.asarray(bytearray(uploaded_qr.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        detector = cv2.QRCodeDetector()
        qr_data, points, _ = detector.detectAndDecode(image)

        if not qr_data:
            st.error("⚠️ No se pudo detectar ningún código QR.")
            return

        # Extraer doc_id del enlace
        parsed = urlparse.urlparse(qr_data)
        params = urlparse.parse_qs(parsed.query)
        doc_id = params.get("doc_id", [None])[0]

        if not doc_id:
            st.error("⚠️ El QR no contiene un ID válido.")
            return

        doc = obtener_documento(doc_id)

        if not doc:
            st.error("❌ Documento no encontrado.")
        else:
            st.success("✅ Código QR leído correctamente.")
            mostrar_documento(doc)

    except Exception as e:
        st.error(f"❌ Error al procesar el QR: {e}")


def reiniciar_pantalla():
    """Reinicia completamente la app."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()

# ==============================================
# 🧭 FLUJO PRINCIPAL
# ==============================================
st.title("📄 Visualizador de Documento por QR")

# Leer parámetros de la URL
query_params = st.experimental_get_query_params()
doc_id = query_params.get("doc_id", [None])[0]

if doc_id:
    doc = obtener_documento(doc_id)
    if doc:
        mostrar_documento(doc)
        st.markdown("---")
        if st.button("Escanear otro QR"):
            reiniciar_pantalla()
    else:
        st.warning("⚠️ QR inválido o documento no encontrado.")
        uploaded_qr = st.file_uploader("📷 Suba la imagen del código QR", type=["png", "jpg", "jpeg"])
        if uploaded_qr:
            procesar_imagen_qr(uploaded_qr)
else:
    st.info("📷 Suba una imagen del código QR para visualizar su documento asociado.")
    uploaded_qr = st.file_uploader("Suba la imagen del código QR", type=["png", "jpg", "jpeg"])
    if uploaded_qr:
        procesar_imagen_qr(uploaded_qr)

# ==============================================
# ✨ FOOTER
# ==============================================
st.markdown("---")
st.markdown(
    "<div class='footer'>© 2025 QR Media App</div>",
    unsafe_allow_html=True,
)
