from scrapy import Item, Field


class Tweet(Item):
    # id_ = Field()
    nickname = Field()
    username = Field()
    content = Field()
    video = Field()
    favorite_count = Field()
    retweet_count = Field()
    viewCount = Field()
    favorite_ratio = Field()
    created_at = Field()

class User(Item):
    id_ = Field()
    raw_data = Field()
