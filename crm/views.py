from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from crm import models
from crm.forms import CustomerForm, StudentEnrollmentForm
from django.db.utils import IntegrityError
import json, os
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.timezone import datetime


@login_required
def dashboard(request):
    """首页"""
    return render(request, 'crm/dashboard.html')


@login_required
def student_enrollment(request):
    """销售分配学员班级，并生成报名链接"""
    customer_data = models.CustomerInfo.objects.all()
    class_list_data = models.ClassList.objects.all()
    if request.method == "POST":
        customer_id = request.POST.get('customer_id')  # 客户
        class_grade_id = request.POST.get('class_grade_id')  # 班级
        consultant_id = request.user.id  # 课程顾问

        try:
            enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id=customer_id,
                class_grade_id=class_grade_id,
                consultant_id=consultant_id
            )
        except IntegrityError as e:
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customer_id,
                                                                  class_grade_id=class_grade_id)

            # 是否同意协议，是则跳转，否则
            if enrollment_obj.contract_agreed:
                return redirect('/crm/student_enrollment/%s/contract_audit/' % enrollment_obj.id)

        # 生成报名链接，传递给前端，销售复制发送给学员填写报名信息
        enrollment_links = 'http://localhost:8002/crm/enrollment/%s/' % enrollment_obj.id

    return render(request, 'crm/student_enrollment.html', locals())


@login_required
def contract_audit(request, enrollment_id):
    """
    合同审核，销售对学员填写的报名表，签署的合同进行审核
    审核通过则跳转到修改页面： http://127.0.0.1:8002/kingadmin/crm/customerinfo/1/change/
    :param request:
    :param enrollment_id:
    :return:
    """
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)

    if request.method == 'POST':
        print(request.POST)
        student_enrollment_form = StudentEnrollmentForm(instance=enrollment_obj, data=request.POST)
        if student_enrollment_form.is_valid():
            student_enrollment_form.save()

            # 学员对象
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
            stu_obj.class_grades.add(enrollment_obj.class_grade_id)  # 将学员添加到相应班级
            stu_obj.save()

            # 更改报名状态
            enrollment_obj.customer.status = 1
            enrollment_obj.customer.save()

            # 合同审核时间
            enrollment_obj.contract_approved_date = datetime.now()
            enrollment_obj.save()

            print(enrollment_obj.customer.status)

            return redirect('http://127.0.0.1:8002/kingadmin/crm/customerinfo/%s/change/' % enrollment_obj.customer.id)
    else:
        customer_form = CustomerForm(instance=enrollment_obj.customer)
        student_enrollment_form = StudentEnrollmentForm(instance=enrollment_obj)

    return render(request, 'crm/contract_audit.html', locals())


@login_required
def enrollment(request, enrollment_id):
    """
    学员报名链接地址
    :param request:
    :return:
    """
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)

    # 如果学员已经报名并填写了合同，那么再访问这个页面时，应该显示
    if enrollment_obj.contract_agreed:
        return HttpResponse('你已经报名，你耐心等待审核！')

    if request.method == 'POST':
        customer_form = CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        # print('form err', customer_form.errors, customer_form.cleaned_data)
        if customer_form.is_valid():
            customer_form.save()

            enrollment_obj.contract_agreed = True  # 合同协议变为 True
            enrollment_obj.contract_signed_date = datetime.now()  # 合同签署时间
            enrollment_obj.save()  # 保存

            return HttpResponse('你已成功提交报名表，请等待审核！')
        print('form err: ', customer_form.errors)

    else:
        customer_form = CustomerForm(instance=enrollment_obj.customer)

    return render(request, 'crm/enrollment.html', locals())


@csrf_exempt
def enrollment_fileupload(request, enrollment_id):
    """
    接收学员上传的证件
    :param request:
    :param enrollment_id:
    :return:
    """

    ret = {'status': False, 'error': None, 'message': None}

    # 文件对象
    file_obj = request.FILES.get('file')
    print(file_obj)

    # 上传文件存储路径，根据报名链接序号创建相应文件夹，以此不会冲突
    path = os.path.join(settings.CRM_FILE_UPLOAD_DIR, enrollment_id)

    if not os.path.exists(path):
        os.mkdir(path)

    # 如果这个目录下文件数量大于 2 ，就限制其上传
    if len(os.listdir(path)) <= 2:
        with open(os.path.join(path, file_obj.name), 'wb') as f:
            for chunks in file_obj.chunks():
                f.write(chunks)
                ret['status'] = True
                ret['message'] = '上传成功！'

    else:
        ret['error'] = '最多只能上传两个文件！'

    return HttpResponse(json.dumps(ret))
