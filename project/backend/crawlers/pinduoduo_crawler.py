
from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from config import SEARCH_LIMIT

class PinduoduoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform = '拼多多'
    
    def search(self, keyword):
        results = []
        url = 'https://search.pinduoduo.com/search'
        params = {
            'keyword': keyword,
            'type': 'keyword'
        }
        
        html = self.get_html(url, params)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all('div', class_='goods-item', limit=SEARCH_LIMIT)
        
        for item in items:
            try:
                name_tag = item.find('div', class_='goods-name')
                name = name_tag.get_text(strip=True) if name_tag else ''
                
                price_tag = item.find('div', class_='goods-price')
                price = self.extract_price(price_tag.get_text(strip=True)) if price_tag else 0.0
                
                sales_tag = item.find('div', class_='goods-sales')
                sales = self.extract_sales(sales_tag.get_text(strip=True)) if sales_tag else 0
                
                url_tag = item.find('a', class_='goods-link')
                url = 'https://www.pinduoduo.com' + url_tag['href'] if url_tag and 'href' in url_tag.attrs else ''
                
                image_tag = item.find('img', class_='goods-img')
                image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''
                
                if name and price > 0:
                    results.append({
                        'name': name,
                        'price': price,
                        'sales': sales,
                        'rating': 0.0,
                        'url': url,
                        'platform': self.platform,
                        'image_url': image_url
                    })
            except Exception as e:
                print(f"解析拼多多商品失败: {e}")
                continue
        
        return results
