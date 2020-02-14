from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_user, logout_user, login_required  # 用户登录插件
from flask_babel import _, get_locale  # _()函数随后返回翻译后的文本
from app.models import User, Post
from app.email import send_password_reset_email
from app import app1, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm,\
    ResetPasswordRequestForm, ResetPasswordForm
from werkzeug.urls import url_parse


@app1.before_request
def before_request():
    """记录用户发起请求时的时间"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()  # 不必要db.session.add()
        # 考虑在引用current_user时，Flask-Login将调用用户加载函数，该函数将运行一个数据库查询并将目标用户添加到数据库会话中。
    g.locale = str(get_locale())  # 将语言环境添加到g对象, 以便我可以从base模板中访问它,并以正确的语言配置moment.js


@app1.route('/', methods=['GET', 'POST'])
@app1.route('/index', methods=['GET', 'POST'])
@login_required  # 将此装饰器添加到位于@app.route装饰器下面的视图函数上时，该函数将要求用户登录。
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))

    # posts = current_user.followed_posts().all()
    # 分页：
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, app1.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    """
    为了渲染模板，需要从flask框架中导入一个名为render_template()的函数。 
    该函数需要传入模板文件名和模板参数的变量列表，并返回模板中所有占位符都用实际变量值替换后的字符串结果。
    """
    return render_template('index.html', title='Home Page', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
    # return render_template('index.html', title='Home Page', posts=posts)


@app1.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # 用户是否已经登陆
        return redirect(url_for('index'))  # 登录则重定向到首页

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
            return redirect(url_for('login'))

        # 该函数会将用户登录状态注册为已登录，这意味着用户导航到任何未来的页面时，应用都会将用户实例赋值给current_user变量。
        login_user(user, remember=form.remember_me.data)

        # 重定向页面
        next_page = request.args.get('next')
        # Werkzeug的url_parse()函数解析，然后检查netloc属性是否被设置。确保next参数的值是相对路径
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')  # url_for('index')返回/index。url_for()的参数是endpoint名称，也就是视图函数的名字。

        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data
        # ))
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app1.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app1.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registration is successful!'))
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app1.route('/user/<username>')  # 被< >包裹的URL <username>是动态的，在base.html中通过current_user.username赋值
@login_required
def user(username):
    """
    用户主页
    """
    userr = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = userr.posts.order_by(Post.timestamp.desc()).paginate(page, app1.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', title='User Home', user=userr, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app1.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    编辑个人资料
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app1.route('/follow/<username>')
@login_required
def follow(username):
    """
    关注
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        # flash('User {} not found'.format(username))
        flash(_("User %(username)s not found", username=username))  # 为了翻译，只能放弃format
        return redirect(url_parse(index))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))  # 回到用户主页
    current_user.follow(user)
    db.session.commit()
    # flash('已关注 {}'.format(username))
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app1.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取关
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s not found", username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s!', username=username))
    return redirect(url_for('user', username=username))


@app1.route('/explore')
@login_required
def explore():
    """
    动态社区
    """
    # 分页：
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app1.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', tiltle='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app1.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """
    邮箱认证重置密码
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='重置密码', form=form)


@app1.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    邮箱中的密码重置链接
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
