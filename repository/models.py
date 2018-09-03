from django.db import models
import django.utils.timezone as timezone


class UserInfo(models.Model):
    """
    用户表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    email = models.EmailField(verbose_name='邮箱', unique=True)
    avatar = models.ImageField(verbose_name='头像', upload_to="./static/imgs/avatar/",
                               default="static/imgs/avatar/default.png")

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    # 自關聯
    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo',  # 要進行關聯的表
                                  through='UserFans',  # 指定第三張表的表名
                                  related_name='f',  # 反向操作時用的字段名,不設置是表名_set
                                  # 指定關係表中那些字段做多對多關係
                                  through_fields=('user', 'follower'))

    def __str__(self):
        return self.username


class UserFans(models.Model):
    """
    互粉关系表
    """
    # related_name 反向操作時用的字段名,不設置是表名_set
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users',
                             on_delete=models.CASCADE)
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers',
                                 on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('user', 'follower'),
        ]


class Role(models.Model):
    caption = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.caption


class User2Role(models.Model):
    u = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    r = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '用户分配角色'

    def __str__(self):
        return "%s-%s" % (self.u.username, self.r.caption,)


class Action(models.Model):
    # get  获取用户信息1
    # post  创建用户2
    # delete 删除用户3
    # put  修改用户4

    #
    caption = models.CharField(max_length=32)
    code = models.CharField(max_length=32)

    class Meta:
        verbose_name_plural = '操作表'

    def __str__(self):
        return self.caption


# 1    菜单1     null
# 2    菜单2     null
# 3    菜单3     null
# 4    菜单1.1    1
# 5    菜单1.2    1
# 6    菜单1.2.1  4
# 无最后一层
class Menu(models.Model):
    caption = models.CharField(max_length=32)
    parent = models.ForeignKey('self', related_name='p', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.caption,)


class Permission(models.Model):
    # http://127.0.0.1:8001/user.html  用户管理 1
    # http://127.0.0.1:8001/order.html 订单管理 1

    # 權限的路徑和描述
    caption = models.CharField(max_length=32)
    url = models.CharField(max_length=128)
    menu = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.CASCADE)  # 權限所屬的菜單
    pattern = models.CharField(max_length=128, default="")
    status = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'URL表'

    def __str__(self):
        return "%s-%s" % (self.caption, self.url,)


class Permission2Action(models.Model):
    # 權限的實際操作
    p = models.ForeignKey(Permission, on_delete=models.CASCADE)
    a = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '权限表'

    def __str__(self):
        return "%s-%s:-%s?t=%s" % (self.p.caption, self.a.caption, self.p.url, self.a.code,)


class Permission2Action2Role(models.Model):
    # 角色擁有的所有權限和操作
    p2a = models.ForeignKey(Permission2Action, on_delete=models.CASCADE)
    r = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = '角色分配权限'

    def __str__(self):
        return "%s==>%s" % (self.r.caption, self.p2a,)


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客前缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)

    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    # blog_id = 1
    def __str__(self):
        return self.title


# blog = Blog.objects.filter(site='bingdujieer').first()
# info = obj.user
# category_list = Category.objects.filter(blog_id=blog.nid)

class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容', )

    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid', on_delete=models.CASCADE)


class UpDown(models.Model):
    """
    文章顶或踩
    """
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='赞或踩用户', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    up = models.BooleanField(verbose_name='是否赞')
    down = models.BooleanField(verbose_name='是否踩')

    class Meta:
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)

    reply = models.ForeignKey(verbose_name='回复评论', to='self', related_name='back', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)
    # m = xx


# blog = Blog.objects.filter(site='bingdujieer').first()
# info = obj.user
# category_list = Category.objects.filter(blog_id=blog.nid)
# Tag.objects.filter(blog_id=blog.nid)

class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True,
                                 on_delete=models.CASCADE)

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]
    # 1,2,3,4
    article_type_id = models.IntegerField(choices=type_choices, default=None)

    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]


# http://127.0.0.1:8000/wupeiqi/tag/1.html

# 自定义第三张表
# a2t = Article2Tag.objects.filter(tag_id=1,blog_id=blog.nid)
# for item in a2t:
#     item.article.title...

# 自动生成第三张表
# Article.objects.filter(m=1,blog_id=blog.nid)
# Article.objects.filter(tag_set=1,blog_id=blog.nid)


# 自定义第三张表+M2M
# Article.objects.filter(tags=1,blog_id=blog.nid)


class Tpl(models.Model):
    title = models.CharField(max_length=32)
    content = models.TextField()

    def __str__(self):
        return self.title


class Trouble(models.Model):
    title = models.CharField(max_length=32)
    detail = models.TextField()
    user = models.ForeignKey(UserInfo, related_name='u', on_delete=models.CASCADE)
    # ctime = models.CharField(max_length=32) # 1491527007.452494
    ctime = models.DateTimeField()
    status_choices = (
        (1, '未处理'),
        (2, '处理中'),
        (3, '已处理'),
    )
    status = models.IntegerField(choices=status_choices, default=1)

    processer = models.ForeignKey(UserInfo, related_name='p', null=True, blank=True, on_delete=models.CASCADE)
    solution = models.TextField(null=True)
    ptime = models.DateTimeField(null=True)
    pj_choices = (
        (1, '不满意'),
        (2, '一般'),
        (3, '活很好'),
    )
    pj = models.IntegerField(choices=pj_choices, null=True, default=2)

    def __str__(self):
        return self.title


class Report(models.Model):

    title = models.CharField(max_length=32)
    status_choices = (
        (1, '未处理'),
        (2, '处理中'),
        (3, '已处理'),
    )
    report_status = models.IntegerField(choices=status_choices, default=1)
    type_choices = (
        (1, '用詞不當'),
        (2, '內容重覆'),
        (3, '無意義內容'),
    )

    report_type = models.IntegerField(choices=type_choices, default=1)
    reporter = models.ForeignKey(UserInfo, related_name='r', on_delete=models.CASCADE)
    article_id = models.ForeignKey(Article, related_name='a', on_delete=models.CASCADE,default=0)
    detail = models.TextField(null=True)
    ctime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def __str__(self):
        return self.title
