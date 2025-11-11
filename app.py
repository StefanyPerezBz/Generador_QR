import streamlit as st
from services.supabase_client import supabase
from services.qr_utils import generate_qr
from services.auth import login
import os
import re
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Gestor de Códigos QR", page_icon="🎥", layout="wide")

# --- CONFIGURACIÓN ---
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

EXTENSIONES_PERMITIDAS = {
    "image": [".png", ".jpg", ".jpeg"],
    "video": [".mp4"],
    "audio": [".mp3"]
}

# --- SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = None

# Mostrar mensaje persistente
if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = None

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Ingreso del Administrador")
    username = st.text_input("Usuario", placeholder="Ingrese su nombre de usuario")
    password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")

    if st.button("Iniciar sesión"):
        if login(username, password):
            st.session_state.logged_in = True
            st.success("¡Bienvenido, Administrador!")
            st.rerun()
        else:
            st.error("Credenciales inválidas.")
    st.stop()

# --- DASHBOARD ---
st.title("📂 Administrador de Documentos Multimedia")
st.sidebar.success(f"Conectado como: **{os.getenv('ADMIN_USER')}**")

menu = ["📤 Subir documento", "📋 Ver / Editar documentos"]
choice = st.sidebar.radio("Menú principal", menu)

# Botón de cerrar sesión
if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged_in = False
    st.rerun()

BASE_URL = "http://localhost:8502/view_media"  # Cambia si usas otro puerto o dominio

# --- SUBIR DOCUMENTO ---
if choice == "📤 Subir documento":
    st.subheader("Subir nuevo documento multimedia")

    title = st.text_input("Título del documento", placeholder="Ejemplo: Entrevista de campo, Video demostrativo...")
    description = st.text_area("Descripción (opcional)", placeholder="Escriba una breve descripción del documento.")

    # Interfaz en español, pero guardamos en inglés para la BD
    media_label = st.selectbox("Tipo de archivo", ["Imagen", "Video", "Audio"])
    media_type = {"Imagen": "image", "Video": "video", "Audio": "audio"}[media_label]

    st.info(f"💾 Tamaño máximo permitido: {MAX_FILE_SIZE_MB} MB por archivo.")
    file = st.file_uploader("Seleccione el archivo", type=["png", "jpg", "jpeg", "mp4", "mp3"])

    if st.button("Generar QR y guardar"):
        if not title:
            st.warning("Por favor, ingrese un título para el documento.")
        elif not file:
            st.warning("Debe seleccionar un archivo para subir.")
        else:
            # --- Validar tamaño del archivo ---
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_FILE_SIZE_BYTES:
                st.error(f"El archivo supera el límite de {MAX_FILE_SIZE_MB} MB.")
            else:
                _, extension = os.path.splitext(file.name)
                extension = extension.lower()

                if extension not in EXTENSIONES_PERMITIDAS[media_type]:
                    tipos_validos = ", ".join(EXTENSIONES_PERMITIDAS[media_type])
                    st.error(
                        f"⚠️ El tipo de archivo no coincide. "
                        f"Seleccionó '{media_label}' y el archivo tiene extensión '{extension}'. "
                        f"Extensiones válidas: {tipos_validos}"
                    )
                else:
                    # --- Limpiar el nombre del archivo ---
                    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', file.name)
                    os.makedirs("media", exist_ok=True)
                    file_path = os.path.join("media", safe_filename)

                    # --- Guardar archivo localmente ---
                    with open(file_path, "wb") as f:
                        f.write(file.read())

                    # --- Guardar registro en la BD ---
                    doc = supabase.table("media_documents").insert({
                        "title": title,
                        "description": description,
                        "media_url": file_path,
                        "media_type": media_type
                    }).execute()

                    doc_id = doc.data[0]["id"]
                    qr_path = generate_qr(doc_id, BASE_URL)

                    supabase.table("media_documents").update({
                        "qr_url": qr_path
                    }).eq("id", doc_id).execute()

                    st.success("✅ ¡QR generado y documento guardado exitosamente!")
                    st.image(qr_path, caption="Código QR generado")

# --- VER / EDITAR DOCUMENTOS ---
elif choice == "📋 Ver / Editar documentos":
    st.subheader("Documentos multimedia registrados")
    docs = supabase.table("media_documents").select("*").execute().data

    if not docs:
        st.info("No hay documentos registrados aún.")
    else:
        for doc in docs:
            with st.expander(doc["title"]):
                st.write(f"**Tipo:** {doc['media_type']}")
                st.write(doc["description"] if doc["description"] else "Sin descripción.")
                st.image(doc["qr_url"], caption="Código QR")
                st.download_button("⬇️ Descargar QR", data=open(doc["qr_url"], "rb"), file_name=f"{doc['id']}.png")

                new_title = st.text_input("Editar título", doc["title"], key=f"title_{doc['id']}",
                                          placeholder="Ingrese un nuevo título")
                new_desc = st.text_area("Editar descripción", doc["description"], key=f"desc_{doc['id']}",
                                        placeholder="Modifique la descripción")

                if st.button("Actualizar", key=f"update_{doc['id']}"):
                    supabase.table("media_documents").update({
                        "title": new_title,
                        "description": new_desc
                    }).eq("id", doc["id"]).execute()
                    st.session_state.mensaje_exito = f"✅ Documento **{new_title}** actualizado correctamente."
                    st.rerun()

                # --- ELIMINAR DOCUMENTO Y ARCHIVOS ---
                if st.button("Eliminar", key=f"del_{doc['id']}"):
                    # Eliminar de la base de datos
                    supabase.table("media_documents").delete().eq("id", doc["id"]).execute()

                    # Eliminar archivo multimedia (si existe)
                    if os.path.exists(doc["media_url"]):
                        try:
                            os.remove(doc["media_url"])
                            st.write(f"🧹 Archivo multimedia eliminado: {doc['media_url']}")
                        except Exception as e:
                            st.error(f"⚠️ Error al eliminar el archivo multimedia: {e}")

                    # Eliminar código QR asociado
                    if doc.get("qr_url") and os.path.exists(doc["qr_url"]):
                        try:
                            os.remove(doc["qr_url"])
                            st.write(f"🧹 QR eliminado: {doc['qr_url']}")
                        except Exception as e:
                            st.error(f"⚠️ Error al eliminar el código QR: {e}")

                    # Eliminar posibles residuos en carpetas
                    if os.path.isdir("media") and not os.listdir("media"):
                        os.rmdir("media")
                    if os.path.isdir("assets/qrs") and not os.listdir("assets/qrs"):
                        os.rmdir("assets/qrs")

                    st.session_state.mensaje_exito = f"🗑️ Documento **{doc['title']}** y sus archivos asociados fueron eliminados correctamente."
                    st.rerun()
