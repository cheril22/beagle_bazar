import json
from datetime import datetime, timezone
import ast
import requests
from django import template
from django.conf import settings
from django.db.models import Sum, Max
from veloce import enums
from veloce import models

register = template.Library()


@register.filter
def check_status(user_id, product_id):
    """
    This function filter whether logged in user.
    Also check if user already given review to product.

    :param user_id:
    :param product_id:
    :return:
    """
    qry = models.ProductRating.objects.filter(product_id=product_id, rated_by_id=user_id)
    if qry.count() > 0:
        return True
    else:
        return False


@register.filter
def get_percentage(product_id):
    """
    This function filter whether logged in user.
    Also check if user already given review to product.

    :param product_id:
    :return:
    """
    get_count = models.ProductRating.objects.filter(product_id=product_id)
    if get_count.count() > 0:
        sum = get_count.aggregate(Sum('rated_value'))['rated_value__sum']
        num_of_rate = get_count.count() * 5
        rated_val_per = int((sum / num_of_rate) * 100)
    else:
        rated_val_per = 0
    return rated_val_per

@register.filter
def get_rating_percentage(value):
    """
    This function filter whether logged in user.
    Also check if user already given review to product.

    :param product_id:
    :return:
    """
    if value:
        rated_val_per = int((value / 5) * 100)
    else:
        rated_val_per = 0
    return rated_val_per


@register.filter
def get_max_price(product_id):
    """
    This function filter whether logged in user.
    Also check if user already given review to product.

    :param product_id:
    :return:
    """
    get_max_price_val = models.PriceStructure.objects.filter(product_id=product_id).aggregate(Max('amount'))
    return get_max_price_val['amount__max']


@register.filter
def is_eligible_for_vendor(user_id):
    """
    This function will check whether user is eligible to become vendor.
    """
    check_user_eligibility = models.Profile.objects.get(user_id=user_id)
    if check_user_eligibility.is_complete and check_user_eligibility.is_verified:
        return True
    else:
        return False


@register.filter
def check_has_offer(product_id):
    """
    This function will check if a product has any offer.

    :param product_id:
    :return:
    """
    check_offer_on_product = models.Sale.objects.filter(product_id=product_id)
    if check_offer_on_product.count() > 0:
        get_offer_on_product = models.Sale.objects.get(product_id=product_id)
        now = datetime.now(timezone.utc)
        if get_offer_on_product.start_date <= now and get_offer_on_product.end_date >= now:
            return True
        else:
            return False
    else:
        return False


@register.filter
def check_user_level(user_id):
    """
    This function will check if a product has any offer.

    :param product_id:
    :return:
    """
    user = models.Profile.objects.get(user_id=user_id)
    data = {'uid': user.user.email}
    res = requests.get('http://innovations.veloce.market/check-updated-module-approved/', params=data).text
    response = json.loads(res)
    response['incomplete_level'] = list(set(response['incomplete_level']))
    response['not_verified_level'] = list(set(response['not_verified_level']))
    if response['status'] == False:
        data = response
    return data


@register.filter
def is_level_one_completed(user_id):
    """
    This function will check if a product has any offer.

    :param product_id:
    :return:
    """
    check_user_eligibility_level = models.Profile.objects.get(user_id=user_id)
    if check_user_eligibility_level.completion_level >= 1 and check_user_eligibility_level.verification_level >= 1:
        return True
    else:
        return False


@register.filter
def is_level_two_completed(user_id):
    """
    This function will check if a product has any offer.

    :param product_id:
    :return:
    """
    check_user_eligibility_level = models.Profile.objects.get(user_id=user_id)
    if check_user_eligibility_level.completion_level >= 2 and check_user_eligibility_level.verification_level >= 2:
        return True
    else:
        return False


@register.filter
def is_level_three_completed(user_id):
    """
    This function will check if a product has any offer.

    :param product_id:
    :return:
    """
    check_user_eligibility_level = models.Profile.objects.get(user_id=user_id)
    if check_user_eligibility_level.completion_level >= 3 and check_user_eligibility_level.verification_level >= 3:
        return True
    else:
        return False


@register.filter
def check_product_own_by_user(user_id, product_id):
    """
    This function will check if user own this product.
    :param product_id:
    :return:
    """
    # all_inquiries = models.ProductInquiry.objects.filter(Q(product__vendor=request.user) | Q(inquiry_by=request.user))
    check_is_owner = models.Product.objects.filter(vendor_id=user_id, pk=product_id)
    if check_is_owner.count() > 0:
        return True
    else:
        return False


@register.filter
def check_has_product(user_id):
    """
    This function will check if user own this product.
    :param product_id:
    :return:
    """
    check_is_owner = models.Product.objects.filter(vendor_id=user_id)
    if check_is_owner.count() > 0:
        return True
    else:
        return False


@register.filter
def get_after_discount_price(id):
    """
    This function will check if user own this product.
    :param product_id:
    :return:
    """
    try:
        get_price_val = models.PriceStructure.objects.get(id=id)
        discounted_price = get_price_val.amount - get_price_val.disc_amt
        return discounted_price
    except Exception as e:
        print("------------------------------------")
        print(e)
        print("------------------------------------")
        return 0


# added by piyush prajapati with ajay for fetch org_name and first_name,last_name base on acc type as on 05/11/2020
# add get-comp-det-by-id/ url in bizcread
@register.filter
def get_org_name(email):
    data= {
        'email':email
    }
    res = requests.get('http://innovations.veloce.market/get-comp-det-by-id/', params=data)
    # print(res)
    if res.status_code == 200:
        data = json.loads(res.content)
        # print(data)
        if data['status']:
            return data['data']
        else:
            return None
    else:
        return None

@register.filter
def get_package_service(data):
    id = ast.literal_eval(data)
    name = []
    for aps in id:
        name.append(enums.WarrantyService(int(aps)).name.replace('_', ' '))
        print(name)

    return ', '.join(name)

@register.filter
def get_sale_service(data):
    id = ast.literal_eval(data)
    name = []
    for aps in id:
        name.append(enums.WarrantyService(int(aps)).name.replace('_', ' '))
        print(name)

    return ', '.join(name)

@register.filter
def get_upload_bill_url(url):
    url = str(url)
    s2 = ' '.join(url.split('/')[1:])
    s3 = s2.replace(' ', '/')
    print(s3)
    return s3


@register.filter
def get_product_name_by_id(id):
    return models.Product.objects.get(id=id)

#
@register.filter
def get_user_profile_level(user):
    singe_profile = models.Profile.objects.get(user=user)
    return singe_profile.account_type



