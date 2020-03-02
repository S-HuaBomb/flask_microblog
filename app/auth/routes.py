from flask import render_template, flash, redirect, url_for, request
from flask_babel import _  # _()函数随后返回翻译后的文本
from flask_login import current_user, login_user, logout_user  # 用户登录插件
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 用户是否已经登陆
        return redirect(url_for('main.index'))  # 登录则重定向到首页

    form = LoginForm()

    if form.validate_on_submit():
        '''
        form.validate_on_submit()实例方法会执行form校验的工作。
        当浏览器发起GET请求的时候，它返回False，这样视图函数就会跳过if块中的代码，直接转到视图函数的最后一句来渲染模板。
        当用户在浏览器点击提交按钮后，浏览器会发送POST请求。
        '''

        # SQLAlchemy查询对象的filter_by()方法。 filter_by()的结果是一个只包含具有匹配用户名的对象的查询结果集。
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password !'))
            return redirect(url_for('auth.login'))

        # 该函数会将用户登录状态注册为已登录，这意味着用户导航到任何未来的页面时，应用都会将用户实例赋值给current_user变量。
        login_user(user, remember=form.remember_me.data)

        # 重定向页面
        next_page = request.args.get('next')
        # Werkzeug的url_parse()函数解析，然后检查netloc属性是否被设置。确保next参数的值是相对路径
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')  # url_for('index')返回/index。url_for()的参数是endpoint名称，也就是视图函数的名字。

        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data
        # ))
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registration is successful!'))
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    发送邮箱认证重置密码
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # 邮箱是否存在
        if user:
            send_password_reset_email(user)  # 发送邮箱，生成邮箱中的链接
            flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='重置密码', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    邮箱中的密码重置链接
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)  # 认证令牌
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
