from django.template import Library
from django.utils.safestring import mark_safe
import datetime, time

register = Library()


# ?source=1&contact_type=2&consultant=&status=&date__gte=

@register.simple_tag
def build_filter_ele(filter_column, admin_class):
    # 字段对象
    column_obj = admin_class.model._meta.get_field(filter_column)
    # print('column_obj', column_obj)

    # 有 choices 的字段走这里，有：source、contact_type、consultant、status
    try:
        # 过滤
        filter_ele = "<div class='col-md-2 text-center' style='font-size: 18px'>%s<select name='%s' class='form-control'>" % \
                     (filter_column, filter_column)  # "<select name='source'>"

        for choice in column_obj.get_choices():

            """
            有 choices 的字段，会变成
            column_obj.get_choices() = 
            [('', '---------'), (0, 'QQ 群'), (1, '51CTO'), (2, '百度推广'), (3, '知乎'), (4, '转介绍'), (5, '其他')]
            也就意味着，会生成类似于：
            <select name="source">
                <option value="">---------</option>
                <option value="0">QQ 群</option>
                <option value="1">51CTO</option>
            </select>
            """
            selected = ''

            # 当前字段被过滤了
            # admin_class.filter_conditions = {'source': '1', 'contact_type': '2'}
            # 'source' in admin_class_filter_conditions
            if filter_column in admin_class.filter_conditions:
                # 当前值被选中了
                # if 1 ==  {'source': '1', 'contact_type': '2'}.get('source')
                if str(choice[0]) == admin_class.filter_conditions.get(filter_column):
                    selected = 'selected'

            # "<option value='1' selected = 'selected'>51CTO</option>"
            option = "<option value='%s' %s>%s</option>" % (choice[0], selected, choice[1])
            filter_ele += option
            #  "<select name='source'><option value='1' selected>51CTO</option>"


    # 没有 choices 的字段走这里，name、contact、consult_content、date
    except AttributeError as e:  # ?source=1&contact_type=2&consultant=&status=&date__gte=2019-4-6
        # print('err', e)
        filter_ele = "<div class='col-md-2 text-center' style='font-size: 18px'>%s<select name='%s__gte' class='form-control'>" % \
                     (filter_column, filter_column)  # <select name='date__gte'>

        # column_obj.get_internal_type() = CharField、TextField、DateTimeField

        if column_obj.get_internal_type() in ('DateField', 'DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [
                ['', '------'],
                [time_obj, 'Today'],
                [time_obj - datetime.timedelta(7), '七天内'],
                [time_obj.replace(day=1), '本月'],
                [time_obj - datetime.timedelta(90), '三个月内'],
                [time_obj.replace(month=1, day=1), 'YearToDay(YTD)'],
                ['', 'ALL'],
            ]

            for i in time_list:
                selected = ''
                # 若 i[0] 不存在，则为 ''， 否则为 '2019-4-13'
                time_to_str = '' if not i[0] else "%s-%s-%s" % (i[0].year, i[0].month, i[0].day)

                # 当前字段被过滤了      {'source': '1', 'contact_type': '2', 'date__gte': '2019-4-6'}
                # filter_column = 'date'
                if "%s__gte" % filter_column in admin_class.filter_conditions:
                    # print('---------gte', filter_column)

                    # 当前值被选中了
                    # if '2019-4-13' == {'source': '1', 'contact_type': '2', 'date__gte': '2019-4-6'}.get('date__gte')
                    if time_to_str == admin_class.filter_conditions.get("%s__gte" % filter_column):
                        selected = 'selected'

                # "<option value='2019-4-6' selected>七天内</option>"
                option = "<option value='%s' %s>%s</option>" % (time_to_str, selected, i[1])
                filter_ele += option

    filter_ele += "</select></div>"
    return mark_safe(filter_ele)


