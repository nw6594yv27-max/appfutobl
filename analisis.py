"""
Asistente de coaching de futbol - version inicial
Gesto analizado: chut a porteria

Nota importante: las reglas de angulo de rodilla usadas aqui son
simplificadas con fines educativos/de prototipo, no son un estandar
medico ni de biomecanica deportiva certificado. Sirven como punto de
partida para ir afinando con la ayuda de un entrenador o fisioterapeuta.

Nota sobre los ejercicios sugeridos: son ejercicios sencillos y de bajo
riesgo (movilidad, tecnica de aterrizaje, fuerza con el propio peso
corporal, y una opcion pliometrica ligera de bajo impacto: saltos suaves
sin caida fuerte), pensados para hacerse en casa. No incluyen pliometria
intensa ni cargas externas. Solo se sugieren cuando el angulo detectado
esta fuera del rango ideal para la edad del jugador.
"""

AVISO_EJERCICIOS = (
    "Aviso: estos ejercicios son orientativos y no sustituyen una valoracion profesional. "
    "Lo ideal es hacerlos con la supervision de un entrenador o preparador fisico."
)

MENCION_FIFA11 = (
    "Como referencia fiable y gratuita, el programa oficial FIFA 11+ ofrece una rutina completa "
    "de prevencion de lesiones para futbolistas jovenes; puede ser buena idea consultarlo con su entrenador."
)


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
    hay_ejercicios = False

    # 1. Comprobamos el angulo de la rodilla contra el rango ideal para su edad
    if angulo_rodilla < angulo_min:
        recomendaciones.append(
            f"La rodilla esta demasiado flexionada ({angulo_rodilla:.0f} grados). "
            f"Para su edad se espera algo entre {angulo_min} y {angulo_max} grados. "
            "Sugerencia: trabajar el golpeo con la pierna algo mas extendida para ganar potencia y precision."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) balanceos de pierna controlados apoyado en una pared, sin balon, buscando el rango completo de la cadera; "
            "2) sentadilla a una pierna asistida (apoyado en silla o pared), para ganar fuerza y equilibrio en la pierna de apoyo; "
            "3) repetir el gesto de chut despacio frente a un espejo, sin balon, exagerando la extension final de la rodilla; "
            "4) saltos suaves con los dos pies juntos, sin desplazamiento, aterrizando de puntillas y con las rodillas "
            "ligeramente flexionadas (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    elif angulo_rodilla > angulo_max:
        recomendaciones.append(
            f"La rodilla esta demasiado extendida ({angulo_rodilla:.0f} grados) para su edad "
            f"(rango esperado {angulo_min}-{angulo_max} grados). "
            "Sugerencia: flexionar un poco mas la rodilla en el momento del impacto para mejorar el control del balon."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) sentadilla a dos piernas con pausa de 2-3 segundos abajo, para ganar control de la flexion; "
            "2) zancada estatica (split squat) sin peso; "
            "3) chut en seco frente al espejo, deteniendo conscientemente el movimiento en el punto de flexion deseado; "
            "4) saltos suaves en el sitio, aterrizando y manteniendo 1-2 segundos la posicion de rodillas flexionadas "
            "al caer (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
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

    # 4. Aviso de supervision, una sola vez, solo si se sugirieron ejercicios
    if hay_ejercicios:
        recomendaciones.append(AVISO_EJERCICIOS)

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
    hay_ejercicios = False

    # 1. Comprobamos la desviacion del pie de apoyo contra el maximo aceptable para su edad
    if angulo_pie_apoyo > desviacion_max:
        recomendaciones.append(
            f"El pie de apoyo se desvia {angulo_pie_apoyo:.0f} grados de la direccion del pase, "
            f"por encima de lo esperado para su edad (maximo {desviacion_max} grados). "
            "Sugerencia: trabajar la orientacion del pie de apoyo apuntando hacia el companero antes de golpear el balon."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) colocar un cono o marca en el suelo simulando al companero, y practicar plantar el pie de apoyo "
            "apuntando hacia ella, sin balon; "
            "2) equilibrio sobre el pie de apoyo 20-30 segundos, para ganar estabilidad; "
            "3) pases cortos contra una pared apuntando a un objetivo marcado, prestando atencion consciente "
            "a la orientacion del pie de apoyo; "
            "4) saltos suaves a la pata coja sobre el pie de apoyo, aterrizando en el mismo sitio y buscando "
            "estabilizar la orientacion del pie nada mas tocar el suelo (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
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

    # 3. Aviso de supervision, una sola vez, solo si se sugirieron ejercicios
    if hay_ejercicios:
        recomendaciones.append(AVISO_EJERCICIOS)

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
    hay_ejercicios = False

    # 1. Comprobamos el angulo de tobillo contra el rango ideal para su edad
    if angulo_tobillo < angulo_min:
        recomendaciones.append(
            f"El tobillo esta demasiado rigido ({angulo_tobillo:.0f} grados). "
            f"Para su edad se espera algo entre {angulo_min} y {angulo_max} grados. "
            "Sugerencia: relajar y flexionar algo mas el tobillo al recibir el balon para amortiguarlo mejor."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) circulos de tobillo en ambos sentidos, sentado o de pie; "
            "2) elevaciones de talon lentas (sin salto), sintiendo el control de la flexion; "
            "3) recibir un balon lanzado suavemente contra una pared, practicando ceder el tobillo al contacto "
            "en vez de bloquearlo; "
            "4) saltos suaves a la comba, sin comba real si no se tiene, aterrizando de puntillas y dejando "
            "que el tobillo ceda un poco al contacto (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    elif angulo_tobillo > angulo_max:
        recomendaciones.append(
            f"El tobillo esta demasiado relajado/flexionado ({angulo_tobillo:.0f} grados) para su edad "
            f"(rango esperado {angulo_min}-{angulo_max} grados). "
            "Sugerencia: mantener algo mas de tension en el tobillo para no perder estabilidad al controlar."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) equilibrio a un pie sobre una superficie firme y estable, para ganar estabilidad; "
            "2) elevaciones de talon (calf raises) con el propio peso corporal; "
            "3) practicar el control buscando un punto intermedio: amortiguar el balon sin dejar que el pie "
            "ceda en exceso; "
            "4) saltos suaves con los dos pies, aterrizando y manteniendo el equilibrio estatico 2 segundos, "
            "buscando un aterrizaje mas firme y controlado (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
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

    # 3. Aviso de supervision, una sola vez, solo si se sugirieron ejercicios
    if hay_ejercicios:
        recomendaciones.append(AVISO_EJERCICIOS)

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def rango_ideal_rodilla_regate_por_edad(edad):
    """
    Devuelve el rango de angulo de rodilla (en grados) considerado
    razonable para la pierna de apoyo al ejecutar un cambio de direccion
    (regate), segun la edad del jugador.

    A diferencia del chut (donde se busca extension para potencia), aqui
    interesa una flexion suficiente para bajar el centro de gravedad y
    mantener el equilibrio y el control del balon durante el cambio de
    direccion.
    """
    if edad <= 9:
        return (90, 120)
    elif edad <= 13:
        return (95, 125)
    else:
        return (100, 130)


