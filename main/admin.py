from django.contrib import admin
from .models import *
from django.contrib.auth.models import Group, User


admin.site.unregister(Group)
admin.site.unregister(User)

@admin.register(UserMod)
class AdminUserMod(admin.ModelAdmin):
    list_display = ('full_name', 'language')
    list_filter = ('language',)
    search_fields = ('full_name',)


@admin.register(CategoryMod)
class AdminCategoryMod(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_en')
    fields = ('name_uz',)
    readonly_fields = ('name_ru', 'name_en')


@admin.register(ProductMod) 
class AdminProductMod(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('category', 'price')
    search_fields = ('name',)


@admin.register(BasketMod)
class AdminBasketMod(admin.ModelAdmin):
    list_display = ('user', 'product', 'category', 'count', 'created_at')
    list_filter = ('user', 'product')
    search_fields = ('user',)


@admin.register(AdminMod)
class AdminAdminMod(admin.ModelAdmin):
    list_display = ('name', 'telegram_id', 'phone')
    search_fields = ('name', 'phone')

    def has_add_permission(self, request):
        if AdminMod.objects.count() >= 1:
            return False
        else:
            return True 
        

@admin.register(OrderMod)
class AdminOrder(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user',)


@admin.register(DiscountMod)
class AdminDiscountMod(admin.ModelAdmin): 
    list_display = ('discount_price', 'discount_percent', 'created_at')

    def has_add_permission(self, request):
        if DiscountMod.objects.count() >= 1:
            return False
        else:
            return True 