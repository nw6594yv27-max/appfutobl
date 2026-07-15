# Misma version de Python que se usa en el venv de desarrollo (3.9.6).
FROM python:3.9-slim

# Librerias de sistema (paquetes apt, no paquetes de Python) que OpenCV y
# MediaPipe necesitan para inicializar su backend grafico interno, aunque
# este servidor no tenga pantalla ni GPU:
#   - libgl1, libgles2, libegl1: implementaciones de OpenGL / OpenGL ES / EGL
#     (mesa). MediaPipe intenta cargar libGLESv2.so y libEGL.so al arrancar
#     incluso en modo solo-CPU; sin estas librerias falla con
#     "OSError: libGLESv2.so.2: cannot open shared object file".
#   - libglib2.0-0: dependencia del modulo highgui de OpenCV (usa GTK/GLib
#     internamente aunque no se abra ninguna ventana).
#   - libsm6, libxext6, libxrender1: librerias X11 de las que depende esa
#     misma pila grafica de OpenCV en Debian/Ubuntu.
#   - ffmpeg: refuerza la decodificacion de los distintos formatos de video
#     que puede subir un usuario (mp4/mov/avi/mkv).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgles2 \
    libegl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Se copian primero solo los requirements para aprovechar la cache de Docker:
# mientras no cambien las dependencias, "docker build" no las reinstala aunque
# cambie el resto del codigo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