def analizar_regate(edad, peso, posicion, angulo_rodilla):
    """
    Analiza un regate (cambio de direccion con el balon) y devuelve una
    recomendacion en texto.

    Parametros:
      edad: edad del jugador en anios (numero)
      peso: peso del jugador en kg (numero)
      posicion: posicion en el campo, por ejemplo "delantero", "centrocampista", "defensa", "portero"
      angulo_rodilla: angulo de la rodilla de la pierna de apoyo durante el
        cambio de direccion, en grados

    Devuelve:
      Un texto (string) con la recomendacion.
    """
    angulo_min, angulo_max = rango_ideal_rodilla_regate_por_edad(edad)

    recomendaciones = []
    hay_ejercicios = False

    # 1. Comprobamos el angulo de rodilla contra el rango ideal para su edad
    if angulo_rodilla < angulo_min:
        recomendaciones.append(
            f"La rodilla esta demasiado flexionada ({angulo_rodilla:.0f} grados) durante el cambio de direccion. "
            f"Para su edad se espera algo entre {angulo_min} y {angulo_max} grados. "
            "Sugerencia: no bajar tanto el centro de gravedad para no perder velocidad de reaccion en el siguiente apoyo."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) desde una flexion moderada, practicar cambios de apoyo rapidos sin saltar; "
            "2) recorrer una cuadricula dibujada en el suelo con apoyos cortos, sin balon; "
            "3) sombra del regate (shadow dribbling) sin balon frente al espejo, controlando cuanto se flexiona "
            "la rodilla de apoyo; "
            "4) saltos laterales suaves de un pie al otro, sin desplazamiento amplio, aterrizando ligero "
            "(pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    elif angulo_rodilla > angulo_max:
        recomendaciones.append(
            f"La rodilla esta demasiado extendida ({angulo_rodilla:.0f} grados) para su edad "
            f"(rango esperado {angulo_min}-{angulo_max} grados) durante el cambio de direccion. "
            "Sugerencia: flexionar mas la rodilla de apoyo para ganar equilibrio y proteger mejor el balon."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) sentadilla a una pierna asistida (apoyo en pared o silla); "
            "2) zancadas laterales controladas, sin peso; "
            "3) practicar el cambio de direccion caminando (no corriendo), exagerando la flexion en cada apoyo; "
            "4) saltos suaves de un apoyo a otro (lado a lado), aterrizando con la rodilla flexionada y "
            "manteniendo el equilibrio 1-2 segundos antes del siguiente salto (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    else:
        recomendaciones.append(
            f"El angulo de rodilla de apoyo ({angulo_rodilla:.0f} grados) esta dentro del rango esperado "
            f"para su edad ({angulo_min}-{angulo_max} grados). Buen fundamento tecnico en este aspecto."
        )

    # 2. Un par de reglas simples extra relacionadas con la posicion
    if posicion.lower() == "delantero":
        recomendaciones.append(
            "Como delantero, un buen regate cerca del area puede generar ocasiones claras de gol; "
            "conviene trabajar este gesto en espacios reducidos."
        )
    elif posicion.lower() == "centrocampista":
        recomendaciones.append(
            "Como centrocampista, el regate ayuda a superar la presion rival y progresar el balon en zonas de mucho trafico."
        )

    # 3. Aviso de supervision, una sola vez, solo si se sugirieron ejercicios
    if hay_ejercicios:
        recomendaciones.append(AVISO_EJERCICIOS)

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def rango_ideal_codo_saque_banda_por_edad(edad):
    """
    Devuelve el rango de angulo de codo (en grados) considerado razonable
    en el instante de soltar el balon en un saque de banda, segun la edad
    del jugador.

    El angulo se mide entre el hombro, el codo y la muneca del brazo
    lanzador. 180 grados = brazo completamente extendido. Un saque de
    banda legal y potente requiere llevar el balon con ambos brazos bien
    extendidos por encima de la cabeza antes de soltarlo.
    """
    if edad <= 9:
        return (135, 180)
    elif edad <= 13:
        return (150, 180)
    else:
        return (160, 180)


