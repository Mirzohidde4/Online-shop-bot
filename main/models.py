from django.db import models


class UserMod(models.Model):
    user_id = models.PositiveBigIntegerField(verbose_name='telegram id')
    user_name = models.CharField(verbose_name='foydalanuvchi ismi', max_length=100, null=True, blank=True)
    full_name = models.CharField(verbose_name='to\'liq ismi', max_length=150)
    language = models.CharField(verbose_name='til', max_length=10)
    phone = models.CharField(max_length=20, verbose_name='tel raqam')

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
    photo = models.ImageField(verbose_name='rasmi', upload_to='media/products/')

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='sana', null=True, blank=True)

    class Meta: 
        verbose_name = 'Savat'
        verbose_name_plural = 'Savatlar'    


class AdminMod(models.Model):
    CHOICES = [('uz', 'uz'), ('ru', 'ru'), ('en', 'en')]
    name = models.CharField(verbose_name='ism', max_length=50)
    telegram_id = models.PositiveBigIntegerField(verbose_name='telegram id')
    phone = models.DecimalField(verbose_name='telefon raqam', max_digits=15, decimal_places=0)
    language = models.CharField(max_length=5, choices=CHOICES, default='uz', verbose_name='til')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admin'


class OrderMod(models.Model):
    user = models.ForeignKey(to=UserMod, on_delete=models.CASCADE, verbose_name='foydalanuvchi') 
    product_name = models.CharField(verbose_name='mahsulot nomi', max_length=100)
    product_price = models.PositiveIntegerField(verbose_name='mahsulot narxi')
    product_count = models.PositiveIntegerField(verbose_name='mahsulot soni')   
    overal_price = models.PositiveBigIntegerField(verbose_name='umumiy narxi') 
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='sana', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'


class DiscountMod(models.Model):
    discount_price = models.PositiveIntegerField(verbose_name="chegirma narxi")
    discount_percent = models.PositiveIntegerField(verbose_name="chegirma foizi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='sana', null=True, blank=True)

    class Meta:
        verbose_name = 'Chegirma'
        verbose_name_plural = 'Chegirmalar'