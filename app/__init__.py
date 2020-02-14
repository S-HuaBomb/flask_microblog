import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask, request
from flask_babel import Babel, lazy_gettext as _l  # 国际化和本地化插件
from flask_bootstrap import Bootstrap
from flask_login import LoginManager  # 管理用户登录状态插件
from flask_mail import Mail  # 邮件发送插件
from flask_migrate import Migrate  # 数据库迁移插件
from flask_moment import Moment  # 日期格式化插件
from flask_sqlalchemy import SQLAlchemy  # ORM插件

from config import Config

"""
__name__变量是一个Python预定义的变量，它表示当前调用它的模块的名字。
当需要加载相关的资源，Flask就使用这个位置作为起点来计算绝对路径。
"""
app1 = Flask(__name__)
app1.config.from_object(Config)

# 以下这种注册Flask插件的模式希望你了然于胸，因为大多数Flask插件都是这样初始化的。
db = SQLAlchemy(app1)
migrate = Migrate(app1, db)
login = LoginManager(app1)
login.login_view = 'login'  # 要求用户登录时跳转到的的登录认证界面
login.login_message = _l('Please log in to access this page.')  # login弹出的消息也要翻译
mail = Mail(app1)
moment = Moment(app1)
babel = Babel(app1)
bootstrap = Bootstrap(app1)
'''初始化插件之后，bootstrap/base.html模板就会变为可用状态，你可以使用extends子句从应用模板中引用。'''


@babel.localeselector
def get_locale():
    """Babel实例提供了一个localeselector装饰器。 为每个请求调用装饰器函数以选择最匹配的的语言
       request: 用于处理客户端发送的带Accept-Language头部的请求。 该头部指定了客户端语言和区域设置首选项。
       该头部的内容可以在浏览器的首选项页面中配置，默认情况下通常从计算机操作系统的语言设置中导入。
       Accept-Languages头部的例子: Accept-Language: da, en-gb;q=0.8, en;q=0.7
       best_match:，该方法将应用提供的语言列表作为参数，并使用客户端提供的权重，查找最佳语言并返回最佳选择
    """
    return request.accept_languages.best_match(app1.config['LANGUAGES'])
    # return 'zh'

# routes中要引用app1，所以要放在后面
from app import routes, models, errors  # models的模块，这个模块将会用来定义数据库结构。

if not app1.debug:
    # 发送日志到邮箱：
    if app1.config['MAIL_SERVER']:
        auth = None
        if app1.config['MAIL_USERNAME'] or app1.config['MAIL_PASSWORD']:
            auth = (app1.config['MAIL_USERNAME'], app1.config['MAIL_PASSWORD'])
        secure = None
        if app1.config['MAIL_USE_SSL']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app1.config['MAIL_SERVER'], app1.config['MAIL_PORT']),
            fromaddr='no-reply@' + app1.config['MAIL_SERVER'],
            toaddrs=app1.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app1.logger.addHandler(mail_handler)

    # 记录日志到文件中：
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app1.logger.addHandler(file_handler)

    app1.logger.setLevel(logging.INFO)
    app1.logger.info('Microblog startup')
