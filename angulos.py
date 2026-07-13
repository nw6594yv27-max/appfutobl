"""
Calculo del angulo formado por tres puntos, tomando el punto del medio
como vertice (por ejemplo: cadera, rodilla, tobillo -> angulo de la rodilla).
"""

import math


def calcular_angulo(punto_a, punto_b, punto_c):
    """
    Devuelve el angulo en grados (0-180) que forman los segmentos
    B->A y B->C, siendo B el vertice (el punto del medio).

    Cada punto puede ser una tupla/lista (x, y) o cualquier objeto con
    atributos .x y .y (por ejemplo, un landmark de MediaPipe).
    """
    ax, ay = _coordenadas(punto_a)
    bx, by = _coordenadas(punto_b)
    cx, cy = _coordenadas(punto_c)

    direccion_ba = math.atan2(ay - by, ax - bx)
    direccion_bc = math.atan2(cy - by, cx - bx)

    angulo = math.degrees(direccion_ba - direccion_bc)
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo

    return angulo


def _coordenadas(punto):
    if hasattr(punto, "x") and hasattr(punto, "y"):
        return punto.x, punto.y
    return punto[0], punto[1]


if __name__ == "__main__":
    # Caso 1: pierna estirada del todo (cadera, rodilla y tobillo en linea recta)
    cadera = (0, 0)
    rodilla = (0, 1)
    tobillo = (0, 2)
    angulo = calcular_angulo(cadera, rodilla, tobillo)
    print(f"Pierna estirada -> angulo calculado: {angulo:.0f} grados (esperado: 180)")

    # Caso 2: rodilla flexionada formando un angulo recto
    cadera = (0, 0)
    rodilla = (0, 1)
    tobillo = (1, 1)
    angulo = calcular_angulo(cadera, rodilla, tobillo)
    print(f"Rodilla en angulo recto -> angulo calculado: {angulo:.0f} grados (esperado: 90)")
