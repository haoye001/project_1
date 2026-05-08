
# 电商商品价格自动化采集与对比工具

## 项目概述
这是一个用于从主流电商平台（京东、淘宝、拼多多）批量抓取商品信息的自动化工具，支持按关键词搜索采集，并提供数据清洗、去重、排序、对比分析和可视化功能。

## 功能特性
- 多平台商品数据采集（京东、淘宝、拼多多）
- 按关键词搜索批量采集
- 数据自动清洗去重
- 价格从低到高排序
- 商品横向对比
- 价格趋势图表
- 性价比推荐标注

## 技术架构
- **后端语言**: Python 3.8+
- **数据库**: SQLite（存储历史价格数据）
- **网页框架**: Flask
- **可视化库**: ECharts
- **数据抓取**: requests + BeautifulSoup4

## 项目结构
```
project/
├── backend/
│   ├── crawlers/          # 爬虫模块
│   ├── database/          # 数据库模块
│   ├── utils/             # 工具函数
│   ├── app.py             # Flask应用
│   └── requirements.txt
├── frontend/              # 前端页面
└── cli.py                 # 命令行工具
```

## 快速开始

### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 命令行使用
```bash
# 搜索并采集商品
python cli.py search "笔记本电脑"

# 查看采集历史
python cli.py history

# 生成价格对比报告
python cli.py report "笔记本电脑"
```

### 启动网页服务
```bash
cd backend
python app.py
```

然后访问 http://localhost:5000

## API接口
- `GET /api/search?q=关键词` - 搜索商品
- `GET /api/products` - 获取所有商品
- `GET /api/trends?product_id=ID` - 获取价格趋势
- `GET /api/compare?ids=ID1,ID2,ID3` - 商品对比

## 数据结构
商品信息包含：
- 商品名称
- 价格
- 销量
- 店铺评分
- 网址链接
- 采集时间
- 平台标识
