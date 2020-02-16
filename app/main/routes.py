from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_babel import _, get_locale  # _()函数随后返回翻译后的文本
from flask_login import current_user, login_required  # 用户登录插件
from langdetect import detect  # 谷歌语言检测
from werkzeug.urls import url_parse

from app import db
from app.main import bp
from app.main.forms import EditProfileForm, PostForm
from app.models import User, Post
from app.translate import translate


@bp.before_request
def before_request():
    """记录用户发起请求时的时间"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()  # 不必要db.session.add()
        # 考虑在引用current_user时，Flask-Login将调用用户加载函数，该函数将运行一个数据库查询并将目标用户添加到数据库会话中。
    g.locale = str(get_locale())  # 将语言环境添加到g对象, 以便我可以从base模板中访问它,并以正确的语言配置moment.js


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required  # 将此装饰器添加到位于@app.route装饰器下面的视图函数上时，该函数将要求用户登录。
def index():
    form = PostForm()
    if form.validate_on_submit():
        diff = current_app.config['LANG_DIFF']  # 翻译和检测出的语言缩写不一致
        language = detect(form.post.data)  # 还是谷歌牛逼！
        if language in diff.keys():
            language = diff.get(language)
        if len(language) > 5:
            language = ''

        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))

    # posts = current_user.followed_posts().all()
    # 分页：
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None

    """
    为了渲染模板，需要从flask框架中导入一个名为render_template()的函数。 
    该函数需要传入模板文件名和模板参数的变量列表，并返回模板中所有占位符都用实际变量值替换后的字符串结果。
    """
    return render_template('index.html', title='Home Page', form=form, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
    # return render_template('index.html', title='Home Page', posts=posts)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """
    request.form属性是Flask用提交中包含的所有数据暴露的字典
    jsonify()返回的值是将被发送回客户端的HTTP响应。
    在base.html中通过Jquery读取'text'
    """
    return jsonify({'text': translate(request.form['text_query'],
                                      request.form['src_lang'],
                                      request.form['dst_lang'])})


@bp.route('/user/<username>')  # 被< >包裹的URL <username>是动态的，在base.html中通过current_user.username赋值
@login_required
def user(username):
    """
    用户主页
    """
    userr = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = userr.posts.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=username, page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', title='User Home', user=userr, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
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
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
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
        return redirect(url_for('main.user', username=username))  # 回到用户主页
    current_user.follow(user)
    db.session.commit()
    # flash('已关注 {}'.format(username))
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """
    取关
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_("User %(username)s not found", username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    """
    动态社区
    """
    # 分页：
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', tiltle='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)
