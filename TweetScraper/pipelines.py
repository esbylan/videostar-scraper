# 链接下载脚本

import os, logging, json
from scrapy.utils.project import get_project_settings
import csv

from TweetScraper.items import Tweet, User
from TweetScraper.utils import mkdirs


logger = logging.getLogger(__name__)
SETTINGS = get_project_settings()

def write_to_csv(item):
    writer = csv.writer(open(SETTINGS['EXPORT_URI'], 'a',encoding='utf-8-sig'), lineterminator='\n')
    writer.writerow([item[key] for key in item.keys()])

class SaveToFilePipeline(object):
    if os.path.isfile(SETTINGS['EXPORT_URI']):
      os.remove(SETTINGS['EXPORT_URI']) 
    # 设置文件第一行的字段名，注意要跟spider传过来的字典key名称相同
    # fieldnames = ["昵称","推特号","推文内容","视频地址","发推日期"]
    # writer = csv.writer(open(SETTINGS['FEED_URI'], 'a'), lineterminator='\n')
    # writer.writerow(["昵称","推特号","推文内容","视频地址","发推日期"]) 
    ''' pipeline that save data to disk '''

    def __init__(self):
        self.saveTweetPath = SETTINGS['SAVE_TWEET_PATH']
        self.saveUserPath = SETTINGS['SAVE_USER_PATH']
        mkdirs(self.saveTweetPath) # ensure the path exists
        mkdirs(self.saveUserPath)


    def process_item(self, item, spider):
        if isinstance(item, Tweet):
          write_to_csv(item)
            # savePath = os.path.join(self.saveTweetPath, item['id_'])
            # if os.path.isfile(savePath):
            #     pass # simply skip existing items
                # logger.debug("skip tweet:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update tweet:%s"%item['id_'])
            # else:
            #     self.save_to_file(item,savePath)
            #     logger.debug("Add tweet:%s" %item['id_'])

        elif isinstance(item, User):
            savePath = os.path.join(self.saveUserPath, item['id_'])
            if os.path.isfile(savePath):
                pass # simply skip existing items
                # logger.debug("skip user:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update user:%s"%item['id_'])
            else:
                self.save_to_file(item, savePath)
                logger.debug("Add user:%s" %item['id_'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))


    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False)