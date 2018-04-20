from zeep import Client
from lxml import etree

def get_price():
    client = Client('http://www.pttplc.com/webservice/pttinfo.asmx?WSDL')
    result = client.service.CurrentOilPrice("en")

    root = etree.fromstring(result)
    prices = []
    for r in root.xpath('DataAccess'):
        product = r.xpath('PRODUCT/text()')[0]
        price = r.xpath('PRICE/text()') or [0]
        prices.append([product,float(price[0])])
        # print(product,float(price[0]),' BAHT')
    return prices

if __name__ == '__main__':
    l = get_price()
    for p in l:
        name = p[0]
        price = p[1]
        print("%s %.2f บาท\n" % (name,price))
    