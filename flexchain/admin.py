from django.contrib import admin
from .models import Vendor, Product, ProductVendor, Advisory, Inventory, Sales, Event, EventSku, Company, UserProfile, \
    Task


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductVendor)
class ProductVendorAdmin(admin.ModelAdmin):
    pass


@admin.register(Advisory)
class AdvisoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    pass


@admin.register(Event, EventSku)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
