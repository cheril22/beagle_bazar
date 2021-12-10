import json
import datetime
from django.utils.timezone import get_current_timezone
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from veloce import models
from veloce import forms
from django.conf import settings
import requests
from django.contrib.auth.models import User
from django.contrib import messages

REQUIRED_LEVEL = True
def index(request):
    """
    this method return all list of featured products
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        if request.user.profile.account_type == 3:
            return redirect(settings.FINTECH_URL)
    featured_products = models.Product.objects.filter(is_featured_product=1)
    top_rated_products = models.Product.objects.order_by("?")[:8]
    return TemplateResponse(request, 'veloce/layout/home.html',
                            {'featured_products': featured_products, 'top_rated_products': top_rated_products,
                             'fintech_url': settings.FINTECH_URL + "/check-user-auth/",'OAUTH_URL':settings.OAUTH_URL})


def get_all_categories(request):
    """
    this method return all the categories for the products
    :param request:
    :return:
    """
    all_categories = models.Category.objects.all()
    return TemplateResponse(request, 'veloce/products/categories.html', {"all_categories": all_categories})


def get_all_sub_categories(request, slug):
    """
    this method will return all the subcgteory for the projects
    :param request:
    :param cat_id:
    :return:
    """
    get_category = models.Category.objects.get(slug__iexact=slug)
    return TemplateResponse(request, 'veloce/products/sub-categories.html', {"category": get_category})


def get_all_industry(request):
    """
    this method return all the industry for the products
    :param request:
    :return:
    """
    all_industry = models.Industry.objects.all()
    return TemplateResponse(request, 'veloce/products/all-industries.html', {"all_industry": all_industry})


def get_products(request, **kwargs):
    """
    this method get subcategory and display all the product related to it.
    :param request:
    :param cat_name:
    :return:
    """
    kwargs = {k: v for k, v in kwargs.items() if v}
    sub_cat_products = models.SubCategory.objects.get(slug__iexact=kwargs['sub_cat_slug'])
    return TemplateResponse(request, 'veloce/products/product-by-category.html', {"sub_cat_products": sub_cat_products})


def get_all_products_by_industry(request, industry_slug):
    """
    this method get subcategory and display all the product related to it.
    :param request:
    :param cat_name:
    :return:
    """
    industry_products = models.Industry.objects.get(slug__iexact=industry_slug)
    return TemplateResponse(request, 'veloce/products/product-by-industry.html',
                            {"industry_products": industry_products})


@login_required
def save_rating(request):
    try:
        if request.method == 'POST':
            product_id = request.POST['product']
            rated_value = request.POST['rated_value']
            message_val = request.POST['message']
            if product_id and rated_value and message_val:
                models.ProductRating.objects.create(product_id=product_id, rated_by_id=request.user.id,
                                                    rated_value=rated_value, message=message_val)
                context = {
                    "status": True
                }
                return JsonResponse(context)
            else:
                context = {
                    "status": False,
                    "message": "some fields are missing!"
                }
                return JsonResponse(context)
        else:
            product_id = request.GET['product_id']
            if product_id:
                get_product_rating = models.ProductRating.objects.filter(product_id=product_id, rated_by=request.user)
                if get_product_rating.count() > 0:
                    context = {
                        "status": True,
                        "product_id": get_product_rating[0].product.id,
                        "rated_value": get_product_rating[0].rated_value,
                        "message": get_product_rating[0].message,
                    }
                    return JsonResponse(context)
                else:
                    context = {
                        "status": False,
                        "message": "Something went wrong!"
                    }
                    return JsonResponse(context)
            else:
                context = {
                    "status": False,
                    "message": "some fields are missing!"
                }
                return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "message": "Product is not in stock!"
        }
        return JsonResponse(context)


@login_required
def edit_rating(request):
    try:
        if request.method == 'POST':
            product_id = request.POST['product']
            rated_value = request.POST['rated_value']
            message_val = request.POST['message']
            if product_id and rated_value and message_val:
                models.ProductRating.objects.filter(product_id=product_id, rated_by_id=request.user.id).update(
                    rated_value=rated_value, message=message_val)
                context = {
                    "status": True,
                    "data": "done!"
                }
                return JsonResponse(context)
            else:
                context = {
                    "status": False,
                    "message": "some fields are missing!"
                }
                return JsonResponse(context)
        else:
            context = {
                "status": False,
                "message": "Invalid Method"
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "message": str(e) + " Filed are missing!"
        }
        return JsonResponse(context)


def auto_complete_model(request):
    try:
        if request.method == "POST":
            term = request.POST['txtSearch']
            search_param = Q(name__icontains=term) | Q(brand_name__icontains=term) | Q(
                category__name__icontains=term) | Q(sub_category__name__icontains=term) | Q(place_of_origin__icontains=term) | Q(
                power_watt__icontains=term) | Q(warranty__icontains=term) | Q(condition__icontains=term)
            search_qs = models.Product.objects.filter(search_param).distinct()
            return TemplateResponse(request, 'veloce/products/search-products.html', {"searched_data": search_qs})
        else:
            term = request.GET['term']
            search_param = Q(name__icontains=term) | Q(brand_name__icontains=term) | Q(
                category__name__icontains=term) | Q(sub_category__name__icontains=term) | Q(place_of_origin__icontains=term) | Q(
                power_watt__icontains=term) | Q(warranty__icontains=term) | Q(condition__icontains=term)
            search_qs = models.Product.objects.filter(search_param).distinct()
            results = []
            for field in search_qs:
                results.append(field.name)
            data = json.dumps(results)
            mimetype = 'application/json'
            return HttpResponse(data, mimetype)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return redirect('index')



def product_details(request, slug):
    """Returns the rendered page for product details by generating a slug for each product page"""

    check_user_eligibility_level = 0
    if check_user_eligibility_level == 0:
        product_detail = get_object_or_404(models.Product, slug=slug)
        return TemplateResponse(request, 'veloce/products/product-detail-page.html', {'product': product_detail})
    else:
        return redirect(settings.FINTECH_URL + '/incomplete-profile')


def get_product_inquiry_form(request):
    try:
        form = forms.ProductInquiryForm()
        context = {
            'status': True,
            'form': form.as_p()
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            'status': False,
            'message': str(e)
        }
        return JsonResponse(context)


@login_required()
def save_inquiry(request):
    try:
        if request.user.profile.completion_level >= 1 and request.user.profile.verification_level >= 1:
            form = forms.ProductInquiryForm(request.POST)
            product_id = request.POST['product_id']
            if form.is_valid():
                if product_id != 'undefined' and product_id and len(product_id) > 0:
                    product = models.Product.objects.get(pk=product_id)
                    inquiry_form = form.save(commit=False)
                    inquiry_form.product = product
                    inquiry_form.inquiry_by = request.user
                    inquiry_form.save()
                    context = {
                        'status': True,
                        'message': " Your inquiry has been submitted successfully!"
                    }
                    print("working++++++++++++==", context)
                    return JsonResponse(context)
                else:
                    context = {
                        'status': False,
                        'message': {"product": " id is required!"}
                    }
                    return JsonResponse(context)
            else:
                context = {
                    'status': False,
                    'message': form.errors
                }
                return JsonResponse(context)
        else:
            context = {
                'status': False,
                'message': "You are not eligible to inquiry any product !!!"
            }
            return JsonResponse(context)
    except Exception as e:
        context = {
            'status': False,
            'message': str(e)
        }
        return JsonResponse(context)

@login_required
def get_all_rating_by_id(request, id):
    """Returns the rendered page for product details by generating a slug for each product page"""

    check_user_eligibility_level = models.Profile.objects.get(user_id=request.user.id)
    if check_user_eligibility_level.completion_level >= 1 and check_user_eligibility_level.verification_level >= 1:
        product_detail = get_object_or_404(models.Product, id=id)
        ratings = models.ProductRating.objects.filter(product=product_detail)
        print(ratings, "_______________________")
        # check_already_visited = models.RecentlyVisited.objects.filter(user=request.user, product_id=product_detail.id)
        # if check_already_visited.exists():
        #     counter_val = check_already_visited[0].visit_counter + 1
        #     check_already_visited.update(last_visited=datetime.datetime.now(tz=get_current_timezone()), visit_counter=counter_val)
        # else:
        #     models.RecentlyVisited.objects.create(user=request.user, visit_counter=1, product_id=product_detail.id, category=product_detail.category, sub_category=product_detail.sub_category, last_visited=datetime.datetime.now(tz=get_current_timezone()))
        return TemplateResponse(request, 'veloce/products/review-ratings.html', {'ratings': ratings})
    else:
        return redirect(settings.FINTECH_URL + '/incomplete-profile')


@login_required
def dealer_list(request):
    url = f'{settings.OAUTH_URL}/user/info/'
    response = json.loads(requests.get(url, headers={
        'Authorization': 'Bearer ' + request.user.social_auth.get().extra_data['access_token']
    }).text)
    dealer_module = response.get("user_data")

    if request.method == "POST" :
        id = int(request.POST.get('id'))
        ajax_dealer =[]

        for dealer_lists in dealer_module:
            for d_list in dealer_lists :
                if d_list['User']['id'] == id:
                    ajax_dealer = d_list

        context ={
            'ajax_dealer': ajax_dealer,
        }
        return JsonResponse(context)

    if request.user.profile.account_type == 2:
        try:
            institution_dealers = models.DealerSelection.objects.filter(institution_id = request.user.id,is_pending = True)
            # print('#### pending product ###',institution_dealers)
            pending_dealers = []
            pending_ajax_dealer = []
            companyselection_request =[]
            for dealer_records in institution_dealers:  
                pending_dealers.append(dealer_records.dealer.username)

                if dealer_records.by_whom == 'dealer':
                        companyselection_request.append(dealer_records.dealer.username)
                        # print('$$$$$$$$$$$$$$$',companyselection_request)
            # print('*****************',pending_dealers)

            for dealer_lists in dealer_module:
                for d_list in dealer_lists :
                    # print(d_list['User']['username'])
                    if d_list['User']['username'] in pending_dealers:
                        pending_ajax_dealer.append(d_list)

            # print('++++++++++++++++',len(pending_ajax_dealer))

        except:
            institution_dealers = {}

        try:
            institution_dealers_completed = models.DealerSelection.objects.filter(institution_id = request.user.id,is_pending = False)
            completed_dealers = []
            completed_ajax_dealer = []
            for dealer_records in institution_dealers_completed:
                completed_dealers.append(dealer_records.dealer.username)
            
            for dealer_lists in dealer_module:
                for d_list in dealer_lists :
                    # print(d_list['User']['username'])
                    if d_list['User']['username'] in completed_dealers:
                        completed_ajax_dealer.append(d_list)

            # print('##########################',completed_dealers)
        except:
            institution_dealers_completed = {}
            
        

        single_dealer_modules =[]
        for dealer_lists in dealer_module:
            c_completed = 'false'
            v_verified = 'false'
            for d_list in dealer_lists :
                for i in d_list['user_level_data']['modules']:
                    if i['completed'] == True and i['verified'] == True:
                        c_completed = 'true'
                        v_verified = 'true'
                    else:
                        c_completed = 'false'
                        v_verified = 'false'

            if c_completed == 'true' and v_verified == 'true':
                single_dealer_modules.append(dealer_lists)


        try:
            context ={
                'dealer_modules' : single_dealer_modules,
                'pending_dealers': pending_dealers,
                'completed_dealers': completed_dealers,
                'institution_dealers_completeds':completed_ajax_dealer,
                'selected_dealers': pending_ajax_dealer,
                'companyselection_request':companyselection_request,

            }
            return render(request,'veloce/layout/dealer-list.html',context)
        except Exception as e:
            print(e)
            context ={
                'dealer_modules' : 'no address',
                'institution_dealers_completeds': completed_ajax_dealer,
                'selected_dealers': 'no pending_ajax_dealer',
            }
            return render(request,'veloce/layout/dealer-list.html',context)
    else:
        return redirect('index')




@login_required    
def approveby_dealer(request):
    url = f'{settings.OAUTH_URL}/company/info/'
    response = json.loads(requests.get(url, headers={
        'Authorization': 'Bearer ' + request.user.social_auth.get().extra_data['access_token']
    }).text)
    
    company_module = response.get("user_data")
    if request.method == "POST" :
        id = int(request.POST.get('id'))
        ajax_company =[]
        for company_lists in company_module:
            for d_list in company_lists :
                if d_list['User']['id'] == id:
                    ajax_company = d_list

        context ={
            'ajax_company': ajax_company,
        }
        return JsonResponse(context)


    if request.user.profile.account_type == 4:
        single_company_modules =[]
        for company_lists in company_module:
            c_completed = 'false'
            v_verified = 'false'
            for d_list in company_lists :
                for i in d_list['user_level_data']['modules']:
                    if i['completed'] == True and i['verified'] == True:
                        c_completed = 'true'
                        v_verified = 'true'
                    else:
                        c_completed = 'false'
                        v_verified = 'false'

            if c_completed == 'true' and v_verified == 'true':
                single_company_modules.append(company_lists)


        try:
            institution_dealers = models.DealerSelection.objects.filter(dealer = request.user,is_pending = True)
            pending_company = []
            dealerselection_request = []
            pending_ajax_company = []
            for dealer_records in institution_dealers: 
                    pending_company.append(dealer_records.institution.username)
                    if dealer_records.by_whom == 'company':
                        dealerselection_request.append(dealer_records.institution.username)
                        # print('dealerselection_request',dealerselection_request)

            for company_lists in company_module:
                for d_list in company_lists :
                    # print(d_list['User']['username'])
                    if d_list['User']['username'] in pending_company:
                        pending_ajax_company.append(d_list)
            # print('########################## pending',pending_company)
            # print(pending_ajax_company)
            
        except:
            institution_dealers = {}


        try:
            institution_dealers_pending = models.DealerSelection.objects.filter(dealer = request.user,is_pending = False)
            completed_companys = []
            completed_ajax_company = []
            for dealer_records in institution_dealers_pending:
                completed_companys.append(dealer_records.institution.username)
            
            for company_lists in company_module:
                for d_list in company_lists :
                    # print(d_list['User']['username'])
                    if d_list['User']['username'] in completed_companys:
                        completed_ajax_company.append(d_list)

            # print('########################## completed',completed_companys)
        except:
            institution_dealers_pending = {}


        try:
            context ={
                'company_modules' : single_company_modules,
                'pending_companys' : pending_company,
                'completed_companys': completed_companys,
                # 'institution_dealers_pendings': institution_dealers_pending,
                'institution_dealers_pendings': completed_ajax_company,
                'dealerselection_request': dealerselection_request,
                'selected_companys': pending_ajax_company,
            }
            return render(request,'veloce/layout/approveby-dealer.html',context)
        except Exception as e:
            print(e)
            context ={
                'company_modules' : 'no address',
                'pending_companys' : 'no pending_company',
                # 'selected_companys': 'no selected_companys',
                'completed_companys': 'no completed_companys',
                'institution_dealers_pendings': 'no institution_dealers_pending',
            }
            return render(request,'veloce/layout/approveby-dealer.html',context)
    else:
        return redirect('index')



@login_required
def ajax_approve_dealer(request):
    url = f'{settings.OAUTH_URL}/user/info/'
    response = json.loads(requests.get(url, headers={
        'Authorization': 'Bearer ' + request.user.social_auth.get().extra_data['access_token']
    }).text)
    dealer_module = response.get("user_data")
    
    if request.method == "POST" :
        id = int(request.POST.get('id'))
        ajax_dealer =[]

        for dealer_lists in dealer_module:
            for d_list in dealer_lists :
                if d_list['User']['id'] == id:
                    ajax_dealer = d_list
                    user_address = d_list['Address']
                    user = d_list['User']

        # print(user_address['city'],user_address['pin_code'],user_address['state'],user['username'],request.user)
        user_filter = User.objects.get(username = user['username'])
        try:
            # print('enater try')
            dealer_selection = models.DealerSelection.objects.get(
                dealer_id = user_filter.id,
                institution_id = request.user.id,
                pin_code = user_address['pin_code'],
                city = user_address['city'],
                state = user_address['state'],
                by_whom = 'company'
            )
            
            context = {
                'messages' : f" This User with Email: {user_filter.username} is already selected as your dealer!",
                'alart_class' : 'danger'
            }

        except:
            # print('enter except')
            dealer_selection = models.DealerSelection.objects.create(
                dealer_id = user_filter.id,
                institution_id = request.user.id,
                pin_code = user_address['pin_code'],
                city = user_address['city'],
                state = user_address['state'],
                is_pending = True,
                by_whom = 'company'
            ).save()
            context = {
                'messages' : f" This User with Email: {user_filter.username} is selected as your dealer!",
                'alart_class' : 'success'
            }

        return JsonResponse(context)

def ajax_approve_company(request):
    url = f'{settings.OAUTH_URL}/company/info/'
    response = json.loads(requests.get(url, headers={
        'Authorization': 'Bearer ' + request.user.social_auth.get().extra_data['access_token']
    }).text)
    company_module = response.get("user_data")

    url1 = f'{settings.OAUTH_URL}/user/info/'
    response1 = json.loads(requests.get(url1, headers={
        'Authorization': 'Bearer ' + request.user.social_auth.get().extra_data['access_token']
    }).text)
    dealer_module = response1.get("user_data")
    
    
    if request.method == "POST" :
        id = int(request.POST.get('id'))
        # print(id)
        ajax_company =[]

        for company_lists in company_module:
            for d_list in company_lists :
                if d_list['User']['id'] == id:
                    ajax_company = d_list
                    user_address = d_list['Address']
                    user = d_list['User']
        user_filter = User.objects.get(username = user['username'])
        
        dealer_id = request.user.username
        # print(dealer_id)
        ajax_dealer =[]
        for dealer_lists in dealer_module:
            for d_list in dealer_lists :
                if d_list['User']['username'] == dealer_id:
                    ajax_dealer = d_list
                    d_user_address = d_list['Address']
                    d_user = d_list['User']

        
        try:
            # print('enater try')
            company_selection = models.DealerSelection.objects.get(
                dealer_id = request.user.id,
                institution_id = user_filter.id,
                pin_code = d_user_address['pin_code'],
                city = d_user_address['city'],
                state = d_user_address['state'],
                by_whom = 'dealer',

            )
            
            context = {
                'messages' : f" This User with Email: {user_filter.username} is already selected as your company!",
                'alart_class' : 'danger'
            }

        except:
            # print('enter except')
            company_selection = models.DealerSelection.objects.create(
                dealer_id = request.user.id,
                institution_id = user_filter.id,
                pin_code = d_user_address['pin_code'],
                city = d_user_address['city'],
                state = d_user_address['state'],
                is_pending = True,
                by_whom = 'dealer',
            ).save()
            context = {
                'messages' : f" This User with Email: {user_filter.username} is selected as your company!",
                'alart_class' : 'success'
            }

        return JsonResponse(context)

def remove_dealer_pending(request):
    user = request.GET.get('user')
    dealer_user= User.objects.get(username = user)
    models.DealerSelection.objects.filter(dealer_id = dealer_user.id,institution = request.user,is_pending = True).delete()
    return redirect(dealer_list)

def remove_company_pending(request):
    user = request.GET.get('user')
    dealer_user= User.objects.get(username = user)
    models.DealerSelection.objects.filter(institution_id = dealer_user.id,dealer = request.user,is_pending = True).delete()
    return redirect(approveby_dealer)

def approveby_institution(request):
    inst_dealer = request.GET.get('user')
    institution_dealer = User.objects.get(username = inst_dealer)
    institution_dealers = models.DealerSelection.objects.filter(institution_id = request.user.id,dealer_id = institution_dealer.id,is_pending = True).update(is_pending = False,by_whom = '')
    # print('finalyyyyyyyyyyyy',institution_dealers)
    return redirect(dealer_list)

def cross_approve_by_dealer(request):
    dealer_inst = request.GET.get('user')
    dealer_institution = User.objects.get(username = dealer_inst)
    dealers_institution = models.DealerSelection.objects.filter(dealer_id = request.user.id,institution_id = dealer_institution.id,is_pending = True).update(is_pending = False,by_whom = '')    
    return redirect(approveby_dealer)

def get_product_by_id(request):
    if request.method == 'POST':
        institution_product_list = []
        pending_query_list = []
        approve_query_list = []
        rejected_query_list = []
        email = request.POST.get('id')
        ven_user = User.objects.get(username = email)
        print('ven_userssssssss',ven_user)
        institution_product = models.Product.objects.filter(vendor_id = ven_user.id)

        select_product_by_del = models.SelectProductByDealer.objects.filter(dealerselection__institution_id = ven_user.id)
        for dealer_product in select_product_by_del:
            if dealer_product.is_product_rejected == True and dealer_product.by_whom == None and dealer_product.reject_reason == None:
                pending_query_list.append(dealer_product.product.name)
            if dealer_product.is_product_rejected == False :
                approve_query_list.append(dealer_product.product.name)
            if dealer_product.is_product_rejected == True and dealer_product.by_whom != None and dealer_product.reject_reason != None:
                rejected_query_list.append(dealer_product.product.name)


        for product in institution_product:
            single_institution_product_dict = {}
            institution_product_media = models.ProductMedia.objects.filter(product_id = product.id).first()
            
            single_institution_product_dict = {
                'product_id': product.id,
                'Product_sub_category' : product.sub_category.name,
                'Product_category' : product.category.name,
                'Product_name' : product.name,
                'Product_slug' : product.slug,
                'product_user': product.vendor.username,
                'product_img':str(institution_product_media.image),
            }

            if product.name in pending_query_list:
                single_institution_product_dict['is_status'] = 'Pending'
            elif product.name in approve_query_list:
                single_institution_product_dict['is_status'] = 'Approved'
            elif product.name in rejected_query_list:
                single_institution_product_dict['is_status'] = 'Rejected'
            else:
                single_institution_product_dict['is_status'] = 'Not_Apply'
                

            institution_product_list.append(single_institution_product_dict)
            #print(institution_product_list)
        return JsonResponse({'data':institution_product_list})


def select_product_by_dealer_sell(request):
    if request.method == 'POST':
        product_list = request.POST.getlist('checkbox_value')
        product_own = request.POST.get('user_id')
        product_o = User.objects.get(username = product_own)
        dealer = request.user
        product_owner = models.DealerSelection.objects.get(institution_id = product_o.id,dealer_id = dealer.id)
        for product in product_list:
            single_product = models.Product.objects.get(id = int(product))
            models.SelectProductByDealer.objects.create(
                product = single_product,
                dealerselection_id = product_owner.id,
                is_product_rejected = True
            ).save()
    return redirect(approveby_dealer)

def view_dealer_selected_by_institution(request):
    selected_product_display_list =[]
    if request.method == 'POST':
        username = request.POST.get('email')
        dealer = User.objects.get(username = username)
        institution = request.user.pk
        dealer_selected_products = models.SelectProductByDealer.objects.filter(dealerselection__institution_id = institution,dealerselection__dealer_id = dealer.id)
        # print('##################',dealer_selected_products)
        
        for dealer_selected_product in dealer_selected_products:
            institution_product_media = models.ProductMedia.objects.filter(product_id = dealer_selected_product.product.id).first()

            single_product_dict = {
                'product_id': dealer_selected_product.product.id,
                'Product_sub_category' : dealer_selected_product.product.sub_category.name,
                'Product_category' : dealer_selected_product.product.category.name,
                'Product_name' : dealer_selected_product.product.name,
                'Product_slug' : dealer_selected_product.product.slug,
                'product_user': dealer_selected_product.product.vendor.username,
                'product_img':str(institution_product_media.image),
            }

            if  dealer_selected_product.is_product_rejected == True and dealer_selected_product.by_whom != None and dealer_selected_product.reject_reason != None: 
                single_product_dict['is_status'] = 'Rejected'
            if dealer_selected_product.is_product_rejected == False:
                single_product_dict['is_status'] = 'Approved'


            selected_product_display_list.append(single_product_dict)
            # print('single_product_dict',single_product_dict)
            
    return JsonResponse({'selected_product_display_list':selected_product_display_list})


def approve_company_selected_product(request):
    reason = request.GET.get('reason')
    product_id = request.GET.get('product_id')
    dealer_email = request.GET.get('dealer_email')
    dealer_user = User.objects.get(email = dealer_email)

    if reason:
        product_by_dealers = models.SelectProductByDealer.objects.filter(dealerselection__dealer_id = dealer_user.id,dealerselection__institution_id = request.user.id,product_id=product_id).update(is_product_rejected = True,by_whom = 'Rejected by company',reject_reason = reason)
        return JsonResponse({'reason':reason,'product_id':product_id,'dealer_email':dealer_email})
    else:
        product_by_dealers = models.SelectProductByDealer.objects.filter(dealerselection__dealer_id = dealer_user.id,dealerselection__institution_id = request.user.id,product_id=product_id).update(is_product_rejected = False)
        return JsonResponse({'product_id':product_id,'dealer_email':dealer_email})


def cross_delete_record_reason(request):
    if request.method == 'POST':
        reject_to_whom = request.POST.get('email')
        reject_reason = request.POST.get('reason')
        by_who = User.objects.get(email = reject_to_whom)
        by_whom = str(reject_to_whom)
        rej_reason = models.DealerSelection.objects.filter(institution_id = request.user.id,dealer_id = by_who.id, by_whom = 'dealer').update(by_whom = by_whom,reject_reason = reject_reason,is_application_rejected = True,is_pending = False)
    return JsonResponse({'email':'email'})

def dealer_cross_delete_record_reason(request):
    if request.method == 'POST':
        reject_to_whom = request.POST.get('email')
        reject_reason = request.POST.get('reason')
        by_who = User.objects.get(email = reject_to_whom)
        by_whom = str(reject_to_whom)
        rej_reason = models.DealerSelection.objects.filter(dealer_id = request.user.id,institution_id = by_who.id, by_whom = 'company').update(by_whom = by_whom,reject_reason = reject_reason,is_application_rejected = True,is_pending = False)
    return JsonResponse({'email':'email'})
