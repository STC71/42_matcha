from flask import Blueprint, render_template
from app.utils.decorators import login_required

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("/")
@login_required
def inbox():
    return render_template("chat/inbox.html")

@chat_bp.route("/<int:conversation_id>")
@login_required
def conversation(conversation_id):
    return render_template("chat/conversation.html", conversation_id=conversation_id)
