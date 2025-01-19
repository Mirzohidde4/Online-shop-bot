from django.db import models


class UserMod(models.Model):
    user_id = models.PositiveBigIntegerField(verbose_name='telegram id')
    user_name = models.CharField(verbose_name='foydalanuvchi ismi', max_length=100, null=True, blank=True)
    full_name = models.CharField(verbose_name='to\'liq ismi', max_length=150)
    language = models.CharField(verbose_name='til', max_length=10)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


class CategoryMod(models.Model):
    name_uz = models.CharField(verbose_name='o\'zbekcha nomi', max_length=100)
    name_ru = models.CharField(verbose_name='ruscha nomi', max_length=100, blank=True, null=True)
    name_en = models.CharField(verbose_name='inglizcha nomi', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name_uz

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    
class ProductMod(models.Model):
    category = models.ForeignKey(CategoryMod, verbose_name='turi', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='nomi', max_length=100)
    price = models.PositiveIntegerField(verbose_name='narxi')
    photo = models.ImageField(verbose_name='rasmi', upload_to='media/products/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'


class BasketMod(models.Model):
    user = models.PositiveBigIntegerField(verbose_name='foydalanuvchi id')
    product = models.ForeignKey(to=ProductMod, on_delete=models.CASCADE, verbose_name='mahsulot')
    category = models.PositiveIntegerField(verbose_name='kategoriya id')    
    count = models.PositiveIntegerField(verbose_name='soni', default=1)  

    def __str__(self):
        return self.product.name if self.product_id else "None"

    class Meta: 
        verbose_name = 'Savat'
        verbose_name_plural = 'Savatlar'    