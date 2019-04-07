from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Sum
from datetime import datetime
from datetime import timedelta

class Vendor(models.Model):
    VENDOR_TYPE_CHOICES = (
        ('T', 'Trading'),
        ('M', 'Manufacturer'),
    )

    VENDOR_FREIGHT_TYPE_CHOICES = (
        ('L', 'Land'),
        ('S', 'Sea'),
        ('A', 'Air')
    )
    vendor_name = models.CharField(
        help_text='Vendor Name',
        max_length=40,
        blank=False,
        unique=True,
    )
    contact_person = models.CharField(
        help_text='Point of contact',
        max_length=50,
        blank=False
    )
    email = models.EmailField(
        help_text='Point of contact email',
        max_length=100,
        blank=False
    )
    address = models.TextField(
        help_text='Address associated with vendor',
        max_length=250,
        blank=False
    )
    vendor_joined = models.DateTimeField(
        help_text='Date the vendor was added.',
        auto_now_add=True,
        blank=False,
        null=False
    )
    order_fixed_cost = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='USD',
        help_text='Fixed Cost when Ordering',
        null=False
    )
    vendor_type = models.TextField(
        help_text='Type of vendor',
        max_length=1,
        choices=VENDOR_TYPE_CHOICES
    )
    freight_type = models.TextField(
        help_text='Method of delivery',
        max_length=1,
        choices=VENDOR_FREIGHT_TYPE_CHOICES
    )
    weight_tariff = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='USD',
        help_text='Variable cost for shipping in USD/lb',
        null=False
    )

    class Meta:
        db_table = 'vendor'

    def __str__(self):
        return "{}".format(self.vendor_name)


class Product(models.Model):
    class Meta:
        db_table = 'product'

    sku = models.CharField(
        help_text='Product SKU',
        primary_key=True,
        blank=False,
        max_length=10,
        unique=True
    )
    name = models.CharField(
        help_text='Product Name',
        blank=False,
        max_length=40
    )
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='USD',
        help_text='Price of the Product',
        null=False
    )
    unit_weight = models.FloatField(
        help_text='Weight in pounds of single item in individual package',
    )

    def __str__(self):
        return "{}".format(self.name)

    def get_reorder_point(self, vendor_id):
        prod_vend_object = ProductVendor.objects.get(product_sku=self.sku, vendor_id=vendor_id)
        weekly_sales_average = Sales.objects.filter(product_sku=self.sku).aggregate(Avg('quantity_sold'))
        weekly_sales_maximum = Sales.objects.filter(product_sku=self.sku).aggregate(Max('quantity_sold'))
        forecast_sum = Forecast.objects.filter(product_sku=self.sku).aggregate(Sum('prediction'))
        popup_add = EventSku.objects.filter(
            product_sku=self.sku,
            event_date__gt=datetime.now(),
            event_date__lt=datetime.now() + timedelta(days=89)
        ).aggregate(Sum('increase'))
        safety_stock = ((weekly_sales_maximum - weekly_sales_average) * prod_vend_object.lead_time) + popup_add
        reorder = (prod_vend_object.lead_time * weekly_sales_average) + safety_stock
        return reorder


class ProductVendor(models.Model):
    class Meta:
        db_table = 'product_vendor'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE
    )
    cost = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='USD',
        help_text='Cost of product via vendor',
        null=False
    )
    moq = models.BigIntegerField(
        null=False,
        help_text='Minimum Order Quantity',
    )

    def __str__(self):
        return "{}-{}".format(
            self.sku.name, self.vendor_id
        )


class Advisory(models.Model):
    class Meta:
        db_table = "advisory"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    quantity = models.BigIntegerField(
        help_text='Quantity of advised purchase',
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    action = models.TextField(
        max_length=500,
        blank=False
    )  # TODO ask about this

    def __str__(self):
        return '{}'.format(self.action)


class Inventory(models.Model):
    class Meta:
        db_table = 'inventory'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    recorded_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )
    amount_on_hand = models.BigIntegerField(
        help_text='Amount of inventory recorded for this day',
        null=False
    )
    amount_back_order = models.BigIntegerField(
        help_text='Amount of products ordered but not delivered.',
        null=False
    )
    amount_pending_return = models.BigIntegerField(
        help_text='Amount of products being returned.',
        null=False
    )
    amount_incoming_order = models.BigIntegerField(
        help_text='Amount of products ordered from supplier arriving by next week.',
        null=False
    )

    def current_inventory(self, product_sku):
        return amount_on_hand + amount_incoming_order + amount_pending_return - amount_back_order

    def __str__(self):
        return '{}'.format(self.sku.name)


class Sales(models.Model):
    class Meta:
        db_table = 'sales'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    sales_date = models.DateTimeField(
        help_text='Date that sales occurred',
        blank=False,
        null=False,
        auto_now_add=True
    )
    quantity_sold = models.BigIntegerField(
        help_text='Quantity sold',
        blank=False,
        null=False
    )

    def __str__(self):
        return 'Sold {} of {}'.format(
            self.quantity_sold, self.sku.name
        )


class Forecast(models.Model):
    class Meta:
        db_table = 'forecast'

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    prediction_date = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )
    prediction = models.BigIntegerField(
        help_text='Forecasted demand',
        null=False
    )

    def __str__(self):
        return '{}'.format(self.name)


class Event(models.Model):
    class Meta:
        db_table = 'event'

    name = models.CharField(
        max_length=40,
        blank=False
    )
    date = models.DateTimeField(
        blank=False,
        null=False
    )

    def __str__(self):
        return '{}'.format(self.name)


class EventSku(models.Model):
    class Meta:
        db_table = 'event_sku'

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    increase = models.BigIntegerField(
        help_text='Expected event sales of item.',
        null=False
    )

    def __str__(self):
        return '{}-{}'.format(
            self.event.name,
            self.sku.name
        )


class Company(models.Model):
    class Meta:
        db_table = 'company'

    name = models.CharField(
        max_length=50,
        help_text='Company Name',
        blank=False
    )
    description = models.TextField(
        max_length=500,
        help_text='Company Description'
    )

    def __str__(self):
        return '{}'.format(self.name)


class UserProfile(models.Model):
    class Meta:
        db_table = 'user_profile'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )
    role = models.CharField(
        max_length=50
    )  # TODO Ask about this
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        null=False
    )

    def __str__(self):
        return '{}'.format(self.user.username)


class Task(models.Model):
    TASK_STATUS_CHOICES = (
        ('CR', 'created'),
        ('AS', 'assigned'),
        ('CO', 'completed'),
        ('CA', 'cancelled')
    )

    class Meta:
        db_table = 'task'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_sku',
        to_field='sku'
    )
    created_at = models.DateTimeField()
    advisory = models.ForeignKey(
        Advisory,
        on_delete=models.CASCADE
    )
    due_date = models.DateTimeField(

    )
    status = models.CharField(
        choices=TASK_STATUS_CHOICES,
        max_length=2
    )
    notes = models.TextField(
        max_length=500
    )
