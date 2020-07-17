# import re
# import os
# import shutil
# import tarfile
# import json
# import requests
# from requests.exceptions import RequestException
# from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
# import re
# import time
# import urllib.request
# import datetime
# from bs4 import BeautifulSoup
import json
import urllib
from urllib.request import Request, urlopen
# import semantic_version
import pymysql
import re
from concurrent.futures import ThreadPoolExecutor
class getoutofloop(Exception): pass
# import datetime
# import itertools
# import os
# from collections import defaultdict
# import requests
# from requests.exceptions import RequestException
from DBUtils.PooledDB import PooledDB
from threading import RLock
import ssl

POOL_temp = PooledDB(
     creator = pymysql, #使用链接数据库的模块
     maxconnections = None,  #连接池允许的最大连接数，0和None表示没有限制
     mincached = 10, #初始化时，连接池至少创建的空闲的连接，0表示不创建
     maxcached = 0, #连接池空闲的最多连接数，0和None表示没有限制
     maxshared = 0, #连接池中最多共享的连接数量，0和None表示全部共享，ps:其实并没有什么用，因为pymsql和MySQLDB等模块中的threadsafety都为1，所有值无论设置多少，_maxcahed永远为0，所以永远是所有链接共享
     blocking = True, #链接池中如果没有可用共享连接后，是否阻塞等待，True表示等待，False表示不等待然后报错
     setsession = [],#开始会话前执行的命令列表
     ping = 0,#ping Mysql 服务端，检查服务是否可用
     host = 'localhost',
     port = 3306,
     user = 'root',
     password = '12345678',
     database = 'npmspider',
     charset = 'utf8'
 )

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

def all_project_name():
    name_list = []
    # SQL 查询语句
    sql = "SELECT id,project_name FROM npm_all_project_name where id >540000 and id<=550000"
    try:
        db =  POOL_temp.connection()
        # 执行sql语句
        allversionname = db.cursor()
        allversionname.execute(sql)
        data = allversionname.fetchall()  # 获取所有的数据
        allversionname.close()
        db.close()
    except:
        print("allnodejsname()  dberror")
    for i in data:
        project_id=i[0]
        project_name=i[1]
        templist=[]
        templist.append(project_id)
        templist.append(project_name)
        name_list.append(templist)
        # print("project_name: ",project_name)
        # print(filename);
    return name_list

def select_releases(project_name):
    releases_list = []
    # SQL 查询语句
    sql = "SELECT id,package_version FROM npm_all_releases where project_name='%s'" %(project_name)
    try:
        db =  POOL_temp.connection()
        # 执行sql语句
        allversionname = db.cursor()
        allversionname.execute(sql)
        data = allversionname.fetchall()  # 获取所有的数据
        allversionname.close()
        db.close()
    except:
        print("allnodejsname()  dberror")
    for i in data:
        project_id=i[0]
        project_version=i[1]
        templist=[]
        templist.append(project_id)
        templist.append(project_version)
        releases_list.append(templist)
        # print("project_name: ",project_name)
        # print(filename);
    return releases_list


def get_unpackedsize(projectname,projectid,versioninfo):
    try:
        # npm_url = "https://registry.npmjs.org" + '/' +
        npm_url = "https://registry.npm.taobao.org" + '/' + projectname
        # print(str(npm_url))
        items = get_results(str(npm_url))
        urlinfos = items["versions"]
        # times=items["time"]
        for urlinfo in urlinfos:
            version=urlinfo
            # time = times[version]
            # print("name: ",projectname," version: ", version)
            for load_versioninfo in versioninfo:
                lid=load_versioninfo[0]
                lversion=load_versioninfo[1]
                # print(lid,lversion)
                if version==lversion:
                    temp_versioninfo = urlinfos[version]
                    dependencies = []
                    unpackedsize=0
                    githubStatus='not in github'
                    try:
                        repositoryinfo = temp_versioninfo['repository']
                        repositoryurl = str(repositoryinfo['url'])
                        if 'github' in repositoryurl:
                            githubStatus='github'
                    except Exception:
                        pass
                    try:
                        distinfo = temp_versioninfo['dist']
                        unpackedsize = distinfo['size']
                    except Exception :
                        pass


                    # print(lid,projectname,lversion, unpackedsize)
                    try:
                        update_unpackedsize(lid, projectname, unpackedsize,githubStatus)
                        print("update_unpackedsize [ projectid:",projectid,projectname,'releaseid:',lid,lversion,unpackedsize,"] finished")
                    except Exception as e:
                        print("error! e1 ", e)
                        pass
                    break

    except Exception as e:
        print("error! e2",projectname,e)
        pass


