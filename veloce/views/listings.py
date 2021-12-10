import os, json
from django.conf import settings
from django.contrib import messages
from django.db.models import Max, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from veloce.decorators import level_required
from veloce import validators
from veloce import models
from veloce import forms, methods
from django.contrib.auth.models import User
from datetime import datetime, timezone
from django.core.exceptions import ValidationError

REQUIRED_LEVEL = True


@login_required
@level_required(REQUIRED_LEVEL)
def dashboard(request):
    return render(request, 'veloce/layout/dashboard.html')


@login_required
@level_required(REQUIRED_LEVEL)
def products_listing(request):
    all_product = models.Product.objects.filter(vendor_id=request.user.id)
    return render(request, 'veloce/products/products-list.html', {'product_data': all_product})


@login_required
@level_required(REQUIRED_LEVEL)
def product_detail(request, pk):
    product_details = get_object_or_404(models.Product, vendor_id=request.user.id, pk=pk)
    return render(request, 'veloce/products/product-detail-page.html', {'product': product_details})


def check_file_ext(req):
    validate_file_ext = True
    valid_extensions_image = ['.jpg', '.jpeg', '.png', '.gif']
    valid_extensions_video = ['.mp4', '.mov', '.avi', '.wmv']
    error = ''
    image_video_dict = req.FILES.keys()
    if 'image' in image_video_dict and 'demo_video' in image_video_dict:
        image_ext = True
        for field_name in req.FILES.keys():
            for formField in req.FILES.getlist(field_name):
                if field_name == 'image':
                    ext_image = formField.name.split('.')[1]
                    file_ext_image = "." + ext_image
                    if file_ext_image not in valid_extensions_image:
                        image_ext = False
                        error = "Invalid file extension!, Please select from " + ', '.join(valid_extensions_image)

                elif field_name == 'demo_video':
                    ext_video = formField.name.split('.')[1]
                    file_ext_video = "." + ext_video
                    if file_ext_video not in valid_extensions_video:
                        validate_file_ext = False
                        if not image_ext:
                            error = mark_safe(
                                "Invalid image and video extension!<br><br> Please select image from" + ', '.join(
                                    valid_extensions_image) + " <br> Please select video from" + ', '.join(
                                    valid_extensions_video))
                            break
                        else:
                            error = "Invalid video extension!, Please select from " + ', '.join(valid_extensions_video)
                            break
                    if not image_ext:
                        validate_file_ext = False
                        error = "Invalid image extension!, Please select from " + ', '.join(valid_extensions_image)
                        break
            if not validate_file_ext:
                break
    elif 'image' in image_video_dict:
        for field_name in req.FILES.keys():
            for formField in req.FILES.getlist(field_name):
                if field_name == 'image':
                    ext_image = formField.name.split('.')[1]
                    file_ext_image = "." + ext_image
                    if file_ext_image not in valid_extensions_image:
                        validate_file_ext = False
                        error = "Invalid file extension!, Please select from " + ', '.join(valid_extensions_image)
                        break
            if not validate_file_ext:
                break
    elif 'demo_video' in image_video_dict:
        for field_name in req.FILES.keys():
            for formField in req.FILES.getlist(field_name):
                if field_name == 'demo_video':
                    ext_video = formField.name.split('.')[1]
                    file_ext_video = "." + ext_video
                    if file_ext_video not in valid_extensions_video:
                        validate_file_ext = False
                        error = "Invalid video extension!"
                        break
            if not validate_file_ext:
                break

    else:
        validate_file_ext = True
    context = {
        "status": validate_file_ext,
        "message": error
    }
    return context


@login_required
@level_required(REQUIRED_LEVEL)
def create_product(request):
    error = ''
    if request.method == 'POST':
        product_form = forms.ProductForm(request.POST, request.FILES)
        price_form = forms.PriceStructureForm(request.POST)
        get_file_check_status = check_file_ext(request)
        if get_file_check_status['status']:
            if product_form.is_valid() and price_form.is_valid():
                product = product_form.save(commit=False)
                product.vendor = request.user
                product.save()
                product_form.save_m2m()
                for field_name in request.FILES.keys():
                    for formField in request.FILES.getlist(field_name):
                        if field_name == 'image':
                            models.ProductMedia.objects.create(image=formField, product=product)
                        elif field_name == 'demo_video':
                            models.ProductMedia.objects.create(demo_video=formField, product=product)
                check_for_price = len(request.POST.getlist('frequency'))
                if check_for_price > 0:
                    for i in range(check_for_price):
                        amt_before_tax = int(request.POST.getlist('amount')[i]) - int(
                            (request.POST.getlist('disc_amt')[i]))
                        models.PriceStructure.objects.create(product=product,
                                                             frequency=request.POST.getlist('frequency')[i],
                                                             label=request.POST.getlist('label')[i],
                                                             amount=request.POST.getlist('amount')[i],
                                                             disc_per=request.POST.getlist('disc_per')[i],
                                                             disc_amt=request.POST.getlist('disc_amt')[i],
                                                             amt_before_tax=amt_before_tax,
                                                             taxes=request.POST.getlist('taxes')[i],
                                                             final_amt=request.POST.getlist('final_amt')[i],
                                                             currency=request.POST.getlist('currency')[i],
                                                             is_visible_home=0)
                else:
                    pass
                if "is_this_physical_product" in request.POST and request.POST['is_this_physical_product']:
                    delivery_form = forms.ProductDeliveryForm(request.POST, request.FILES)
                    product_delivery = delivery_form.save(commit=False)
                    product_delivery.product = product
                    product_delivery.save()
                messages.success(request, "Product add successfully!")
                return redirect('products_listing')
        else:
            error = get_file_check_status['message']
    else:
        product_form = forms.ProductForm()
        price_form = forms.PriceStructureForm()
    return render(request, 'veloce/products/create-product.html',
                  {'form': product_form, 'price_form': price_form, 'error': error})


