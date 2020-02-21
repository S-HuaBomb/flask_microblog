import os
base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    配置设置被定义为Config类中的属性。 一旦应用程序需要更多配置选项，直接依样画葫芦，附加到这个类上即可，
    稍后如果我发现需要多个配置集，则可以创建它的子类。拥有了这样一份配置文件，我还需要通知Flask读取并使用它。
    可以在生成Flask应用之后，(__init__.py里面)利用app.config.from_object()方法来完成这个操作
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'You will never guess'  # 获取安全密钥，防止CRSF攻击

    """我从DATABASE_URL环境变量中获取数据库URL，如果没有定义，
       我将其配置为base_dir变量表示的应用顶级目录下的一个名为app.db的文件路径。
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(base_dir, 'app.db') + '?check_same_thread=False'  # 使用SQLite，最后这句有利于再console中测试
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 此项用于设置数据发生变更之后是否发送信号给应用，我不需要，因此将其设置为False。

    '''电子邮件服务器配置，用于发送debug日志邮件'''
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['1712317024@qq.com']

    POSTS_PER_PAGE = 10  # 每页展示的数据列表长度

    LANGUAGES = ['en', 'zh']  # 国际化语言种类

    """百度翻译"""
    FANYI_APP_ID = str(os.environ.get('FANYI_APP_ID'))
    FANYI_SECRET_KEY = os.environ.get('FANYI_SECRET_KEY')
    # 百度翻译语言列表:
    LANG_LIST = ['zh', 'en', 'yue', 'wyw', 'jp', 'kor', 'fra', 'spa', 'th', 'ara', 'ru', 'pt', 'de', 'it', 'el',
                 'nl', 'pl', 'bul', 'est', 'dan', 'fin', 'cs', 'rom', 'slo', 'swe', 'hu', 'cht', 'vie']
    # 百度翻译语言列表，与语言检测的缩写不一致:
    LANG_DIFF = {'ja': 'jp', 'es': 'spa', 'fr': 'fra', 'ko': 'kor', 'zh-cn': 'zh', 'ro': 'rom'}

    """elasticsearch 配置"""
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
