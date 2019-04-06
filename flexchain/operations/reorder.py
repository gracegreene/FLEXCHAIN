# LP function, Output: Amount to order
def order_quantity(vendor, product):
    x = Vendor.order_fixed_cost / (Product.price * ProductVendor.cost * Product.unit_weight * Vendor.weight_tariff)
    if x > ProductVendor.moq:
        return x
    else:
        return 0


# Inventory vs ROP check, Output: Amount to order, Supplier
def reorder():
    for product_vendor in ProductVendor.objects.filter(product_sku=product_sku).order(ProductVendor.lead_time):
        if Inventory.current_inventory(product_sku=product_sku) <= Product.get_reorder_point(vendor_id):
            order_amount = order_quantity(vendor_id, product_sku)
            if order_amount > 0:
                return product_sku, order_amount, vendor_id
            else:
                continue
    return None
