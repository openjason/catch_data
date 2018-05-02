from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import time
import urllib.request, urllib.parse, http.cookiejar

def getHtml(url):
    try:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'),
        ('Cookie', '4564564564564564565646540')]

        urllib.request.install_opener(opener)
        html_bytes = urllib.request.urlopen(url).read()
        html_string = html_bytes.decode('utf-8')
        return html_string
    except:
        return "can not get html file."

def get_curr(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    stock_info = soup.find_all(class_ = "price s-up ")

    get_text = ""
    if len(stock_info)>0:
        i = stock_info[0]
        get_text = i.get_text()
        if len(get_text)>0:
            get_text = get_text.split()
    return (get_text)

if __name__ == "__main__":
    sz2407 = r"https://gupiao.baidu.com/stock/sz002407.html"
    for i in range (1000):
#        print(time.localtime(time.time()),end="")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),end="")
        html_doc = getHtml(sz2407)
        new_price = get_curr(html_doc)
        print (new_price)
        time.sleep(4)