@login_required
@level_required(REQUIRED_LEVEL)
def edit_product(request, pk):
    get_product_obj = get_object_or_404(models.Product, pk=pk)
    check_product_delivery = models.PackagingDeliveryDetails.objects.filter(product=get_product_obj)
    price_form_lst = []
    af_sales = None
    af_warranty = None
    error = ''
    for price_obj in get_product_obj.product_prices.all():
        price_form = forms.PriceStructureForm(instance=price_obj)
        price_form_lst.append(price_form)
    if get_product_obj.vendor == request.user:
        if request.method == 'POST':
            form = forms.ProductEditForm(request.POST, instance=get_product_obj)
            get_file_check_status = check_file_ext(request)
            if get_file_check_status['status']:
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^", request.POST)
                if form.is_valid():
                    # print("^^^^^^^^^^^^^^^^^^^^^^^^^^", request.FILES)
                    product = form.save(commit=True)
                    product.vendor = request.user
                    product.save()
                    # form.save_m2m()
                    for field_name in request.FILES.keys():
                        for formField in request.FILES.getlist(field_name):
                            if field_name == 'image':
                                models.ProductMedia.objects.create(image=formField, product=product)
                            elif field_name == 'demo_video':
                                models.ProductMedia.objects.create(demo_video=formField, product=product)
                    check_for_price = len(request.POST.getlist('frequency'))
                    if check_for_price > 0:
                        for price_obj in get_product_obj.product_prices.all():
                            price_obj.delete()
                        for i in range(check_for_price):
                            amt_before_tax = int(request.POST.getlist('amount')[i]) - int(
                                (request.POST.getlist('disc_amt')[i]))
                            models.PriceStructure.objects.create(product=product,
                                                                 frequency=request.POST.getlist('frequency')[i],
                                                                 label=request.POST.getlist('label')[i],
                                                                 amount=request.POST.getlist('amount')[i],
                                                                 disc_per=request.POST.getlist('disc_per')[i],
                                                                 disc_amt=request.POST.getlist('disc_amt')[i],
                                                                 amt_before_tax=amt_before_tax,
                                                                 taxes=request.POST.getlist('taxes')[i],
                                                                 final_amt=request.POST.getlist('final_amt')[i],
                                                                 currency=request.POST.getlist('currency')[i])

                    if "is_this_physical_product" in request.POST and request.POST['is_this_physical_product']:
                        if check_product_delivery.count() > 0:
                            product_delivery_obj = models.PackagingDeliveryDetails.objects.get(product=get_product_obj)
                            delivery_form = forms.ProductDeliveryForm(request.POST, request.FILES,
                                                                      instance=product_delivery_obj)
                            product_delivery = delivery_form.save(commit=False)
                            product_delivery.product = product
                            product_delivery.save()
                        else:
                            delivery_form = forms.ProductDeliveryForm(request.POST, request.FILES)
                            product_delivery = delivery_form.save(commit=False)
                            product_delivery.product = product
                            product_delivery.save()
                    else:
                        if check_product_delivery.count() > 0:
                            check_product_delivery.delete()
                    messages.success(request, get_product_obj.name + " updated successfully!")
                    return redirect('products_listing')
            else:
                error = get_file_check_status['message']
        else:
            form = forms.ProductEditForm(instance=get_product_obj)
            af_sales = get_product_obj.after_sales_service_provided
            af_warranty = get_product_obj.after_warranty_service
        return render(request, 'veloce/products/create-product.html',
                      {'form': form, 'price_form_list': price_form_lst, 'af_sales': af_sales,
                       'af_warranty': af_warranty, 'error': error, 'pk': pk})
    else:
        messages.error(request, mark_safe("<b>Access Denied!</b> You are not a valid user for the entered url !"))
        return redirect('products_listing')


