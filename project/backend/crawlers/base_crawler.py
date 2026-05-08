
import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT

class BaseCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def get_html(self, url, params=None):
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            return None
    
    def parse(self, html):
        raise NotImplementedError("子类必须实现 parse 方法")
    
    def search(self, keyword):
        raise NotImplementedError("子类必须实现 search 方法")
    
    def extract_price(self, text):
        import re
        price_pattern = r'(\d+\.?\d*)'
        match = re.search(price_pattern, text)
        return float(match.group(1)) if match else 0.0
    
    def extract_sales(self, text):
        import re
        sales_pattern = r'(\d+(?:\.?\d*))\s*(万|千|百)?'
        match = re.search(sales_pattern, text)
        if match:
            num = float(match.group(1))
            unit = match.group(2)
            if unit == '万':
                return int(num * 10000)
            elif unit == '千':
                return int(num * 1000)
            elif unit == '百':
                return int(num * 100)
            return int(num)
        return 0
    
    def extract_rating(self, text):
        import re
        rating_pattern = r'(\d+\.?\d*)'
        match = re.search(rating_pattern, text)
        return float(match.group(1)) if match else 0.0
