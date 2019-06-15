from kingadmin.admin_base import BaseKingAdmin


class AdminSite(object):
    def __init__(self):
        """
        构造字典
        enabled_admins = {
            'crm': {'UserProfile': 'UserProfileAdmin}
            #格式： 'app 名': {'表名': '自定制表名'}
        }
        """
        self.enabled_admins = {}

    def register(self, model_class, admin_class=None):
        """
        注册 admin  models"
        :param model_class: 数据表名
        :param admin_class: 自定制的类名
        :return:
        """
        app_name = model_class._meta.app_label      # crm   models.UserProfile._meta.app_label
        model_name = model_class._meta.model_name   # userprofile   models.UserProfile._meta.model_name

        # 如果没有定义自定制的 admin 样式类，就用默认的样式类
        if not admin_class:
            admin_class = BaseKingAdmin()

        # 如果有自定制的 admin 样式类，就用自定制的
        else:
            admin_class = admin_class()     # 如：UserProfileAdmin()

        admin_class.model = model_class     # 把 model_class 赋值给 admin_class

        if app_name not in self.enabled_admins:
            self.enabled_admins[app_name] = {}
        self.enabled_admins[app_name][model_name] = admin_class

site = AdminSite()