def update_unpackedsize(id,projectname,unpackedSize,githubStatus):
    sql_update_unpackedsize = "update  npm_all_releases set unpacked_size='%s',repository='%s' where id='%s'" % (unpackedSize,githubStatus,id)
    # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)

    try:
        db_update_unpackedsize = POOL_temp.connection()
        # 执行sql语句
        unpackedsize_cursor = db_update_unpackedsize.cursor()
        unpackedsize_cursor.execute(sql_update_unpackedsize)
        db_update_unpackedsize.commit()
    except Exception as e:
        print("sql_update:", sql_update_unpackedsize)
        print("update_unpackedsize error ", e)
        db_update_unpackedsize.rollback()
    finally:
        db_update_unpackedsize.close()


# def insert_releases(projectname,version,creat_time):
#     # now = datetime.datetime.now()
#     # now = now.strftime("%Y-%m-%d %H:%M:%S")
#     sql_insert = "INSERT INTO npm_all_releases (project_name, package_version,creat_time) VALUES ('%s','%s','%s')" % (projectname, version,creat_time)
#     # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)
#     # db = pymysql.connect(host, user, password, db_name)
#
#     try:
#         db_insert_releases = POOL_temp.connection()
#         # 执行sql语句
#         insert_releases_cursor = db_insert_releases.cursor()
#         insert_releases_cursor.execute(sql_insert)
#         db_insert_releases.commit()
#     except Exception as e:
#         print("sql_update:", sql_insert)
#         print("npm_all_releases error ", e)
#         db_insert_releases.rollback()
#     finally:
#         db_insert_releases.close()
#
#     #
#     # try:
#     #     cursor_insertpypi = db.cursor()
#     #     # 执行sql语句
#     #     cursor_insertpypi.execute(sql_insert)
#     #     # 执行sql语句
#     #     db.commit()
#     #     cursor_insertpypi.close()
#     #     print("insert_releases  [ name:", projectname,"] FINISHED")
#     #     # print("update: ", git_name, " FINISHED")
#     # except Exception as e:
#     #     print("sql_update:", sql_insert)
#     #     print("npm_all_releases error ",e)
#     #     # 发生错误时回滚
#     #     db.rollback()
#     # db.close()
#
# def insert_dependencies(projectname,version,dependency,version_range,priority):
#     # now = datetime.datetime.now()
#     # now = now.strftime("%Y-%m-%d %H:%M:%S")
#     sql_insert_dependencies = "INSERT INTO npm_project_dependencies (project_name, package_version,dependency,version_range,priority) VALUES ('%s','%s','%s','%s','%s')" % (projectname,version,dependency,version_range,priority)
#     # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)
#     # db = pymysql.connect(host, user, password, db_name)
#
#     try:
#         db_insert_dependencies = POOL_temp.connection()
#         # 执行sql语句
#         dependencies_cursor = db_insert_dependencies.cursor()
#         dependencies_cursor.execute(sql_insert_dependencies)
#         db_insert_dependencies.commit()
#     except Exception as e:
#         print("sql_update:", sql_insert_dependencies)
#         print("insert_dependencies error ", e)
#         db_insert_dependencies.rollback()
#     finally:
#         db_insert_dependencies.close()
#
#     # try:
#     #     cursor_insertpypi = db.cursor()
#     #     # 执行sql语句
#     #     cursor_insertpypi.execute(sql_insert)
#     #     # 执行sql语句
#     #     db.commit()
#     #     cursor_insertpypi.close()
#     #     print("insert_dependencies  [ name:", projectname,"] FINISHED")
#     #     # print("update: ", git_name, " FINISHED")
#     # except Exception as e:
#     #     print("sql_update:", sql_insert)
#     #     print("npm_all_releases error ",e)
#     #     # 发生错误时回滚
#     #     db.rollback()
#     # db.close()

def main():


    names_list=all_project_name()
    for name_list in names_list:
        projectid=name_list[0]
        projectname=name_list[1]
        # print(projectid,projectname)
        releases_list=select_releases(projectname)
        versioninfo=[]
        for release_list in releases_list:
            releaseid=release_list[0]
            version=release_list[1]
            templist=[]
            templist.append(releaseid)
            templist.append(version)
            versioninfo.append(templist)
        try:
            # print(projectname, versioninfo,versioninfo)
            get_unpackedsize(projectname,projectid, versioninfo)
        except Exception as e:
            print("get_project_info error! ",e)
            pass


if __name__ == '__main__':
    # 数据库配置文件
    # host = "localhost"
    # host = "localhost"
    # user = "lzm"
    # password = "12345678"
    # db_name = "nodejsspider"
    # file_url = "D:/PycharmProjects/NodejsSpider/dependencyinfo.txt"
    # # 声明线程池
    # executor = ThreadPoolExecutor(5)
    main()