@register.simple_tag
def build_table_row(data_obj, admin_class):
    """
    生成一条数据行，放在 table_obj_list 表格中展示
    :param data_obj: 数据对象
    :param admin_class: 自定制的样式类，admin_class.model = model_class
    :return:

    data_list = <QuerySet [<CustomerInfo: lila>, <CustomerInfo: tom>]>

    """
    # admin_class.list_display
    # list_display = ['name', 'source', 'contact_type', 'contact', 'consultant', 'consult_content', 'status', 'date']

    ele = ""
    if admin_class.list_display:
        for index, column_name in enumerate(admin_class.list_display):
            # admin_class.model = model_class
            # model_class._meta.get_field('name')  = <django.db.models.fields.CharField: name>  字段对象
            # 要是字段本身有 choices的，column_obj.choices = ((0, 'QQ 群'), (1, '51CTO'), (2, '百度推广'), (3, '知乎'), (4, '转介绍'), (5, '其他'))
            #
            column_obj = admin_class.model._meta.get_field(column_name)

            if column_obj.choices:
                # getattr(data_obj, 'get_source_display')   ==> functools.partial(<bound method Model._get_FIELD_display of <CustomerInfo: lila>>, field=<django.db.models.fields.SmallIntegerField: source>)
                # 是 CustomerInfo 一个绑定的方法
                column_data = getattr(data_obj, 'get_%s_display' % column_name)()

            else:
                column_data = getattr(data_obj, column_name)  # 直接获得名字 lila 、tom

            td_ele = '<td>%s</td>' % column_data
            if index == 0:
                td_ele = '<td><a href="%s/change/">%s</a></td>' % (data_obj.id, column_data)

            ele += td_ele
    else:
        td_ele = '<td><a href="%s/change/">%s</a></td>' % (data_obj.id, data_obj)
        ele += td_ele
    return mark_safe(ele)


@register.simple_tag
def build_model_name(admin_class):
    """构建 model name"""
    model_name = admin_class.model._meta.model_name.upper()

    return model_name


@register.simple_tag
def render_paginator(data_list, admin_class, sorted_column):
    """分页"""
    ele = """
            <ul class="pagination">
            """
    # 上一页
    if data_list.has_previous():
        active = 'active'
        p1_ele = """<li><a href="?page=%s">%s</a></li>""" % (data_list.previous_page_number(), '上一页')
        if data_list.number == 1:
            p1_ele = """<li class="%s"><a href="?page=%s">%s</a></li>""" % (
            active, data_list.previous_page_number(), '上一页')
        ele += p1_ele

    for i in data_list.paginator.page_range:
        if abs(data_list.number - i) < 2:
            active = ''
            if data_list.number == i:
                active = 'active'

            sorted_ele = ''
            if sorted_column:  # {'id': 0} 或 {'id': -0}
                sorted_ele = '&_o=%s' % list(sorted_column.values())[0]

            p_ele = """<li class="%s"><a href="?page=%s%s">%s</a></li>""" % (active, i, sorted_ele, i)
            ele += p_ele

    # 下一页
    if data_list.has_next():
        active = 'active'
        p1_ele = """<li><a href="?page=%s">%s</a></li>""" % (data_list.next_page_number(), '下一页')
        if data_list.number == data_list.paginator.num_pages:
            p1_ele = """<li class="%s"><a href="?page=%s">%s</a></li>""" % (active, data_list.next_page_number(), '下一页')
        ele += p1_ele

    ele += '</ul>'
    return mark_safe(ele)


@register.simple_tag
def get_sorted_column(column, sorted_column, forloop):
    # sorted_column = {'name': '-0'}

    # 这一列被排序了
    if column in sorted_column:
        # 上一次排序顺序，这一次取反
        last_sort_index = sorted_column[column]  # {'id': '-0'}['id']

        if last_sort_index.startswith('-'):
            this_time_index = last_sort_index.strip('-')  # 0
        else:
            this_time_index = '-%s' % last_sort_index  # -0
        return this_time_index
    else:
        return forloop


