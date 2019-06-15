from django import conf


def kingadmin_auto_discover():
    """
    这个函数可以找到每个 app 下的 kingadmin ，并执行
    :return:
    """
    for app_name in conf.settings.INSTALLED_APPS:
        # mod = importlib.import_module(app_name, 'kingadmin')
        print('app_name', app_name)
        try:
            mod = __import__('%s.kingadmin' % app_name)

        except ImportError:
            pass




