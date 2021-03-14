# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Entry(Item):
    title_id = Field()
    content = Field()
    author = Field()
    author_id = Field()
    likes = Field()
    id = Field()
    date = Field()

class Title(Item):
    id = Field()
    name = Field()