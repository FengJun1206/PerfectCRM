# from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        default='hj123@qq.com',
    )
    name = models.CharField(max_length=64, verbose_name='姓名')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    role = models.ManyToManyField('Role', blank=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.get_username()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    class Meta:
        verbose_name_plural = '用户表'
        permissions = (
            ('crm_table_list', '可以查看kingadmin每张表里所有的数据'),
            ('crm_table_list_view', '可以访问kingadmin表里每条数据的修改页'),
            ('crm_table_list_change', '可以对kingadmin表里的每条数据进行修改'),
            ('crm_table_obj_add_view', '可以访问kingadmin每张表的数据增加页'),
            ('crm_table_obj_add', '可以对kingadmin每张表进行数据添加'),

        )


# class UserProfile(models.Model):
#     """用户信息表"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=64, verbose_name='姓名')
#     role = models.ManyToManyField('Role', blank=True, null=True)
#
#     class Meta:
#         verbose_name_plural = '用户信息表'
#
#     def __str__(self):
#         return self.name


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=64, verbose_name='角色名字', unique=True)
    menus = models.ManyToManyField("Menus", blank=True)

    class Meta:
        verbose_name_plural = '角色表'

    def __str__(self):
        return self.name


class CustomerInfo(models.Model):
    """客户信息表"""
    name = models.CharField(max_length=64, default=None, verbose_name='客户姓名')
    contact_type_choices = ((0, 'qq'), (1, '微信'), (2, '手机'))
    contact_type = models.SmallIntegerField(choices=contact_type_choices, verbose_name='联系方式类型', default=0)
    contact = models.CharField(max_length=64, unique=True, verbose_name='联系方式')
    source_choices = ((0, 'QQ 群'),
                      (1, '51CTO'),
                      (2, '百度推广'),
                      (3, '知乎'),
                      (4, '转介绍'),
                      (5, '其他'),)
    source = models.SmallIntegerField(choices=source_choices, verbose_name='客户来源途径')
    referral_from = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='转介绍', blank=True, null=True)
    consult_course = models.ManyToManyField('Course', verbose_name='咨询课程')
    consult_content = models.TextField(verbose_name='咨询内容')

    status_choices = ((0, '未报名'), (1, '已报名'), (2, '已退学'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name='客户咨询状态')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='课程顾问')

    id_num = models.CharField(max_length=128, blank=True, null=True, verbose_name='身份证')
    emergency_contract = models.PositiveIntegerField(blank=True, null=True, verbose_name='紧急联系人')
    sex_choices = ((0, '男'), (1, '女'))
    sex = models.SmallIntegerField(choices=sex_choices, verbose_name='性别', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='咨询时间')

    class Meta:
        verbose_name_plural = '客户信息表'

    def __str__(self):
        return self.name


class Student(models.Model):
    """学员表"""
    customer = models.ForeignKey('CustomerInfo', on_delete=models.CASCADE, verbose_name='客户')
    class_grades = models.ManyToManyField('ClassList', verbose_name='班级')

    class Meta:
        verbose_name_plural = '学员表'

    def __str__(self):
        return self.customer.name


class CustomerFollowUp(models.Model):
    """客户跟踪记录表"""
    customer = models.ForeignKey('CustomerInfo', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='跟踪内容')
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='跟踪人')
    status_choices = (
        (0, '近期无报名计划'),
        (1, '一个月内报名'),
        (2, '两周内报名'),
        (3, '已报名'),
    )
    status = models.SmallIntegerField(choices=status_choices, verbose_name='当前跟踪客户状态')

    date = models.DateTimeField(auto_now_add=True, verbose_name='跟踪时间')

    class Meta:
        verbose_name_plural = '客户跟踪记录表'

    def __str__(self):
        return self.content


class Course(models.Model):
    """课程表"""
    name = models.CharField(max_length=64, verbose_name='课程名称', unique=True)
    price = models.PositiveSmallIntegerField(verbose_name='课程价格')
    period = models.PositiveSmallIntegerField(verbose_name='课程周期（月）', default=5)
    outline = models.TextField(verbose_name='课程大纲')

    class Meta:
        verbose_name_plural = '课程表'

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """班级列表"""
    class_type_choices = ((0, '脱产班'), (1, '周末班'), (2, '网络班'))
    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name='班级类型', default=0)
    semester = models.SmallIntegerField(verbose_name='学期')
    teacher = models.ManyToManyField('UserProfile', verbose_name='讲师')

    start_date = models.DateField('开班日期')
    graduate_date = models.DateField('毕业日期', blank=True, null=True)
    contract_template = models.ForeignKey('ContractTemplate', on_delete=models.CASCADE, verbose_name='合同模板', blank=True, null=True)

    course = models.ForeignKey('Course', on_delete=models.CASCADE, verbose_name='课程')
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, verbose_name='校区')

    class Meta:
        verbose_name_plural = '班级表'
        unique_together = ('branch', 'class_type', 'course', 'semester')

    def __str__(self):
        return "%s(%s)期" % (self.course.name, self.semester)


