import os
from urllib.parse import urljoin, quote, unquote

import requests
import xlrd

# 获取下载的文件的文件名
def get_file_name(file_url, headers, default_name):
    filename = ''
    if 'Content-Disposition' in headers and headers['Content-Disposition']:
        disposition_split = headers['Content-Disposition'].split(';')
        if len(disposition_split) > 1:
            if disposition_split[1].strip().lower().startswith('filename='):
                file_name = disposition_split[1].split('=')
                if len(file_name) > 1:
                    filename = unquote(file_name[1])
    if not filename and os.path.basename(file_url):
        filename = os.path.basename(file_url).split("?")[0]
    if not filename:
        return default_name
    return default_name + os.path.splitext(filename)[1]

def download_simple_file(file_url, path, user_name):
    try:
        r = requests.get(file_url)
        name = get_file_name(file_url, r.headers, user_name).strip('"')
        file_name = os.path.join(path, name)
        file_name= file_name.replace(':','-')
        with open(file_name, 'wb') as f:
            f.write(r.content)
        print("%s保存成功" % file_name)
    except:
        file_name = os.path.join(path, user_name)
        file_name= file_name.replace(':','-')
        with open(file_name + '.txt','a') as f:
            f.write(file_url)
        print("%s下载失败" % file_name)

def download_file(file_path):
    base_dir = os.path.dirname(file_path)
    download_file_path = "./videostar下载内容"
    if not os.path.exists(download_file_path):
        os.makedirs(download_file_path)
    excel = xlrd.open_workbook(file_path)
    sheets = excel.sheets()
    for sheet in sheets:
        for rx in range(1, sheet.nrows):  # 因为第一行是表头，所以从1开始迭代，跳过表头
            try:
                row = sheet.row(rx)
                user_name = row[1].value.strip() + '_' + str(xlrd.xldate.xldate_as_datetime(row[8].value,0))
                url = row[3].value.strip()
                print("开始下载%s - %s" % (user_name, url))
                download_simple_file(url, download_file_path, user_name) 
            except Exception as e:
                print(e)
                raise e  # 如果确认执行不会保存可以注释

download_file('./export_data/videostar.xlsx')