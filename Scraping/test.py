import requests
from bs4 import BeautifulSoup

url = "https://finance.sina.cn/roll.d.html?rollCid=57038"
# "https://finance.sina.cn/2025-07-05/detail-infemuii8216637.d.html?vt=4"
# https://finance.sina.com.cn/roll/index.d.html?cid=57038&page=1"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

print(soup)

a_tags = soup.find_all('a', attrs={'data-cid': True})

urls = []
headlines = []

# Print all href links from those <a> tags
for tag in a_tags:
    href = tag.get('href')
    urls.append(href)
    print(href)



for i in range(5):
    response = requests.get(urls[i], headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    title = soup.select('title')  
    headlines.append(title)


for i in headlines:
    print(i)


def get_stock_price(stock_code="sh600000"):
    url = f"http://hq.sinajs.cn/list={stock_code}"  # sh for Shanghai, sz for Shenzhen
    headers = {
        'Referer': 'https://finance.sina.com.cn/',
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    data = response.text

    # Example response: var hq_str_sh600000="浦发银行,10.350,10.340,10.420,..."
    if '=' in data:
        info = data.split('"')[1].split(',')
        name = info[0]
        price = info[3]  # current price
        print(f"{stock_code}: {name} - {price} RMB")

get_stock_price("sh600000")  # SPDB
get_stock_price("sz000001")  # Ping An Bank

# # Example: find main headlines in <a> tags inside <div class="blk_hd">
# headlines = soup.select('title') 

# print("=== Headline Examples ===")
# for a in headlines[:10]:  # Print top 10
#     title = a.get_text(strip=True)
#     link = a.get('href')
#     if title and link and link.startswith("http"):
#         print(f"{title}\n{link}\n")
