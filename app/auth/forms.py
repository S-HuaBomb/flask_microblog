"""
Flask-WTF插件使用Python类来表示Web表单。表单类只需将表单的字段定义为类属性即可。
"""
from flask_babel import _, lazy_gettext as _l  # 翻译文本
from flask_wtf import FlaskForm  # Flask-WTF的所有内容都在flask_wtf包中
# 由于Flask-WTF插件本身不提供字段类型，因此我直接从WTForms包中导入了四个表示表单字段的类。
# 每个字段类都接受一个描述或别名作为第一个参数，并生成一个实例来作为LoginForm的类属性。
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length  # 各种校验器
from app.models import User


class LoginForm(FlaskForm):
    """
    登录表单
    要求用户输入username和password，并提供一个“remember me”的复选框和提交按钮
    在login.html中调用这些属性渲染出表单
    """
    username = StringField(_l('Username'), validators=[DataRequired()])  # 用户名表单字段
    password = PasswordField(_l('Password'), validators=[DataRequired()])  # 密码表单字段
    remember_me = BooleanField(_l('Remember Me'))  # 复选框表单字段
    submit = SubmitField(_l('Sign In'))  # 提交按钮


class RegistrationForm(FlaskForm):
    """
    注册表单
    """
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    '''
    添加任何匹配模式validate_ <field_name>的方法时，WTForms将这些方法作为自定义验证器，并在已设置验证器之后调用它们。
    '''
    def  validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address'))



class ResetPasswordRequestForm(FlaskForm):
    """
    输入重置密码
    """
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
