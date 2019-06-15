from django.forms import ModelForm


def create_dynamic_model_form(admin_class, form_add=False):
    """
    form_add: 默认 为False ，即是生成修改页面的 form 表单，为 True 时为生成增加页面的 form 表单
    :param admin_class:
    :param form_add:
    :return:
    """
    class Meta:
        model = admin_class.model
        fields = '__all__'
        # 如果没有只读字段
        if not form_add:
            exclude = admin_class.readonly_fields       # 排除只读字段
            admin_class.form_add = False
        else:
            admin_class.form_add = True

    def __new__(cls, *args, **kwargs):
        # print(cls, args, kwargs)    # <class 'django.forms.widgets.DynamicModelForm'> () {'instance': <CustomerInfo: lila>}
        print('cls___', cls.base_fields)    #有序字典： OrderedDict([('name', <django.forms.fields.CharField object at 0x0000024A31E3D160>), ('contact_type', <django.forms.fields.TypedChoiceField object at 0x0000024A31E3D2B0>), ])
        for field_name in cls.base_fields:
            field_obj = cls.base_fields[field_name]
            field_obj.widget.attrs.update({'class': 'form-control'})
        ret = ModelForm.__new__(cls)

        return ret
    dynamic_form = type('DynamicModelForm', (ModelForm,), {'Meta': Meta, '__new__': __new__})
    return dynamic_form
