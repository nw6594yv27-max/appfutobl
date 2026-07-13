"""
Asistente de coaching de futbol - version inicial
Gesto analizado: chut a porteria

Nota importante: las reglas de angulo de rodilla usadas aqui son
simplificadas con fines educativos/de prototipo, no son un estandar
medico ni de biomecanica deportiva certificado. Sirven como punto de
partida para ir afinando con la ayuda de un entrenador o fisioterapeuta.
"""


def rango_ideal_por_edad(edad):
    """
    Devuelve el rango de angulo de rodilla (en grados) considerado
    razonable para un chut equilibrado, segun la edad del jugador.

    El angulo se mide en el momento del contacto con el balon,
    entre el muslo y la espinilla de la pierna que chuta.
    """
    if edad <= 9:
        # Ninos pequenos: se prioriza el equilibrio sobre la potencia
        return (100, 130)
    elif edad <= 13:
        return (105, 135)
    else:
        # Adolescentes/adultos: mecanica mas cercana a la adulta
        return (110, 140)


def desviacion_maxima_pie_apoyo_por_edad(edad):
    """
    Devuelve la desviacion maxima (en grados) que se considera aceptable
    para el pie de apoyo respecto a la direccion exacta del pase.

    0 grados = el pie de apoyo apunta perfectamente hacia el companero.
    Cuanto mayor la desviacion, menos preciso tiende a salir el pase.
    """
    if edad <= 9:
        # Ninos pequenos: se tolera mas desviacion, es normal que aun no dominen la orientacion del pie
        return 15
    elif edad <= 13:
        return 12
    else:
        # Adolescentes/adultos: se espera mayor precision en la orientacion
        return 10


def rango_ideal_tobillo_control_por_edad(edad):
    """
    Devuelve el rango de angulo de tobillo (en grados) considerado
    razonable al controlar/amortiguar el balon, segun la edad del jugador.

    El angulo se mide entre el pie y la pierna en el momento del contacto:
    90 grados = pie totalmente rigido y perpendicular a la pierna,
    angulos mayores indican un pie mas relajado/flexionado que cede al impacto.
    """
    if edad <= 9:
        # Ninos pequenos: el pie suele estar mas rigido, se tolera un rango mas bajo
        return (95, 115)
    elif edad <= 13:
        return (100, 120)
    else:
        # Adolescentes/adultos: se espera mas soltura de tobillo para amortiguar
        return (105, 125)


