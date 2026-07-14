"""
Historial de analisis guardados en SQLite.

Cada vez que la web analiza un video con exito (se detecto un angulo
valido), se guarda una fila con la fecha/hora, el gesto, los datos del
jugador, el angulo detectado y la recomendacion generada. No se guarda
nada cuando no se detecta un gesto valido en el video, porque no hay un
angulo real que registrar.

Cada fila lleva tambien un usuario_id: un identificador aleatorio guardado
en la cookie de sesion de Flask (ver app.py), distinto para cada navegador.
El historial se filtra siempre por ese id, para que cada navegador solo
vea sus propios analisis.

Se usa sqlite3 (incluido en la libreria estandar de Python, no hace falta
instalar nada) contra un unico archivo, historial.db, en la carpeta del
proyecto.
"""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, "historial.db")


def inicializar_db():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            usuario_id TEXT,
            gesto TEXT NOT NULL,
            icono_gesto TEXT NOT NULL,
            etiqueta_gesto TEXT NOT NULL,
            etiqueta_angulo TEXT NOT NULL,
            edad INTEGER NOT NULL,
            peso REAL NOT NULL,
            posicion TEXT NOT NULL,
            angulo REAL NOT NULL,
            segundo REAL NOT NULL,
            recomendacion TEXT NOT NULL
        )
        """
    )

    # Migracion ligera: si la tabla ya existia de antes de tener usuario_id
    # (bases de datos creadas antes de este cambio), le añadimos la columna.
    # Las filas antiguas quedan con usuario_id NULL: no aparecen en ningun
    # historial filtrado, en vez de aparecer en el de todo el mundo.
    columnas = [fila[1] for fila in conexion.execute("PRAGMA table_info(analisis)").fetchall()]
    if "usuario_id" not in columnas:
        conexion.execute("ALTER TABLE analisis ADD COLUMN usuario_id TEXT")

    conexion.commit()
    conexion.close()


def guardar_analisis(
    usuario_id,
    gesto,
    icono_gesto,
    etiqueta_gesto,
    etiqueta_angulo,
    edad,
    peso,
    posicion,
    angulo,
    segundo,
    recomendacion,
):
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute(
        """
        INSERT INTO analisis (
            fecha_hora, usuario_id, gesto, icono_gesto, etiqueta_gesto, etiqueta_angulo,
            edad, peso, posicion, angulo, segundo, recomendacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            usuario_id,
            gesto,
            icono_gesto,
            etiqueta_gesto,
            etiqueta_angulo,
            edad,
            peso,
            posicion,
            angulo,
            segundo,
            recomendacion,
        ),
    )
    conexion.commit()
    conexion.close()


def obtener_historial(usuario_id):
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    filas = conexion.execute(
        "SELECT * FROM analisis WHERE usuario_id = ? ORDER BY fecha_hora DESC, id DESC",
        (usuario_id,),
    ).fetchall()
    conexion.close()
    return filas
