"""
Analiza tres videos ya grabados por separado, cada uno con un solo gesto
bien recortado (videos/chut1.mov, videos/pase1.mov, videos/control1.mov),
en vez de la camara en directo. Para cada video se detecta el esqueleto
fotograma a fotograma y se busca solo el angulo relevante para ese gesto
(chut1.mov -> rodilla, pase1.mov -> pie de apoyo, control1.mov -> tobillo),
como aproximacion al instante del gesto.

Diferencias frente a la camara en directo (VideoCapture(0)):
  - Aqui "no hay mas fotogramas" (read() devuelve False) es el final normal
    del video, no un error.
  - El timestamp que necesita la Tasks API en modo VIDEO se pide al propio
    video (CAP_PROP_POS_MSEC), no con time.time(), porque el archivo se lee
    y decodifica mucho mas rapido que el tiempo real de grabacion.
  - No hay ventana ni teclado: no hay nadie mirando en directo para decidir
    cuando capturar, asi que se recorre cada video entero sin cv2.imshow ni
    cv2.waitKey.

Nota sobre el "angulo mas extremo" como sustituto de pulsar una tecla:
  - Rodilla (chut1.mov): se guarda el MINIMO angulo visto (mayor flexion).
  - Pie de apoyo (pase1.mov): se guarda el MAXIMO angulo visto (mayor
    desviacion).
  - Tobillo (control1.mov): se guarda el MAXIMO angulo visto (mayor
    flexion/cesion del pie al controlar el balon).

Nota sobre landmarks poco fiables: cada landmark trae, ademas de x/y/z, dos
campos de confianza: "visibility" (probabilidad de no estar tapado/ocluido
por otra parte del cuerpo) y "presence" (probabilidad de estar dentro del
encuadre). Ambos van de 0.0 a 1.0. Si alguno de los landmarks necesarios
para un angulo tiene visibility o presence por debajo de UMBRAL_CONFIANZA
en un fotograma (por ejemplo, un pie que se sale de plano), ese fotograma
se descarta para ese angulo, para no contaminar el "extremo" guardado con
una estimacion poco fiable.

Nota sobre falsos positivos "fugaces": un valor extremo detectado en un
solo fotograma suelto puede ser un giro rapido o un paso al caminar, no el
gesto real. Para reducir esto, un angulo solo se considera candidato a
"extremo" si se mantiene relativamente estable (rango <= TOLERANCIA_GRADOS)
durante una ventana de VENTANA_SEGUNDOS segundos de fotogramas consecutivos
y confiables. La ventana se define en segundos, no en numero de fotogramas,
porque el framerate varia segun el video; se convierte a fotogramas con el
fps real de cada video. Esto no elimina el riesgo de falsos positivos
"sostenidos" (por ejemplo, quedarse quieto de pie con el pie girado tambien
seria "estable"); grabar cada gesto por separado y bien recortado, como se
hace aqui, reduce mucho ese riesgo.
"""

import collections
import os

import cv2
import mediapipe as mp

from angulos import calcular_angulo
from analisis import (
    analizar_chut,
    analizar_pase,
    analizar_control,
    analizar_regate,
    analizar_saque_banda,
)

BaseOptions = mp.tasks.BaseOptions
PoseLandmark = mp.tasks.vision.PoseLandmark
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_MODELO = os.path.join(CARPETA_SCRIPT, "modelos", "pose_landmarker_lite.task")

RUTA_VIDEO_CHUT = os.path.join(CARPETA_SCRIPT, "videos", "chut1.mov")
RUTA_VIDEO_PASE = os.path.join(CARPETA_SCRIPT, "videos", "pase1.mov")
RUTA_VIDEO_CONTROL = os.path.join(CARPETA_SCRIPT, "videos", "control1.mov")
RUTA_VIDEO_REGATE = os.path.join(CARPETA_SCRIPT, "videos", "regate1.mov")
RUTA_VIDEO_SAQUE_BANDA = os.path.join(CARPETA_SCRIPT, "videos", "saque_banda1.mov")

opciones = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=RUTA_MODELO),
    running_mode=VisionRunningMode.VIDEO,
)

