import scrapy
from scrapy import FormRequest
from ..items import LawyerSearchItem
from pyexcel_xlsx import get_data


class LawyerSpider(scrapy.Spider):
    name = "lawyer"

    allowed_domains = ["texasbar.com"]

    start_urls = [
        "https://www.texasbar.com/AM/Template.cfm?Section=Find_A_Lawyer&Template=/CustomSource/MemberDirectory/Search_Form_Client_Main.cfm"]

    lawyers = get_data('./Names.xlsx')
    lawyers_list = list(lawyers.values())[0]
    fixed_list = lawyers_list[1:len(lawyers_list)-1]

    def parse(self, response):
        for person in self.fixed_list:
            yield FormRequest.from_response(
                response,
                formname="SearchForm_Public",
                url="/AM/Template.cfm?Section=Find_A_Lawyer&Template=/CustomSource/MemberDirectory/Result_form_client.cfm",
                formdata={
                    "FirstName": person[1],
                    "LastName": person[0],
                },
                callback=self.parse_result,
                dont_filter=True,
            )
    def parse_result(self, response):
        item = LawyerSearchItem()
        try:
            city, rest = response.xpath('//div[@class="avatar-column"]/p[@class="address"]/text()')[1].extract().strip().split(',')
            state, zip_num = rest.split()
        except IndexError:
            city = 'No info'
            state = 'No info'
            zip_num = 'No info'
        try:
            item['firm_name'] = response.xpath('//div[@class="avatar-column"]/h5/text()')[0].extract().strip()
        except IndexError:
            item['firm_name'] = 'No info'
        try:
            item['phone'] = response.xpath('//div[@class="contact"]/a[2]/text()')[0].extract().strip().split(':')[1].strip()
        except IndexError:
            item['phone'] = 'No info'
        try:
            item['name'] = response.xpath('//div[@class="avatar-column"]/h3/a/span[@class="given-name"][1]/text()')[0].extract().strip()
        except IndexError:
            item['name'] = 'No info'
        try:
            item['address'] = response.xpath('//div[@class="avatar-column"]/p[@class="address"]/text()')[0].extract().strip()
        except IndexError:
            item['address'] = 'No info'
        item['city'] = city
        item['state'] = state
        item['zip_num'] = zip_num
        item['areas'] = response.xpath('//div[@class="avatar-column"]/p[@class="areas"]/text()')[1].extract().strip()
        yield item

