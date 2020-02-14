from app import app1, db
from app.models import User, Post

'''
从 1.0 版本开始，Flask 允许你设置只会在运行flask命令时自动注册生效的环境变量，要实现这点，你需要安装 python-dotenv

在项目的根目录下新建一个名为 .flaskenv 的文件，其内容是：
FLASK_APP=microblog.py
'''


@app1.shell_context_processor
def make_shell_context():
    """
    app.shell_context_processor装饰器将该函数注册为一个shell上下文函数。
    当flask shell命令运行时，它会调用这个函数并在shell会话中注册它返回的项目。
    函数返回一个字典而不是一个列表，原因是对于每个项目，你必须通过字典的键提供一个名称以便在shell中被调用。
    在添加shell上下文处理器函数后，你无需导入就可以使用数据库实例
    """
    return {'db': db, 'User': User, 'Post': Post}
