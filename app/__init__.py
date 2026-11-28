"""
Application Factory de Matcha.
Crea y configura la instancia de Flask.
"""

"""
Qué hace:
Es el corazón de la aplicación. 
Usa el patrón Application Factory, registra blueprints, inicializa extensiones (CSRF, Mail, SocketIO) 
y define manejadores de error limpios (importante para el subject: no se pueden ver stack traces).
"""

import os
from flask import Flask
from app.config import config_by_name
from app.extensions import socketio, mail, csrf


def create_app(config_name=None):
    """
    Factory pattern: crea la aplicación Flask configurada.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )

    # Cargamos la configuración según el entorno
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Aseguramos que exista la carpeta de uploads
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inicializamos las extensiones
    csrf.init_app(app)
    mail.init_app(app)
    socketio.init_app(
        app,
        message_queue=app.config.get("SOCKETIO_MESSAGE_QUEUE"),
        cors_allowed_origins="*",
        async_mode="eventlet",
    )

    # Registramos los blueprints (rutas)
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.profile import profile_bp
    from app.routes.browse import browse_bp
    from app.routes.chat import chat_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(browse_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # Eventos de SocketIO
    from app import socket_events  # noqa: F401

    # Manejadores de errores
    register_error_handlers(app)

    # Context processor: hace disponible current_user en todas las plantillas
    @app.context_processor
    def inject_user():
        from flask import session
        user = None
        if session.get("user_id"):
            user = {
                "id": session["user_id"],
                "username": session.get("username", "User"),
                "first_name": session.get("first_name", ""),
            }
        return dict(current_user=user)

    return app


def register_error_handlers(app):
    """Registra manejadores de errores HTTP limpios (sin stack traces)."""
    from flask import render_template, jsonify, request

    @app.errorhandler(400)
    def bad_request(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Bad request", message=str(e)), 400
        return render_template("errors/400.html", error=e), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Unauthorized"), 401
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Forbidden"), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Not found"), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify(error="File too large"), 413

    @app.errorhandler(500)
    def internal_error(e):
        # Nunca exponemos el stack trace al cliente
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(error="Internal server error"), 500
        return render_template("errors/500.html"), 500
