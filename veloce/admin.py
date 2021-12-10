from django.contrib import admin
from veloce import models

admin.site.register(models.VeloceUser)
admin.site.register(models.Category)
admin.site.register(models.SubCategory)
admin.site.register(models.BookSale)
admin.site.register(models.BookSaleDetails)
admin.site.register(models.GeneralRewardPoints)
admin.site.register(models.TransactionRewardDetails)
admin.site.register(models.DealersGivenFinanceScheme)
admin.site.register(models.SpecialRewardPoints)
# admin.site.register(models.Industry)
admin.site.register(models.Product)
admin.site.register(models.ProductRating)
admin.site.register(models.PriceStructure)
admin.site.register(models.ProductMedia)
admin.site.register(models.ProductInquiry)
admin.site.register(models.PackagingDeliveryDetails)
admin.site.register(models.Profile)
admin.site.register(models.Sale)
admin.site.register(models.Voucher)
admin.site.register(models.RecentlyVisited)
# created by ravi
admin.site.register(models.DealerSelection)
admin.site.register(models.SelectProductByDealer)