@login_required
@level_required(REQUIRED_LEVEL)
def delete_product(request, pk):
    get_product_obj = get_object_or_404(models.Product, pk=pk)
    if get_product_obj.vendor == request.user:
        product_name = get_product_obj.name.title()
        product_media_instance = models.ProductMedia.objects.filter(product_id=pk)
        for media in product_media_instance:
            if os.path.exists(str(media.image)):
                if media.image:
                    os.remove(str(media.image))
                if media.demo_video:
                    os.remove(str(media.demo_video))
            else:
                print("File not exist")
        product_media_instance.delete()
        get_product_obj.delete()
        messages.success(request, product_name + " is deleted successfully!")
        return redirect('products_listing')
    else:
        messages.warning(request, mark_safe("<b>Access Denied!</b> You are not a valid user for the entered url !"))
        return redirect('products_listing')


def get_price_form(request):
    form = forms.PriceStructureForm()
    context = {
        'form': form.as_p()
    }
    return JsonResponse(context)


def get_product_delivery_form(request):
    form = forms.ProductDeliveryForm()
    context = {
        'form': form.as_p()
    }
    return JsonResponse(context)


@login_required
@level_required(REQUIRED_LEVEL)
def make_image_as_feature_img(request, pk):
    try:
        get_images_data = models.ProductMedia.objects.get(pk=pk)
        product_obj = get_images_data.product
        models.ProductMedia.objects.filter(product=product_obj).update(is_feature_image=0)
        get_images_data.is_feature_image = True
        get_images_data.save()
        context = {
            "status": True
        }
    except Exception as err:
        context = {
            "status": False
        }
    return JsonResponse(context)


@login_required
def get_sub_categories_by_cat_id(request):
    try:
        sub_cat_list = []
        cat_id = request.GET['cat_id']
        sub_categories = models.SubCategory.objects.filter(category_id=cat_id)
        for data in sub_categories:
            cat_context = {
                'id': data.id,
                'name': data.name
            }
            sub_cat_list.append(cat_context)
        html = '<option value selected>---------</option>'
        for item in sub_cat_list:
            html += '<option value="{0}">{1}</option>'.format(item['id'], item['name'])
        context = {
            "status": True,
            'sub_category': html
        }
    except Exception as e:
        context = {
            "status": False
        }
    return JsonResponse(context)


@login_required
def get_delivery_detail_by_product_id(request):
    try:
        product_id = request.GET['product_id']
        product_delivery_obj = models.PackagingDeliveryDetails.objects.filter(product_id=product_id)
        if product_delivery_obj.count() > 0:
            context = {
                "status": True,
                "data": list(product_delivery_obj.values())
            }
            return JsonResponse(context, safe=False)
        else:
            context = {
                "status": False
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False
        }
        return JsonResponse(context)