# Mismo umbral que usa MediaPipe internamente (en su propio drawing_utils)
# para decidir si un landmark es lo bastante fiable como para dibujarlo
UMBRAL_CONFIANZA = 0.5

# Ventana de estabilidad: cuantos segundos debe mantenerse un angulo dentro
# de la tolerancia para considerarlo el "momento del gesto" (no un giro o
# paso fugaz)
VENTANA_SEGUNDOS = 0.2
TOLERANCIA_GRADOS = 7


def landmark_es_confiable(landmark, umbral=UMBRAL_CONFIANZA):
    """
    Devuelve True si el landmark tiene suficiente visibility y presence
    (cuando el modelo los proporciona; si no estan disponibles, se
    considera fiable por defecto).
    """
    if landmark.visibility is not None and landmark.visibility < umbral:
        return False
    if landmark.presence is not None and landmark.presence < umbral:
        return False
    return True


class VentanaEstable:
    """
    Acumula fotogramas consecutivos y confiables de un mismo angulo, y solo
    ofrece un candidato a "extremo" cuando el rango (max-min) de la ventana
    mas reciente de num_frames fotogramas no supera tolerancia_grados.

    Un fotograma no confiable (o la ausencia de deteccion) rompe la
    continuidad y reinicia la ventana, porque no se puede afirmar que el
    angulo se mantuvo estable durante un hueco sin datos.

    tipo_extremo debe ser "minimo" (ej. rodilla, mayor flexion) o "maximo"
    (ej. pie de apoyo/tobillo, mayor desviacion o flexion).
    """

    def __init__(self, num_frames, tolerancia_grados, tipo_extremo):
        assert tipo_extremo in ("minimo", "maximo")
        self.num_frames = num_frames
        self.tolerancia_grados = tolerancia_grados
        self.tipo_extremo = tipo_extremo
        self.buffer = collections.deque(maxlen=num_frames)
        self.mejor_angulo = None
        self.mejor_segundo = None

    def procesar(self, segundo, angulo, confiable):
        if not confiable:
            self.buffer.clear()
            return

        self.buffer.append((segundo, angulo))

        if len(self.buffer) < self.num_frames:
            return

        angulos_ventana = [a for _, a in self.buffer]
        if max(angulos_ventana) - min(angulos_ventana) > self.tolerancia_grados:
            return

        # Ventana estable: nos quedamos con el fotograma mas extremo dentro de ella
        if self.tipo_extremo == "minimo":
            segundo_candidato, angulo_candidato = min(self.buffer, key=lambda t: t[1])
            mejora = self.mejor_angulo is None or angulo_candidato < self.mejor_angulo
        else:
            segundo_candidato, angulo_candidato = max(self.buffer, key=lambda t: t[1])
            mejora = self.mejor_angulo is None or angulo_candidato > self.mejor_angulo

        if mejora:
            self.mejor_angulo = angulo_candidato
            self.mejor_segundo = segundo_candidato


def angulo_rodilla_derecha(landmarks_persona, ancho, alto):
    """Cadera-rodilla-tobillo derechos (chut). Devuelve (angulo, confiable)."""
    cadera = landmarks_persona[PoseLandmark.RIGHT_HIP.value]
    rodilla = landmarks_persona[PoseLandmark.RIGHT_KNEE.value]
    tobillo = landmarks_persona[PoseLandmark.RIGHT_ANKLE.value]

    if not all(landmark_es_confiable(p) for p in (cadera, rodilla, tobillo)):
        return None, False

    punto_cadera = (cadera.x * ancho, cadera.y * alto)
    punto_rodilla = (rodilla.x * ancho, rodilla.y * alto)
    punto_tobillo = (tobillo.x * ancho, tobillo.y * alto)
    return calcular_angulo(punto_cadera, punto_rodilla, punto_tobillo), True


