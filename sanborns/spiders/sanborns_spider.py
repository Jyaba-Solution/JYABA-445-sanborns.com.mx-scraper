import scrapy
import datetime


'''
Date == Script run date  (DD/MM/YYYY) 

Canal == “Sanborns” 

Category == category 

Subcategory = Subcategory 

Subcategory2= Subcategory2 

Subcategory3=  BLANK 

Marca == Brand 

Modelo == Model 

SKU ==SKU 

UPC == UPC 

Item == Item 

Item Characteristics == Item Characteristics 

URL SKU == URL 

Image == image 

Price == Price 

Sale Price == Sale Price 

Shipment Cost == BLANK 

Sales Flag == Sales Flag 

Store ID == BLANK 

Store Name = BLANK 

Store Address = BLANK 

Stock == Stock 

UPC WM == UPC[0:-1].zifll(16) 

Final Price == min (price, sale price). 
'''

class SanbornScrapy(scrapy.Spider):
    name = "sanborn"
    start_urls = ['https://snapi.sanborns.com.mx/management/v2/home-app']

    def parse(self, response):
        breakpoint()
        product_json = response.json()
        item = {}
        item['Date'] = datetime.datetime.now().strftime("%d/%m/%Y")
        item['Canal'] = "Sanborns"
        item['Category'] = response.xpath('//div[@class="breadcrumb"]/a[1]/text()').get()
        item['Subcategory'] = response.xpath('//div[@class="breadcrumb"]/a[2]/text()').get()
        item['Subcategory2'] = response.xpath('//div[@class="breadcrumb"]/a[3]/text()').get()
        item['Subcategory3'] = ""
        item['Marca'] = product_json.get('data',{}).get('brand')
        item['Modelo'] = product_json.get('data',{}).get('model')
        item['SKU'] = product_json.get('data',{}).get('sku')
        item['UPC'] = product_json.get('data',{}).get('ean')
        item['Item'] = product_json.get('data',{}).get('title')
        item['Item Characteristics'] = product_json.get('data',{}).get('description')
        product_id = product_json.get('data',{}).get('id')
        item['URL SKU'] = f"https://www.sanborns.com.mx/producto/{product_id}/{product_json.get('data',{}).get('title_seo')}"
        item['Image'] = ','.join([image_product['url'] for image_product in product_json.get('data',{}).get('images')])
        item['Price'] = product_json.get('data',{}).get('price')
        item['Sale Price'] = product_json.get('data',{}).get('sale_price')
        item['Shipment Cost'] = ""
        item['Sales Flag'] = product_json.get('data',{}).get('discount')
        item['Store ID'] = ""
        item['Store Name'] = ""
        item['Store Address'] = ""
        item['Stock'] = product_json.get('data',{}).get('stock')
        item['UPC WM'] = product_json.get('data',{}).get('ean')[0:-1].zfill(16)
        item['Final Price'] = min(item['Price'], item['Sale Price'])
        yield item