def analizar_chut(edad, peso, posicion, angulo_rodilla):
    """
    Analiza un chut a porteria y devuelve una recomendacion en texto.

    Parametros:
      edad: edad del jugador en anios (numero)
      peso: peso del jugador en kg (numero)
      posicion: posicion en el campo, por ejemplo "delantero", "centrocampista", "defensa", "portero"
      angulo_rodilla: angulo de la rodilla al golpear el balon, en grados

    Devuelve:
      Un texto (string) con la recomendacion.
    """
    angulo_min, angulo_max = rango_ideal_por_edad(edad)

    recomendaciones = []

    # 1. Comprobamos el angulo de la rodilla contra el rango ideal para su edad
    if angulo_rodilla < angulo_min:
        recomendaciones.append(
            f"La rodilla esta demasiado flexionada ({angulo_rodilla:.0f} grados). "
            f"Para su edad se espera algo entre {angulo_min} y {angulo_max} grados. "
            "Sugerencia: trabajar el golpeo con la pierna algo mas extendida para ganar potencia y precision."
        )
    elif angulo_rodilla > angulo_max:
        recomendaciones.append(
            f"La rodilla esta demasiado extendida ({angulo_rodilla:.0f} grados) para su edad "
            f"(rango esperado {angulo_min}-{angulo_max} grados). "
            "Sugerencia: flexionar un poco mas la rodilla en el momento del impacto para mejorar el control del balon."
        )
    else:
        recomendaciones.append(
            f"El angulo de rodilla ({angulo_rodilla:.0f} grados) esta dentro del rango esperado "
            f"para su edad ({angulo_min}-{angulo_max} grados). Buen fundamento tecnico en este aspecto."
        )

    # 2. Un par de reglas simples extra relacionadas con la posicion
    if posicion.lower() == "portero":
        recomendaciones.append(
            "Como portero, el chut a porteria no suele ser su gesto principal; "
            "usar este analisis mas bien para saques de puerta con el pie."
        )
    elif posicion.lower() == "defensa":
        recomendaciones.append(
            "Como defensa, ademas de la potencia conviene priorizar la limpieza del golpeo "
            "para despejes seguros."
        )

    # 3. Regla simple relacionada con el peso (solo como ejemplo ilustrativo)
    if peso > 0 and edad > 0:
        indice = peso / edad  # relacion simple peso/edad, solo para ejemplo
        if indice > 4.5:
            recomendaciones.append(
                "Su relacion peso/edad es relativamente alta; vigilar la carga sobre la rodilla "
                "de apoyo durante el golpeo para prevenir molestias."
            )

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def analizar_pase(edad, peso, posicion, angulo_pie_apoyo):
    """
    Analiza un pase y devuelve una recomendacion en texto.

    Parametros:
      edad: edad del jugador en anios (numero)
      peso: peso del jugador en kg (numero)
      posicion: posicion en el campo, por ejemplo "delantero", "centrocampista", "defensa", "portero"
      angulo_pie_apoyo: desviacion en grados del pie de apoyo respecto a la
        direccion exacta del pase (0 = perfectamente alineado hacia el companero).
        Se espera un valor positivo, sin importar si la desviacion es hacia
        la izquierda o la derecha.

    Devuelve:
      Un texto (string) con la recomendacion.
    """
    desviacion_max = desviacion_maxima_pie_apoyo_por_edad(edad)

    recomendaciones = []

    # 1. Comprobamos la desviacion del pie de apoyo contra el maximo aceptable para su edad
    if angulo_pie_apoyo > desviacion_max:
        recomendaciones.append(
            f"El pie de apoyo se desvia {angulo_pie_apoyo:.0f} grados de la direccion del pase, "
            f"por encima de lo esperado para su edad (maximo {desviacion_max} grados). "
            "Sugerencia: trabajar la orientacion del pie de apoyo apuntando hacia el companero antes de golpear el balon."
        )
    else:
        recomendaciones.append(
            f"El pie de apoyo se desvia solo {angulo_pie_apoyo:.0f} grados de la direccion del pase, "
            f"dentro de lo esperado para su edad (maximo {desviacion_max} grados). Buena orientacion de cara al pase."
        )

    # 2. Un par de reglas simples extra relacionadas con la posicion
    if posicion.lower() == "portero":
        recomendaciones.append(
            "Como portero, la precision del pase con el pie es clave para iniciar jugadas desde atras; "
            "prestar especial atencion a este gesto."
        )
    elif posicion.lower() == "centrocampista":
        recomendaciones.append(
            "Como centrocampista, el pase es su gesto mas repetido; "
            "conviene priorizar este trabajo de orientacion del pie de apoyo sobre otros gestos."
        )

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def analizar_control(edad, peso, posicion, angulo_tobillo):
    """
    Analiza un control de balon y devuelve una recomendacion en texto.

    Parametros:
      edad: edad del jugador en anios (numero)
      peso: peso del jugador en kg (numero)
      posicion: posicion en el campo, por ejemplo "delantero", "centrocampista", "defensa", "portero"
      angulo_tobillo: angulo del tobillo del pie de control en el momento
        del contacto con el balon, en grados (ver rango_ideal_tobillo_control_por_edad
        para el significado del angulo).

    Devuelve:
      Un texto (string) con la recomendacion.
    """
    angulo_min, angulo_max = rango_ideal_tobillo_control_por_edad(edad)

    recomendaciones = []

    # 1. Comprobamos el angulo de tobillo contra el rango ideal para su edad
    if angulo_tobillo < angulo_min:
        recomendaciones.append(
            f"El tobillo esta demasiado rigido ({angulo_tobillo:.0f} grados). "
            f"Para su edad se espera algo entre {angulo_min} y {angulo_max} grados. "
            "Sugerencia: relajar y flexionar algo mas el tobillo al recibir el balon para amortiguarlo mejor."
        )
    elif angulo_tobillo > angulo_max:
        recomendaciones.append(
            f"El tobillo esta demasiado relajado/flexionado ({angulo_tobillo:.0f} grados) para su edad "
            f"(rango esperado {angulo_min}-{angulo_max} grados). "
            "Sugerencia: mantener algo mas de tension en el tobillo para no perder estabilidad al controlar."
        )
    else:
        recomendaciones.append(
            f"El angulo de tobillo ({angulo_tobillo:.0f} grados) esta dentro del rango esperado "
            f"para su edad ({angulo_min}-{angulo_max} grados). Buen control del balon."
        )

    # 2. Un par de reglas simples extra relacionadas con la posicion
    if posicion.lower() == "portero":
        recomendaciones.append(
            "Como portero, un buen control con el pie es clave para jugar el balon con seguridad "
            "en salidas desde atras."
        )
    elif posicion.lower() == "delantero":
        recomendaciones.append(
            "Como delantero, conviene trabajar el control orientado hacia el espacio o la porteria, "
            "no solo amortiguar el balon."
        )

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def main():
    # 1. Preguntamos que gesto se quiere analizar
    gesto = input("Que gesto quieres analizar? (chut / pase / control): ").strip().lower()

    # 2. Pedimos los datos comunes a los tres gestos
    edad = int(input("Edad del jugador (anios): "))
    peso = float(input("Peso del jugador (kg): "))
    posicion = input("Posicion en el campo (delantero/centrocampista/defensa/portero): ").strip()

    # 3. Segun el gesto elegido, pedimos el angulo especifico y llamamos a la funcion correspondiente
    if gesto == "chut":
        angulo = float(input("Angulo de rodilla al chutar (grados): "))
        recomendacion = analizar_chut(edad, peso, posicion, angulo)

    elif gesto == "pase":
        angulo = float(input("Desviacion del pie de apoyo respecto a la direccion del pase (grados): "))
        recomendacion = analizar_pase(edad, peso, posicion, angulo)

    elif gesto == "control":
        angulo = float(input("Angulo de tobillo al controlar el balon (grados): "))
        recomendacion = analizar_control(edad, peso, posicion, angulo)

    else:
        print("Gesto no reconocido. Escribe: chut, pase o control.")
        return

    # 4. Mostramos el resultado
    print()
    print("Recomendaciones:")
    print(recomendacion)


# Esto hace que main() se ejecute solo cuando corres este archivo directamente
if __name__ == "__main__":
    main()