def angulo_pie_apoyo_izquierdo(landmarks_persona, ancho, alto):
    """Desviacion del pie de apoyo izquierdo respecto a la linea recta hacia la camara (pase)."""
    talon = landmarks_persona[PoseLandmark.LEFT_HEEL.value]
    punta_pie = landmarks_persona[PoseLandmark.LEFT_FOOT_INDEX.value]

    if not all(landmark_es_confiable(p) for p in (talon, punta_pie)):
        return None, False

    punto_talon = (talon.x * ancho, talon.y * alto)
    punto_punta_pie = (punta_pie.x * ancho, punta_pie.y * alto)
    punto_recto_arriba = (punto_talon[0], punto_talon[1] - 100)
    return calcular_angulo(punto_punta_pie, punto_talon, punto_recto_arriba), True


def angulo_tobillo_derecho(landmarks_persona, ancho, alto):
    """Rodilla-tobillo-punta del pie derechos (control)."""
    rodilla = landmarks_persona[PoseLandmark.RIGHT_KNEE.value]
    tobillo = landmarks_persona[PoseLandmark.RIGHT_ANKLE.value]
    punta_pie = landmarks_persona[PoseLandmark.RIGHT_FOOT_INDEX.value]

    if not all(landmark_es_confiable(p) for p in (rodilla, tobillo, punta_pie)):
        return None, False

    punto_rodilla = (rodilla.x * ancho, rodilla.y * alto)
    punto_tobillo = (tobillo.x * ancho, tobillo.y * alto)
    punto_punta_pie = (punta_pie.x * ancho, punta_pie.y * alto)
    return calcular_angulo(punto_rodilla, punto_tobillo, punto_punta_pie), True


def angulo_codo_derecho(landmarks_persona, ancho, alto):
    """
    Hombro-codo-muneca derechos (saque de banda). A diferencia de los demas
    gestos, este mide el brazo, no la pierna: el saque de banda se ejecuta
    con las manos, no con el pie. Devuelve (angulo, confiable).
    """
    hombro = landmarks_persona[PoseLandmark.RIGHT_SHOULDER.value]
    codo = landmarks_persona[PoseLandmark.RIGHT_ELBOW.value]
    muneca = landmarks_persona[PoseLandmark.RIGHT_WRIST.value]

    if not all(landmark_es_confiable(p) for p in (hombro, codo, muneca)):
        return None, False

    punto_hombro = (hombro.x * ancho, hombro.y * alto)
    punto_codo = (codo.x * ancho, codo.y * alto)
    punto_muneca = (muneca.x * ancho, muneca.y * alto)
    return calcular_angulo(punto_hombro, punto_codo, punto_muneca), True


def procesar_video_angulo(ruta_video, tipo_extremo, extraer_angulo):
    """
    Recorre un video entero buscando un unico angulo (el que calcule
    extraer_angulo(landmarks_persona, ancho, alto) -> (angulo, confiable)),
    aplicando el filtro de confianza y la ventana de estabilidad.

    Devuelve (angulo_mas_extremo, segundo_del_video_en_que_se_dio), o
    (None, None) si no se pudo abrir el video o nunca hubo una ventana estable.
    """
    captura = cv2.VideoCapture(ruta_video)

    if not captura.isOpened():
        print(f"No se pudo abrir el video: {ruta_video}")
        return None, None

    fps = captura.get(cv2.CAP_PROP_FPS) or 30.0
    num_frames_ventana = max(1, round(VENTANA_SEGUNDOS * fps))
    ventana = VentanaEstable(num_frames_ventana, TOLERANCIA_GRADOS, tipo_extremo)

    with PoseLandmarker.create_from_options(opciones) as landmarker:
        while True:
            hay_frame, frame = captura.read()
            if not hay_frame:
                # No es un error: el video ha terminado
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen_mediapipe = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # El timestamp lo da el propio video, no el reloj del sistema
            timestamp_ms = int(captura.get(cv2.CAP_PROP_POS_MSEC))
            segundo_actual = timestamp_ms / 1000

            resultado = landmarker.detect_for_video(imagen_mediapipe, timestamp_ms)
            alto, ancho = frame.shape[:2]

            if not resultado.pose_landmarks:
                # Nadie detectado en este fotograma: se rompe la continuidad de la ventana
                ventana.procesar(segundo_actual, None, confiable=False)

            for landmarks_persona in resultado.pose_landmarks:
                angulo, confiable = extraer_angulo(landmarks_persona, ancho, alto)
                ventana.procesar(segundo_actual, angulo, confiable)

    captura.release()
    return ventana.mejor_angulo, ventana.mejor_segundo


