"""
Script de prueba: comprueba que MediaPipe detecta el esqueleto de una persona
usando la camara web en directo, dibuja los landmarks (puntos del cuerpo)
sobre la imagen en tiempo real, y calcula el angulo de la rodilla derecha
(cadera derecha - rodilla derecha - tobillo derecho).

Nota: este script usa la "Tasks API" de MediaPipe (mediapipe.tasks), que es la
API actual. La API antigua (mediapipe.solutions) ya no existe en las versiones
recientes de la libreria. La Tasks API necesita un archivo de modelo (.task)
descargado aparte, que ya se descargo en modelos/pose_landmarker_lite.task.

Nota sobre "derecha/izquierda": MediaPipe nombra los landmarks desde el punto
de vista de la propia persona, no de la camara. Con una webcam normal (sin
espejo), la pierna derecha de la persona aparece en el lado izquierdo del video.

Nota sobre el pase: para aproximar la desviacion del pie de apoyo respecto a
la direccion del pase sin saber donde esta el companero (la camara no tiene
ese dato), se asume que el companero esta en linea recta enfrente, hacia la
camara. Se mide cuanto se desvia el pie de apoyo (el izquierdo, ya que el
derecho se usa como pierna de chut) de esa linea vertical imaginaria.

Nota sobre el control: el angulo de tobillo se mide entre la espinilla
(rodilla-tobillo) y el pie (tobillo-punta del pie), con el tobillo como
vertice, usando la misma pierna derecha que en el chut (simplificacion:
se asume que tambien controla con el pie dominante).

Nota sobre el regate: se reutiliza el mismo angulo de rodilla derecha que
el chut (cadera-rodilla-tobillo), pero interpretado de forma distinta: no
buscamos el instante de golpeo sino el de un cambio de direccion, donde
interesa que la rodilla de apoyo este suficientemente flexionada para
mantener el equilibrio y proteger el balon.

Nota sobre el saque de banda: a diferencia de los demas gestos, este se
ejecuta con las manos, no con el pie, asi que el angulo relevante deja de
ser de la pierna y pasa a ser del brazo lanzador (hombro-codo-muneca
derechos). Se busca el instante de mayor extension del codo, que es cuando
se suelta el balon.

Controles:
  - Barra espaciadora: captura el angulo de rodilla del momento y muestra en
    la terminal la recomendacion de coaching completa para un chut.
  - p: captura la desviacion del pie de apoyo y muestra la recomendacion
    de coaching completa para un pase.
  - c: captura el angulo de tobillo y muestra la recomendacion de coaching
    completa para un control de balon.
  - r: captura el angulo de rodilla del momento (mismo dato que el chut) y
    muestra la recomendacion de coaching completa para un regate.
  - b: captura el angulo de codo del momento y muestra la recomendacion de
    coaching completa para un saque de banda.
  - q: sale del programa.
"""

import os
import time

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
drawing_utils = mp.tasks.vision.drawing_utils

# Conexiones entre landmarks (que puntos se unen con una linea).
# draw_landmarks necesita los objetos Connection tal cual (con atributos
# .start/.end), no tuplas sueltas, asi que se usan directamente.
POSE_CONNECTIONS = mp.tasks.vision.PoseLandmarksConnections.POSE_LANDMARKS

# Ruta al modelo, relativa a este mismo archivo (para que funcione sin importar
# desde que carpeta se ejecute el script)
CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
RUTA_MODELO = os.path.join(CARPETA_SCRIPT, "modelos", "pose_landmarker_lite.task")

opciones = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=RUTA_MODELO),
    running_mode=VisionRunningMode.VIDEO,
)

# Pedimos los datos del jugador una sola vez, antes de abrir la camara
edad = int(input("Edad del jugador (anios): "))
peso = float(input("Peso del jugador (kg): "))
posicion = input("Posicion en el campo (delantero/centrocampista/defensa/portero): ").strip()

# Abrimos la camara web (0 = camara por defecto del ordenador)
captura = cv2.VideoCapture(0)

