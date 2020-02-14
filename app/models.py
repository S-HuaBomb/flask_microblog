from datetime import datetime
from time import time
import jwt  # JSON Web Token
from hashlib import md5  # 用于Gravatar的URL的哈希
from app import db, login, app1
from werkzeug.security import generate_password_hash, check_password_hash  # 密码hash插件
from flask_login import UserMixin

"""
初始化运行flask db init(创建microblog的迁移存储库)
    数据表每次修改时，都要：
    >> flask db migrate(自动迁移将把整个User模型添加到迁移脚本中)
    >> flask db upgrade(将更改应用到数据库)
"""

# 粉丝关联表(用户表自关联多对多)
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    """
    用户表
    :posts: 用户发送的动态，不是实际的数据表字段，一对多
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))  # 哈希加密存储密码的字段
    about_me = db.Column(db.String(200))  # 签名
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # 最近访问时间
    '''
    db.relationship的第一个参数表示代表关系“多”的类。 backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。
    这将会为用户动态添加一个属性post.author，调用它将返回给该用户动态的用户实例。 lazy参数定义了这种关系调用的数据库查询是如何执行的
    '''
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # 对于一对多关系，db.relationship字段通常在“一”的这边定义

    '''用户的粉丝(自关联多对多)，即这是被关注者'''
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),  # 关联粉丝的条件
                               secondaryjoin=(followers.c.followed_id == id),  # 关联被关注者的条件
                               backref=db.backref('followers', lazy='dynamic'),  # 被关注者访问此字段的调用方式(查看自己粉丝)
                               lazy='dynamic')

    def avatar(self, size):
        """
        :size: 图像大小
        :?d=: Gravatar提供的随机图像，identicon是随机几何图像
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()  # MD5的参数类型需要是字节而不是字符串
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def __repr__(self):
        # __repr__方法用于在Console调试时打印用户实例
        return '<{}><User {}>, <Email {}> \n'.format(self.id, self.username, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        """关注"""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """取消关注"""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """关注的用户的动态"""
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)  # 同时显示自己的动态
        return followed.union(own).order_by(Post.timestamp.desc())  # 合并之后再排序

    def get_reset_password_token(self, expires_in=600):
        """生成令牌"""
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in},
                          app1.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        """认证令牌"""
        try:
            id = jwt.decode(token, app1.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):
    """
    用户发送的动态表
    :user_id: user表id字段的外键约束，多对一（一个用户可发送多条动态）
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  # 时间戳加索引，有利于按时间顺序检索
    '''
    当你将一个函数作为默认值传入后，SQLAlchemy会将该字段设置为调用该函数的值
    （请注意，在utcnow之后我没有包含()，所以我传递函数本身，而不是调用它的结果）。
    '''
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Flask-SQLAlchemy自动设置类名为小写来作为对应表的名称。

    def __repr__(self):
        return '<Post {}>'.format(self.body)


""" 用户会话是Flask分配给每个连接到应用的用户的存储空间，每当已登录的用户导航到新页面时，Flask-Login将从会话中检索用户的ID，
然后将该用户实例加载到内存中。因为数据库对Flask-Login透明，所以需要应用来辅助加载用户。基于此，插件期望应用配置一个用户加载函数，
可以调用该函数来加载给定ID的用户。
"""


@login.user_loader
def load_user(uid):
    """
    使用Flask-Login的@login.user_loader装饰器来为用户加载功能注册函数。即在routes/login中获取current_user
    Flask-Login将字符串类型的参数id传入用户加载函数，因此使用数字ID的数据库需要如上所示地将字符串转换为整数。
    """
    return User.query.get(int(uid))
