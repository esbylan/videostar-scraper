# 链接下载脚本

import os, logging, json
from scrapy.utils.project import get_project_settings
import csv

from TweetScraper.items import Tweet, User
from TweetScraper.utils import mkdirs

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import requests
import datetime


logger = logging.getLogger(__name__)
SETTINGS = get_project_settings()

def write_to_csv(item):
    writer = csv.writer(open(SETTINGS['EXPORT_URI'], 'a',encoding='utf-8-sig'), lineterminator='\n')
    writer.writerow([item[key] for key in item.keys()])

def writeArticle(item):
    wp = Client('http://wotagei.online/xmlrpc.php', 'lty', 'lty')

    title= item['username'] + '_' + (datetime.datetime.strptime(item['created_at'],'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H-%M-%S') 
    coverUrl = item['cover'] #上传的图片文件路径
    imgData = requests.get(coverUrl)
    # prepare metadata
    data = {
            'name': title + '.jpg',
            'type': 'image/jpeg',  # mimetype
    }

    data['bits'] = xmlrpc_client.Binary(imgData.content)
    response = wp.call(media.UploadFile(data))
    attachment_id = response['id']
    videoUrl = item['video']
    print('正在下载'+ videoUrl)
    videoData = requests.get(videoUrl)
    videoDataObj = {
            'name': title+ '.mp4',
            'type': 'video/mp4',  # mimetype
    }
    videoDataObj['bits'] = xmlrpc_client.Binary(videoData.content)
    videoOssData = wp.call(media.UploadFile(videoDataObj))

    post = WordPressPost()
    post.title = title
    post.date= datetime.datetime.strptime(item['created_at'],'%Y-%m-%d %H:%M:%S')
    post.content = '<!-- wp:aiovg/video {"src":"'+videoOssData['url']+'","autoplay":true} /-->'
    post.post_status = 'publish'  #文章状态，不写默认是草稿，private表示私密的，draft表示草稿，publish表示发布
    post.terms_names = {
        'post_tag': ['サンダースネーク'], #文章所属标签，没有则自动创建
        'category': ['ヲタ芸'] #文章所属分类，没有则自动创建
    }
    post.thumbnail = attachment_id #缩略图的id
    post.id = wp.call(posts.NewPost(post))
    print('已录入'+ title)
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
          writeArticle(item)
          # write_to_csv(item)
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

        # elif isinstance(item, User):
        #     savePath = os.path.join(self.saveUserPath, item['id_'])
        #     if os.path.isfile(savePath):
        #         pass # simply skip existing items
                # logger.debug("skip user:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update user:%s"%item['id_'])
            # else:
            #     self.save_to_file(item, savePath)
            #     logger.debug("Add user:%s" %item['id_'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))


    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False)
    
    
