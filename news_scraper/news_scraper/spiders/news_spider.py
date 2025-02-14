import random

import scrapy
from news_scraper.items import NewsItem


class NewsSpiderSpider(scrapy.Spider):
    name = "news-spider"
    custom_settings = {
        "FEED_EXPORT_ENCODING": "utf-8",
        "FEEDS": {"news.json": {"format": "json", "overwrite": True}},
    }
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.6",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.86",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.6",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.6",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.16",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.6",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.6",
    ]
    to_page = 25
    cur_level = 1
    base_url = "https://www.khabaronline.ir"
    allowed_domains = ["www.khabaronline.ir"]
    start_urls = ["https://www.khabaronline.ir/page/archive.xhtml?tp=74"]

    def parse(self, response):
        tech_news = response.css("#box202>div>ul>li")
        for news in tech_news:
            item_url = self.base_url + news.css("div.desc>h3>a::attr(href)").get()
            yield response.follow(
                item_url,
                callback=self.parse_news_page,
                headers={"User-Agent": random.choice(self.user_agent_list)},
            )

        next_btn = response.css("#box202>footer>div>ul>li:last-child>a")
        if self.cur_level < self.to_page:
            self.cur_level += 1
            next_page_url = self.base_url + next_btn.attrib["href"]
            print("💀 next url >> ", next_page_url)
            yield response.follow(
                next_page_url,
                callback=self.parse,
                headers={"User-Agent": random.choice(self.user_agent_list)},
            )

    def parse_news_page(self, response):
        contents = ""
        for text in response.css(
            "div.item-body p::text, div.item-body h1::text, div.item-body h2::text, div.item-body h3::text, div.item-body h4::text, div.item-body h5::text, div.item-body h6::text"
        ).getall():
            contents += text.strip() + "\n"

        news_item = NewsItem()
        news_item["title"] = response.css(
            "#item>.item-header>div.item-title>h1>a::text"
        ).get()
        news_item["processed_title"] = response.css(
            "#item>.item-header>div.item-title>h1>a::text"
        ).get()
        news_item["summery"] = response.css("#item>div.item-summary>p::text").get()
        news_item["summery_image"] = response.css(
            "#item>div.item-summary>figure>img::attr(src)"
        ).get()
        news_item["content_text"] = contents
        news_item["processed_content_text"] = contents
        news_item["news_code"] = response.css(
            "#item>div.item-body div.item-code span::text"
        ).get()
        news_item["news_short_url"] = (
            "https://"
            + response.css(
                "#item>div.item-footer.row .short-link-container input::attr(value)"
            ).get()
        )
        news_item["tags"] = response.css(
            "#item>section.box.tags>div>ul>li>a::text"
        ).getall()
        news_item["rate_stars"] = response.css(
            "#item>div.item-header>div.item-nav div.rating-stars>ul::attr(data-value)"
        ).get()
        news_item["publish_date"] = response.css(
            "#item>div.item-header>div.item-nav div.item-date>span::text"
        ).get()
        news_item["publish_persian_date"] = response.css(
            "#item>div.item-header>div.item-nav div.item-date>span::text"
        ).get()

        yield news_item
