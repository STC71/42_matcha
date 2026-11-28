"""
Extensiones de Flask.
Se inicializan aquí y se vinculan a la app en create_app().
"""

"""
Qué hace:
Declara las extensiones que usaremos. 
Se inicializan de forma “perezosa”, o sea que no se asocian a la app todavía, 
pero se declaran aquí para que estén disponibles en toda la aplicación.
Y luego se asocian a la app en el factory con create_app() (app/__init__.py).
"""

from flask_socketio import SocketIO
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# SocketIO para chat y notificaciones en tiempo real
socketio = SocketIO(cors_allowed_origins="*", logger=False, engineio_logger=False)

# Envío de emails (verificación y reset de contraseña)
mail = Mail()

# Protección CSRF en todos los formularios
csrf = CSRFProtect()
