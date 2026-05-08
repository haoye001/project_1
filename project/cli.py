
#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from crawlers import JDCrawler, TaobaoCrawler, PinduoduoCrawler
from database.db import insert_product, get_products_by_keyword, get_all_products, get_price_history, get_keywords
from utils import deduplicate_products, sort_by_price, calculate_value_score, format_price, format_sales
import time

def search_products(keyword, platforms=None):
    if platforms is None:
        platforms = ['京东', '淘宝', '拼多多']
    
    crawlers = {
        '京东': JDCrawler(),
        '淘宝': TaobaoCrawler(),
        '拼多多': PinduoduoCrawler()
    }
    
    all_products = []
    for platform in platforms:
        if platform in crawlers:
            print(f"正在抓取 {platform}...")
            try:
                products = crawlers[platform].search(keyword)
                print(f"  成功获取 {len(products)} 件商品")
                all_products.extend(products)
                time.sleep(1)
            except Exception as e:
                print(f"  抓取失败: {e}")
    
    if not all_products:
        print("未找到任何商品")
        return []
    
    print(f"\n去重前: {len(all_products)} 件")
    all_products = deduplicate_products(all_products)
    print(f"去重后: {len(all_products)} 件")
    
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
            pass
    
    return all_products

def display_products(products):
    if not products:
        print("暂无商品数据")
        return
    
    print("\n" + "=" * 120)
    print(f"{'平台':<8} {'价格':<12} {'销量':<10} {'性价比':<10} {'商品名称'}")
    print("=" * 120)
    
    for i, product in enumerate(products, 1):
        platform = product['platform']
        price = format_price(product['price'])
        sales = format_sales(product['sales'])
        value_level = product.get('value_level', '-')
        name = product['name'][:60] + '...' if len(product['name']) > 60 else product['name']
        
        print(f"{platform:<8} {price:<12} {sales:<10} {value_level:<10} {name}")
    
    print("=" * 120)

def show_history():
    keywords = get_keywords()
    if not keywords:
        print("暂无搜索历史")
        return
    
    print("\n搜索历史关键词:")
    for i, keyword in enumerate(keywords, 1):
        print(f"  {i}. {keyword}")

def show_report(keyword):
    products = get_products_by_keyword(keyword)
    if not products:
        print(f"未找到关键词 '{keyword}' 的记录")
        return
    
    products = calculate_value_score(products)
    
    print(f"\n商品价格对比报告 - {keyword}")
    print("=" * 120)
    display_products(products)
    
    avg_price = sum(p['price'] for p in products) / len(products)
    max_price = max(p['price'] for p in products)
    min_price = min(p['price'] for p in products)
    
    print(f"\n统计信息:")
    print(f"  商品总数: {len(products)}")
    print(f"  平均价格: {format_price(avg_price)}")
    print(f"  最高价格: {format_price(max_price)}")
    print(f"  最低价格: {format_price(min_price)}")
    
    high_value = [p for p in products if p.get('value_level') == '高性价比']
    if high_value:
        print(f"\n高性价比推荐 ({len(high_value)}件):")
        for p in high_value[:3]:
            print(f"  - {format_price(p['price'])} | {p['platform']} | {p['name'][:40]}...")

def main():
    parser = argparse.ArgumentParser(description='电商商品价格采集与对比工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    search_parser = subparsers.add_parser('search', help='搜索商品')
    search_parser.add_argument('keyword', type=str, help='搜索关键词')
    search_parser.add_argument('--platforms', type=str, default='京东,淘宝,拼多多',
                               help='指定平台，用逗号分隔')
    
    history_parser = subparsers.add_parser('history', help='查看搜索历史')
    
    report_parser = subparsers.add_parser('report', help='生成对比报告')
    report_parser.add_argument('keyword', type=str, help='搜索关键词')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        platforms = [p.strip() for p in args.platforms.split(',')]
        products = search_products(args.keyword, platforms)
        display_products(products)
    
    elif args.command == 'history':
        show_history()
    
    elif args.command == 'report':
        show_report(args.keyword)
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
