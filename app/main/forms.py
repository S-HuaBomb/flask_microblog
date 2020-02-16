"""
Flask-WTF插件使用Python类来表示Web表单。表单类只需将表单的字段定义为类属性即可。
"""
from flask import request
from flask_babel import _, lazy_gettext as _l  # 翻译文本
from flask_wtf import FlaskForm  # Flask-WTF的所有内容都在flask_wtf包中
# 由于Flask-WTF插件本身不提供字段类型，因此我直接从WTForms包中导入了四个表示表单字段的类。
# 每个字段类都接受一个描述或别名作为第一个参数，并生成一个实例来作为LoginForm的类属性。
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length  # 各种校验器
from app.models import User


class EditProfileForm(FlaskForm):
    """
    个人资料编辑器，可更改用户名和签名
    """
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About Me'), validators=[Length(min=0, max=200)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    """
    动态发布
    """
    post = TextAreaField(_l('Say Something'), validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    """
    搜索框
    """
    q = StringField(_('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enable' not in kwargs:
            kwargs['csrf_enable'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
