
from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from config import SEARCH_LIMIT

class TaobaoCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.platform = '淘宝'
    
    def search(self, keyword):
        results = []
        url = 'https://s.taobao.com/search'
        params = {
            'q': keyword,
            'imgfile': '',
            'commend': 'all',
            'ssid': 's5-e',
            'search_type': 'item',
            'sourceId': 'tb.index',
            'spm': 'a21bo.jianhua%2Fa.201856-taobao-item.1',
            'ie': 'utf8',
            'initiative_id': 'tbindexz_20170306'
        }
        
        html = self.get_html(url, params)
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all('div', class_='item J_MouserOnverReq', limit=SEARCH_LIMIT)
        
        for item in items:
            try:
                name_tag = item.find('div', class_='row-2 title')
                name = name_tag.get_text(strip=True) if name_tag else ''
                
                price_tag = item.find('strong', class_='price J_price')
                price = self.extract_price(price_tag.get_text(strip=True)) if price_tag else 0.0
                
                sales_tag = item.find('div', class_='deal-cnt')
                sales = self.extract_sales(sales_tag.get_text(strip=True)) if sales_tag else 0
                
                url_tag = item.find('a', class_='J_ClickStat')
                url = 'https:' + url_tag['href'] if url_tag and 'href' in url_tag.attrs else ''
                
                image_tag = item.find('img', class_='J_ItemImg')
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
                print(f"解析淘宝商品失败: {e}")
                continue
        
        return results
