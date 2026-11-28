"""
wsgi.py - Punto de entrada de la aplicación.
Gunicorn y Flask-SocketIO usan este archivo.
"""

"""
Qué hace:
Es el archivo que Gunicorn carga. 
Importa la factory create_app() y expone la variable app.
"""

from app import create_app
"""
from app dice que queremos importar algo del paquete app.
create_app() es la función que crea la aplicación Flask y la configura.
La aplicación FLASK es la instancia que maneja las rutas, la base de datos, etc.
En resumen, estamos diciendo: 
"Crea la aplicación Flask usando la función create_app() y guárdala en la variable app".
"""
from app.extensions import socketio
"""

"""

# Creamos la instancia de la aplicación
app = create_app()

if __name__ == "__main__":
    # Solo se ejecuta si lanzamos el archivo directamente (desarrollo)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
