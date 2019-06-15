import json
from django.shortcuts import render


class BaseKingAdmin(object):
    def __init__(self):
        self.actions.extend(self.default_actions)

    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 8
    default_actions = ['delete_selected_objs']
    actions = []

    def delete_selected_objs(self, request, data_list):
        """默认删除动作：action"""
        print(data_list)        # <QuerySet [<CustomerInfo: 刘老二>]>
        data_list_ids = json.dumps([i.id for i in data_list])
        # print('data_list_ids', data_list_ids)
        return render(request, 'kingadmin/table_obj_delete.html', {
            'admin_class': self,
            'objs': data_list,
            'data_list_ids': data_list_ids
        })
