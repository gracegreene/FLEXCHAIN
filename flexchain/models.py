from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import User


class Vendor(models.Model):
    VENDOR_TYPE_CHOICES = (
        ('T', 'Trading'),
        ('M', 'Manufacturer'),
    )

    VENDOR_FREIGHT_TYPE_CHOICES = (
        ('S', 'Ship'),
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
        max_length=4,
        unique=True
    )
    name = models.CharField(
        help_text='Product Name',
        blank=False,
        max_length=40
    )
    collection = models.CharField(
        help_text='Collection Product Belongs To',
        max_length=40
    )
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency='USD',
        help_text='Price of the Product',
        null=False
    )

    def __str__(self):
        return "{}".format(self.name)


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
    lead_time = models.DurationField(
        help_text='Time it takes for delivery of item',
        null=False
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