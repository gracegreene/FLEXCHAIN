from flexchain.models import Vendor, ProductVendor, Product, Inventory, Forecast
from datetime import datetime
from datetime import timedelta


def order_quantity(product_vendor):
    number_of_items = product_vendor.vendor.order_fixed_cost / (
                product_vendor.product.price * product_vendor.cost * product_vendor.product.unit_weight * product_vendor.vendor.weight_tariff)
    if number_of_items > product_vendor.moq:
        return number_of_items
    else:
        return 0


# Inventory vs ROP check, Output: product, Amount to order, Supplier
def reorder(product_sku):
    for product_vendor in ProductVendor.objects.filter(product_sku=product_sku).order(ProductVendor.lead_time):
        if Inventory.current_inventory(product_sku=product_sku) <= Product.get_reorder_point(product_vendor.vendor.id):
            order_amount = order_quantity(product_vendor)
            if order_amount > 0:
                return product_sku, order_amount, product_vendor.vendor.id
            else:
                continue
    return None


# Determines how many weeks before stockout
def stockout(product_sku):
    inventory_now = Inventory.current_inventory(product_sku=product_sku)
    forecasts = Forecast.objects.filter(prediction_date__gte=datetime.now()).order_by('prediction_date')
    current_forecast = 0
    weeks = 0
    for forecast in forecasts:
        weeks = weeks + 1
        current_forecast = current_forecast + forecast.prediction
        if inventory_now < current_forecast:
            return weeks
    return weeks
