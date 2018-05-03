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
        ('Cookie', '4564563564564564565646544')]

        urllib.request.install_opener(opener)
        html_bytes = urllib.request.urlopen(url).read()
        html_string = html_bytes.decode('utf-8')
        return html_string
    except:
        print("can not get html file.")
        return "can not get html file."

def get_curr(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    stock_info = soup.find_all(class_ = "price s-up ") #price s-down
    get_text = ""
    if len(stock_info)>0:
        i = stock_info[0]
        get_text = i.get_text()
        if len(get_text)>0:
            get_text = get_text.split()
    else:
        stock_info = soup.find_all(class_="price s-down ")  # price s-down
        if len(stock_info) > 0:
            i = stock_info[0]
            get_text = i.get_text()
            if len(get_text) > 0:
                get_text = get_text.split()
        else:
            print("no price.")
    return (get_text)

if __name__ == "__main__":
    sz002407 = r"https://gupiao.baidu.com/stock/sz002407.html"
    sz300719 = r"https://gupiao.baidu.com/stock/sz300719.html"
    for i in range (1400):
        str_time = time.strftime('%Y%m%d %H%M%S', time.localtime(time.time()))
        print(str_time,end=" ")
        if (int(str_time[9:16]) in range(92500, 113500)) or (int(str_time[9:16]) in range(125500, 150500)):
#            print(str_time,end=" ")
            html_doc = getHtml(sz002407)
            new_price = get_curr(html_doc)
            print (new_price,end=" ")

            html_doc = getHtml(sz300719)
            new_price = get_curr(html_doc)
            print(new_price)
        else:
            print("out of exchange time.")
        time.sleep(6)
