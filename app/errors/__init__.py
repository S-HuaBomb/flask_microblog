from flask import Blueprint


bp = Blueprint('errors', __name__)

from app.errors import handlers  # 此处必须位于底部以避免循环依赖