@login_required
def inquiry_lists(request):
    if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
        my_product_inquiries = models.ProductInquiry.objects.filter(product__vendor=request.user)
        my_inquiries = models.ProductInquiry.objects.filter(inquiry_by=request.user)
        upload_bill_info = models.ProductInquiry.objects.filter(is_product_bill_generated=True,
                                                                product__vendor=request.user)
        bill_discount_url = settings.FINTECH_URL + "/application/bill/new/loan"
        if request.method == "POST":
            inq_id = request.POST['inquiry']
            book_sale_detail_form = forms.BookSalesDetailsForm(request.POST)
            print("ajax-----------------------", book_sale_detail_form)
            form = forms.BookSalesForm(request.POST, request.FILES)
            if form.is_valid():
                if book_sale_detail_form.is_valid():
                    b_sale_form = form.save(commit=False)
                    b_sale_form.save()
                    models.ProductInquiry.objects.filter(id=inq_id).update(is_product_bill_generated=True)
                    book_sale_detail_frm = book_sale_detail_form.save(commit=False)
                    book_sale_detail_frm.book_sale = b_sale_form
                    book_sale_detail_frm.save()
                    try:
                        current_sale = models.BookSale.objects.get(id=b_sale_form.id)
                        get_buyer = User.objects.get(email=request.POST['inquired_by'])
                        get_bill_amt = int(request.POST['bill_amount'])
                        now = datetime.now(timezone.utc)
                        check_special_reward_exists = models.SpecialRewardPoints.objects.filter(
                            gen_reward_end_date__gte=now)
                        if check_special_reward_exists.count() > 0:
                            check_if_dealer_reward_exists = models.SpecialRewardPoints.objects.filter(
                                reward_to_dealer=request.user, reward_product=current_sale.inquiry.product)
                            if check_if_dealer_reward_exists.count() > 0:
                                get_spl_dealer_reward = models.SpecialRewardPoints.objects.get(
                                    reward_to_dealer=request.user)
                                get_spl_dealer_reward_point = (
                                                                      get_bill_amt * get_spl_dealer_reward.dealer_reward_point) / 100
                                get_spl_customer_reward_point = (
                                                                        get_bill_amt * get_spl_dealer_reward.customer_reward_point) / 100
                                models.TransactionRewardDetails.objects.create(book_sale=b_sale_form,
                                                                               dealer_rewards_id=request.user.id,
                                                                               dealer_reward_point=get_spl_dealer_reward_point,
                                                                               customer_rewards_id=get_buyer.id,
                                                                               customer_reward_point=get_spl_customer_reward_point)
                            else:
                                check_general_reward_exists = models.GeneralRewardPoints.objects.filter(
                                    gen_reward_end_date__gte=now)
                                if check_general_reward_exists.count() > 0:
                                    get_general_reward = models.GeneralRewardPoints.objects.all()
                                    get_spl_dealer_reward_point = (get_bill_amt * get_general_reward[
                                        0].dealer_reward_point) / 100
                                    get_spl_customer_reward_point = (get_bill_amt * get_general_reward[
                                        0].customer_reward_point) / 100
                                    models.TransactionRewardDetails.objects.create(book_sale=b_sale_form,
                                                                                   dealer_rewards_id=request.user.id,
                                                                                   dealer_reward_point=get_spl_dealer_reward_point,
                                                                                   customer_rewards_id=get_buyer.id,
                                                                                   customer_reward_point=get_spl_customer_reward_point)
                                else:
                                    pass
                        else:
                            check_general_reward_exists = models.GeneralRewardPoints.objects.filter(
                                gen_reward_end_date__gte=now)
                            if check_general_reward_exists.count() > 0:
                                get_general_reward = models.GeneralRewardPoints.objects.all()
                                get_spl_dealer_reward_point = (get_bill_amt * get_general_reward[
                                    0].dealer_reward_point) / 100
                                get_spl_customer_reward_point = (get_bill_amt * get_general_reward[
                                    0].customer_reward_point) / 100
                                models.TransactionRewardDetails.objects.create(book_sale=b_sale_form,
                                                                               dealer_rewards_id=request.user.id,
                                                                               dealer_reward_point=get_spl_dealer_reward_point,
                                                                               customer_rewards_id=get_buyer.id,
                                                                               customer_reward_point=get_spl_customer_reward_point)
                            else:
                                pass
                    except Exception as e:
                        print("Error -> " + str(e))
                else:
                    print("working-------------------------")
        else:
            form = forms.BookSalesForm()
        return render(request, 'veloce/products/inquiry-lists.html',
                      {'my_product_inquiries': my_product_inquiries, 'my_inquiries': my_inquiries,
                       'upload_bill_info': upload_bill_info, 'form': form, 'bill_discount_url': bill_discount_url})
    else:
        # messages.warning(request, "Not eligible for inquiry!")
        return redirect('index')


