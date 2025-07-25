import requests
from bs4 import BeautifulSoup

url = r"https://www.qcckyc.com/enterprise-details?token=QCN165MD7X-1753325823171-1b1e899bc34bdb51bb3c04e0f73ae148"#https://find-and-update.company-information.service.gov.uk/company/02723534"#https://top.qcc.com/"#https://finance.sina.com.cn/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# Example: find main headlines in <a> tags inside <div class="blk_hd">
headlines = soup.select('a')  # You can refine this with actual structure

print("=== Headline Examples ===")
for a in headlines[:10]:  # Print top 10
    title = a.get_text(strip=True)
    link = a.get('href')
    if title and link and link.startswith("http"):
        print(f"{title}\n{link}\n")

# import asyncio
# import aiohttp
# import aiofiles
# from bs4 import BeautifulSoup
# import csv
# import time

# # 替换为新浪财经股票列表API（示例）
# STOCK_LIST_API = "https://finance.sina.com.cn/stock/sl/stock_list.html"
# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }

# async def fetch(session, url):
#     """异步获取网页内容"""
#     async with session.get(url, headers=HEADERS) as response:
#         return await response.text()

# async def parse_stock_data(html):
#     """解析股票数据（示例：仅提取名称和价格）"""
#     soup = BeautifulSoup(html, "html.parser")
#     stock_name = soup.select_one(".stock-name").text.strip() if soup.select_one(".stock-name") else "N/A"
#     stock_price = soup.select_one(".price").text.strip() if soup.select_one(".price") else "N/A"
#     return {"name": stock_name, "price": stock_price}

# async def save_to_csv(data, filename="stocks.csv"):
#     """异步写入CSV"""
#     async with aiofiles.open(filename, mode="a", encoding="utf-8", newline="") as f:
#         writer = csv.writer(f)
#         await writer.writerow([data["name"], data["price"]])

# async def crawl_stock(stock_code, session):
#     """爬取单只股票数据"""
#     url = f"https://finance.sina.com.cn/realstock/company/{stock_code}/nc.shtml"
#     try:
#         html = await fetch(session, url)
#         data = await parse_stock_data(html)
#         await save_to_csv(data)
#         print(f"爬取成功：{stock_code} - {data['name']}")
#     except Exception as e:
#         print(f"爬取失败：{stock_code} - {str(e)}")

# async def main():
#     """主协程：并发爬取多个股票"""
#     stock_codes = ["sh600000", "sh601318", "sz000001"]  # 示例股票代码（可扩展）

#     # 使用uvloop加速（仅限Unix系统）
#     try:
#         # import uvloop
#         # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
#         pass
#     except ImportError:
#         pass

#     # 创建aiohttp会话
#     async with aiohttp.ClientSession() as session:
#         tasks = [crawl_stock(code, session) for code in stock_codes]
#         await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     start_time = time.time()
#     asyncio.run(main())
#     print(f"爬取完成，耗时：{time.time() - start_time:.2f}秒")