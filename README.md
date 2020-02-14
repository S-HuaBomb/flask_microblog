# flask_microblog
这是使用 Flask 创建的微博客，以熟悉和掌握 Flask WEB 开发


## 一、Flask中的数据库

Flask本身不支持数据库，相信你已经听说过了。 正如表单那样，这也是Flask有意为之。对使用的数据库插件自由选择，岂不是比被迫适应其中之一，更让人拥有主动权吗？

绝大多数的数据库都提供了Python客户端包，它们之中的大部分都被封装成Flask插件以便更好地和Flask应用结合。数据库被划分为两大类，遵循*关系*模型的一类是关系数据库，另外的则是非关系数据库，简称*NoSQL*，表现在它们不支持流行的关系查询语言[SQL](https://en.wikipedia.org/wiki/SQL)（译者注：部分人也宣称NoSQL代表不仅仅只是SQL）。虽然两类数据库都是伟大的产品，但我认为关系数据库更适合具有结构化数据的应用程序，例如用户列表，用户动态等，而NoSQL数据库往往更适合非结构化数据。 本应用可以像大多数其他应用一样，使用任何一种类型的数据库来实现，但是出于上述原因，我将使用关系数据库。

在[第三章](https://github.com/luhuisicnu/The-Flask-Mega-Tutorial-zh/blob/master/docs/%E7%AC%AC%E4%B8%89%E7%AB%A0%EF%BC%9AWeb%E8%A1%A8%E5%8D%95.md)中，我向你展示了第一个Flask扩展，在本章中，我还要用到两个。 第一个是[Flask-SQLAlchemy](http://packages.python.org/Flask-SQLAlchemy)，这个插件为流行的[SQLAlchemy](http://www.sqlalchemy.org/)包做了一层封装以便在Flask中调用更方便，类似*SQLAlchemy*这样的包叫做[Object Relational Mapper](http://en.wikipedia.org/wiki/Object-relational_mapping)，简称ORM。 ORM允许应用程序使用高级实体（如类，对象和方法）而不是表和SQL来管理数据库。 ORM的工作就是将高级操作转换成数据库命令。

SQLAlchemy不只是某一款数据库软件的ORM，而是支持包含[MySQL](https://www.mysql.com/)、[PostgreSQL](https://www.postgresql.org/)和[SQLite](https://www.sqlite.org/)在内的很多数据库软件。简直是太强大了，你可以在开发的时候使用简单易用且无需另起服务的SQLite，需要部署应用到生产服务器上时，则选用更健壮的MySQL或PostgreSQL服务，并且不需要修改应用代码（译者注：只需修改应用配置）。

确认激活虚拟环境之后，利用如下命令来安装Flask-SQLAlchemy插件：
```
(venv) $ pip install flask-sqlalchemy
```

### 数据库迁移

我所见过的绝大多数数据库教程都是关于如何创建和使用数据库的，却没有指出当需要对现有数据库更新或者添加表结构时，应当如何应对。 这是一项困难的工作，因为关系数据库是以结构化数据为中心的，所以当结构发生变化时，数据库中的已有数据需要被迁移到修改后的结构中。

我将在本章中介绍的第二个插件是[Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)。 这个插件是[Alembic](https://bitbucket.org/zzzeek/alembic)的一个Flask封装，是SQLAlchemy的一个数据库迁移框架。 使用数据库迁移增加了启动数据库时候的一些工作，但这对将来的数据库结构稳健变更来说，是一个很小的代价。

安装Flask-Migrate和安装你见过的其他插件的方式一样：
```
(venv) $ pip install flask-migrate
```

### Flask-SQLAlchemy配置

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

### 数据库模型

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

### 创建数据库迁移存储库

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

### 第一次数据库迁移

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

### 数据库升级和降级流程

目前，本应用还处于初期阶段，但讨论一下未来的数据库迁移战略也无伤大雅。 假设你的开发计算机上存有应用的源代码，并且还将其部署到生产服务器上，运行应用并上线提供服务。

而应用在下一个版本必须对模型进行更改，例如需要添加一个新表。 如果没有迁移机制，这将需要做许多工作。无论是在你的开发机器上，还是在你的服务器上，都需要弄清楚如何变更你的数据库结构才能完成这项任务。

通过数据库迁移机制的支持，在你修改应用中的模型之后，将生成一个新的迁移脚本（`flask db migrate`），你可能会审查它以确保自动生成的正确性，然后将更改应用到你的开发数据库（`flask db upgrade`）。 测试无误后，将迁移脚本添加到源代码管理并提交。

当准备将新版本的应用发布到生产服务器时，你只需要获取包含新增迁移脚本的更新版本的应用，然后运行`flask db upgrade`即可。 Alembic将检测到生产数据库未更新到最新版本，并运行在上一版本之后创建的所有新增迁移脚本。

正如我前面提到的，`flask db downgrade`命令可以回滚上次的迁移。 虽然在生产系统上不太可能需要此选项，但在开发过程中可能会发现它非常有用。 你可能已经生成了一个迁移脚本并将其应用，只是发现所做的更改并不完全是你所需要的。 在这种情况下，可以降级数据库，删除迁移脚本，然后生成一个新的来替换它。

### 数据库模型变更生效

一旦我变更了应用模型，就需要生成一个新的数据库迁移：
```
(venv) $ flask db migrate -m "posts table"
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'post'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_post_timestamp' on '['timestamp']'
  Generating /home/miguel/microblog/migrations/versions/780739b227a7_posts_table.py ... done
```

并将这个迁移应用到数据库：
```
(venv) $ flask db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade e517276bb1c2 -> 780739b227a7, posts table
```

如果你对项目使用了版本控制，记得将新的迁移脚本添加进去并提交。

## 二、国际化和本地化

`Babel`实例提供了一个`localeselector`装饰器。 为每个请求调用装饰器函数以选择用于该请求的语言：

`app/__init__.py`：选择最匹配的语言。

```
from flask import request

# ...

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])
```

这里我使用了Flask中`request`对象的属性`accept_languages`。 `request`对象提供了一个高级接口，用于处理客户端发送的带[Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)头部的请求。 该头部指定了客户端语言和区域设置首选项。 该头部的内容可以在浏览器的首选项页面中配置，默认情况下通常从计算机操作系统的语言设置中导入。 大多数人甚至不知道存在这样的设置，但是这是有用的，因为应用可以根据每个语言的权重，提供优选语言的列表。 为了满足你的好奇心，下面是一个复杂的`Accept-Languages`头部的例子：

```
Accept-Language: da, en-gb;q=0.8, en;q=0.7
```

这表示丹麦语（`da`）是首选语言（默认权重= 1.0），其次是英式英语（`en-GB`），其权重为0.8，最后是通用英语（`en`），权重为0.7。

要选择最佳语言，你需要将客户请求的语言列表与应用支持的语言进行比较，并使用客户端提供的权重，查找最佳语言。 这样做的逻辑有点复杂，但它已经全部封装在`best_match()`方法中了，该方法将应用提供的语言列表作为参数并返回最佳选择。

### 提取文本进行翻译

一旦应用所有`_()`和`_l()`都到位了，你可以使用`pybabel`命令将它们提取到一个*.pot*文件中，该文件代表*可移植对象模板*。 这是一个文本文件，其中包含所有标记为需要翻译的文本。 这个文件的目的是作为一个模板来为每种语言创建翻译文件。

提取过程需要一个小型配置文件，告诉pybabel哪些文件应该被扫描以获得可翻译的文本。 下面你可以看到我为这个应用创建的*babel.cfg*：

*babel.cfg*：PyBabel配置文件。

```
[python: app/**.py]
[jinja2: app/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
```

前两行分别定义了Python和Jinja2模板文件的文件名匹配模式。 第三行定义了Jinja2模板引擎提供的两个扩展，以帮助Flask-Babel正确解析模板文件。

可以使用以下命令来将所有文本提取到* .pot *文件：

```
(venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .
```

`pybabel extract`命令读取`-F`选项中给出的配置文件，然后从命令给出的目录（当前目录或本处的`.` ）扫描与配置的源匹配的目录中的所有代码和模板文件。 默认情况下，`pybabel`将查找`_()`以作为文本标记，但我也使用了重命名为`_l()`的延迟版本，所以我需要用`-k _l`来告诉该工具也要查找它 。 `-o`选项提供输出文件的名称。

我应该注意，*messages.pot*文件不需要合并到项目中。 这是一个只要再次运行上面的命令，就可以在需要时轻松地重新生成的文件。 因此，不需要将该文件提交到源代码管理。

### 生成语言目录

该过程的下一步是在除了原始语言（在本例中为英语）之外，为每种语言创建一份翻译。 我要从添加中文（语言代码`zh`）开始，所以这样做的命令是：

```
(venv) $ pybabel init -i messages.pot -d app/translations -l zh
creating catalog app/translations/es/LC_MESSAGES/messages.po based on messages.pot
```

`pybabel init`命令将*messages.pot*文件作为输入，并将语言目录写入`-d`选项中指定的目录中，`-l`选项中指定的是翻译语言。 我将在*app/translations*目录中安装所有翻译，因为这是Flask-Babel默认提取翻译文件的地方。 该命令将在该目录内为中文数据文件创建一个*zh*子目录。 特别是，将会有一个名为*app/translations/zh/LC_MESSAGES/messages.po*的新文件，是需要翻译的文件路径。

如果你想支持其他语言，只需要各自的语言代码重复上述命令，就能使得每种语言都有一个包含*messages.po*文件的存储库。

当你想开始使用这些翻译后的文本时，这个文件需要被编译成一种格式，这种格式在运行时可以被应用程序使用。 要编译应用程序的所有翻译，可以使用`pybabel compile`命令，如下所示：

```
(venv) $ pybabel compile -d app/translations
compiling catalog app/translations/zh/LC_MESSAGES/messages.po to
app/translations/zh/LC_MESSAGES/messages.mo
```

此操作在每个语言存储库中的*messages.po*旁边添加*messages.mo*文件。 *.mo*文件是Flask-Babel将用于为应用程序加载翻译的文件。

在为中文或任何其他添加到项目中的语言创建*messages.mo*文件之后，可以在应用中使用这些语言。 如果你想查看应用程序以中文显示的方式，则可以在Web浏览器中编辑语言配置，以将中文语作为首选语言。 对Chrome，这是设置页面的高级部分：

![Chrome语言选项](http://upload-images.jianshu.io/upload_images/4961528-e943991eeb05c2fc..png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

如果你不想更改浏览器设置，另一种方法是通过使`localeselector`函数始终返回一种语言来强制实现。 对中文，你可以这样做：

`app/__init__.py`：选择最佳语言。

```
@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'zh'
```

使用为中文配置的浏览器运行该应用或返回`zh`的`localeselector`函数，将使所有文本在使用该应用时显示为中文。

### 更新翻译

处理翻译时的一个常见情况是，即使翻译文件不完整，你也可能要开始使用翻译文件。 这是非常好的，你可以编译一个不完整的*messages.po*文件，任何可用的翻译都将被使用，而任何缺失的部分将使用原始语言。 随后，你可以继续处理翻译并再次编译，以便在取得进展时更新*messages.mo*文件。

如果在添加`_()`包装器时错过了一些文本，则会出现另一种常见情况。 在这种情况下，你会发现你错过的那些文本将保持为英文，因为Flask-Babel对他们一无所知。 当你检测到这种情况时，会想要将其用`_()`或`_l()`包装，然后执行更新过程，这包括两个步骤：

```
(venv) $ pybabel extract -F babel.cfg -k _l -o messages.pot .
(venv) $ pybabel update -i messages.pot -d app/translations
```

`extract`命令与我之前执行的命令相同，但现在它会生成*messages.pot*的新版本，其中包含所有以前的文本以及最近用`_()`或`_l()`包装的文本。 `update`调用采用新的`messages.pot`文件并将其合并到与项目相关的所有*messages.po*文件中。 这将是一个智能合并，其中任何现有的文本将被单独保留，而只有在*messages.pot*中添加或删除的条目才会受到影响。

*messages.po*文件更新后，你就可以继续新的测试了，再次编译它，以便对应用生效。
