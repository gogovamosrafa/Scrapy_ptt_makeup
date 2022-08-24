from ptt_makeup.items import PostItem
import scrapy
from datetime import datetime
from scrapy.exceptions import CloseSpider


class PTTSpider(scrapy.Spider):
    # 設定爬取頁數最大值
    count = 218
    name = 'ptt_makeup'
    allowed_domains = ['ptt.cc']
    start_urls = ('https://www.ptt.cc/bbs/MakeUp/index.html',)

    # article from 2021/01 to 2022/8
    # https://www.ptt.cc/bbs/MakeUp/index3578.html
    def parse(self, response):
        hrefs = response.xpath(
            "//div[@class='r-ent']//div[@class='title']//a/@href")
        for href in hrefs:
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_page)
        next_page = response.css('.wide:nth-child(2)::attr(href)').get()
        url = response.urljoin(next_page.split('/')[-1])
        if self.count <= 0:
            raise CloseSpider('close it')
        self.count -= 1
        yield scrapy.Request(url, self.parse)

    def parse_page(self, response):
        item = PostItem()
        try:
            item['title'] = response.xpath(
                '//meta[@property="og:title"]/@content').extract()
            datetime2 = response.xpath(
                '//div[@id="main-content"]//span[@class="article-meta-value"]/text()')[-1].extract()
            item['date'] = datetime.strptime(datetime2, '%a %b %d %H:%M:%S %Y')
            contentList = response.css("#main-content::text").getall()
            text = ''
            for i in contentList:
                text += "".join(i.split())
            item['article'] = text
            comments = []
            for comment in response.xpath('//div[@class="push"]'):
                user = comment.css('span.push-userid::text')[0].extract()
                reply = comment.css('span.push-content::text')[0].extract()
                comments.append({'user': user, 'reply': reply})
            # 處理被截斷的推文
            # 如果有推文
            new_comments = []
            if comments:
                cat_resp = {
                    'user': comments[0]['user'],
                    'reply': comments[0]['reply']
                }
                for j in range(len(comments)):
                    if(comments[j]['user'] == cat_resp['user']):
                        if(comments[j]['reply']) != (cat_resp['reply']):
                            cat_resp['reply'].strip('\n')
                            cat_resp['reply'] += comments[j]['reply']
                    else:
                        new_comments.append(cat_resp)
                        cat_resp = {
                            'user': comments[j]['user'],
                            'reply': comments[j]['reply']
                        }
                new_comments.append(cat_resp)
            item['comment'] = new_comments
            item['url'] = response.url
            yield item

        except IndexError:
            pass