@login_required
def validate_promo_code(request):
    try:
        product_id = request.GET['product_id']
        coupon_code = request.GET['coupon_code']
        check_coupon_exist = models.Voucher.objects.filter(product_id=product_id)
        if check_coupon_exist.count() > 0:
            if check_coupon_exist.filter(discount_code__exact=coupon_code).count() > 0:
                get_max_price_val = models.PriceStructure.objects.filter(product_id=product_id).aggregate(Max('amount'))
                get_coupon_data = models.Voucher.objects.get(product_id=product_id, discount_code__iexact=coupon_code)
                mas = ''
                discount_type = 1
                value = 0
                if get_coupon_data.discount_type == 1:  # for percentage
                    amount = (get_max_price_val['amount__max'] * get_coupon_data.value) / 100
                    msg = "You got " + str(get_coupon_data.value) + "% discount !"
                    discount_type = 1
                    value = get_coupon_data.value
                else:
                    amount = (get_max_price_val['amount__max'] - get_coupon_data.value)
                    msg = "You got " + str(get_coupon_data.value) + "discount !"
                    discount_type = 2
                    value = get_coupon_data.value
                context = {
                    "status": True,
                    "amx_amt": get_max_price_val['amount__max'] - amount,
                    "msg": msg,
                    "value": value,
                    "discount_type": discount_type
                }
                return JsonResponse(context, safe=False)
            else:
                context = {
                    "status": False,
                    "msg": "Invalid coupon code !"
                }
                return JsonResponse(context)
        else:
            context = {
                "status": False,
                "msg": "This product has no coupon code !"
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def get_max_price(request):
    try:
        product_id = request.GET['product_id']
        get_max_price_val = models.PriceStructure.objects.filter(product_id=product_id)
        if get_max_price_val.count() > 0:
            amount__max = get_max_price_val.aggregate(Max('amount'))
            context = {
                "status": True,
                "amx_amt": amount__max['amount__max'],
                "all_price": list(get_max_price_val.values('amount'))
            }
            return JsonResponse(context)
        else:
            context = {
                "status": False,
                "msg": "No data found!"
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def get_borrowers_lists(request):
    try:
        borrowers = models.BookSale.objects.filter(is_loan_approved=False)
        html = ''
        for borrower in borrowers:
            html += '<option value="{0}-{1}">{2}</option>'.format(borrower.id, borrower.inquiry.inquiry_by,
                                                                  borrower.inquiry.inquiry_by)
        context = {
            "status": True,
            "data": html
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def get_borrower_details(request):
    try:
        borrower_dict = {}
        inq_id = request.GET['inq_id'].split('-')[0]
        borrower_details = models.BookSale.objects.get(pk=inq_id)
        borrower_dict['bill_no'] = borrower_details.bill_no
        borrower_dict['bill_date'] = borrower_details.bill_date
        borrower_dict['bill_amount'] = borrower_details.bill_amount
        borrower_dict['bill_due_date'] = borrower_details.bill_due_date
        borrower_dict['billing_party_name'] = borrower_details.billing_party_name
        borrower_dict['inquired_by'] = borrower_details.inquired_by
        context = {
            "status": True,
            "data": borrower_dict
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def check_bill_no_exists(request):
    try:
        bill_no = request.GET['bill_no']
        if models.BookSale.objects.filter(bill_no=bill_no).count() > 0:
            context = {
                "status": False,
                "data": str(bill_no) + " bill number already exists !!!"
            }
            return JsonResponse(context)
        else:
            context = {
                "status": True
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def get_reward_point(request):
    dealer_rewards = models.TransactionRewardDetails.objects.filter(dealer_rewards=request.user)
    customer_rewards = models.TransactionRewardDetails.objects.filter(customer_rewards=request.user)
    return render(request, 'veloce/products/reward-lists.html',
                  {'dealer_rewards': dealer_rewards, 'customer_rewards': customer_rewards})


@login_required
def dealers_scheme_list(request):
    current_date = datetime.now(timezone.utc)
    current_date = current_date.strftime('%Y-%m-%d %H:%M:%S')
    if validators.check_user_level_and_has_product(request.user):
        dealer_scheme_lists = models.DealersGivenFinanceScheme.objects.filter(dealer=request.user)
        return render(request, 'veloce/products/product-scheme-lists.html',
                      {'dealer_scheme_lists': dealer_scheme_lists, 'current_date': current_date})
    else:
        return redirect('index')


@login_required
def dealers_scheme_create(request):
    product_list = []
    current_date = datetime.now()
    current_date = datetime.strftime(current_date, '%Y-%m-%d %H:%M:%S')
    valid_scheme = False
    if validators.check_user_level_and_has_product(request.user):
        form = forms.SalersGivenFinanceSchemeForm()
        scheme_obj = models.DealersGivenFinanceScheme.objects.filter(dealer=request.user, is_active=True)
        form.fields['product'].queryset = models.Product.objects.filter(vendor=request.user)
        if request.method == "POST":
            request.POST._mutable = True
            request.POST['start_date'] = datetime.strptime(request.POST['start_date'], '%Y-%m-%d %H:%M %p')
            request.POST['end_date'] = datetime.strptime(request.POST['end_date'], '%Y-%m-%d %H:%M %p')
            request.POST._mutable = False
            form = forms.SalersGivenFinanceSchemeForm(request.POST)
            for data in scheme_obj:
                end_date = data.end_date
                end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
                if end_date > current_date:
                    product_list.append(data.product)
                if valid_scheme:
                    valid_scheme = True if data.start_date <= request.POST['start_date'] >= data.end_date else False
            res = [x for x in request.POST.getlist('product') if x in product_list]
            if form.is_valid():
                if len(res) > 0 and valid_scheme:
                    form.fields['product'].queryset = models.Product.objects.filter(vendor=request.user)
                    form._errors['product'] = ['Scheme with this product already exists/active.']
                else:
                    for product in request.POST.getlist('product'):
                        scheme = models.DealersGivenFinanceScheme.objects.create(
                            product=product,
                            rate_of_interest=request.POST['rate_of_interest'],
                            tenure=request.POST['tenure'],
                            start_date=request.POST['start_date'],
                            end_date=request.POST['end_date'],
                            is_active=True if request.POST['is_active'] == 'on' else False,
                            dealer=request.user
                        )
                        # scheme = form.save(commit=False)
                        scheme.dealer = request.user
                        scheme.save()
                    messages.success(request, 'Finance Scheme created successfully!')
                    return redirect('dealers_scheme_list')
            else:
                form.fields['product'].queryset = models.Product.objects.filter(vendor=request.user)
        return render(request, 'veloce/products/product-scheme-create.html', {'form': form})
    else:
        return redirect('index')


@login_required
def dealers_scheme_edit(request, id):
    if validators.check_user_level_and_has_product(request.user):
        product_name = ''
        expired = False
        current_date = datetime.now()
        current_date = datetime.strftime(current_date, '%Y-%m-%d %H:%M:%S')
        get_scheme_obj = models.DealersGivenFinanceScheme.objects.get(pk=id, dealer=request.user)
        product_details = models.Product.objects.get(id=get_scheme_obj.product)
        product_list = models.DealersGivenFinanceScheme.objects.filter(dealer=request.user, product=get_scheme_obj.product, is_active=True).exclude(pk=id)
        print("#####################", product_list)
        product_name = product_details.name
        end_date = get_scheme_obj.end_date
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        expired = True if end_date < current_date else False
        expired_scheme = methods.auth.get_active_scheme(product_list)
        print("#####################", product_list)
        product_list = product_list.exclude(id__in=expired_scheme)
        print(product_list, "***********", expired_scheme)
        if request.method == "POST":
            form = forms.SalersGivenFinanceSchemeEditForm(request.POST, instance=get_scheme_obj)
            form.fields['rate_of_interest'].disabled = True
            form.fields['tenure'].disabled = True
            form.fields['product'].disabled = True
            form.fields['start_date'].disabled = True
            form.fields['end_date'].disabled = True
            request.POST._mutable = True
            form.fields['product'].initial = request.POST.getlist('product')
            request.POST._mutable = False
            if form.is_valid():
                if len(product_list) > 0 and request.POST.get('is_active') == 'on':
                    form._errors['is_active'] = ['Scheme with this product is already active.']
                else:
                    is_active = True if request.POST.get('is_active') == 'on' else False
                    models.DealersGivenFinanceScheme.objects.filter(pk=id, dealer=request.user).update(is_active=is_active)
                    messages.success(request, 'Finance Scheme for %s product edited successfully!' % product_name)
                    return redirect('dealers_scheme_list')
        else:
            form = forms.SalersGivenFinanceSchemeEditForm(instance=get_scheme_obj)
            form.fields['product'].queryset = models.Product.objects.filter(vendor=request.user)
            form.fields['rate_of_interest'].disabled = True
            form.fields['tenure'].disabled = True
            form.fields['product'].disabled = True
            form.fields['start_date'].disabled = True
            form.fields['end_date'].disabled = True
            if expired:
                form.fields['is_active'].disabled = True
        return render(request, 'veloce/products/product-scheme-create.html', {'form': form, 'expired': expired})
    else:
        return redirect('index')


@login_required
def dealers_scheme_delete(request, id):
    if validators.check_user_level_and_has_product(request.user):
        try:
            product_name = ''
            get_scheme_obj = models.DealersGivenFinanceScheme.objects.get(pk=id, dealer=request.user)
            product = models.Product.objects.get(id=get_scheme_obj.product)
            product_name = product.name
            get_scheme_obj.delete()
            messages.success(request, 'Finance Scheme for %s product deleted successfully!' % product_name)
            return redirect('dealers_scheme_list')
        except models.DealersGivenFinanceScheme.DoesNotExist:
            messages.error(request, 'Finance Scheme with %s id is not exists!' % id)
            return redirect('dealers_scheme_list')
        except Exception as e:
            messages.error(request, 'Something went wrong!')
            return redirect('dealers_scheme_list')
    else:
        return redirect('index')


@login_required
def check_scheme_exists(request):
    try:
        product_id = request.GET['product_id']
        scheme_data = models.DealersGivenFinanceScheme.objects.filter(product=product_id, dealer=request.user,
                                                                      is_admin_approved=True, is_active=True)
        start_date = datetime.strftime(scheme_data[0].start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strftime(scheme_data[0].start_date, '%Y-%m-%d %H:%M:%S')
        print("^^^^^^^^^^^^^^^^^^^^^", scheme_data)
        if scheme_data.exists():
            context = {
                "status": True,
                'scheme_value': "<option value=" + str(scheme_data[0].id) + ">" + str(
                    scheme_data[0].rate_of_interest) + "%, " + str(scheme_data[0].tenure) + " months</option>",
                'started_date': start_date,
                'ended_date': end_date
            }
            print(context, "context")
            return JsonResponse(context)
        else:
            context = {"status": False}
            return JsonResponse(context)
    except Exception as e:
        context = {"status": False}
        print(e)
        return JsonResponse(context)


def about_veloce_market(request):
    context = {"status": True, }
    return render(request, 'veloce/content/about-veloce-market.html')


def how_veloce_market_work(request):
    context = {"status": True, }
    return render(request, 'veloce/content/how-veloce-market-work.html')


def faqs_ftr(request):
    context = {"status": True, }
    return render(request, 'veloce/content/faqs-ftr.html')


def buy_sell(request):
    context = {"status": True, }
    return render(request, 'veloce/content/buy-sell.html')


def equipment_finance(request):
    context = {"status": True, }
    return render(request, 'veloce/content/equipment-finance.html')


def bill_finance(request):
    context = {"status": True, }
    return render(request, 'veloce/content/bill-finance.html')


def testimonials(request):
    context = {"status": True, }
    return render(request, 'veloce/content/testimonials.html')


def contactus(request):
    context = {"status": True, }
    return render(request, 'veloce/content/contact-us.html')


def terms_of_use(request):
    context = {"status": True, }
    return render(request, 'veloce/content/terms-of-use.html')


def privacy_security_policy(request):
    context = {"status": True, }
    return render(request, 'veloce/content/privacy-security-policy.html')


def grievance_redressal(request):
    context = {"status": True, }
    return render(request, 'veloce/content/grievance-redressal.html')


def fair_practices_code(request):
    context = {"status": True, }
    return render(request, 'veloce/content/fair-practices-code.html')


def rbi_guidelines_disclaimer(request):
    context = {"status": True, }
    return render(request, 'veloce/content/rbi-guidelines-disclaimer.html')


def support(request):
    context = {"status": True, }
    return render(request, 'veloce/content/support.html')


def fb_text(request):
    return render(request, 'veloce/content/fb.html')


@login_required
def compare_product(request):
    sub_categories = []
    if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
        all_category = models.Category.objects.all()
        for cat in all_category:
            sub_categories += models.SubCategory.objects.filter(category_id=cat.id)
        products = models.Product.objects.all()
        return render(request, 'veloce/products/compare-products.html',
                      {'products': products, 'all_category': all_category, 'sub_category':sub_categories})
    else:
        messages.warning(request, "To compare product you must have to complete at least 1 level.")
        return redirect('index')


@login_required
def get_product_by_sub_cat(request):
    try:
        if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
            sub_cat_product_list = []
            sub_cat_id = request.GET['sub_cat_id']
            sub_categories_product = models.Product.objects.filter(sub_category_id=sub_cat_id)
            for data in sub_categories_product:
                cat_context = {
                    'id': data.id,
                    'name': data.name
                }
                sub_cat_product_list.append(cat_context)
            # html = '<option value selected>---------</option>'
            # for item in sub_cat_product_list:
            #     html += '<option value="{0}">{1}</option>'.format(item['id'], item['name'])
            context = {
                "status": True,
                'sub_category_products': sub_cat_product_list
            }
        else:
            messages.warning(request, "To compare product you must have to complete at least 1 level.")
            return redirect('index')
    except Exception as e:
        context = {
            "status": False
        }
    return JsonResponse(context)


@login_required
def get_product_by_ids(request):
    try:
        if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
            product_ids = request.GET['id']
            all_product = models.Product.objects.filter(id=product_ids)
            html = ''
            for item in all_product:
                html = str(item.product_media.all().first().image.name[6:])
                name = item.name
            compare_lnk = None
            # if len(product_ids) == 2:
            #     compare_lnk = '<a class="btn btn-primary w-25" href="/compare_products_details?p1={0}&p2={1}">Compare</a>'.format(
            #         product_ids[0], product_ids[1])
            # elif len(product_ids) == 3:
            #     print("product length3", product_ids)
            #     compare_lnk = '<a class="btn btn-primary w-25" href="/compare_products_details?p1={0}&p2={1}&p3={2}">Compare</a>'.format(
            #         product_ids[0], product_ids[1], product_ids[2])
            # else:
            #     compare_lnk = None
            context = {
                "status": True,
                'products': html,
                'name': name,
                'id': product_ids,
                'compare_url': compare_lnk
            }
        else:
            messages.warning(request, "To compare product you must have to complete at least 1 level.")
            return redirect('index')
    except Exception as e:
        print(e)
        context = {
            "status": False
        }
    return JsonResponse(context)


@login_required
def compare_products_details(request):
    try:
        if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
            if 'p1' in request.GET and 'p2' in request.GET:
                get_product1_jd = request.GET['p1']
                get_product2_jd = request.GET['p2']
                if 'p3' in request.GET:
                    get_product3_jd = request.GET['p3']
                    product3_details = models.Product.objects.get(id=get_product3_jd)
                    product3_img = product3_details.product_media.all().first().image.name[6:]
                else:
                    product3_details = ''
                    product3_img = ''

                product1_details = models.Product.objects.get(id=get_product1_jd)
                product1_img = product1_details.product_media.all().first().image.name[6:]
                product2_details = models.Product.objects.get(id=get_product2_jd)
                product2_img = product2_details.product_media.all().first().image.name[6:]
                return render(request, 'veloce/products/compare-product-lists.html',
                              {'product1_details': product1_details, 'product2_details': product2_details,
                              'product3_details': product3_details,'product1_img': product1_img,
                              'product2_img': product2_img, 'product3_img': product3_img})
            else:
                messages.error(request, "Select at least two products for comparison!")
                return redirect('compare_product')
        else:
            messages.warning(request, "To compare product you must have to complete at least 1 level.")
            return redirect('index')
    except Exception as e:
        print("^^^^^^^^^^^^", e)
        return redirect('compare_product')

@login_required
def delete_image_by_id(request):
    col_id = request.GET['id']
    delete_from_model = request.GET['delete_from_model']
    print(col_id, delete_from_model)
    try:
        if delete_from_model == 'product':
            img = models.ProductMedia.objects.get(id=col_id).delete()
        else:
            bill = models.BookSale.objects.get(inquiry_id=col_id).upload_bill.delete(save=False)
    except:
        pass

    context = {
        "status": True,
        "id": col_id,
    }
    return JsonResponse(context)

def delete_bill_upload_by_id(request):
    inq_id = request.GET['inq_id']
    try:
        bill = models.BookSale.objects.get(inquiry_id=inq_id).upload_bill.delete(save=True)
    except:
        pass
    context = {
        "status": True,
        "id": inq_id,
    }
    return JsonResponse(context)

@login_required()
def get_bill_details(request):
    try:
        import json
        bill_id = request.GET['bill_id']
        get_bill_detail = models.BookSale.objects.filter(inquiry__product__vendor=request.user, id=bill_id).values(
            'inquiry', 'bill_no', 'bill_date', 'bill_amount', 'billing_party_name', 'inquired_by', 'dealer_gst_no',
            'billing_party_gst_no', 'upload_bill', 'dealers_given_finance_scheme', 'inquiry__product__name')[0]
        print(get_bill_detail)
        context = {
            "status": True,
            "data": get_bill_detail
        }
    except Exception as e:
        context = {
            "status": False,
            "error": str(e)
        }
    return JsonResponse(context)


@login_required()
def edit_uploaded_bill(request, id):
    try:
        if validators.check_user_level_and_has_product(request.user):
            get_bill_detail = models.BookSale.objects.get(inquiry__product__vendor=request.user, id=id)
            scheme = models.DealersGivenFinanceScheme.objects.filter(dealer=request.user, product=get_bill_detail.inquiry.product.id, is_active=True)
            book_sale_details = models.BookSaleDetails.objects.get(book_sale=get_bill_detail)
            product_inquiries = models.ProductInquiry.objects.get(id=get_bill_detail.inquiry.id)
            schemes = models.DealersGivenFinanceScheme.objects.filter(dealer=request.user,
                                                                      product=product_inquiries.product.id,
                                                                      is_active=True, is_admin_approved=True)
            expired_products = methods.auth.get_active_scheme(schemes)
            product_expired_scheme = schemes.exclude(id__in=expired_products)
            print()
            if request.method == "POST":
                get_bill_detail_form = forms.EditUploadedBillForm(request.POST, request.FILES, instance=get_bill_detail)
                if get_bill_detail.dealers_given_finance_scheme:
                    get_bill_detail_form.fields['dealers_given_finance_scheme'].queryset = models.DealersGivenFinanceScheme.objects.filter(id=get_bill_detail.dealers_given_finance_scheme.id)
                else:
                    get_bill_detail_form.fields['dealers_given_finance_scheme'].queryset = product_expired_scheme
                book_sale_detailsl_form = forms.EditBookSaleDetailsForm(request.POST, instance=book_sale_details)
                book_sale_detailsl_form.fields['ref_inq_no'].queryset = models.ProductInquiry.objects.filter(id=get_bill_detail.inquiry.id)
                if get_bill_detail_form.is_valid() and book_sale_detailsl_form.is_valid():
                    get_bill_detail_form.save()
                    book_sale_detailsl_form.save()
                    return redirect('inquiry_lists')
            else:
                book_sale_detailsl_form = forms.EditBookSaleDetailsForm(instance=book_sale_details)
                book_sale_detailsl_form.fields['ref_inq_no'].queryset = models.ProductInquiry.objects.filter(id=get_bill_detail.inquiry.id)
                get_bill_detail_form = forms.EditUploadedBillForm(instance=get_bill_detail)
                if get_bill_detail.dealers_given_finance_scheme:
                    get_bill_detail_form.fields['dealers_given_finance_scheme'].queryset = models.DealersGivenFinanceScheme.objects.filter(id=get_bill_detail.dealers_given_finance_scheme.id)
                else:
                    get_bill_detail_form.fields['dealers_given_finance_scheme'].queryset = product_expired_scheme
            return render(request, 'veloce/products/edit-uploaded-bill.html', {'get_bill_detail_form': get_bill_detail_form, 'book_sale_detailsl_form': book_sale_detailsl_form, 'bill_id': id, 'bill_no': get_bill_detail.bill_no, 'is_product_financed': product_inquiries.is_product_financed})
        else:
            messages.error(request, "Not eligible for vendor!")
            return redirect('index')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('inquiry_lists')


@login_required()
def bill_finance_details(request, id):
    finance_scheme = ''
    my_product_inquiries = models.ProductInquiry.objects.get(inquiry_by=request.user, id=id)
    get_bill_detail = models.BookSale.objects.get(inquiry=my_product_inquiries)
    book_sale_details = models.BookSaleDetails.objects.get(book_sale=get_bill_detail)
    print(my_product_inquiries, get_bill_detail, book_sale_details)
    if my_product_inquiries.is_product_financed:
        finance_scheme = methods.auth.get_finance_scheme_details_by_billno(request, get_bill_detail.bill_no, my_product_inquiries.inquiry_by)
    print(type(finance_scheme))
    return render(request, 'veloce/products/bill-finance-details.html', {'get_bill_detail': get_bill_detail, 'book_sale_details': book_sale_details, 'my_product_inquiries': my_product_inquiries, 'finance_scheme': finance_scheme})
