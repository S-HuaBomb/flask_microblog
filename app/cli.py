"""在顶级目录的microblog.py文件中导入这个模块即可"""
import os
import click


def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""

        """该命令的名称来自被装饰函数的名称，并且帮助消息来自文档字符串。
        由于这是一个父命令，它的存在只为子命令提供基础，函数本身不需要执行任何操作。"""
        pass

    @translate.command()
    def update():
        """更新语言翻译包"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):  # 提取文本进行翻译，生成messages.pot
            # 运行成功返回值为0
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):  # 基于messages.pot更新翻译包messages.po
            raise RuntimeError('update command failed')
        # 如果两步都成功的话，可以在更新完成后删除messages.pot文件，因为当再次需要这个文件时，可以很容易地重新生成 。
        os.remove('messages.pot')  # 删除messages.pot

    @translate.command()
    def compile():
        """编译语言翻译包"""
        if os.system('pybabel compile -d app/translations'):  # 生成messages.mo, 这是Babel最终加载翻译的文件
            raise RuntimeError('compile command failed')

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """添加新的语言"""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')

        # 并将语言目录写入-d选项中指定的目录中，-l选项中指定的是翻译语言。
        # 我将在app/translations目录中安装所有翻译，因为这是Flask-Babel默认提取翻译文件的地方。
        if os.system('pybabel init -i messages.pot -d app/translations -l' + lang):  # 生成messages.po
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
