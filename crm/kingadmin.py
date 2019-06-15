from crm import models
from kingadmin.sites import site
from kingadmin.admin_base import BaseKingAdmin


class UserProfileAdmin(BaseKingAdmin):
    pass


class CustomerAdmin(BaseKingAdmin):
    list_display = ['id', 'name', 'source', 'contact_type', 'contact', 'consultant', 'consult_content', 'status', 'date']
    list_filter = ['source', 'consultant', 'status', 'date']
    search_fields = ['contact', 'consultant__name']
    readonly_fields = ['status', 'contact']     # 只读字段，不可修改
    filter_horizontal = ['consult_course', ]        # 两排并列，点击左边切换到右边，点击右边切换到左边
    list_per_page = 8       # 分页

    actions = ['change_status']

    def change_status(self, request, data_list):
        """改变报名状态"""
        data_list.update(status=1)

site.register(models.UserProfile, BaseKingAdmin)
site.register(models.Role)
site.register(models.CustomerInfo, CustomerAdmin)
site.register(models.CustomerFollowUp)
site.register(models.Branch)
site.register(models.Student)
site.register(models.StudyRecord)
site.register(models.ClassList)
site.register(models.Menus)
site.register(models.StudentEnrollment)
site.register(models.StudyRecord)
site.register(models.PaymentRecord)
site.register(models.ContractTemplate)