def analizar_saque_banda(edad, peso, posicion, angulo_codo):
    """
    Analiza un saque de banda (gesto con las manos, no con el pie) y
    devuelve una recomendacion en texto.

    Parametros:
      edad: edad del jugador en anios (numero)
      peso: peso del jugador en kg (numero)
      posicion: posicion en el campo, por ejemplo "delantero", "centrocampista", "defensa", "portero"
      angulo_codo: angulo del codo del brazo lanzador en el momento de
        soltar el balon, en grados (ver rango_ideal_codo_saque_banda_por_edad).

    Devuelve:
      Un texto (string) con la recomendacion.
    """
    angulo_min, angulo_max = rango_ideal_codo_saque_banda_por_edad(edad)

    recomendaciones = []
    hay_ejercicios = False

    # 1. Comprobamos el angulo de codo contra el rango ideal para su edad
    if angulo_codo < angulo_min:
        recomendaciones.append(
            f"El codo esta demasiado flexionado en el momento de soltar el balon ({angulo_codo:.0f} grados). "
            f"Para su edad se espera al menos {angulo_min} grados de extension. "
            "Sugerencia: llevar el balon bien atras y por encima de la cabeza, y extender completamente ambos "
            "brazos antes de soltarlo, para ganar potencia y evitar una posible falta por saque incompleto."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) movilidad de hombros con rotaciones de hombro y brazos en cruz contra la pared; "
            "2) repetir el gesto completo del saque sin balon (o con un balon muy ligero) frente al espejo, "
            "exagerando la extension de ambos codos; "
            "3) fondos de brazos suaves apoyado de rodillas, para fortalecer con control; "
            "4) saltos suaves con los dos brazos elevados por encima de la cabeza sosteniendo el balon (sin "
            "lanzarlo), aterrizando ligero, para asociar la extension de brazos con un gesto explosivo "
            "controlado (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    elif angulo_codo > angulo_max:
        recomendaciones.append(
            f"El codo supera el rango tipico de extension para su edad ({angulo_codo:.0f} grados, "
            f"rango esperado {angulo_min}-{angulo_max} grados). "
            "Sugerencia: revisar que no se este forzando la articulacion del codo al final del lanzamiento."
        )
        recomendaciones.append(
            "Ejercicios sugeridos para trabajar esto en casa: "
            "1) movilidad de hombro/codo con control excentrico, bajando el brazo despacio desde arriba; "
            "2) repetir el gesto completo frenando conscientemente justo antes de la extension maxima, "
            "sin forzar la articulacion; "
            "3) saltos suaves sosteniendo el balon arriba, controlando la extension de brazos sin bloquear "
            "los codos al aterrizar (pliometria ligera, sin caida fuerte)."
        )
        recomendaciones.append(MENCION_FIFA11)
        hay_ejercicios = True
    else:
        recomendaciones.append(
            f"El codo alcanza una buena extension al soltar el balon ({angulo_codo:.0f} grados), "
            f"dentro del rango esperado para su edad ({angulo_min}-{angulo_max} grados). Buen fundamento tecnico en este aspecto."
        )

    # 2. Un par de reglas simples extra relacionadas con la posicion
    if posicion.lower() == "portero":
        recomendaciones.append(
            "Como portero, no suele encargarse de los saques de banda; este analisis es mas util "
            "para el resto de jugadores de campo."
        )
    elif posicion.lower() == "defensa":
        recomendaciones.append(
            "Como defensa, un saque de banda largo y bien ejecutado puede ser una forma rapida "
            "de progresar el balon desde zonas cercanas a su propia area."
        )

    # 3. Aviso de supervision, una sola vez, solo si se sugirieron ejercicios
    if hay_ejercicios:
        recomendaciones.append(AVISO_EJERCICIOS)

    # Unimos todas las recomendaciones en un solo texto, una por linea
    return "\n".join(recomendaciones)


def main():
    # 1. Preguntamos que gesto se quiere analizar
    gesto = input("Que gesto quieres analizar? (chut / pase / control / regate / saque_banda): ").strip().lower()

    # 2. Pedimos los datos comunes a todos los gestos
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

    elif gesto == "regate":
        angulo = float(input("Angulo de rodilla de apoyo durante el cambio de direccion (grados): "))
        recomendacion = analizar_regate(edad, peso, posicion, angulo)

    elif gesto == "saque_banda":
        angulo = float(input("Angulo de codo al soltar el balon en el saque de banda (grados): "))
        recomendacion = analizar_saque_banda(edad, peso, posicion, angulo)

    else:
        print("Gesto no reconocido. Escribe: chut, pase, control, regate o saque_banda.")
        return

    # 4. Mostramos el resultado
    print()
    print("Recomendaciones:")
    print(recomendacion)


# Esto hace que main() se ejecute solo cuando corres este archivo directamente
if __name__ == "__main__":
    main()
