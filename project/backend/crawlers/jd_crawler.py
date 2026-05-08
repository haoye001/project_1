
from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from config import SEARCH_LIMIT

class JDCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform = '京东'
    
    def search(self, keyword):
        results = []
        url = 'https://search.jd.com/Search'
        params = {
            'keyword': keyword,
            'enc': 'utf-8',
            'wq': keyword
        }
        
        html = self.get_html(url, params)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all('div', class_='gl-i-wrap', limit=SEARCH_LIMIT)
        
        for item in items:
            try:
                name_tag = item.find('div', class_='p-name')
                name = name_tag.get_text(strip=True) if name_tag else ''
                
                price_tag = item.find('div', class_='p-price')
                price = self.extract_price(price_tag.get_text(strip=True)) if price_tag else 0.0
                
                sales_tag = item.find('div', class_='p-commit')
                sales = self.extract_sales(sales_tag.get_text(strip=True)) if sales_tag else 0
                
                url_tag = item.find('a', class_='J_ClickStat')
                url = 'https:' + url_tag['href'] if url_tag and 'href' in url_tag.attrs else ''
                
                image_tag = item.find('img', class_='J_ItemImg')
                image_url = 'https:' + image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''
                
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
                print(f"解析京东商品失败: {e}")
                continue
        
        return results
