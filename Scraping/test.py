import requests
from bs4 import BeautifulSoup

url = "https://finance.sina.cn/2025-07-05/detail-infemuii8216637.d.html?vt=4"
#https://finance.sina.cn/roll.d.html?rollCid=57038"
# https://finance.sina.com.cn/roll/index.d.html?cid=57038&page=1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# Example: find main headlines in <a> tags inside <div class="blk_hd">
headlines = soup.select('title')  # You can refine this with actual structure

print("=== Headline Examples ===")
for a in headlines[:10]:  # Print top 10
    title = a.get_text(strip=True)
    link = a.get('href')
    if title and link and link.startswith("http"):
        print(f"{title}\n{link}\n")