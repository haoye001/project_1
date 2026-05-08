
import hashlib

def deduplicate_products(products):
    seen = set()
    unique_products = []
    for product in products:
        identifier = hashlib.md5(product['name'].encode('utf-8')).hexdigest()
        if identifier not in seen:
            seen.add(identifier)
            unique_products.append(product)
    return unique_products

def sort_by_price(products, ascending=True):
    return sorted(products, key=lambda x: x['price'], reverse=not ascending)

def calculate_value_score(products):
    if not products:
        return products
    
    avg_price = sum(p['price'] for p in products) / len(products)
    avg_sales = sum(p['sales'] for p in products) / len(products) if products else 0
    
    for product in products:
        price_score = max(0, (avg_price - product['price']) / avg_price) if avg_price > 0 else 0
        sales_score = product['sales'] / avg_sales if avg_sales > 0 else 0
        rating_score = product['rating'] / 5.0 if product['rating'] > 0 else 0.5
        
        product['value_score'] = (price_score * 0.4 + sales_score * 0.3 + rating_score * 0.3) * 100
        product['value_level'] = get_value_level(product['value_score'])
    
    return products

def get_value_level(score):
    if score >= 80:
        return '高性价比'
    elif score >= 60:
        return '性价比中等'
    else:
        return '性价比偏低'

def filter_by_platform(products, platforms):
    if not platforms:
        return products
    return [p for p in products if p['platform'] in platforms]

def format_sales(sales):
    if sales >= 10000:
        return f"{sales/10000:.1f}万"
    elif sales >= 1000:
        return f"{sales/1000:.1f}千"
    return str(sales)

def format_price(price):
    return f"¥{price:.2f}"
