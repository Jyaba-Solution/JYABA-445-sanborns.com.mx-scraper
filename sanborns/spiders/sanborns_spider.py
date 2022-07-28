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
    def start_requests(self):
        categories_list = [10,12,2,5,13,4,14,6,1,16,7]
        urls = [f"https://snapi.sanborns.com.mx/anteater/search?cliente=sanborns_2&proxystylesheet=xml2json&oe=UTF-8&getfields=*&sort=&start=0&num=100&requiredfields=&requiredobjects=categories->id:{x}&ds=marcas:attribute_marca:0:0:200:1:0.sale_precio:sale_price:1:1:1000.ranking:review:0:0:8:0:1.full:fulfillment:0:0:8:0:1.free:shipping_price:0:0:8:0:1.discount:discount:0:0:1000:0:1&do=breadcrumbs:breadcrumbs:id,name,padre:100:1" for x in categories_list]
        for url in urls:
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_categories, meta={'start_page': 0, 'url': url})
    def parse_categories(self, response):
        results = response.json().get('GSP',{}).get('RES', {})
        total_count = results.get('M')
        products_list = [f"https://snapi.sanborns.com.mx/app/v1/product/{x.get('MT')[0]['V']}" for x in results.get('R')]
        products_list = set(products_list)
        for product in products_list:
            yield scrapy.Request(product, callback=self.parse_product)
        if total_count and response.meta.get('start_page') == 0:
            total_count = int(total_count)
            start_page = response.meta.get('start_page')
            url = response.meta.get('url')
            start_page = start_page + 100
            for i in range(start_page, total_count, 100):
                new_url = url.replace(f"start=0", f"start={i}")
                yield scrapy.Request(url=new_url, callback=self.parse_categories, meta={'start_page': i, 'url': url})
        else:
            with open('log.txt', 'a') as f:
                f.write(f"{response.url}\n")

    def parse(self, response, **kwargs):
        product_json = response.json()
        products_list = [f"https://snapi.sanborns.com.mx/app/v1/product/{x.get('MT')[0]['V']}" for x in product_json.get('GSP').get('RES').get('R')]
        products_list = set(products_list)
        for product in products_list:
            yield scrapy.Request(product, callback=self.parse_product, dont_filter=True)
       

    def parse_product(self, response):
        product_json = response.json()
        item = {}
        item['Date'] = datetime.datetime.now().strftime("%d/%m/%Y")
        item['Canal'] = "Sanborns"
        xp = [x.get('name') for x in product_json.get('data',{}).get('categories')]
        xp.reverse()
        xp_dict = {xp.index(x):x for x in xp}
        item['Category'] = xp_dict.get(0)
        item['Subcategory'] = xp_dict.get(1)
        item['Subcategory2'] = xp_dict.get(2)
        item['Subcategory3'] = xp_dict.get(3)
        item['Marca'] = product_json.get('data',{}).get('brand')
        item['Modelo'] = product_json.get('data',{}).get('attributes',{}).get('modelo')
        item['SKU'] = product_json.get('data',{}).get('sku')
        item['UPC'] = product_json.get('data',{}).get('ean')
        description = product_json.get('data',{}).get('description')
        attributes = product_json.get('data',{}).get('attributes')
        item['Item'] = product_json.get('data',{}).get('title')
        item['Item Characteristics'] = {'Descripción': description, 'Especificaciones': attributes}
        product_id = product_json.get('data',{}).get('id')
        item['URL SKU'] = f"https://www.sanborns.com.mx/producto/{product_id}/{product_json.get('data',{}).get('title_seo')}"
        try:
            item['Image'] = ','.join([image_product['url'] for image_product in product_json.get('data',{}).get('images')])
        except:
            item['Image'] = ''
        item['Price'] = product_json.get('data',{}).get('price')
        item['Sale Price'] = product_json.get('data',{}).get('sale_price')
        item['Shipment Cost'] = ""
        item['Sales Flag'] = product_json.get('data',{}).get('discount')
        item['Store ID'] = ""
        item['Store Name'] = ""
        item['Store Address'] = ""
        item['Stock'] = product_json.get('data',{}).get('stock')
        item['UPC WM'] = product_json.get('data',{}).get('ean')[0:-1].zfill(16)
        item['Final Price'] = min(item['Price'], item['Sale Price']) if item['Sale Price'] else item['Price']
        yield item
