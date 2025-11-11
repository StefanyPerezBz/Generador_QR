# 📸 QR Media App — Sistema de Gestión de Documentos con Códigos QR  

<p align="center">
  <a href="https://streamlit.io/">
    <img src="https://img.shields.io/badge/streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python"/>
  </a>
  <a href="https://supabase.com/">
    <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
  </a>
  <a href="https://qrcode.meetheed.com/">
    <img src="https://img.shields.io/badge/QRCode-000000?style=for-the-badge&logo=Qrcode&logoColor=white" alt="QR"/>
  </a>
</p>

---

## 🎯 Propósito del proyecto  

Desarrollar una **aplicación web moderna y segura** que permita a un único **administrador** subir y gestionar documentos multimedia (📷 imágenes, 🎥 videos, 🎧 audios), generando **códigos QR únicos** para cada archivo, los cuales pueden ser escaneados o subidos como imagen para visualizar el contenido directamente en el navegador.  

### 🎓 Objetivo general  

Simplificar la gestión, almacenamiento y consulta de material audiovisual o documental mediante una plataforma accesible que **automatiza la creación de códigos QR** y permite **visualización instantánea** desde cualquier dispositivo.  

### 🎯 Objetivos específicos  

- 📤 Permitir la **subida y clasificación de archivos multimedia** (imagen, video, audio).  
- 🔐 Implementar un sistema con **rol único de administrador** (login con usuario y contraseña).  
- 🧩 Generar un **QR único** por documento con enlace directo de acceso.  
- 📱 Facilitar la visualización desde dispositivos móviles al escanear el QR.  
- 🧹 Automatizar la **eliminación de archivos y QRs** asociados al borrar un registro.  
- ☁️ Permitir despliegue simple en **Streamlit Cloud**, sin servidores adicionales.

---

## 🧰 Tecnologías utilizadas  

| Tecnología | Uso principal |
|-------------|----------------|
| 🐍 **Python 3.11** | Lenguaje de desarrollo |
| 🎈 **Streamlit** | Interfaz web interactiva |
| 🗃️ **Supabase (PostgreSQL)** | Base de datos en la nube |
| 🧾 **QRCode / Pillow** | Generación de códigos QR |
| 🧠 **Pyzbar** | Lectura de códigos QR desde imágenes |
| ⚙️ **Dotenv** | Manejo de variables de entorno (.env) |

---

## 🧩 Arquitectura general  

```
qr_media_app/
│
├── app.py                # Panel del Administrador (CRUD + QR)
├── view_media.py         # Visualizador público de QR
│
├── auth.py               # Módulo de autenticación
├── qr_utils.py           # Generación de códigos QR únicos
├── supabase_client.py    # Conexión con la base de datos Supabase
│
├── requirements.txt      # Dependencias del proyecto
├── .env.example          # Variables de entorno de ejemplo
│
├── /media/               # Archivos multimedia subidos
└── /assets/qrs/          # Códigos QR generados
```

---

## 🧠 Base de datos en Supabase  

Ejecuta este script SQL en tu proyecto de Supabase:

```sql
create table media_documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  media_url text not null,
  qr_url text,
  media_type text check (media_type in ('image', 'video', 'audio')),
  created_at timestamp default now()
);
```

---

## ⚙️ Variables de entorno  

Configura tu archivo `.env` o **secrets** en Streamlit Cloud:  

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key
ADMIN_USER=admin
ADMIN_PASS=admin123
```

---

## ⚙️ Instalación local  

```bash
git clone https://github.com/tuusuario/qr_media_app.git
cd qr_media_app
pip install -r requirements.txt
```

### Ejecutar localmente  

- **Panel del Administrador:**  
  ```bash
  streamlit run app.py
  ```

- **Visualizador de QR:**  
  ```bash
  streamlit run view_media.py --server.port=8502
  ```

Luego abre en tu navegador:
- Panel Admin → http://localhost:8501  
- Visualizador → http://localhost:8502/view_media

---

## ☁️ Despliegue en Streamlit Cloud  

1️⃣ Sube tu proyecto a **GitHub**.  
2️⃣ Entra a [https://share.streamlit.io](https://share.streamlit.io).  
3️⃣ Crea dos apps:  
   - **App 1:** `app.py` (Panel del Administrador).  
   - **App 2:** `view_media.py` (Visualizador de QR).  
4️⃣ En cada app, configura los **secrets**:  
   ```toml
   SUPABASE_URL="https://tu-proyecto.supabase.co"
   SUPABASE_KEY="tu-service-role-key"
   ADMIN_USER="admin"
   ADMIN_PASS="admin123"
   ```
5️⃣ Modifica `BASE_URL` en `app.py` para apuntar al dominio del visualizador:  
   ```python
   BASE_URL = "https://tuusuario-qr-media-view.streamlit.app/view_media"
   ```

---

## 🧹 Eliminación inteligente  

- Al eliminar un documento, el sistema también borra:
  - 🗑️ El archivo multimedia en `/media/`.
  - 🗑️ El código QR correspondiente en `/assets/qrs/`.
  - ✅ Limpieza automática de carpetas vacías.

---

## 🔒 Seguridad  

- Acceso restringido a un único **Administrador**.  
- Variables sensibles gestionadas con `.env` o **secrets.toml**.  
- Sin exposición de claves ni credenciales en el código fuente.  

---

## 💡 Ideas futuras  

- 📦 Integrar **Supabase Storage** para almacenamiento persistente en la nube.  
- 🌍 Añadir soporte multiusuario (roles: admin, editor, visitante).  
- 📤 Exportar QR en PDF con información del documento.  
- 🔔 Agregar notificaciones por correo o Telegram.

---

## 👩‍💻 Autores  

1. **José Andrés Farro Lagos** — Universidad Nacional de Trujillo  
2. **Stefany Marisel Pérez Bazán** — Universidad Nacional de Trujillo  

📧 Contacto: joseandres.farro@unitru.edu.pe  
🌐 GitHub: [https://github.com/tuusuario](https://github.com/tuusuario)

---

## 📜 Licencia  

Este proyecto está licenciado bajo **MIT License**.  
Eres libre de usarlo, modificarlo y distribuirlo con atribución al autor original.
