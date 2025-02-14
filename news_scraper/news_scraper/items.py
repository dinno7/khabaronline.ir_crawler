# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import datetime

import jdatetime
import scrapy


def persian_date_str_serializer(persian_date_str):
    date_part, time_part = persian_date_str.split(" - ")
    jalali_date = jdatetime.datetime.strptime(date_part, "%d %B %Y")
    hour, minute = map(int, time_part.split(":"))
    return str(jalali_date.replace(hour=hour, minute=minute))


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    processed_title = scrapy.Field()
    summery = scrapy.Field()
    summery_image = scrapy.Field()
    content_text = scrapy.Field()
    processed_content_text = scrapy.Field()
    news_code = scrapy.Field()
    news_short_url = scrapy.Field()
    tags = scrapy.Field()
    rate_stars = scrapy.Field()
    publish_date = scrapy.Field(serializer=persian_date_str_serializer)
    publish_persian_date = scrapy.Field()
