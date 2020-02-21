import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, request, current_app
from flask_babel import Babel, lazy_gettext as _l  # 国际化和本地化插件
from flask_bootstrap import Bootstrap
from flask_login import LoginManager  # 管理用户登录状态插件
from flask_mail import Mail  # 邮件发送插件
from flask_migrate import Migrate  # 数据库迁移插件
from flask_moment import Moment  # 日期格式化插件
from flask_sqlalchemy import SQLAlchemy  # ORM插件

from elasticsearch import Elasticsearch

from config import Config

"""
__name__变量是一个Python预定义的变量，它表示当前调用它的模块的名字。
当需要加载相关的资源，Flask就使用这个位置作为起点来计算绝对路径。
"""

# 以下这种注册Flask插件的模式希望你了然于胸，因为大多数Flask插件都是这样初始化的。
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'  # 要求用户登录时跳转到的的登录认证界面
login.login_message = _l('Please log in to access this page.')  # login弹出的消息也要翻译
mail = Mail()
moment = Moment()
babel = Babel()
bootstrap = Bootstrap()
'''初始化插件之后，bootstrap/base.html模板就会变为可用状态，你可以使用extends子句从应用模板中引用。'''


def create_app(config_class=Config):
    """
    应用工厂函数

    return: app, 成了局部变量
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化插件
    db.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)  # 注册错误处理blueprint

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 注册用户认证blueprint

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)  # 注册主业务blueprint

    # elasticsearch 属性
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    if not app.debug and not app.testing:
        # 发送日志到邮箱：
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_SSL']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        # 记录日志到文件中：
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app


@babel.localeselector
def get_locale():
    """Babel实例提供了一个localeselector装饰器。 为每个请求调用装饰器函数以选择最匹配的的语言
       request: 用于处理客户端发送的带Accept-Language头部的请求。 该头部指定了客户端语言和区域设置首选项。
       该头部的内容可以在浏览器的首选项页面中配置，默认情况下通常从计算机操作系统的语言设置中导入。
       Accept-Languages头部的例子: Accept-Language: da, en-gb;q=0.8, en;q=0.7
       best_match:，该方法将应用提供的语言列表作为参数，并使用客户端提供的权重，查找最佳语言并返回最佳选择
    """
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    # return 'zh'
