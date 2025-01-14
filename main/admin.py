from django.contrib import admin
from .models import UserMod, CategoryMod, ProductMod
from unfold.admin import ModelAdmin
from django.contrib.auth.models import Group, User


admin.site.unregister(Group)

@admin.register(UserMod)
class AdminUserMod(ModelAdmin):
    list_display = ('full_name', 'language')
    list_filter = ('language',)


@admin.register(CategoryMod)
class AdminCategoryMod(ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_en')
    fields = ('name_uz',)
    readonly_fields = ('name_ru', 'name_en')


@admin.register(ProductMod) 
class AdminProductMod(ModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('category', 'price')