if not captura.isOpened():
    print("No se pudo abrir la camara web.")
else:
    with PoseLandmarker.create_from_options(opciones) as landmarker:
        while True:
            hay_frame, frame = captura.read()
            if not hay_frame:
                print("No se pudo leer un fotograma de la camara.")
                break

            # MediaPipe espera los colores en formato RGB, y OpenCV los da en BGR
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen_mediapipe = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

            # La Tasks API en modo VIDEO necesita una marca de tiempo creciente en milisegundos
            timestamp_ms = int(time.time() * 1000)
            resultado = landmarker.detect_for_video(imagen_mediapipe, timestamp_ms)

            # Si se detecto al menos una persona, dibujamos sus landmarks sobre el frame original
            # y calculamos el angulo de su rodilla derecha
            alto, ancho = frame.shape[:2]

            # Angulos de la ultima persona detectada en este fotograma (None si no hay nadie)
            angulo_rodilla_actual = None
            angulo_pie_apoyo_actual = None
            angulo_tobillo_actual = None
            angulo_codo_actual = None

            for landmarks_persona in resultado.pose_landmarks:
                drawing_utils.draw_landmarks(frame, landmarks_persona, POSE_CONNECTIONS)

                cadera = landmarks_persona[PoseLandmark.RIGHT_HIP.value]
                rodilla = landmarks_persona[PoseLandmark.RIGHT_KNEE.value]
                tobillo = landmarks_persona[PoseLandmark.RIGHT_ANKLE.value]

                # Los landmarks vienen normalizados (0.0-1.0); los pasamos a pixeles
                # segun el tamano real del frame para que el angulo no salga distorsionado
                punto_cadera = (cadera.x * ancho, cadera.y * alto)
                punto_rodilla = (rodilla.x * ancho, rodilla.y * alto)
                punto_tobillo = (tobillo.x * ancho, tobillo.y * alto)

                angulo_rodilla_actual = calcular_angulo(punto_cadera, punto_rodilla, punto_tobillo)

                texto_rodilla = f"Rodilla: {angulo_rodilla_actual:.0f} grados"
                posicion_texto_rodilla = (int(punto_rodilla[0]) + 10, int(punto_rodilla[1]))
                cv2.putText(frame, texto_rodilla, posicion_texto_rodilla, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2)

                # Pie de apoyo (izquierdo): talon y punta del pie
                talon = landmarks_persona[PoseLandmark.LEFT_HEEL.value]
                punta_pie = landmarks_persona[PoseLandmark.LEFT_FOOT_INDEX.value]

                punto_talon = (talon.x * ancho, talon.y * alto)
                punto_punta_pie = (punta_pie.x * ancho, punta_pie.y * alto)

                # Punto virtual justo encima del talon: representa la linea recta
                # imaginaria hacia donde se asume que esta el companero del pase
                punto_recto_arriba = (punto_talon[0], punto_talon[1] - 100)

                angulo_pie_apoyo_actual = calcular_angulo(
                    punto_punta_pie, punto_talon, punto_recto_arriba
                )

                texto_pie = f"Pie apoyo: {angulo_pie_apoyo_actual:.0f} grados"
                posicion_texto_pie = (int(punto_talon[0]) + 10, int(punto_talon[1]))
                cv2.putText(frame, texto_pie, posicion_texto_pie, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255, 0, 0), 2)

                # Tobillo (pierna derecha, la misma del chut): rodilla-tobillo-punta del pie
                punta_pie_derecho = landmarks_persona[PoseLandmark.RIGHT_FOOT_INDEX.value]
                punto_punta_pie_derecho = (punta_pie_derecho.x * ancho, punta_pie_derecho.y * alto)

                angulo_tobillo_actual = calcular_angulo(
                    punto_rodilla, punto_tobillo, punto_punta_pie_derecho
                )

                texto_tobillo = f"Tobillo: {angulo_tobillo_actual:.0f} grados"
                posicion_texto_tobillo = (int(punto_tobillo[0]) + 10, int(punto_tobillo[1]) + 20)
                cv2.putText(frame, texto_tobillo, posicion_texto_tobillo, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 165, 255), 2)

                # Codo (brazo derecho, saque de banda): hombro-codo-muneca.
                # A diferencia de los angulos anteriores, este es del brazo, no de la pierna.
                hombro = landmarks_persona[PoseLandmark.RIGHT_SHOULDER.value]
                codo = landmarks_persona[PoseLandmark.RIGHT_ELBOW.value]
                muneca = landmarks_persona[PoseLandmark.RIGHT_WRIST.value]

                punto_hombro = (hombro.x * ancho, hombro.y * alto)
                punto_codo = (codo.x * ancho, codo.y * alto)
                punto_muneca = (muneca.x * ancho, muneca.y * alto)

                angulo_codo_actual = calcular_angulo(punto_hombro, punto_codo, punto_muneca)

                texto_codo = f"Codo: {angulo_codo_actual:.0f} grados"
                posicion_texto_codo = (int(punto_codo[0]) + 10, int(punto_codo[1]))
                cv2.putText(frame, texto_codo, posicion_texto_codo, cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255, 0, 255), 2)

            cv2.imshow(
                "Prueba MediaPipe - espacio: chut, p: pase, c: control, r: regate, b: saque de banda, q: salir",
                frame,
            )

            # Esperamos 1 milisegundo por una tecla y guardamos cual fue
            tecla = cv2.waitKey(1) & 0xFF

            if tecla == ord("q"):
                break
            elif tecla == ord(" "):
                if angulo_rodilla_actual is None:
                    print("\nNo se detecta a ninguna persona ahora mismo, no se puede analizar el chut.")
                else:
                    recomendacion = analizar_chut(edad, peso, posicion, angulo_rodilla_actual)
                    print(f"\n--- Angulo de rodilla capturado: {angulo_rodilla_actual:.0f} grados ---")
                    print("Recomendaciones:")
                    print(recomendacion)
            elif tecla == ord("p"):
                if angulo_pie_apoyo_actual is None:
                    print("\nNo se detecta a ninguna persona ahora mismo, no se puede analizar el pase.")
                else:
                    recomendacion = analizar_pase(edad, peso, posicion, angulo_pie_apoyo_actual)
                    print(f"\n--- Desviacion del pie de apoyo capturada: {angulo_pie_apoyo_actual:.0f} grados ---")
                    print("Recomendaciones:")
                    print(recomendacion)
            elif tecla == ord("c"):
                if angulo_tobillo_actual is None:
                    print("\nNo se detecta a ninguna persona ahora mismo, no se puede analizar el control.")
                else:
                    recomendacion = analizar_control(edad, peso, posicion, angulo_tobillo_actual)
                    print(f"\n--- Angulo de tobillo capturado: {angulo_tobillo_actual:.0f} grados ---")
                    print("Recomendaciones:")
                    print(recomendacion)
            elif tecla == ord("r"):
                if angulo_rodilla_actual is None:
                    print("\nNo se detecta a ninguna persona ahora mismo, no se puede analizar el regate.")
                else:
                    recomendacion = analizar_regate(edad, peso, posicion, angulo_rodilla_actual)
                    print(f"\n--- Angulo de rodilla de apoyo capturado: {angulo_rodilla_actual:.0f} grados ---")
                    print("Recomendaciones:")
                    print(recomendacion)
            elif tecla == ord("b"):
                if angulo_codo_actual is None:
                    print("\nNo se detecta a ninguna persona ahora mismo, no se puede analizar el saque de banda.")
                else:
                    recomendacion = analizar_saque_banda(edad, peso, posicion, angulo_codo_actual)
                    print(f"\n--- Angulo de codo capturado: {angulo_codo_actual:.0f} grados ---")
                    print("Recomendaciones:")
                    print(recomendacion)

    captura.release()
    cv2.destroyAllWindows()
