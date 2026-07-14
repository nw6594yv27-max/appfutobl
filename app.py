import os
import time

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from analisis import (
    analizar_chut,
    analizar_pase,
    analizar_control,
    analizar_regate,
    analizar_saque_banda,
)
from analizar_video import (
    procesar_video_angulo,
    angulo_rodilla_derecha,
    angulo_pie_apoyo_izquierdo,
    angulo_tobillo_derecho,
    angulo_codo_derecho,
)
from historial import inicializar_db, guardar_analisis, obtener_historial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
inicializar_db()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Config de cada gesto: como se busca el angulo en el video (procesar_video_angulo
# necesita el "tipo_extremo" y la funcion que extrae el angulo por fotograma) y
# que funcion de analisis.py genera la recomendacion final a partir de ese angulo.
GESTOS = {
    "chut": {
        "etiqueta": "Chut a porteria",
        "icono": "⚽",
        "etiqueta_angulo": "Angulo de rodilla",
        "tipo_extremo": "minimo",
        "extraer_angulo": angulo_rodilla_derecha,
        "analizar": analizar_chut,
    },
    "pase": {
        "etiqueta": "Pase",
        "icono": "🎯",
        "etiqueta_angulo": "Desviacion del pie de apoyo",
        "tipo_extremo": "maximo",
        "extraer_angulo": angulo_pie_apoyo_izquierdo,
        "analizar": analizar_pase,
    },
    "control": {
        "etiqueta": "Control de balon",
        "icono": "🛑",
        "etiqueta_angulo": "Angulo de tobillo",
        "tipo_extremo": "maximo",
        "extraer_angulo": angulo_tobillo_derecho,
        "analizar": analizar_control,
    },
    "regate": {
        "etiqueta": "Regate",
        "icono": "🔀",
        "etiqueta_angulo": "Angulo de rodilla de apoyo",
        "tipo_extremo": "minimo",
        "extraer_angulo": angulo_rodilla_derecha,
        "analizar": analizar_regate,
    },
    "saque_banda": {
        "etiqueta": "Saque de banda",
        "icono": "🤾",
        "etiqueta_angulo": "Angulo de codo (extension al soltar)",
        "tipo_extremo": "maximo",
        "extraer_angulo": angulo_codo_derecho,
        "analizar": analizar_saque_banda,
    },
}

# Palabras clave que usa analisis.py en cada linea de recomendacion, para poder
# resaltarlas visualmente (verde/ambar/info) sin tener que tocar su logica.
PALABRAS_AVISO = ("demasiado", "por encima de lo esperado", "relativamente alta")
PALABRAS_EXITO = ("dentro del rango esperado", "dentro de lo esperado")


def clasificar_lineas(recomendacion):
    lineas = []
    for texto in recomendacion.split("\n"):
        texto_normalizado = texto.lower()
        if any(palabra in texto_normalizado for palabra in PALABRAS_AVISO):
            estado = "warning"
        elif any(palabra in texto_normalizado for palabra in PALABRAS_EXITO):
            estado = "success"
        else:
            estado = "info"
        lineas.append({"texto": texto, "estado": estado})
    return lineas


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_video():
    gesto = request.form.get("gesto", "")
    if gesto not in GESTOS:
        return "Gesto no reconocido. Elige chut, pase, control, regate o saque_banda.", 400

    try:
        edad = int(request.form.get("edad", ""))
        peso = float(request.form.get("peso", ""))
    except ValueError:
        return "Edad y peso deben ser numeros validos.", 400

    posicion = request.form.get("posicion", "").strip()
    if not posicion:
        return "Falta la posicion del jugador.", 400

    if "video" not in request.files:
        return "No se ha enviado ningún archivo.", 400

    video = request.files["video"]

    if video.filename == "":
        return "No se ha seleccionado ningún archivo.", 400

    if not allowed_file(video.filename):
        return "Formato de archivo no permitido.", 400

    filename = f"{int(time.time())}_{secure_filename(video.filename)}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    video.save(filepath)

    config = GESTOS[gesto]
    angulo, segundo = procesar_video_angulo(
        filepath, config["tipo_extremo"], config["extraer_angulo"]
    )

    if angulo is None:
        return render_template(
            "resultado.html",
            etiqueta_gesto=config["etiqueta"],
            icono_gesto=config["icono"],
            error=(
                "No se ha detectado un momento de gesto valido y estable en el video. "
                "Prueba con un video mejor recortado, con mas luz o con el gesto mas centrado en el encuadre."
            ),
        )

    recomendacion = config["analizar"](edad, peso, posicion, angulo)

    guardar_analisis(
        gesto=gesto,
        icono_gesto=config["icono"],
        etiqueta_gesto=config["etiqueta"],
        etiqueta_angulo=config["etiqueta_angulo"],
        edad=edad,
        peso=peso,
        posicion=posicion,
        angulo=angulo,
        segundo=segundo,
        recomendacion=recomendacion,
    )

    return render_template(
        "resultado.html",
        etiqueta_gesto=config["etiqueta"],
        icono_gesto=config["icono"],
        etiqueta_angulo=config["etiqueta_angulo"],
        angulo=angulo,
        segundo=segundo,
        lineas=clasificar_lineas(recomendacion),
        edad=edad,
        peso=peso,
        posicion=posicion,
    )


@app.route("/historial")
def historial():
    registros = obtener_historial()
    entradas = [
        {"registro": registro, "lineas": clasificar_lineas(registro["recomendacion"])}
        for registro in registros
    ]
    return render_template("historial.html", entradas=entradas)


if __name__ == "__main__":
    app.run(debug=True)
