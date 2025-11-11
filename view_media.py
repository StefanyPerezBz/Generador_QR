import streamlit as st
from services.supabase_client import supabase
from PIL import Image
from pyzbar.pyzbar import decode
import io
import urllib.parse as urlparse
import os
import re
import shutil

st.set_page_config(page_title="Ver documento", page_icon="🎧", layout="centered")

st.title("📄 Visualizador de Documento por QR")

query_params = st.query_params
doc_id = query_params.get("doc_id", None)

# --- Función para obtener documento desde Supabase ---
def obtener_documento(doc_id):
    doc = supabase.table("media_documents").select("*").eq("id", doc_id).execute()
    if not doc.data:
        return None
    return doc.data[0]

# --- Función para limpiar nombres de archivo problemáticos ---
def limpiar_nombre_archivo(file_path):
    if not os.path.exists(file_path):
        return file_path
    folder, filename = os.path.split(file_path)
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    safe_path = os.path.join(folder, safe_name)
    if safe_path != file_path:
        try:
            shutil.move(file_path, safe_path)
        except Exception:
            pass
    return safe_path

# --- Mostrar documento multimedia ---
def mostrar_documento(doc):
    st.subheader(doc["title"])
    st.write(doc["description"] if doc["description"] else "Sin descripción disponible.")

    try:
        safe_path = limpiar_nombre_archivo(doc["media_url"])
        if doc["media_type"] == "image":
            st.image(safe_path, caption="Imagen")
        elif doc["media_type"] == "video":
            st.video(safe_path)
        elif doc["media_type"] == "audio":
            st.audio(safe_path)
    except Exception as e:
        st.error(f"⚠️ No se pudo abrir el archivo multimedia: {e}")
        st.info("Verifique que el archivo exista en la carpeta `media/` y que no tenga espacios o símbolos especiales en el nombre.")

# --- Procesar QR subido ---
def procesar_imagen_qr(uploaded_qr):
    try:
        image = Image.open(io.BytesIO(uploaded_qr.read()))
        decoded_objects = decode(image)
        if not decoded_objects:
            st.error("⚠️ No se detectó ningún código QR en la imagen. Intente con una imagen más clara.")
            return
        qr_data = decoded_objects[0].data.decode("utf-8")
        parsed = urlparse.urlparse(qr_data)
        params = urlparse.parse_qs(parsed.query)
        doc_id = params.get("doc_id", [None])[0]
        if not doc_id:
            st.error("⚠️ El código QR no contiene un ID de documento válido.")
            return
        doc = obtener_documento(doc_id)
        if not doc:
            st.error("❌ Documento no encontrado en la base de datos.")
        else:
            st.success("✅ Código QR leído correctamente.")
            mostrar_documento(doc)
    except Exception as e:
        st.error(f"Ocurrió un error al leer el código QR: {e}")

# --- Mostrar vista según doc_id ---
if doc_id:
    doc = obtener_documento(doc_id)
    if not doc:
        st.warning("⚠️ Por favor, escanee un código QR válido o suba una imagen del QR.")
        uploaded_qr = st.file_uploader("Suba la imagen del código QR", type=["png", "jpg", "jpeg"])
        if uploaded_qr:
            procesar_imagen_qr(uploaded_qr)
    else:
        mostrar_documento(doc)
        if st.button("🔁 Escanear o subir otro QR"):
            st.query_params.clear()
            st.rerun()
else:
    st.info("📷 Puede subir una imagen del código QR para ver el documento asociado.")
    uploaded_qr = st.file_uploader("Suba la imagen del código QR", type=["png", "jpg", "jpeg"])
    if uploaded_qr:
        procesar_imagen_qr(uploaded_qr)
