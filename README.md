# flask_microblog
这是使用 Flask 创建的微博客，以熟悉和掌握 Flask WEB 开发


本文翻译自 [The Flask Mega-Tutorial Part IV: Database](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

在Flask Mega-Tutorial系列的第四部分，我将告诉你如何使用*数据库*。

本章的主题是重中之重！大多数应用都需要持久化存储数据，并高效地执行的增删查改的操作，*数据库*为此而生。

*本章的GitHub链接为： [Browse](https://github.com/miguelgrinberg/microblog/tree/v0.4), [Zip](https://github.com/miguelgrinberg/microblog/archive/v0.4.zip), [Diff](https://github.com/miguelgrinberg/microblog/compare/v0.3...v0.4).*

## Flask中的数据库

Flask本身不支持数据库，相信你已经听说过了。 正如表单那样，这也是Flask有意为之。对使用的数据库插件自由选择，岂不是比被迫适应其中之一，更让人拥有主动权吗？

绝大多数的数据库都提供了Python客户端包，它们之中的大部分都被封装成Flask插件以便更好地和Flask应用结合。数据库被划分为两大类，遵循*关系*模型的一类是关系数据库，另外的则是非关系数据库，简称*NoSQL*，表现在它们不支持流行的关系查询语言[SQL](https://en.wikipedia.org/wiki/SQL)（译者注：部分人也宣称NoSQL代表不仅仅只是SQL）。虽然两类数据库都是伟大的产品，但我认为关系数据库更适合具有结构化数据的应用程序，例如用户列表，用户动态等，而NoSQL数据库往往更适合非结构化数据。 本应用可以像大多数其他应用一样，使用任何一种类型的数据库来实现，但是出于上述原因，我将使用关系数据库。

在[第三章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%89%E7%AB%A0%EF%BC%9AWeb%E8%A1%A8%E5%8D%95.md)中，我向你展示了第一个Flask扩展，在本章中，我还要用到两个。 第一个是[Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy)，这个插件为流行的[SQLAlchemy](http://www.sqlalchemy.org/)包做了一层封装以便在Flask中调用更方便，类似*SQLAlchemy*这样的包叫做[Object Relational Mapper](http://en.wikipedia.org/wiki/Object-relational_mapping)，简称ORM。 ORM允许应用程序使用高级实体（如类，对象和方法）而不是表和SQL来管理数据库。 ORM的工作就是将高级操作转换成数据库命令。

SQLAlchemy不只是某一款数据库软件的ORM，而是支持包含[MySQL](https://www.mysql.com/)、[PostgreSQL](https://www.postgresql.org/)和[SQLite](https://www.sqlite.org/)在内的很多数据库软件。简直是太强大了，你可以在开发的时候使用简单易用且无需另起服务的SQLite，需要部署应用到生产服务器上时，则选用更健壮的MySQL或PostgreSQL服务，并且不需要修改应用代码（译者注：只需修改应用配置）。

确认激活虚拟环境之后，利用如下命令来安装Flask-SQLAlchemy插件：
```
(venv) $ pip install flask-sqlalchemy
```

## 数据库迁移

我所见过的绝大多数数据库教程都是关于如何创建和使用数据库的，却没有指出当需要对现有数据库更新或者添加表结构时，应当如何应对。 这是一项困难的工作，因为关系数据库是以结构化数据为中心的，所以当结构发生变化时，数据库中的已有数据需要被迁移到修改后的结构中。

我将在本章中介绍的第二个插件是[Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)。 这个插件是[Alembic](https://bitbucket.org/zzzeek/alembic)的一个Flask封装，是SQLAlchemy的一个数据库迁移框架。 使用数据库迁移增加了启动数据库时候的一些工作，但这对将来的数据库结构稳健变更来说，是一个很小的代价。

安装Flask-Migrate和安装你见过的其他插件的方式一样：
```
(venv) $ pip install flask-migrate
```

## Flask-SQLAlchemy配置

开发阶段，我会使用SQLite数据库，SQLite数据库是开发小型乃至中型应用最方便的选择，因为每个数据库都存储在磁盘上的单个文件中，并且不需要像MySQL和PostgreSQL那样运行数据库服务。

配置文件的两个配置项：
```
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'  # 使用SQLite，最后这句有利于再console中测试
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Flask-SQLAlchemy插件从`SQLALCHEMY_DATABASE_URI`配置变量中获取应用的数据库的位置。 当回顾[第三章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%89%E7%AB%A0%EF%BC%9AWeb%E8%A1%A8%E5%8D%95.md)可以发现，首先从环境变量获取配置变量，未获取到就使用默认值，这样做是一个好习惯。 本处，我从`DATABASE_URL`环境变量中获取数据库URL，如果没有定义，我将其配置为`basedir`变量表示的应用顶级目录下的一个名为*app.db*的文件路径。

`SQLALCHEMY_TRACK_MODIFICATIONS`配置项用于设置数据发生变更之后是否发送信号给应用，我不需要这项功能，因此将其设置为`False`。我将`check_same_thread`设置为False有利于在console中测试数据库操作，否则当你提交一次修改之后都会开启一个新的线程处理之后的操作，而此前导入的模块将不在新的线程中。

数据库在应用的表现形式是一个*数据库实例*，数据库迁移引擎同样如此。它们将会在应用实例化之后进行实例化和注册操作。

在这个初始化脚本中我更改了三处。首先，我添加了一个`db`对象来表示数据库。然后，我又添加了数据库迁移引擎`migrate`。这种注册Flask插件的模式希望你了然于胸，因为大多数Flask插件都是这样初始化的。最后，我在底部导入了一个名为`models`的模块，这个模块将会用来定义数据库结构。

## 数据库模型

定义数据库中一张表及其字段的类，通常叫做数据模型。ORM(SQLAlchemy)会将类的实例关联到数据库表中的数据行，并翻译相关操作。

就让我们从用户模型开始吧，利用 [WWW SQL Designer](http://ondras.zarovi.cz/sql/demo)工具，我画了一张图来设计用户表的各个字段（译者注：实际表名为user）：

![用户表](http://upload-images.jianshu.io/upload_images/4961528-3d7f26d60dd340ad.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

`id`字段通常存在于所有模型并用作*主键*。每个用户都会被数据库分配一个id值，并存储到这个字段中。大多数情况下，主键都是数据库自动赋值的，我只需要提供`id`字段作为主键即可。

`username`，`email`和`password_hash`字段被定义为字符串（数据库术语中的`VARCHAR`），并指定其最大长度，以便数据库可以优化空间使用率。 `username`和`email`字段的用途不言而喻，`password_hash`字段值得提一下。 我想确保我正在构建的应用采用安全最佳实践，因此我不会将用户密码明文存储在数据库中。 明文存储密码的问题是，如果数据库被攻破，攻击者就会获得密码，这对用户隐私来说可能是毁灭性的。 如果使用*哈希密码*，这就大大提高了安全性。 这将是另一章的主题，所以现在不需分心。

用户表构思完毕之后，我将其用代码实现，并存储到新建的模块*app/models.py*中.

创建的模板类继承自db.Model，它是Flask-SQLAlchemy中所有模型的基类。 这个类将表的字段定义为类属性，字段被创建为`db.Column`类的实例，它传入字段类型以及其他可选参数，例如，可选参数中允许指示哪些字段是唯一的并且是可索引的，这对高效的数据检索十分重要。

该类的`__repr__`方法用于在调试时打印用户实例。在下面的Python交互式会话中你可以看到`__repr__()`方法的运行情况：
```
>>> from app.models import User
>>> u = User(username='gigi', email='gigi@example.com')
>>> u
<None><User gigi>, <Email gigi@example.com>
```

## 创建数据库迁移存储库

上一节中创建的模型类定义了此应用程序的初始数据库结构（*元数据*）。 但随着应用的不断增长，很可能会新增、修改或删除数据库结构。 Alembic（Flask-Migrate使用的迁移框架）将以一种不需要重新创建数据库的方式进行数据库结构的变更。

这是一个看起来相当艰巨的任务，为了实现它，Alembic维护一个*数据库迁移存储库*，它是一个存储迁移脚本的目录。 每当对数据库结构进行更改后，都需要向存储库中添加一个包含更改的详细信息的迁移脚本。 当应用这些迁移脚本到数据库时，它们将按照创建的顺序执行。

Flask-Migrate通过`flask`命令暴露来它的子命令。 你已经看过`flask run`，这是一个Flask本身的子命令。 Flask-Migrate添加了`flask db`子命令来管理与数据库迁移相关的所有事情。 那么让我们通过运行`flask db init`来创建microblog的迁移存储库：
```
(venv) $ flask db init
  Creating directory /home/miguel/microblog/migrations ... done
  Creating directory /home/miguel/microblog/migrations/versions ... done
  Generating /home/miguel/microblog/migrations/alembic.ini ... done
  Generating /home/miguel/microblog/migrations/env.py ... done
  Generating /home/miguel/microblog/migrations/README ... done
  Generating /home/miguel/microblog/migrations/script.py.mako ... done
  Please edit configuration/connection/logging settings in
  '/home/miguel/microblog/migrations/alembic.ini' before proceeding.
```

请记住，`flask`命令依赖于`FLASK_APP`环境变量来知道Flask应用入口在哪里。 对于本应用，正如[第一章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%80%E7%AB%A0%EF%BC%9AHello%2C%20World!.md)，你需要设置`FLASK_APP = microblog.py`。

运行迁移初始化命令之后，你会发现一个名为*migrations*的新目录。该目录中包含一个名为*versions*的子目录以及若干文件。从现在起，这些文件就是你项目的一部分了，应该添加到代码版本管理中去。

## 第一次数据库迁移

包含映射到`User`数据库模型的用户表的迁移存储库生成后，是时候创建第一次数据库迁移了。 有两种方法来创建数据库迁移：手动或自动。 要自动生成迁移，Alembic会将数据库模型定义的数据库模式与数据库中当前使用的实际数据库模式进行比较。 然后，使用必要的更改来填充迁移脚本，以使数据库模式与应用程序模型匹配。 当前情况是，由于之前没有数据库，自动迁移将把整个User模型添加到迁移脚本中。 `flask db migrate`子命令生成这些自动迁移：
```
(venv) $ flask db migrate -m "users table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'user'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_email' on '['email']'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_user_username' on '['username']'
  Generating /home/miguel/microblog/migrations/versions/e517276bb1c2_users_table.py ... done
```

通过命令输出，你可以了解到Alembic在创建迁移的过程中执行了哪些逻辑。前两行是常规信息，通常可以忽略。 之后的输出表明检测到了一个用户表和两个索引。 然后它会告诉你迁移脚本的输出路径。 `e517276bb1c2`是自动生成的一个用于迁移的唯一标识（你运行的结果会有所不同）。 `-m`可选参数为迁移添加了一个简短的注释。

生成的迁移脚本现在是你项目的一部分了，需要将其合并到源代码管理中。 如果你好奇，并检查了它的代码，就会发现它有两个函数叫`upgrade()`和`downgrade()`。 `upgrade()`函数应用迁移，`downgrade()`函数回滚迁移。 Alembic通过使用降级方法可以将数据库迁移到历史中的任何点，甚至迁移到较旧的版本。

`flask db migrate`命令不会对数据库进行任何更改，只会生成迁移脚本。 要将更改应用到数据库，必须使用`flask db upgrade`命令。
```
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> e517276bb1c2, users table
```

因为本应用使用SQLite，所以`upgrade`命令检测到数据库不存在时，会创建它（在这个命令完成之后，你会注意到一个名为*app.db*的文件，即SQLite数据库）。 在使用类似MySQL和PostgreSQL的数据库服务时，必须在运行`upgrade`之前在数据库服务器上创建数据库。

## 数据库升级和降级流程

目前，本应用还处于初期阶段，但讨论一下未来的数据库迁移战略也无伤大雅。 假设你的开发计算机上存有应用的源代码，并且还将其部署到生产服务器上，运行应用并上线提供服务。

而应用在下一个版本必须对模型进行更改，例如需要添加一个新表。 如果没有迁移机制，这将需要做许多工作。无论是在你的开发机器上，还是在你的服务器上，都需要弄清楚如何变更你的数据库结构才能完成这项任务。

通过数据库迁移机制的支持，在你修改应用中的模型之后，将生成一个新的迁移脚本（`flask db migrate`），你可能会审查它以确保自动生成的正确性，然后将更改应用到你的开发数据库（`flask db upgrade`）。 测试无误后，将迁移脚本添加到源代码管理并提交。

当准备将新版本的应用发布到生产服务器时，你只需要获取包含新增迁移脚本的更新版本的应用，然后运行`flask db upgrade`即可。 Alembic将检测到生产数据库未更新到最新版本，并运行在上一版本之后创建的所有新增迁移脚本。

正如我前面提到的，`flask db downgrade`命令可以回滚上次的迁移。 虽然在生产系统上不太可能需要此选项，但在开发过程中可能会发现它非常有用。 你可能已经生成了一个迁移脚本并将其应用，只是发现所做的更改并不完全是你所需要的。 在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的来替换它。
