import streamlit as st
from services.supabase_client import supabase
from services.qr_utils import generate_qr
from services.auth import login
import os
import re
import time
from dotenv import load_dotenv
import requests

# ==============================================
# ⚙️ CONFIGURACIÓN INICIAL
# ==============================================
load_dotenv()
st.set_page_config(page_title="Gestor de Códigos QR", page_icon="🎥", layout="wide")

# ==============================================
# 🎨 ESTILOS PERSONALIZADOS
# ==============================================
st.markdown(
    """
<style>
    .stButton>button {
        width: auto;
        min-width: 160px;
        max-width: 220px;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color: white;
        transform: scale(1.03);
    }
    div[data-testid="column"] button {
        width: 90%;
        margin: 0.2rem auto;
    }
    .stButton>button:first-child {
        display: block;
        margin: auto;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================
# CONFIGURACIÓN GENERAL
# ==============================================
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

EXTENSIONES_PERMITIDAS = {
    "image": [".png", ".jpg", ".jpeg"],
    "video": [".mp4"],
    "audio": [".mp3"],
}

BUCKET_MEDIA = "media_files"
BUCKET_QRS = "qr_codes"
BASE_URL = os.getenv("BASE_URL_VIEW_MEDIA")

# ==============================================
# 🔐 SESIÓN DE ADMINISTRADOR
# ==============================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = None

if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = None

# ==============================================
# LOGIN
# ==============================================
if not st.session_state.logged_in:
    st.title("🔐 Ingreso del Administrador")
    st.markdown("Ingrese sus credenciales para acceder al panel de gestión.")

    username = st.text_input("👤 Usuario", placeholder="Ingrese su nombre de usuario")
    password = st.text_input(
        "🔑 Contraseña", type="password", placeholder="Ingrese su contraseña"
    )

    if st.button("Iniciar sesión", use_container_width=True):
        if login(username, password):
            st.session_state.logged_in = True
            st.success("✅ ¡Bienvenido, Administrador!")
            st.rerun()
        else:
            st.error("❌ Credenciales inválidas. Inténtelo nuevamente.")
    st.stop()

# ==============================================
# 🏠 DASHBOARD
# ==============================================
st.title("📂 Administrador de Documentos Multimedia")
st.sidebar.markdown("### ⚙️ Menú principal")
st.sidebar.success(f"Conectado como: **{os.getenv('ADMIN_USER')}**")

menu = ["Subir documento", "Ver / Editar documentos"]
choice = st.sidebar.radio("", menu, index=0)

if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged_in = False
    st.rerun()

# ==============================================
# 📤 SUBIR DOCUMENTO
# ==============================================
if choice == "Subir documento":
    st.subheader("📤 Subir nuevo documento multimedia")
    st.markdown(
        "Complete la información del documento y cargue el archivo correspondiente."
    )

    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "📌 Título del documento",
            placeholder="Ejemplo: Video de campo, Entrevista, Imagen satelital...",
        )
    with col2:
        media_label = st.selectbox("🎞️ Tipo de archivo", ["Imagen", "Video", "Audio"])
        media_type = {"Imagen": "image", "Video": "video", "Audio": "audio"}[
            media_label
        ]

    description = st.text_area(
        "📝 Descripción (opcional)",
        placeholder="Escriba una breve descripción del documento.",
    )
    st.info(f"💾 Tamaño máximo permitido: **{MAX_FILE_SIZE_MB} MB** por archivo.")
    file = st.file_uploader(
        "📁 Seleccione el archivo", type=["png", "jpg", "jpeg", "mp4", "mp3"]
    )

    st.markdown("---")

    if st.button("🚀 Generar QR y guardar", use_container_width=True):
        if not title:
            st.warning("⚠️ Por favor, ingrese un título.")
        elif not file:
            st.warning("⚠️ Debe seleccionar un archivo.")
        else:
            _, extension = os.path.splitext(file.name)
            extension = extension.lower()

            if extension not in EXTENSIONES_PERMITIDAS[media_type]:
                tipos_validos = ", ".join(EXTENSIONES_PERMITIDAS[media_type])
                st.error(
                    f"❌ El tipo de archivo no coincide. Extensiones válidas: {tipos_validos}"
                )
            elif file.size > MAX_FILE_SIZE_BYTES:
                st.error(f"❌ El archivo supera el límite de {MAX_FILE_SIZE_MB} MB.")
            else:
                # Limpieza del nombre
                safe_filename = re.sub(r"[^a-zA-Z0-9._-]", "_", file.name)
                st.info("⏳ Subiendo archivo ...")

                try:
                    # Verificar si el archivo ya existe y renombrar si es necesario
                    existing_files = supabase.storage.from_(BUCKET_MEDIA).list()
                    existing_names = [f["name"] for f in existing_files if "name" in f]

                    if safe_filename in existing_names:
                        base, ext = os.path.splitext(safe_filename)
                        timestamp = int(time.time())
                        safe_filename = f"{base}_{timestamp}{ext}"

                    # Subir archivo
                    supabase.storage.from_(BUCKET_MEDIA).upload(
                        safe_filename, file.read()
                    )
                    media_url = supabase.storage.from_(BUCKET_MEDIA).get_public_url(
                        safe_filename
                    )

                except Exception as e:
                    st.error(f"❌ Error al subir el archivo: {e}")
                    st.stop()

                # Guardar registro en la base de datos
                doc = (
                    supabase.table("media_documents")
                    .insert(
                        {
                            "title": title,
                            "description": description,
                            "media_url": media_url,
                            "media_type": media_type,
                        }
                    )
                    .execute()
                )

                doc_id = doc.data[0]["id"]

                # Generar QR y subir al bucket
                qr_local = generate_qr(doc_id, BASE_URL)
                qr_filename = f"{doc_id}.png"

                try:
                    existing_qrs = supabase.storage.from_(BUCKET_QRS).list()
                    if qr_filename in [q["name"] for q in existing_qrs if "name" in q]:
                        qr_filename = f"{doc_id}_{int(time.time())}.png"

                    with open(qr_local, "rb") as qr_file:
                        supabase.storage.from_(BUCKET_QRS).upload(qr_filename, qr_file)
                        qr_url = supabase.storage.from_(BUCKET_QRS).get_public_url(
                            qr_filename
                        )
                except Exception as e:
                    st.error(f"❌ Error al subir el QR: {e}")
                    st.stop()

                # Actualizar el documento con la URL del QR
                supabase.table("media_documents").update({"qr_url": qr_url}).eq(
                    "id", doc_id
                ).execute()

                st.success("✅ Documento y QR guardados correctamente.")
                st.image(qr_url, caption="Código QR generado", use_container_width=True)
                st.download_button(
                    label="Descargar QR",
                    data=requests.get(qr_url).content,
                    file_name=f"{title}_QR.png",
                    mime="image/png",
                )

# ==============================================
# 📋 VER / EDITAR DOCUMENTOS
# ==============================================
elif choice == "Ver / Editar documentos":
    st.subheader("📑 Documentos multimedia registrados")
    st.markdown("Administre, edite o elimine los registros existentes.")

    docs = supabase.table("media_documents").select("*").execute().data

    if not docs:
        st.info("📭 No hay documentos registrados todavía.")
    else:
        for doc in docs:
            with st.expander(f"{doc['title']}"):
                tipo_traduccion = {
                    "image": "Imagen",
                    "video": "Video",
                    "audio": "Audio",
                }.get(doc["media_type"], doc["media_type"].capitalize())
                st.markdown(f"**🎞️ Tipo:** {tipo_traduccion}")
                st.markdown(
                    f"**📝 Descripción:** {doc['description'] or 'Sin descripción.'}"
                )
                st.image(doc["qr_url"], caption="Código QR", use_container_width=True)

                try:
                    qr_bytes = requests.get(doc["qr_url"]).content
                    st.download_button(
                        label="Descargar QR",
                        data=qr_bytes,
                        file_name=f"{doc['title']}_QR.png",
                        mime="image/png",
                        key=f"download_{doc['id']}",
                    )
                except Exception:
                    st.warning("⚠️ No se pudo generar el archivo de descarga.")

                new_title = st.text_input(
                    "✏️ Editar título", doc["title"], key=f"title_{doc['id']}"
                )
                new_desc = st.text_area(
                    "🧾 Editar descripción", doc["description"], key=f"desc_{doc['id']}"
                )

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button(
                        "Actualizar",
                        key=f"update_{doc['id']}",
                        use_container_width=True,
                    ):
                        supabase.table("media_documents").update(
                            {"title": new_title, "description": new_desc}
                        ).eq("id", doc["id"]).execute()
                        st.session_state.mensaje_exito = (
                            f"✅ Documento **{new_title}** actualizado correctamente."
                        )
                        st.rerun()

                with col_delete:
                    if st.button(
                        "Eliminar", key=f"del_{doc['id']}", use_container_width=True
                    ):
                        try:
                            # Eliminar archivos del Storage
                            file_path = os.path.basename(doc["media_url"])
                            qr_path = os.path.basename(doc["qr_url"])

                            if file_path:
                                supabase.storage.from_(BUCKET_MEDIA).remove([file_path])
                            if qr_path:
                                supabase.storage.from_(BUCKET_QRS).remove([qr_path])

                            # Eliminar registro de la base de datos
                            supabase.table("media_documents").delete().eq(
                                "id", doc["id"]
                            ).execute()

                            st.session_state.mensaje_exito = f"🗑️ Documento **{doc['title']}** y sus archivos fueron eliminados correctamente."
                        except Exception as e:
                            st.error(
                                f"⚠️ Error al eliminar archivos del Storage o BD: {e}"
                            )

                        st.rerun()

# ==============================================
# FOOTER
# ==============================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 14px; color: gray;'>© 2025 QR Media App</div>",
    unsafe_allow_html=True,
)