@register.simple_tag
def render_sorted_arrow(column, sorted_column):
    """生成正逆序图标"""
    # 排序字段以及索引：sorted_column = {'id': '-0'}

    # 这一列被排序
    if column in sorted_column:
        last_sorted_index = sorted_column[column]

        # 逆序
        if last_sorted_index.startswith('-'):
            arrow_direction = 'bottom'
        # 正序
        else:
            arrow_direction = 'top'

        ele = """<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>""" % arrow_direction

        return mark_safe(ele)

    return ''


@register.simple_tag
def render_filter_args(admin_class, render_html=True):
    """过滤时能够排序，拼接 ?-o=0  +  &source=0&consultant=3 """
    if admin_class.filter_conditions:  # # filter_conditions {'source': '0', 'consultant': '3'}
        ele = ''
        for k, v in admin_class.filter_conditions.items():
            ele += '&%s=%s' % (k, v)  # ele = &source=0&consultant=3

        if render_html:
            return mark_safe(ele)
        else:
            return ele
    else:
        return ''


@register.simple_tag
def get_current_sorted_column_index(sorted_column):
    """"
    返回 -0 、0
    d.values()
    dict_values(['-0'])
    list(d.values())
    ['-0']
    """
    return list(sorted_column.values())[0] if sorted_column else ''


@register.simple_tag
def get_obj_field_val(form_obj, field):
    """
    返回model obj具体字段的值
    :param form_obj:
    :param field:
    :return:
    """
    return getattr(form_obj.instance, field)


@register.simple_tag
def get_available_m2m_data(field_name, form_obj, admin_class):
    # 字段对象
    field_obj = admin_class.model._meta.get_field(field_name)

    obj_list = set(field_obj.related_model.objects.all())

    selected_data = set(getattr(form_obj.instance, field_name).all())

    return obj_list - selected_data

    # return obj_list


@register.simple_tag
def get_selected_m2m_data(field_name, form_obj, admin_class):
    """
    右边已选好的字段
    :param field_name:
    :param form_obj:
    :param admin_class:
    :return:
    """
    selected_data = getattr(form_obj.instance, field_name).all()

    return selected_data


@register.simple_tag
def display_all_related_objs(obj):
    """
    删除时，显示所有与之相关的字段，对象等，包括 fk、m2m，递归
    :param obj: 要删除的对象 obj = <QuerySet [<CustomerInfo: lila>, ]>
    :return:
    related_objects：获取反向关联的字段，Fk 中的多
    obj = models.CustomerInfo.objects.get(id=8)
     obj._meta.related_objects
     (<ManyToOneRel: crm.customerinfo>,
 <ManyToOneRel: crm.student>,
 <ManyToOneRel: crm.customerfollowup>)
    """
    ele = '<ul><b style="color:red">%s</b>' % obj

    for reversed_fk_obj in obj._meta.related_objects:
        reversed_fk_name = reversed_fk_obj.name     # customerinfo、type：str
        related_lookup_key = '%s_set' % reversed_fk_name    # customerinfo_set  ，拼接，反向查询
        related_objs = getattr(obj, related_lookup_key).all()   # 反射，反向查询所有关联的数据
        # print('related_objs', getattr(obj, related_lookup_key))
        ele += "<li>%s<ul> " % reversed_fk_name

        if reversed_fk_obj.get_internal_type() == 'ManyToManyField':    # 不需要深入查找
            for i in related_objs:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a> 记录里与[%s]相关的的数据将被删除</li>" \
                       % (i._meta.app_label, i._meta.model_name, i.id, i, obj)
        else:
            for i in related_objs:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a></li>" %(i._meta.app_label,
                                                                                 i._meta.model_name,
                                                                                 i.id,i)
                ele += display_all_related_objs(i)

        ele += "</ul></li>"

    ele += "</ul>"

    return ele


@register.simple_tag
def get_model_verbose_name(admin_class):
    """get model verbose_name"""
    name = admin_class.model._meta.verbose_name_plural
    return name


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.model_name

