#https://api.github.com/search/repositories?q=nodejs+language:JavaScript&page=1&pe r_page=100
import requests
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import re
import time
import urllib.request
import datetime
from bs4 import BeautifulSoup
import json
import urllib
from urllib.request import Request, urlopen
import pymysql
import ssl
def get_page(url):
    #Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36
    # headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/74.0.3729.157 Safari/537.36'}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'}
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def get_results(url):

    headers = {
               'User-Agent': 'Mozilla/5.0',
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': ' token 30ad34440e1bdc0016db7ae316c3d4a1d75d18c1'
               }
    context = ssl._create_unverified_context()
    req = Request(url, headers=headers)
    response = urlopen(req,context = context).read()
    result = json.loads(response.decode())
    return result


def find_all_projectname():
    url="https://skimdb.npmjs.com/registry/_all_docs"
    try:
        # items = get_results(url)
        items = get_results(url)
        rows = items['rows']
        # file_url = "D:/PycharmProjects/NodejsSpider/projectnameinfo3.txt"
        # with open(file_url, 'a', encoding='utf-8') as f:
        #     f.write(str(rows))
        i = 1162384
        for row in rows:
            i = i + 1
            projectname=row['id']
            count=find_project_count(projectname)
            if count==0 or count=='0':
                insert_all_projectname(projectname,i)
        # projectinfos=item['id']
        # with open(file_url, 'a', encoding='utf-8') as f:
        #  f.write(str(projectinfos))
        # i=1
        # for projectinfo in projectinfos:
        #     i=i+1
        #     print("num: ",i," name: ",projectinfo)
    except Exception as e:
        print("error!",e)
#
# def find_githubinfo():
#     for num in range(1,11):
#         list=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
#         for j in range(0, 26):
#             api_url = "https://api.github.com/search/repositories?q=npm+%s+language:JavaScript&page=%s&per_page=100"% (list[j],num)
#             print(api_url)
#             try:
#                 html_url_packagejson=""
#                 items = get_results(api_url)
#                 # print(items)
#                 item=items['items']
#                 for i in item:
#                     print(num)
#                     git_html_url = i['html_url']
#                     git_name = i['name']
#                     git_url = i['url']
#                     if find_htmlurl_count(git_name) == 0:
#                         html_url_packagejson = git_html_url + "/blob/master/package.json"
#                         date_html = get_page(html_url_packagejson)
#                         pattern_github = ""
#                         if date_html != "" and date_html is not None:
#                             # print(date_html)
#                             peerDependencies_status = "0"
#                             if "peerDependencies" in date_html:
#                                 print("git_html_url", git_html_url)
#                                 print("git_name: " + git_name)
#                                 print("git_url: " + git_url)
#                                 print("html_url_packagejson: " + html_url_packagejson)
#                                 peerDependencies_status = "1"
#                             else:
#                                 print("no peerDependencies")
#                         insert_githubinfo(git_name, git_html_url, git_url, html_url_packagejson,
#                                       peerDependencies_status)
#                     print("***************************************************")
#
#
#                     # print("open_user: " + open_user)
#
#             except Exception as exp:
#                 print("get search error",exp)
#
#
#
def insert_all_projectname(projectname,num):
    now = datetime.datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_insert = "INSERT INTO npm_all_project_name (project_name, insertdate) VALUES ('%s','%s')" % (projectname, now)
    # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)
    db = pymysql.connect(host, user, password, db_name)
    try:
        cursor_insertpypi = db.cursor()
        # 执行sql语句
        cursor_insertpypi.execute(sql_insert)
        # 执行sql语句
        db.commit()
        cursor_insertpypi.close()
        print("insert  [num:", num, " name:", projectname,"] FINISHED")
        # print("update: ", git_name, " FINISHED")
    except:
        print("sql_update:", sql_insert)
        print("insert_all_projectname error")
        # 发生错误时回滚
        db.rollback()
    db.close()
#
#
#查询该html_url是否存在，返回查询数量
def find_project_count(project_name):
    sql = "SELECT COUNT(*) FROM npm_all_project_name WHERE project_name = '%s'" % (project_name)
    try:
        # 执行sql语句
        db_v = pymysql.connect(host, user, password, db_name)
        cursor_find_versionname = db_v.cursor()
        cursor_find_versionname.execute(sql)
        nums = cursor_find_versionname.fetchone()
        cursor_find_versionname.close()
        db_v.close()
        num = nums[0]
        print("num: ",num)
        return num
    except Exception:
        print("find_versionname() dberror")


def main():

    find_all_projectname()
    # do_find_githubinfo("autocommand")

if __name__ == '__main__':

    #数据库配置文件
    # host = "localhost"
    host = "localhost"
    user = "root"
    password = "12345678"
    db_name = "npmspider"
    #声明线程池
    executor = ThreadPoolExecutor(5)
    main()
