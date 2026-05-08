
import sqlite3
import os
from datetime import datetime
from config import DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            sales INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            url TEXT NOT NULL UNIQUE,
            platform TEXT NOT NULL,
            image_url TEXT,
            crawl_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            keyword TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            price REAL NOT NULL,
            record_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_products_keyword ON products(keyword)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id)
    ''')
    
    conn.commit()
    conn.close()

def insert_product(name, price, sales, rating, url, platform, image_url, keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO products 
            (name, price, sales, rating, url, platform, image_url, crawl_time, keyword)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, price, sales, rating, url, platform, image_url, datetime.now(), keyword))
        
        product_id = cursor.lastrowid
        
        cursor.execute('''
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
        ''', (product_id, price))
        
        conn.commit()
        return product_id
    except sqlite3.IntegrityError:
        cursor.execute('SELECT id, price FROM products WHERE url = ?', (url,))
        row = cursor.fetchone()
        if row:
            product_id, old_price = row
            if old_price != price:
                cursor.execute('''
                    UPDATE products SET price = ?, crawl_time = ? WHERE id = ?
                ''', (price, datetime.now(), product_id))
                cursor.execute('''
                    INSERT INTO price_history (product_id, price)
                    VALUES (?, ?)
                ''', (product_id, price))
                conn.commit()
            return product_id
        return None
    finally:
        conn.close()

def get_products_by_keyword(keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, price, sales, rating, url, platform, image_url, crawl_time
        FROM products WHERE keyword = ? ORDER BY price ASC
    ''', (keyword,))
    results = cursor.fetchall()
    conn.close()
    return [
        {
            'id': r[0],
            'name': r[1],
            'price': r[2],
            'sales': r[3],
            'rating': r[4],
            'url': r[5],
            'platform': r[6],
            'image_url': r[7],
            'crawl_time': r[8]
        } for r in results
    ]

def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, price, sales, rating, url, platform, image_url, crawl_time, keyword
        FROM products ORDER BY price ASC
    ''')
    results = cursor.fetchall()
    conn.close()
    return [
        {
            'id': r[0],
            'name': r[1],
            'price': r[2],
            'sales': r[3],
            'rating': r[4],
            'url': r[5],
            'platform': r[6],
            'image_url': r[7],
            'crawl_time': r[8],
            'keyword': r[9]
        } for r in results
    ]

def get_product_by_id(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, price, sales, rating, url, platform, image_url, crawl_time
        FROM products WHERE id = ?
    ''', (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'sales': row[3],
            'rating': row[4],
            'url': row[5],
            'platform': row[6],
            'image_url': row[7],
            'crawl_time': row[8]
        }
    return None

def get_price_history(product_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price, record_time FROM price_history WHERE product_id = ? ORDER BY record_time ASC
    ''', (product_id,))
    results = cursor.fetchall()
    conn.close()
    return [
        {'price': r[0], 'record_time': r[1]} for r in results
    ]

def get_keywords():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT keyword FROM products ORDER BY keyword')
    results = cursor.fetchall()
    conn.close()
    return [r[0] for r in results if r[0]]

init_db()
