from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
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
    )
    name = models.CharField(max_length=64, verbose_name="姓名")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    role = models.ManyToManyField("Role", blank=True, null=True)

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    class Meta:
        permissions = (
            ('crm_table_list', '可以查看kingadmin每张表里所有的数据'),
            ('crm_table_list_view', '可以访问kingadmin表里每条数据的修改页'),
            ('crm_table_list_change', '可以对kingadmin表里的每条数据进行修改'),
            ('crm_table_obj_add_view', '可以访问kingadmin每张表的数据增加页'),
            ('crm_table_obj_add', '可以对kingadmin每张表进行数据添加'),

        )


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=64, unique=True)
    menus = models.ManyToManyField("Menus", blank=True)

    def __str__(self):
        return self.name


class CustomerInfo(models.Model):
    """客户信息表"""
    name = models.CharField(verbose_name='姓名', max_length=64, default=None)
    contact_type_choices = ((0, 'qq'), (1, '微信'), (2, '手机'))
    contact_type = models.SmallIntegerField(verbose_name='联系方式', choices=contact_type_choices, default=0)
    contact = models.CharField(verbose_name='号码', max_length=64, unique=True)
    source_choices = ((0, 'QQ群'),
                      (1, '51CTO'),
                      (2, '百度推广'),
                      (3, '知乎'),
                      (4, '转介绍'),
                      (5, '其它'),
                      )
    source = models.SmallIntegerField(verbose_name='客户来源', choices=source_choices)
    referral_from = models.ForeignKey("self", blank=True, null=True, verbose_name="转介绍")
    consult_courses = models.ManyToManyField("Course", verbose_name="咨询课程")
    consult_content = models.TextField(verbose_name="咨询内容")
    status_choices = ((0, '未报名'), (1, '已报名'), (2, '已退学'))
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices)
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问")

    id_num = models.CharField(max_length=128, blank=True, null=True)
    sex_choices = ((0, '男'), (1, '女'))
    sex = models.PositiveSmallIntegerField(verbose_name='性别',choices=sex_choices, blank=True, null=True)
    email = models.EmailField()

    date = models.DateField(auto_now_add=True, verbose_name='时间')

    def __str__(self):
        return self.name


class Student(models.Model):
    """学员表"""
    customer = models.OneToOneField("CustomerInfo")
    class_grades = models.ManyToManyField("ClassList")

    def __str__(self):
        return self.customer.name


class CustomerFollowUp(models.Model):
    """客户跟踪记录表"""
    customer = models.ForeignKey("CustomerInfo")
    content = models.TextField(verbose_name="跟踪内容")
    user = models.ForeignKey("UserProfile", verbose_name="跟进人")
    status_choices = ((0, '近期无报名计划'),
                      (1, '一个月内报名'),
                      (2, '2周内内报名'),
                      (3, '已报名'),
                      )
    status = models.SmallIntegerField(choices=status_choices)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.content


class Course(models.Model):
    """课程表"""
    name = models.CharField(verbose_name='课程名称', max_length=64, unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="课程周期(月)", default=5)
    outline = models.TextField(verbose_name="大纲")

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """班级列表"""
    branch = models.ForeignKey("Branch")
    course = models.ForeignKey("Course")
    class_type_choices = ((0, '脱产'), (1, '周末'), (2, '网络班'))
    class_type = models.SmallIntegerField(choices=class_type_choices, default=0)
    semester = models.SmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile", verbose_name="讲师")

    contract_template = models.ForeignKey("ContractTemplate", blank=True, null=True)  # 讲师忽略

    start_date = models.DateField("开班日期")
    graduate_date = models.DateField("毕业日期", blank=True, null=True)

    def __str__(self):
        return "%s(%s)期" % (self.course.name, self.semester)

    class Meta:
        unique_together = ('branch', 'class_type', 'course', 'semester')


class CourseRecord(models.Model):
    """上课记录"""
    class_grade = models.ForeignKey("ClassList", verbose_name="上课班级")
    day_num = models.PositiveSmallIntegerField(verbose_name="课程节次")
    teacher = models.ForeignKey("UserProfile")
    title = models.CharField("本节主题", max_length=64)
    content = models.TextField("本节内容")
    has_homework = models.BooleanField("本节有作业", default=True)
    homework = models.TextField("作业需求", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s%s第(%s)天" % (self.class_grade, self.class_grade.class_type, self.day_num)

    class Meta:
        unique_together = ('class_grade', 'day_num')


class StudyRecord(models.Model):
    """学习记录表"""
    course_record = models.ForeignKey("CourseRecord")
    student = models.ForeignKey("Student")

    score_choices = ((100, "A+"),
                     (90, "A"),
                     (85, "B+"),
                     (80, "B"),
                     (75, "B-"),
                     (70, "C+"),
                     (60, "C"),
                     (40, "C-"),
                     (-50, "D"),
                     (0, "N/A"),
                     (-100, "COPY"),
                     )
    score = models.SmallIntegerField(choices=score_choices, default=0)
    show_choices = ((0, '缺勤'),
                    (1, '已签到'),
                    (2, '迟到'),
                    (3, '早退'),
                    )
    show_status = models.SmallIntegerField(choices=show_choices, default=1)
    note = models.TextField("成绩备注", blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s" % (self.course_record, self.student, self.score)

    class Meta:
        unique_together = (
            'course_record', 'student'
        )


class Branch(models.Model):
    """校区"""
    name = models.CharField(max_length=64, unique=True)
    addr = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name


class Menus(models.Model):
    """动态菜单"""
    name = models.CharField(max_length=64)
    url_type_choices = ((0, 'absolute'), (1, 'dynamic'))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0)
    url_name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'url_name')


class StudentEnrollment(models.Model):
    """学员报名表"""
    customer = models.ForeignKey("CustomerInfo")
    class_grade = models.ForeignKey("ClassList", verbose_name='报名班级')
    consultant = models.ForeignKey("UserProfile")
    contract_agreed = models.BooleanField(default=False, verbose_name='合同是否同意')
    contract_signed_date = models.DateTimeField(blank=True, null=True, verbose_name='签署时间')
    contract_approved = models.BooleanField(default=False,verbose_name='是否审核通过')
    contract_approved_date = models.DateTimeField(verbose_name="合同审核时间", blank=True, null=True)

    class Meta:
        unique_together = ('customer', 'class_grade')

    def __str__(self):
        return "%s" % self.customer


class PaymentRecord(models.Model):
    """存储学员缴费记录"""
    enrollment = models.ForeignKey(StudentEnrollment)
    payment_type_choices = ((0, '报名费'), (1, '学费'), (2, '退费'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices, default=0)
    amount = models.IntegerField("费用", default=500)
    consultant = models.ForeignKey("UserProfile")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.enrollment


class ContractTemplate(models.Model):
    """存储合同模板"""
    name = models.CharField(max_length=64)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)