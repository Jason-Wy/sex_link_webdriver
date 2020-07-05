from bs4 import BeautifulSoup

import requests
import os
import threading
import csv

base_url = 'http://www.605nn.com'


def request_html(url):
    # print("开始请求地址"+url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            name = 'url.html'
            try:
                url_list = url.split('?')
                if len(url_list) == 2:
                    name = url_list[1]
            except requests.RequestException:
                return None
            name = 'html/' + name
            # print(name)
            # write_to_file(name,response.text)
            return response.text
    except requests.RequestException:
        return None


def check_and_creat_dir(file_url):
    '''
    判断文件是否存在，文件路径不存在则创建文件夹
    :param file_url: 文件路径，包含文件名
    :return:
    '''
    file_gang_list = file_url.split('/')
    if len(file_gang_list) > 1:
        [fname, fename] = os.path.split(file_url)
        # print(fname,fename)
        if not os.path.exists(fname):
            os.makedirs(fname)
        else:
            return None
        pass
    else:
        return None


def write_to_file(name, content):
    file_name = name
    # print('写入文件信息'+file_name)
    check_and_creat_dir(file_name)
    with open(file_name, 'w', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(content)


def write_to_continue_file(name, content):
    file_name = name
    # #print('文件继续写入'+file_name)
    check_and_creat_dir(file_name)
    with open(file_name, 'a', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(content)


def beautiful_request_url(name, url, is_novel):
    '''解析网页详情数据'''
    html = request_html(url)
    soup = BeautifulSoup(html, 'lxml')
    temp_name = 'content/' + name + '.csv'

    try:
        if (is_novel == 0):
            '''
            是小说的话，我就找出列表，并且进入详情页，爬取出来所有小说内容
            '''
            next_file_list = soup.find_all(attrs={"class": "col-md-14 col-sm-16 col-xs-12 clearfix news-box"})
            '''本页数据循环'''
            for next_file_item in next_file_list:
                # #print(next_file_item)
                if '/?' in next_file_item.a['href']:
                    th2 = threading.Thread(target=detail_next_file,
                                           args=(name, next_file_item.a['title'], base_url + next_file_item.a['href']))
                    th2.start()

        elif (is_novel == 1):
            '''
                    如果是图片的话，我就把内容记录下，写入列表
                    '''
            items = soup.find_all(attrs={"class": "col-md-14 col-sm-16 col-xs-12 clearfix news-box"})
            for item in items:
                video_url = base_url + item.a['href']
                if "https://www.3970ok.com/promo#" in video_url:
                    continue
                try:
                    video_name = item.a['title']
                except:
                    print(item)
                    print("video name  报错")
                    video_name = '  '
                try:
                    video_time = item.find(attrs={"class": "xslist text-bg-c"}).text
                    video_time = video_time.split('  ')[-1]
                except:
                    print(item)
                    print("video_time  报错")
                    video_time = '  '

                write_to_continue_file(temp_name, [video_name, video_time, video_url])

        else:
            '''
            如果是视频的话，我就把内容记录下，写入列表
            '''
            items = soup.find_all(attrs={"class": "col-md-2 col-sm-3 col-xs-4"})
            for item in items:
                video_url = base_url + item.a['href']
                video_name = item.a['title']
                video_time = item.find(attrs={"align": "left"}).text
                video_type = item.find(attrs={"align": "right"}).text
                write_to_continue_file(temp_name, [video_name, video_time, video_url, video_type])
    except:
        import traceback
        traceback.print_exc()

    try:
        temp_list = str(soup.find(attrs={'class': "box-page clearfix"}))
        end_list = temp_list.split('/')
        current_page_list = end_list[0].split(':')
        current_page = current_page_list[1]

        end_page_list = end_list[1].split('页')
        end_page = end_page_list[0]
        # print('*' * 100)
        # print(name + '当前页数' + current_page)

        if current_page == end_page:
            # print('*' * 100)
            print(name + '已经查找结束')
            return None

        '''开启下一页的数据循环'''
        next_page_list = soup.find_all(attrs={"class": "pagelink_a"})
        for next_page_item in next_page_list:
            if next_page_item.text == '下一页':
                beautiful_request_url(name, 'http://www.605nn.com' + next_page_item['href'], is_novel)
                break
    except:
        print('*' * 100)
        print('查找结束，报错了，报错了')


def detail_next_file(root_file, name, url):
    name = 'file/' + root_file + '/' + name + '.txt'
    html = request_html(url)
    soup = BeautifulSoup(html, 'lxml')
    next_file_list = soup.find(attrs={"class": "details-content text-justify"})
    write_to_file(name, next_file_list.get_text('\n'))


if __name__ == "__main__":
    url = "http://www.605nn.com"
    html = request_html(url)
    soup = BeautifulSoup(html, 'lxml')
    temp_list_item = soup.find_all(attrs={"class": "row-item-content"})
    for item in temp_list_item:
        for item_two in item:
            # #print(item_two)
            if item_two != '\n':
                href_str = item_two.a['href']
                if item_two.a.text in ['都市色区', '迷情校园', '家庭乱来', '人妻艳妇', '武侠古典', '另类小说', '强暴虐待', '男同系列']:
                    th1 = threading.Thread(target=beautiful_request_url,
                                           args=(item_two.a.text, 'http://www.605nn.com' + href_str, 0))
                    th1.start()
                elif item_two.a.text in ['亚洲淫图', '欧美色图', '自拍偷窥', '卡通动漫', '美腿丝袜', '清纯另类', '乱伦熟女', '综合套图']:
                    th1 = threading.Thread(target=beautiful_request_url,
                                           args=(item_two.a.text, 'http://www.605nn.com' + href_str, 1))
                    th1.start()
                else:
                    th1 = threading.Thread(target=beautiful_request_url,
                                           args=(item_two.a.text, 'http://www.605nn.com' + href_str, 2))
                    th1.start()