def main():
    print(f"Procesando video de chut: {RUTA_VIDEO_CHUT}")
    angulo_rodilla, segundo_rodilla = procesar_video_angulo(
        RUTA_VIDEO_CHUT, "minimo", angulo_rodilla_derecha
    )

    print(f"Procesando video de pase: {RUTA_VIDEO_PASE}")
    angulo_pie_apoyo, segundo_pase = procesar_video_angulo(
        RUTA_VIDEO_PASE, "maximo", angulo_pie_apoyo_izquierdo
    )

    print(f"Procesando video de control: {RUTA_VIDEO_CONTROL}")
    angulo_tobillo, segundo_control = procesar_video_angulo(
        RUTA_VIDEO_CONTROL, "maximo", angulo_tobillo_derecho
    )

    print(f"Procesando video de regate: {RUTA_VIDEO_REGATE}")
    angulo_regate, segundo_regate = procesar_video_angulo(
        RUTA_VIDEO_REGATE, "minimo", angulo_rodilla_derecha
    )

    print(f"Procesando video de saque de banda: {RUTA_VIDEO_SAQUE_BANDA}")
    angulo_codo, segundo_saque_banda = procesar_video_angulo(
        RUTA_VIDEO_SAQUE_BANDA, "maximo", angulo_codo_derecho
    )

    print("\nVideos procesados.\n")

    # Los datos del jugador solo hacen falta una vez, al final, para generar las recomendaciones
    edad = int(input("Edad del jugador (anios): "))
    peso = float(input("Peso del jugador (kg): "))
    posicion = input("Posicion en el campo (delantero/centrocampista/defensa/portero): ").strip()

    print("\n=== Resultados del analisis de los videos ===")

    print("\n--- Chut (rodilla) ---")
    if angulo_rodilla is None:
        print("No se detecto un momento de gesto valido en el video de chut.")
    else:
        print(f"Angulo minimo detectado: {angulo_rodilla:.0f} grados (segundo {segundo_rodilla:.1f} del video)")
        print("Recomendaciones:")
        print(analizar_chut(edad, peso, posicion, angulo_rodilla))

    print("\n--- Pase (pie de apoyo) ---")
    if angulo_pie_apoyo is None:
        print("No se detecto un momento de gesto valido en el video de pase.")
    else:
        print(f"Angulo maximo detectado: {angulo_pie_apoyo:.0f} grados (segundo {segundo_pase:.1f} del video)")
        print("Recomendaciones:")
        print(analizar_pase(edad, peso, posicion, angulo_pie_apoyo))

    print("\n--- Control (tobillo) ---")
    if angulo_tobillo is None:
        print("No se detecto un momento de gesto valido en el video de control.")
    else:
        print(f"Angulo maximo detectado: {angulo_tobillo:.0f} grados (segundo {segundo_control:.1f} del video)")
        print("Recomendaciones:")
        print(analizar_control(edad, peso, posicion, angulo_tobillo))

    print("\n--- Regate (rodilla de apoyo) ---")
    if angulo_regate is None:
        print("No se detecto un momento de gesto valido en el video de regate.")
    else:
        print(f"Angulo minimo detectado: {angulo_regate:.0f} grados (segundo {segundo_regate:.1f} del video)")
        print("Recomendaciones:")
        print(analizar_regate(edad, peso, posicion, angulo_regate))

    print("\n--- Saque de banda (codo) ---")
    if angulo_codo is None:
        print("No se detecto un momento de gesto valido en el video de saque de banda.")
    else:
        print(f"Angulo maximo detectado: {angulo_codo:.0f} grados (segundo {segundo_saque_banda:.1f} del video)")
        print("Recomendaciones:")
        print(analizar_saque_banda(edad, peso, posicion, angulo_codo))


if __name__ == "__main__":
    main()
