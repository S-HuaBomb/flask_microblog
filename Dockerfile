# 指定解释器版本和基础操作系统
# 3.7-alpine标签选择安装在Alpine Linux上的Python 3.7解释器
FROM python:3.7-alpine
#FROM python:3.6-alpine

# 创建一个名为microblog的新用户,而不是使用root用户
RUN adduser -D microblog

# 转移到此作为当前工作目录，绝对路径
WORKDIR /home/microblog

# COPY src dst。相对路径。表示：/home/microblog/requirements.txt
COPY requirements.txt requirements.txt
# RUN命令在容器的上下文中执行任意命令。这与你在shell提示符下输入命令相似。
RUN python -m venv venv
# 安装所有依赖
RUN venv/bin/pip --default-timeout=200 install -r requirements.txt
# 安装gunicorn，以将其用作Web服务器
RUN venv/bin/pip install gunicorn cython pymysql

# 讲道理不应该把下面这个文件放进去
COPY .flaskenv .flaskenv

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
# RUN chmod命令确保将这个新的boot.sh文件设置为可执行文件
RUN chmod +x boot.sh

# ENV命令在容器中设置环境变量
ENV FLASK_APP microblog.py

# 将存储在 /home/microblog 中的所有目录和文件的所有者设置为新的microblog用户
# 尽管我在Dockerfile的顶部附近创建了该用户，但所有命令的默认用户仍为root
# 需要切换到microblog用户，以便在容器启动时该用户可以正确运行这些文件。
RUN chown -R microblog:microblog ./
# USER命令使得这个新的microblog用户成为任何后续指令的默认用户，并且也是容器启动时的默认用户。
USER microblog

# EXPOSE命令配置该容器将用于服务的端口
EXPOSE 5000
# ENTRYPOINT命令定义了容器启动时应该执行的默认命令
ENTRYPOINT ["./boot.sh"]