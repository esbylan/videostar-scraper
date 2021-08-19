import re, json, logging
from urllib.parse import quote
import time
from scrapy import http
from scrapy.spiders import CrawlSpider
from scrapy.shell import inspect_response
from scrapy.core.downloader.middleware import DownloaderMiddlewareManager
from scrapy_selenium import SeleniumRequest, SeleniumMiddleware

from TweetScraper.items import Tweet, User


logger = logging.getLogger(__name__)


class TweetScraper(CrawlSpider):
    name = 'TweetScraper'
    allowed_domains = ['twitter.com']

    def __init__(self, query=''):
        self.url = (
            f'https://api.twitter.com/2/search/adaptive.json?'
            f'include_profile_interstitial_type=1'
            f'&include_blocking=1'
            f'&include_blocked_by=1'
            f'&include_followed_by=1'
            f'&include_want_retweets=1'
            f'&include_mute_edge=1'
            f'&include_can_dm=1'
            f'&include_can_media_tag=1'
            f'&skip_status=1'
            f'&cards_platform=Web-12'
            f'&include_cards=1'
            f'&include_ext_alt_text=true'
            f'&include_quote_count=true'
            f'&include_reply_count=1'
            f'&tweet_mode=extended'
            f'&include_entities=true'
            f'&include_user_entities=true'
            f'&include_ext_media_color=true'
            f'&include_ext_media_availability=true'
            f'&send_error_codes=true'
            f'&simple_quoted_tweet=true'
            f'&query_source=typed_query'
            f'&pc=1'
            f'&spelling_corrections=1'
            f'&ext=mediaStats%2ChighlightedLabel'
            f'&count=20'
            f'&tweet_search_mode=live'
        )
        self.url = self.url + '&q={query}'
        self.query = query
        self.num_search_issued = 0
        # regex for finding next cursor
        self.cursor_re = re.compile('"(scroll:[^"]*)"')


    def start_requests(self):
        """
        Use the landing page to get cookies first
        """
        yield SeleniumRequest(url="https://twitter.com/explore", callback=self.parse_home_page)


    def parse_home_page(self, response):
        """
        Use the landing page to get cookies first
        """
        # inspect_response(response, self)
        self.update_cookies(response)
        for r in self.start_query_request():
            yield r


    def update_cookies(self, response):
        driver = response.meta['driver']
        try:
            self.cookies = driver.get_cookies()
            self.x_guest_token = driver.get_cookie('gt')['value']
            # self.x_csrf_token = driver.get_cookie('ct0')['value']
        except:
            logger.info('cookies are not updated!')

        self.headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'x-guest-token': self.x_guest_token,
            # 'x-csrf-token': self.x_csrf_token,
        }
        print('headers:\n--------------------------\n')
        print(self.headers)
        print('\n--------------------------\n')



    def start_query_request(self, cursor=None):
        """
        Generate the search request
        """
        if cursor:
            url = self.url + '&cursor={cursor}'
            url = url.format(query=quote(self.query), cursor=quote(cursor))
        else:
            url = self.url.format(query=quote(self.query))
        request = http.Request(url, callback=self.parse_result_page, cookies=self.cookies, headers=self.headers)
        yield request

        self.num_search_issued += 1
        if self.num_search_issued % 100 == 0:
            # get new SeleniumMiddleware            
            for m in self.crawler.engine.downloader.middleware.middlewares:
                if isinstance(m, SeleniumMiddleware):
                    m.spider_closed()
            self.crawler.engine.downloader.middleware = DownloaderMiddlewareManager.from_crawler(self.crawler)
            # update cookies
            yield SeleniumRequest(url="https://twitter.com/explore", callback=self.update_cookies, dont_filter=True)


    def parse_result_page(self, response):
        """
        Get the tweets & users & next request
        """
        # inspect_response(response, self)

        # handle current page
        data = json.loads(response.text)
        for item in self.parse_tweet_item(data['globalObjects']['tweets'],data['globalObjects']['users']):
            yield item
        for item in self.parse_user_item(data['globalObjects']['users']):
            yield item

        # get next page
        cursor = self.cursor_re.search(response.text).group(1)
        for r in self.start_query_request(cursor=cursor):
            yield r


    def parse_tweet_item(self, items,userObj):
        for k,v in items.items():
            # assert k == v['id_str'], (k,v)
            url = ''
            cover=''
            try:
              videoArr = []
              for video in v['extended_entities']['media'][0]['video_info']['variants']:
                if video['content_type'] == 'video/mp4':
                  videoArr.append(video) 
              bitrateArr= [item['bitrate'] for item in videoArr]
              maxBitrateIndex = bitrateArr.index(max(bitrateArr))
              url = videoArr[maxBitrateIndex]['url']
              cover = v['extended_entities']['media'][0]['media_url_https']
              tweet = Tweet()
              # tweet['id_'] = k
              tweet['nickname'] = userObj[v['user_id_str']]['name']
              tweet['username'] = '@'+userObj[v['user_id_str']]['screen_name']
              tweet['content'] = v['full_text']
              tweet['cover'] = cover
              tweet['video'] = url
              tweet['favorite_count'] = v['favorite_count']
              tweet['retweet_count'] = v['retweet_count'] + v['quote_count']
              try:
                tweet['viewCount'] = int(v['extended_entities']['media'][0]['ext']['mediaStats']['r']['ok']['viewCount'])
              except:
                tweet['viewCount'] = 0
              tweet['favorite_ratio'] = str((tweet['favorite_count'] / tweet['viewCount'] if tweet['viewCount'] != 0 else 0)*100) + '%'
              tweet['created_at'] = self.cst_to_str(v['created_at'])
            
              yield tweet
            except:
              logger.info('find a tweet without video')


    def parse_user_item(self, items):
        for k,v in items.items():
            # assert k == v['id_str'], (k,v)
            user = User()
            user['id_'] = k
            user['raw_data'] = v
            yield user


    def cst_to_str(self,cstTime):

      tempTime = time.strptime(cstTime,'%a %b %d %H:%M:%S +0000 %Y')

      resTime = time.strftime("%Y-%m-%d %H:%M:%S",tempTime)

      return resTime 