class CourseRecord(models.Model):
    """上课记录"""
    class_grade = models.ForeignKey('ClassList', verbose_name='上课班级', on_delete=models.CASCADE)

    day_num = models.PositiveSmallIntegerField(verbose_name='课程节次')
    teacher = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='讲师')
    title = models.CharField(max_length=64, verbose_name='本节课主题')
    content = models.TextField(verbose_name='本节课内容')

    has_homework = models.BooleanField('本节课是否有作业', default=True)
    homework = models.TextField(verbose_name='作业内容', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='本节课时间')

    class Meta:
        verbose_name_plural = '上课记录表'
        unique_together = ('class_grade', 'day_num')

    def __str__(self):
        return "%s第（%s)节" % (self.class_grade, self.day_num)


class StudyRecord(models.Model):
    """学员记录表"""
    course_record = models.ForeignKey('CourseRecord', on_delete=models.CASCADE, verbose_name='课程记录')
    student = models.ForeignKey('Student', verbose_name='报名的学员', on_delete=models.CASCADE)

    score_choice = ((100, "A+"),
                     (90, "A"),
                     (85, "B+"),
                     (80,"B"),
                     (75, "B-"),
                     (70, "C+"),
                     (60, "C"),
                     (40, "C-"),
                     (-50, "D"),
                     (0, "N/A"), #not avaliable
                     (-100, "COPY"), #not avaliable
                     )
    score = models.SmallIntegerField(choices=score_choice, default=0, verbose_name='学员成绩')
    show_choice = ((0, '缺勤'),
                    (1, '已签到'),
                    (2, '迟到'),
                    (3, '早退'),
                    )
    show_status = models.SmallIntegerField(choices=show_choice, verbose_name='学员考勤记录', default=1)
    note = models.TextField('成绩备注', blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '学员记录表'

    def __str__(self):
        return "%s %s %s" % (self.course_record, self.student, self.score)


class Branch(models.Model):
    """校区表"""
    name = models.CharField(max_length=64, verbose_name='校区名字', unique=True)
    addr = models.CharField(max_length=128, verbose_name='校区地址', blank=True, null=True)

    class Meta:
        verbose_name_plural = '校区表'

    def __str__(self):
        return self.name


class Menus(models.Model):
    """动态菜单表"""
    name = models.CharField(max_length=64, verbose_name='菜单名称')
    url_type_choices = ((0, 'absolute'), (1, 'dynamic'))
    url_type = models.SmallIntegerField(choices=url_type_choices, verbose_name='菜单类型（固定|动态）', default=0)
    url_name = models.CharField(max_length=128, verbose_name='url 地址')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '菜单'
        unique_together = ('name', 'url_name')


class ContractTemplate(models.Model):
    """存储合同模板"""
    name = models.CharField(max_length=64, verbose_name='合同模板名字')
    content = models.TextField(verbose_name='合同内容')

    class Meta:
        verbose_name_plural = '合同模板表'

    def __str__(self):
        return self.name


class StudentEnrollment(models.Model):
    """学员报名表"""
    customer = models.ForeignKey('CustomerInfo', on_delete=models.CASCADE, verbose_name='客户')
    class_grade = models.ForeignKey('ClassList', on_delete=models.CASCADE, verbose_name='班级')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE, verbose_name='课程顾问')
    contract_agreed = models.BooleanField(default=False, verbose_name='是否同意协议')
    contract_signed_date = models.DateTimeField(blank=True, null=True, verbose_name='报名及合同签署时间')
    contract_approved = models.BooleanField(default=False, verbose_name='审核通过')
    contract_approved_date = models.DateTimeField(verbose_name='合同审核时间', blank=True, null=True)

    class Meta:
        unique_together = ['customer', 'class_grade']
        verbose_name_plural = '学员报名表'

    def __str__(self):
        return '%s' % self.customer


class PaymentRecord(models.Model):
    """学员缴费记录表"""
    enrollment = models.ForeignKey('StudentEnrollment', on_delete=models.CASCADE)
    payment_type_choices = ((0, '报名费'), (1, '学费'), (2, '退费'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices, default=0)
    amount = models.IntegerField(verbose_name='缴纳的费用', default=500)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, verbose_name='缴费时间')

    class Meta:
        verbose_name_plural = '学员缴费记录表'

    def __str__(self):
        return '%s' % self.enrollment




