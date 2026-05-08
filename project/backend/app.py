
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from crawlers import JDCrawler, TaobaoCrawler, PinduoduoCrawler
from database.db import insert_product, get_products_by_keyword, get_all_products, get_product_by_id, get_price_history, get_keywords
from utils import deduplicate_products, sort_by_price, calculate_value_score
import time

app = Flask(__name__, template_folder='../frontend')
CORS(app)

crawlers = {
    '京东': JDCrawler(),
    '淘宝': TaobaoCrawler(),
    '拼多多': PinduoduoCrawler()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def api_search():
    keyword = request.args.get('q', '')
    platforms = request.args.getlist('platforms[]', ['京东', '淘宝', '拼多多'])
    
    if not keyword:
        return jsonify({'error': '请输入搜索关键词'}), 400
    
    all_products = []
    for platform in platforms:
        if platform in crawlers:
            try:
                print(f"正在抓取 {platform}...")
                products = crawlers[platform].search(keyword)
                all_products.extend(products)
                time.sleep(1)
            except Exception as e:
                print(f"抓取 {platform} 失败: {e}")
    
    all_products = deduplicate_products(all_products)
    all_products = sort_by_price(all_products)
    all_products = calculate_value_score(all_products)
    
    for product in all_products:
        try:
            insert_product(
                product['name'],
                product['price'],
                product['sales'],
                product['rating'],
                product['url'],
                product['platform'],
                product.get('image_url', ''),
                keyword
            )
        except Exception as e:
            print(f"保存商品失败: {e}")
    
    return jsonify({
        'keyword': keyword,
        'count': len(all_products),
        'products': all_products
    })

@app.route('/api/products', methods=['GET'])
def api_products():
    keyword = request.args.get('keyword', '')
    if keyword:
        products = get_products_by_keyword(keyword)
    else:
        products = get_all_products()
    return jsonify({'products': products})

@app.route('/api/trends', methods=['GET'])
def api_trends():
    product_id = request.args.get('product_id', '')
    if not product_id:
        return jsonify({'error': '请提供商品ID'}), 400
    
    history = get_price_history(product_id)
    product = get_product_by_id(product_id)
    
    return jsonify({
        'product': product,
        'history': history
    })

@app.route('/api/compare', methods=['GET'])
def api_compare():
    ids = request.args.get('ids', '')
    if not ids:
        return jsonify({'error': '请提供商品ID列表'}), 400
    
    product_ids = [int(id.strip()) for id in ids.split(',') if id.strip()]
    products = []
    for pid in product_ids:
        product = get_product_by_id(pid)
        if product:
            products.append(product)
    
    products = calculate_value_score(products)
    
    return jsonify({'products': products})

@app.route('/api/keywords', methods=['GET'])
def api_keywords():
    keywords = get_keywords()
    return jsonify({'keywords': keywords})

@app.route('/api/sample', methods=['GET'])
def api_sample():
    sample_products = [
        {
            'id': 1,
            'name': 'Apple MacBook Pro 14英寸 M3 Pro芯片 18GB内存 512GB固态硬盘 深空灰',
            'price': 14999.00,
            'sales': 12580,
            'rating': 4.9,
            'url': 'https://item.jd.com/100054055825.html',
            'platform': '京东',
            'image_url': 'https://img10.360buyimg.com/n1/jfs/t1/200032/33/25333/44659/647d2253F0c756853/8c29978d40880863.jpg',
            'value_score': 78.5,
            'value_level': '性价比中等'
        },
        {
            'id': 2,
            'name': 'Apple MacBook Pro 14英寸 M3 Pro芯片 18GB内存 512GB固态硬盘 深空灰',
            'price': 14599.00,
            'sales': 8920,
            'rating': 4.8,
            'url': 'https://item.taobao.com/item.htm?id=7234567890',
            'platform': '淘宝',
            'image_url': 'https://img.alicdn.com/imgextra/i1/1234567890/O1CN01abcDEF2345678901_!!0-item_pic.jpg',
            'value_score': 85.2,
            'value_level': '高性价比'
        },
        {
            'id': 3,
            'name': 'Apple MacBook Pro 14英寸 M3 Pro芯片 18GB内存 512GB固态硬盘',
            'price': 13888.00,
            'sales': 5680,
            'rating': 4.6,
            'url': 'https://www.pinduoduo.com/goods-detail.html?goods_id=123456789',
            'platform': '拼多多',
            'image_url': 'https://t00img.yangkeduo.com/goods/images/2023-10/01/2345678901234.jpg',
            'value_score': 92.1,
            'value_level': '高性价比'
        },
        {
            'id': 4,
            'name': '华为MateBook 14s 2023款 14.2英寸 酷睿i7-13700H 16GB 1TB 深空灰',
            'price': 7999.00,
            'sales': 23450,
            'rating': 4.7,
            'url': 'https://item.jd.com/100060088888.html',
            'platform': '京东',
            'image_url': 'https://img14.360buyimg.com/n1/jfs/t1/198765/22/25678/39876/6501a9e9F2e881c3b/34d53a9d8d35d488.jpg',
            'value_score': 88.6,
            'value_level': '高性价比'
        },
        {
            'id': 5,
            'name': '联想ThinkPad X1 Carbon 2023款 14英寸 i7-1360P 16GB 1TB SSD',
            'price': 11999.00,
            'sales': 9870,
            'rating': 4.8,
            'url': 'https://item.jd.com/100058866666.html',
            'platform': '京东',
            'image_url': 'https://img12.360buyimg.com/n1/jfs/t1/201234/18/24890/45123/64f8b7a8F9d69b09d/10199f34192c8d59.jpg',
            'value_score': 76.3,
            'value_level': '性价比中等'
        }
    ]
    
    return jsonify({
        'keyword': '笔记本电脑',
        'count': len(sample_products),
        'products': sample_products
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
