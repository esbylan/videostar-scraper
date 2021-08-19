from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
import requests
import time
import datetime
# wp = Client('http://wotagei.online/xmlrpc.php', 'lty', 'lty')

# title= 'xxx ' + time.strftime( '%Y-%m-%d %H-%M-%S',time.strptime('2021-08-17 14:00:01','%Y-%m-%d %H:%M:%S'))
# coverUrl = 'https://pbs.twimg.com/ext_tw_video_thumb/1294148623375065088/pu/img/THXGFLZpBtiNTCJV.jpg' #上传的图片文件路径
# imgData = requests.get(coverUrl)
# # prepare metadata
# data = {
#         'name': title + '.jpg',
#         'type': 'image/jpeg',  # mimetype
# }

# data['bits'] = xmlrpc_client.Binary(imgData.content)
# response = wp.call(media.UploadFile(data))
# attachment_id = response['id']
# videoUrl = 'https://video.twimg.com/ext_tw_video/1294148623375065088/pu/vid/1280x720/2jnb_OQ7XKpf-MIP.mp4?tag=10'
# videoData = requests.get(videoUrl)
# videoDataObj = {
#         'name': title+ '.mp4',
#         'type': 'video/mp4',  # mimetype
# }
# videoDataObj['bits'] = xmlrpc_client.Binary(videoData.content)
# videoOssData = wp.call(media.UploadFile(videoDataObj))

# post = WordPressPost()
# post.title = title
# post.date= datetime.datetime.strptime('2021-08-17 13:30:01','%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=8)
# post.content = '<!-- wp:aiovg/video {"src":"'+videoOssData['url']+'","autoplay":true} /-->'
# post.post_status = 'publish'  #文章状态，不写默认是草稿，private表示私密的，draft表示草稿，publish表示发布
# post.terms_names = {
#     'post_tag': ['サンダースネーク'], #文章所属标签，没有则自动创建
#     'category': ['ヲタ芸'] #文章所属分类，没有则自动创建
# }
# post.thumbnail = attachment_id #缩略图的id
# post.id = wp.call(posts.NewPost(post))