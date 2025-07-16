"""
Sistema de migraciones para la base de datos
"""
import sqlite3
import os
from flask import current_app
from app import db
from sqlalchemy import or_

def get_db_path():
    """Obtiene la ruta de la base de datos"""
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        return db_uri.replace('sqlite:///', '')
    return 'servicio_tecnico.db'

def check_column_exists(table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        conn.close()
        return column_name in columns
    except Exception as e:
        print(f"Error verificando columna: {e}")
        return False

def check_table_exists(table_name):
    """Verifica si una tabla existe"""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()

        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error verificando tabla: {e}")
        return False

def add_column_if_not_exists(table_name, column_name, column_type, default_value=None):
    """Agrega una columna si no existe"""
    try:
        if not check_table_exists(table_name):
            print(f"Tabla {table_name} no existe, se creará con db.create_all()")
            return False

        if not check_column_exists(table_name, column_name):
            db_path = get_db_path()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            print(f"Agregando columna {column_name} a tabla {table_name}")

            # Construir la consulta ALTER TABLE
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value is not None:
                alter_query += f" DEFAULT {default_value}"

            cursor.execute(alter_query)

            # Crear índice si es necesario
            if column_name == 'usuario_id':
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column_name} ON {table_name}({column_name})")

            conn.commit()
            conn.close()
            print(f"Columna {column_name} agregada exitosamente")
            return True
        else:
            print(f"Columna {column_name} ya existe en tabla {table_name}")
            return False
    except Exception as e:
        print(f"Error agregando columna: {e}")
        return False

def run_migrations():
    """Ejecuta todas las migraciones necesarias"""
    print("Ejecutando migraciones de base de datos...")

    try:
        # Migración 1: Agregar usuario_id a tecnicos
        add_column_if_not_exists('tecnicos', 'usuario_id', 'INTEGER', 'NULL')

        print("Migraciones completadas exitosamente")
        return True
    except Exception as e:
        print(f"Error en migraciones: {e}")
        return False

def update_tecnico_model():
    """Actualiza el modelo Tecnico para incluir usuario_id dinámicamente"""
    try:
        if check_column_exists('tecnicos', 'usuario_id'):
            # Si la columna existe, agregar la relación al modelo
            from app.models.models import Tecnico, Usuario

            # Agregar la columna al modelo dinámicamente
            if not hasattr(Tecnico, 'usuario_id'):
                Tecnico.usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
                Tecnico.usuario = db.relationship('Usuario', backref='tecnico_profile')
                print("Modelo Tecnico actualizado con usuario_id")

        return True
    except Exception as e:
        print(f"Error actualizando modelo: {e}")
        return False

def associate_existing_tecnicos():
    """Asocia técnicos existentes con usuarios"""
    try:
        from app.models.models import Usuario, Tecnico

        # Solo proceder si la columna usuario_id existe
        if not check_column_exists('tecnicos', 'usuario_id'):
            print("Columna usuario_id no existe, saltando asociaciones")
            return

        # Obtener técnicos sin usuario asociado
        tecnicos_sin_usuario = Tecnico.query.filter(
            or_(Tecnico.usuario_id == None, Tecnico.usuario_id == 0)
        ).all()

        print(f"Asociando {len(tecnicos_sin_usuario)} técnicos con usuarios...")

        for tecnico in tecnicos_sin_usuario:
            if tecnico.email:
                # Buscar usuario existente
                usuario = Usuario.query.filter_by(email=tecnico.email, rol='tecnico').first()

                if usuario:
                    tecnico.usuario_id = usuario.id
                    print(f"Asociado técnico '{tecnico.nombre}' con usuario existente")
                else:
                    # Crear nuevo usuario
                    nuevo_usuario = Usuario(
                        nombre=tecnico.nombre,
                        email=tecnico.email,
                        telefono=tecnico.telefono or '',
                        rol='tecnico'
                    )
                    nuevo_usuario.set_password('tecnico123')

                    db.session.add(nuevo_usuario)
                    db.session.flush()

                    tecnico.usuario_id = nuevo_usuario.id
                    print(f"Creado usuario para técnico '{tecnico.nombre}'")

        db.session.commit()
        print("Asociaciones completadas")

    except Exception as e:
        print(f"Error en asociaciones: {e}")
        db.session.rollback()
