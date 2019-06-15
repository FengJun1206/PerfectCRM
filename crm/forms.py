from crm import models
from django import forms
from django.forms import ModelForm


class StudentEnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field in cls.base_fields:
            field_obj = cls.base_fields[field]
            field_obj.widget.attrs.update({'class': 'form-control'})

            if field in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)

    class Meta:
        model = models.StudentEnrollment
        fields = '__all__'
        readonly_fields = ['contract_agreed']
        exclude = ['customer', 'consultant', 'contract_approved_date']


class CustomerForm(ModelForm):
    """
    动态 ModelForm
    """

    def __new__(cls, *args, **kwargs):
        # print('cls, args, kwargsc', cls, args, kwargs, cls.base_fields)
        """
        cls：<class 'crm.forms.CustomerForm'>  类 CustomerForm 本身
        args：()
        kwargs：{} 
        cls.base_fields：有序字典：OrderedDict([('customer', <django.forms.models.ModelChoiceField object at 0x00000217E58BFDD8>),
         ('class_grade', <django.forms.models.ModelChoiceField object at 0x00000217E58BFF98>), 
         ('consultant', <django.forms.models.ModelChoiceField object at 0x00000217E58CB198>), 
         ('contract_agreed', <django.forms.fields.BooleanField object at 0x00000217E58CB208>), 
         ('contract_signed_date', <django.forms.fields.DateTimeField object at 0x00000217E58CB358>), 
         ('contract_approved', <django.forms.fields.BooleanField object at 0x00000217E58CB3C8>), 
         ('contract_approved_date', <django.forms.fields.DateTimeField object at 0x00000217E58CB438>)])

        """
        for field in cls.base_fields:  # field = customer
            field_obj = cls.base_fields[field]  # <django.forms.models.ModelChoiceField object at 0x0000021B787DFDD8>
            field_obj.widget.attrs.update({'class': 'form-control'})

            if field in cls.Meta.readonly_fields:
                field_obj.widget.attrs.update({'disabled': 'true'})

        return ModelForm.__new__(cls)

    class Meta:
        model = models.CustomerInfo
        fields = '__all__'
        exclude = ['consult_content', 'status', 'consult_courses']
        readonly_fields = ['contact_type', 'contact', 'consultant', 'referral_from', 'source']

    def clean(self):
        # 整体错误
        if self.errors:
            raise forms.ValidationError('请在重新提交前修正错误')
        # 如果前端有人恶意修改了 readonly 字段，将 disabled 修改为 false，默认还是使用 readonly 里面的字段
        if self.instance.id is not None:
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, field)  # 数据库里的数据
                form_val = self.cleaned_data.get(field)  # form 表单提交过来的字段
                print(old_field_val, form_val)

                # 如果两者不相等， 说明前端 readonly 字段被修改了
                if old_field_val != form_val:
                    self.add_error(field, '可读字段是 %s，而不是 %s' % (old_field_val, form_val))
