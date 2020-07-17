# https://api.github.com/search/repositories?q=nodejs+language:JavaScript&page=1&pe r_page=100
# import requests
# from requests.exceptions import RequestException
# from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
# import re
# import time
# import urllib.request
# import datetime
# from bs4 import BeautifulSoup
# import json
# import urllib
# from urllib.request import Request, urlopen
import pymysql
# import grab_npm_tars
# import npmdependency
from DBUtils.PooledDB import PooledDB
import semantic_version
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
class getoutofloop(Exception): pass


POOL_temp = PooledDB(
     creator = pymysql, #使用链接数据库的模块
     maxconnections = None,  #连接池允许的最大连接数，0和None表示没有限制
     mincached = 10, #初始化时，连接池至少创建的空闲的连接，0表示不创建
     maxcached = 0, #连接池空闲的最多连接数，0和None表示没有限制
     maxshared = 0, #连接池中最多共享的连接数量，0和None表示全部共享，ps:其实并没有什么用，因为pymsql和MySQLDB等模块中的threadsafety都为1，所有值无论设置多少，_maxcahed永远为0，所以永远是所有链接共享
     blocking = True, #链接池中如果没有可用共享连接后，是否阻塞等待，True表示等待，False表示不等待然后报错
     setsession = [],#开始会话前执行的命令列表
     ping = 0,#ping Mysql 服务端，检查服务是否可用
     host = '219.216.64.227',
     port = 3306,
     user = 'root',
     password = '12345678',
     database = 'npmspider',
     charset = 'utf8'
 )

# # 查询文件名
# def all_project_name():
#     name_list = []
#     # SQL 查询语句
#     sql = "SELECT id,project_name FROM npm_all_project_name where id >=1 and id <=1000"
#     try:
#         db =  POOL_temp.connection()
#         # 执行sql语句
#         allversionname = db.cursor()
#         allversionname.execute(sql)
#         data = allversionname.fetchall()  # 获取所有的数据
#         allversionname.close()
#         db.close()
#     except:
#         print("allnodejsname()  dberror")
#     for i in data:
#         project_id=i[0]
#         project_name=i[1]
#         templist=[]
#         templist.append(project_id)
#         templist.append(project_name)
#         name_list.append(templist)
#         # print("project_name: ",project_name)
#         # print(filename);
#     return name_list

# 查询文件名
def all_project_name():
    name_list = []
    # SQL 查询语句
    sql = "select * from npm_all_project_name where dependencies_num != '0' and dependencies_num is not null  and project_name in " \
          "(select project_name from npm_all_releases where  repository='github' group by project_name) ORDER BY dependencies_num DESC limit 10000"
    # sql="select  id,project_name from npm_all_project_name where dependencies_num != '0' and dependencies_num is not null  ORDER BY dependencies_num DESC limit 50000"

    # sql = "SELECT id,project_name FROM npm_all_project_name where project_name in (select project_name from npm_all_releases where  unpacked_size>30000 and repository='github' group by project_name) and id >230000 limit 1000"
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

# 查询文件名最新版本
def latest_version(project_name):
    name_list = []
    # SQL 查询语句
    sql = "SELECT package_version,unpacked_size FROM npm_all_releases where project_name='%s' ORDER BY creat_time DESC limit 1" % (project_name)
    try:
        db_latest_version =  POOL_temp.connection()
        # 执行sql语句
        latest_version_cursor = db_latest_version.cursor()
        latest_version_cursor.execute(sql)
        latest_version_datas = latest_version_cursor.fetchone()  # 获取所有的数据
        temp_version=''
        temp_unpacked_size=''
        if latest_version_datas is not None:
            temp_version = latest_version_datas[0]
            temp_unpacked_size=latest_version_datas[1]
        latest_version_cursor.close()
        db_latest_version.close()
    except:
        print("all_project_name()  dberror")
    if temp_unpacked_size == '' or temp_unpacked_size is None:
        temp_unpacked_size=0
    return temp_version,temp_unpacked_size



# 查询文件版本列表
def get_version_list(project_name):
    version_list = []
    # SQL 查询语句
    sql = "SELECT package_version FROM npm_all_releases where project_name='%s' ORDER BY creat_time DESC" % (project_name)
    try:
        db_get_version_list =  POOL_temp.connection()
        # 执行sql语句
        allversionname = db_get_version_list.cursor()
        allversionname.execute(sql)
        datas = allversionname.fetchall()  # 获取所有的数据
        temp_version=''
        if datas is not None:
            temp_version = datas[0]
        allversionname.close()
        db_get_version_list.close()
    except:
        print("get_version_list()  dberror")
    for data in datas:
        version_list.append(data[0])
    return version_list

# 查询文件名ID
def get_id(project_name):
    id_data = 0
    # SQL 查询语句
    sql = "SELECT id FROM npm_all_project_name where project_name='%s' limit 1" % (project_name)
    try:
        db_select_id =  POOL_temp.connection()
        # 执行sql语句
        projectid_cursor = db_select_id.cursor()
        projectid_cursor.execute(sql)
        id_datas = projectid_cursor.fetchone()  # 获取所有的数据
        temp_version=''
        if id_datas is not None:
            id_data = id_datas[0]
        projectid_cursor.close()
        db_select_id.close()
    except:
        print("get_id()  dberror")
    return id_data

# 查询依赖
def get_dependencies(project_name,package_version):
    datas=''
    project_id=get_id(project_name)
    table_name=""
    if project_id<200000:
        table_name = "npm_project_dependencies"
    elif project_id>=200000 and project_id<=400000:
        table_name = "npm_project_dependencies_02"
    elif project_id>=400000 and project_id<=600000:
        table_name = "npm_project_dependencies_03"
    elif project_id>=600000 and project_id<=800000:
        table_name = "npm_project_dependencies_04"
    elif project_id>=800000 and project_id<=1000000:
        table_name = "npm_project_dependencies_05"
    elif project_id>=1000000 :
        table_name = "npm_project_dependencies_06"
    sql = "SELECT dependency,version_range FROM "+table_name+" where project_name='%s' and package_version='%s' ORDER BY priority ASC" % (project_name, package_version)
    dependencies_list = []
    # SQL 查询语句
    # sql = "SELECT dependency,version_range FROM npm_project_dependencies where project_name='%s' and package_version='%s' ORDER BY priority ASC" % (project_name,package_version)
    try:
        db = POOL_temp.connection()
        # 执行sql语句
        dependenciesdb = db.cursor()
        dependenciesdb.execute(sql)
        datas = dependenciesdb.fetchall()  # 获取所有的数据
        dependenciesdb.close()
    except Exception as e:
        print("get_dependencies()  dberror",e)
    finally:
        db.close()
    if datas!='' and datas is not None:
        for data in datas:
            project_dependency = data[0]
            project_version_range = data[1]
            templist = []
            templist.append(project_dependency)
            templist.append(project_version_range)
            dependencies_list.append(templist)
        # print("project_name: ",project_name)
        # print(filename);
    return dependencies_list


# 查询依赖包大小
def get_unpackedsize(projectname, projectversion):
    # SQL 查询语句
    temp_size = 0
    sql = "SELECT unpacked_size FROM npm_all_releases where project_name='%s' and package_version='%s' limit 1" % (projectname,projectversion)
    try:
        db_unpacked_size =  POOL_temp.connection()
        # 执行sql语句
        unpacked_size_cursor = db_unpacked_size.cursor()
        unpacked_size_cursor.execute(sql)
        unpacked_size_datas = unpacked_size_cursor.fetchone()  # 获取所有的数据
        # temp_size=0
        if unpacked_size_datas is not None:
            temp_size = unpacked_size_datas[0]
        unpacked_size_cursor.close()
        db_unpacked_size.close()
    except:
        print("all_project_name()  dberror")
    return temp_size




def get_dep(projectname,version,dep_num):
    # 1为直接依赖
    if dep_num==0:
        direct_dependency = 1
    else:
        direct_dependency=0
    if dep_num>10:
        return
    stra = '-'
    for numa in range(dep_num):
        stra = stra + '-'
    print(stra, projectname, version)

    temp_dependencies_list=[]
    dep_list=[]
    dependencies_list = get_dependencies(projectname, version)
    for dependency in dependencies_list:
        dependencyname = dependency[0]
        version_range = dependency[1].replace("< ", "<").replace("<= ", "<=").replace("> ", ">").replace(">= ", ">=")
        # print(projectname, version,dependencyname,version_range)
        dp_status = 0
        for dp_temp_top in TOP_dependencies_list:
            dp_temp_top_name = dp_temp_top["dep_name"]
            dp_temp_top_verison = dp_temp_top["dep_version"]
            if dependencyname==dp_temp_top_name and check_version_range(dp_temp_top_verison, version_range) is not True:
                dp_status=1
                # print(dp_status,dependencyname, version_range)
            elif dependencyname==dp_temp_top_name and check_version_range(dp_temp_top_verison, version_range):
                dp_status=2
                # print(dp_status, dependencyname, version_range)

        if dp_status==0:
            version_list = get_version_list(dependencyname)
            try:
                for temp_version in version_list:
                    if check_version_range(temp_version, version_range):
                        dep_obj = {"dep_name": dependencyname, "dep_version": temp_version,"dep_version_range": version_range,"direct_dependency":direct_dependency}
                        TOP_dependencies_list.append(dep_obj)
                        dep_list.append(dep_obj)
                        raise getoutofloop()
            except getoutofloop:
                pass
        elif dp_status==1:
            version_list = get_version_list(dependencyname)
            try:
                for temp_version in version_list:
                    if check_version_range(temp_version, version_range):
                        # print(dependencyname,temp_version, version_range)
                        dep_obj = {"dep_name": dependencyname, "dep_version": temp_version,"dep_version_range": version_range,"direct_dependency":direct_dependency}
                        OTHER_dependencies_list.append(dep_obj)
                        dep_list.append(dep_obj)
                        raise getoutofloop()
            except getoutofloop:
                pass
    # 第二次深度优先，递归遍历每项依赖
    dep_num = dep_num + 1
    for dependencytemp_02 in dep_list:
        tempname = dependencytemp_02["dep_name"]
        tempversion = dependencytemp_02["dep_version"]
        get_dep(tempname, tempversion, dep_num)


def check_version_range(version,versionrange):
    try:
        return semantic_version.Version(version) in semantic_version.NpmSpec(versionrange)
    except:
        return False

def statistic(OTHER_dependencies_list):
    repeat_list_samename = []
    repeat_list_samenameverison = []
    for tempinfo01 in OTHER_dependencies_list:
        repeat_name = ""
        repeat_version = ""
        repeat_num_samename = 0
        repeat_num_samenameverison = 0
        tempname01 = tempinfo01["dep_name"]
        tempversion01 = tempinfo01["dep_version"]
        # print("tempname01:",tempname01,"tempversion01:",tempversion01)
        for tempinfo02 in OTHER_dependencies_list:
            tempname02 = tempinfo02["dep_name"]
            tempversion02 = tempinfo02["dep_version"]
            if tempname01 == tempname02:
                repeat_num_samename = repeat_num_samename + 1
                # repeat_list_samename.append(tempname01)
            if tempname01 == tempname02 and tempversion01 == tempversion02:
                repeat_num_samenameverison = repeat_num_samenameverison + 1
                # repeat_list_samenameverison.append(tempname01)
        # total_repeat_num=total_repeat_num+repeat_num_samename
        if repeat_num_samename > 1:
            temp_list = []
            temp_list.append(tempname01)
            temp_list.append(repeat_num_samename)
            status_n=0
            for temp_repeat_list_samename in repeat_list_samename:
                if temp_repeat_list_samename[0]==tempname01:
                    status_n=1
            if status_n==0:
                repeat_list_samename.append(temp_list)
        if repeat_num_samenameverison > 1:
            temp_list = []
            temp_list.append(tempname01 + "@" + tempversion01)
            temp_list.append(repeat_num_samenameverison)
            status_nv = 0
            for temp_repeat_list_samenameverison in repeat_list_samenameverison:
                if temp_repeat_list_samenameverison[0] == tempname01 + "@" + tempversion01:
                    status_nv = 1
            if status_nv == 0:
                repeat_list_samenameverison.append(temp_list)

    # print("repeat_list_samename:", repeat_list_samename)
    # print("repeat_list_samenameverison:", repeat_list_samenameverison)
    return repeat_list_samename, repeat_list_samenameverison

def reduce_size(TOP_dependencies_list,OTHER_dependencies_list):
    repeat_list_samename = []
    repeat_list_samenameverison = []
    total_reduce_size=0
    total_reduce_acount=0

    for temp_topinfo in TOP_dependencies_list:
        dependencies_list=[]
        temp_top_name = temp_topinfo["dep_name"]
        temp_top_version = temp_topinfo["dep_version"]
        temp_top_versionrange = temp_topinfo["dep_version_range"]
        temp_top_directdependency = temp_topinfo["direct_dependency"]
        if temp_top_directdependency ==0:
            # print(temp_top_name,temp_top_version,temp_top_versionrange,temp_top_directdependency)
            for temp_otherinfo in OTHER_dependencies_list:
                temp_other_name = temp_otherinfo["dep_name"]
                temp_other_version = temp_otherinfo["dep_version"]
                temp_other_versionrange = temp_otherinfo["dep_version_range"]
                temp_other_directdependency = temp_otherinfo["direct_dependency"]
                if temp_other_name==temp_top_name:
                    dependencies_list.append(temp_otherinfo)
        if dependencies_list!=[]:
            dependencies_list.append(temp_topinfo)
            # print(dependencies_list)
            version_list = get_version_list(temp_top_name)
            max_version = ''
            max_count = 0
            max_versionrange=''
            for temp_version in version_list:
                temp_count = 0
                for dependency_list in dependencies_list:
                    dependency_versionrange = dependency_list["dep_version_range"]
                    if check_version_range(temp_version,dependency_versionrange):
                        temp_count=temp_count+1
                if max_count <= temp_count:
                    max_count = temp_count
                    max_version = temp_version
                    max_versionrange=dependency_versionrange
            if max_count>1:
                unpackedsize=get_unpackedsize(temp_top_name, max_version)
                for dnum in range(max_count-1):
                    if unpackedsize is None:
                        unpackedsize=0
                    total_reduce_size=total_reduce_size+unpackedsize
                    total_reduce_acount=total_reduce_acount+1
    return total_reduce_size,total_reduce_acount

    # for tempinfo01 in OTHER_dependencies_list:
    #     repeat_name = ""
    #     repeat_version = ""
    #     repeat_num_samename = 0
    #     repeat_num_samenameverison = 0
    #     tempname01 = tempinfo01["dep_name"]
    #     tempversion01 = tempinfo01["dep_version"]
    #     # print("tempname01:",tempname01,"tempversion01:",tempversion01)
    #     for tempinfo02 in OTHER_dependencies_list:
    #         tempname02 = tempinfo02["dep_name"]
    #         tempversion02 = tempinfo02["dep_version"]
    #         if tempname01 == tempname02:
    #             repeat_num_samename = repeat_num_samename + 1
    #             # repeat_list_samename.append(tempname01)
    #         if tempname01 == tempname02 and tempversion01 == tempversion02:
    #             repeat_num_samenameverison = repeat_num_samenameverison + 1
    #             # repeat_list_samenameverison.append(tempname01)
    #     # total_repeat_num=total_repeat_num+repeat_num_samename
    #     if repeat_num_samename > 1:
    #         temp_list = []
    #         temp_list.append(tempname01)
    #         temp_list.append(repeat_num_samename)
    #         status_n=0
    #         for temp_repeat_list_samename in repeat_list_samename:
    #             if temp_repeat_list_samename[0]==tempname01:
    #                 status_n=1
    #         if status_n==0:
    #             repeat_list_samename.append(temp_list)
    #     if repeat_num_samenameverison > 1:
    #         temp_list = []
    #         temp_list.append(tempname01 + "@" + tempversion01)
    #         temp_list.append(repeat_num_samenameverison)
    #         status_nv = 0
    #         for temp_repeat_list_samenameverison in repeat_list_samenameverison:
    #             if temp_repeat_list_samenameverison[0] == tempname01 + "@" + tempversion01:
    #                 status_nv = 1
    #         if status_nv == 0:
    #             repeat_list_samenameverison.append(temp_list)
    #
    # # print("repeat_list_samename:", repeat_list_samename)
    # # print("repeat_list_samenameverison:", repeat_list_samenameverison)
    # return repeat_list_samename, repeat_list_samenameverison


def insert_statistical_data(project_name,dependencies_num,duplicate_dependencies_num,duplicate_dependencies_proportion,dependencies_size,duplicate_dependencies_size,reduce_count,reduce_size,reduce_duplicate_count_proportion,reduce_duplicate_size_proportion):
    # now = datetime.datetime.now()
    # now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_insert = "INSERT INTO npm_statistical_data (project_name,dependencies_num,duplicate_dependencies_num," \
                 "duplicate_dependencies_proportion,dependencies_size,duplicate_dependencies_size,reduce_count," \
                 "reduce_size,reduce_duplicate_count_proportion,reduce_duplicate_size_proportion) " \
                 "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (project_name,dependencies_num,
                                                                                 duplicate_dependencies_num,duplicate_dependencies_proportion,
                                                                                 dependencies_size,duplicate_dependencies_size,
                                                                                 reduce_count,reduce_size,reduce_duplicate_count_proportion,
                                                                                 reduce_duplicate_size_proportion)
    # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)
    # db = pymysql.connect(host, user, password, db_name)

    try:
        db_insert_releases = POOL_temp.connection()
        # 执行sql语句
        insert_releases_cursor = db_insert_releases.cursor()
        insert_releases_cursor.execute(sql_insert)
        db_insert_releases.commit()
    except Exception as e:
        print("sql_update:", sql_insert)
        print("npm_all_releases error ", e)
        db_insert_releases.rollback()
    finally:
        db_insert_releases.close()


def test(projectname):
    try:
        global TOP_dependencies_list, OTHER_dependencies_list
        TOP_dependencies_list = []
        OTHER_dependencies_list = []
        latestversion, unpacked_size = latest_version(projectname)
        print("*********************************************************** ")
        print("项目名: ", projectname, " 最新版本: ", latestversion)

        get_dep(projectname, latestversion, 0)
        print("TOP_dependencies_list: ",TOP_dependencies_list)
        print("OTHER_dependencies_list: ", OTHER_dependencies_list)
        duplicate_dependencies_num = len(OTHER_dependencies_list)
        # 可减少的总体积
        total_reduce_size = 0
        total_reduce_count = 0
        total_reduce_size, total_reduce_count = reduce_size(TOP_dependencies_list, OTHER_dependencies_list)
        (repeat_list_samename, repeat_list_samenameverison) = statistic(OTHER_dependencies_list)
        dependencies_num,duplicate_dependencies_proportion,reduce_duplicate_count_proportion,reduce_duplicate_size_proportion=0,0,0,0
        totalsize = unpacked_size
        othersize = 0
        if OTHER_dependencies_list != []:
            dependencies_num = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
            totalnum = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
            otherproportion = 0
            reduce_sizeproportion = 0
            for top_dependencie in TOP_dependencies_list:
                top_dependenciename = top_dependencie["dep_name"]
                top_dependencieversion = top_dependencie["dep_version"]
                packedsize = get_unpackedsize(top_dependenciename, top_dependencieversion)
                if packedsize == '' or packedsize is None:
                    packedsize = 0
                totalsize = totalsize + int(packedsize)

            for other_dependencie in OTHER_dependencies_list:
                other_dependenciename = other_dependencie["dep_name"]
                other_dependencieversion = other_dependencie["dep_version"]
                packedsize = get_unpackedsize(other_dependenciename, other_dependencieversion)
                if packedsize == '' or packedsize is None:
                    packedsize = 0
                totalsize = totalsize + int(packedsize)
                othersize = othersize + int(packedsize)

            if totalsize != 0:
                # OTHER_dependencies_list大小占总体积比例
                otherproportion = othersize / totalsize
                # 可减少重复依赖大小占总体积比例
                reduce_sizeproportion = total_reduce_size / totalsize

            duplicate_dependencies_proportion = duplicate_dependencies_num / dependencies_num
            reduce_duplicate_count_proportion = total_reduce_count / duplicate_dependencies_num
            if othersize != 0:
                reduce_duplicate_size_proportion = total_reduce_size / othersize
            else:
                reduce_duplicate_size_proportion = 0
        print("依赖数:", dependencies_num)
        print("冗余依赖数:", duplicate_dependencies_num)
        print("冗余包占总体比例:", duplicate_dependencies_proportion)
        print("体积:", totalsize)
        print("冗余体积:", othersize)
        print("可消除冗余个数:", total_reduce_count)
        print("可消除冗余体积:", total_reduce_size)
        print("可消除个数占冗余总数比例:", reduce_duplicate_count_proportion)
        print("可消除个数占冗余体积比例:", reduce_duplicate_size_proportion)

    except Exception as e:
        print("test error ", e)
        pass


def main_db():
    project_list = all_project_name()
    for project in project_list:
        projectid = project[0]
        projectname = project[1]

        executor.submit(do_main_db, projectid,projectname)

        # do_main_db(projectid,projectname)

def do_main_db(projectid,projectname):
    try:
        global TOP_dependencies_list, OTHER_dependencies_list
        TOP_dependencies_list = []
        OTHER_dependencies_list = []
        latestversion, unpacked_size = latest_version(projectname)
        print("*********************************************************** ")
        print("projectname: ", projectname, " latestversion: ", latestversion)

        get_dep(projectname, latestversion, 0)
        # print("TOP_dependencies_list: ",TOP_dependencies_list)
        # print("OTHER_dependencies_list: ", OTHER_dependencies_list)
        duplicate_dependencies_num = len(OTHER_dependencies_list)
        # 可减少的总体积
        total_reduce_size = 0
        total_reduce_count = 0
        total_reduce_size, total_reduce_count = reduce_size(TOP_dependencies_list, OTHER_dependencies_list)
        (repeat_list_samename, repeat_list_samenameverison) = statistic(OTHER_dependencies_list)
        # print("repeat_list_samename: ", repeat_list_samename)
        # print("repeat_list_samenameverison: ", repeat_list_samenameverison)
        # print("total_repeat_num: ", duplicate_dependencies_num)
        # print("total_reduce_count: ", total_reduce_count)

        if OTHER_dependencies_list != []:
            dependencies_num = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
            totalsize = unpacked_size
            othersize = 0
            totalnum = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
            otherproportion = 0
            reduce_sizeproportion = 0
            for top_dependencie in TOP_dependencies_list:
                top_dependenciename = top_dependencie["dep_name"]
                top_dependencieversion = top_dependencie["dep_version"]
                packedsize = get_unpackedsize(top_dependenciename, top_dependencieversion)
                if packedsize == '' or packedsize is None:
                    packedsize = 0
                totalsize = totalsize + int(packedsize)

            for other_dependencie in OTHER_dependencies_list:
                other_dependenciename = other_dependencie["dep_name"]
                other_dependencieversion = other_dependencie["dep_version"]
                packedsize = get_unpackedsize(other_dependenciename, other_dependencieversion)
                if packedsize == '' or packedsize is None:
                    packedsize = 0
                totalsize = totalsize + int(packedsize)
                othersize = othersize + int(packedsize)

            if totalsize != 0:
                # OTHER_dependencies_list大小占总体积比例
                otherproportion = othersize / totalsize
                # 可减少重复依赖大小占总体积比例
                reduce_sizeproportion = total_reduce_size / totalsize

            duplicate_dependencies_proportion = duplicate_dependencies_num / dependencies_num
            reduce_duplicate_count_proportion = total_reduce_count / duplicate_dependencies_num
            if othersize != 0:
                reduce_duplicate_size_proportion = total_reduce_size / othersize
            else:
                reduce_duplicate_size_proportion = 0

            insert_statistical_data(projectname, dependencies_num, duplicate_dependencies_num,
                                    duplicate_dependencies_proportion, totalsize, othersize,
                                    total_reduce_count, total_reduce_size, reduce_duplicate_count_proportion,
                                    reduce_duplicate_size_proportion)
        else:
            insert_statistical_data(projectname, len(TOP_dependencies_list), 0, 0, 0, 0, 0, 0, 0, 0)
    except Exception as e:
        print("main_db error ", e)
        pass


def main():
    project_list = all_project_name()
    num = 0
    all_repeat_num = 0
    all_reduce_size = 0
    all_reduce_size_proportion = 0
    all_size = 0
    all_proportion = 0
    all_othersize=0
    num0_50 = 0
    num50_100 = 0
    num100_500 = 0
    numup500 = 0

    all_dependency_num = 0
    all_dependency_num0_50 = 0
    all_dependency_num50_100 = 0
    all_dependency_num100_500 = 0
    all_dependency_num500 = 0

    all_reduce_count = 0
    all_reduce_count0_50 = 0
    all_reduce_count50_100 = 0
    all_reduce_count100_500 = 0
    all_reduce_count500 = 0

    all_repeat_num0_50 = 0
    all_repeat_num50_100 = 0
    all_repeat_num100_500 = 0
    all_repeat_num500 = 0

    all_size0_50 = 0
    all_size50_100 = 0
    all_size100_500 = 0
    all_size500 = 0

    all_proportion0_50 = 0
    all_proportion50_100 = 0
    all_proportion100_500 = 0
    all_proportion500 = 0

    all_reduce_size0_50 = 0
    all_reduce_size50_100 = 0
    all_reduce_size100_500 = 0
    all_reduce_size500 = 0

    all_reduce_size_proportion0_50 = 0
    all_reduce_size_proportion50_100 = 0
    all_reduce_size_proportion100_500 = 0
    all_reduce_size_proportion500 = 0

    url = "D://nodejsinfo20200505_01.txt"
    for project in project_list:

        projectid = project[0]
        projectname = project[1]
        global TOP_dependencies_list,OTHER_dependencies_list
        TOP_dependencies_list=[]
        OTHER_dependencies_list=[]
        latestversion,unpacked_size=latest_version(projectname)
        print("*********************************************************** ")
        print("projectname: ",projectname," latestversion: ", latestversion)
        # dependencies_list = []
        # dependencies_list=get_dependencies(projectname,latestversion)
        #
        # version_list=get_version_list(projectname)

        get_dep(projectname, latestversion, 0)
        print("TOP_dependencies_list: ",TOP_dependencies_list)
        print("OTHER_dependencies_list: ", OTHER_dependencies_list)
        total_repeat_num=len(OTHER_dependencies_list)
        # 可减少的总体积
        total_reduce_size=0
        total_reduce_count = 0
        total_reduce_size,total_reduce_count=reduce_size(TOP_dependencies_list,OTHER_dependencies_list)
        (repeat_list_samename, repeat_list_samenameverison) = statistic(OTHER_dependencies_list)

        print("repeat_list_samename: ", repeat_list_samename)
        print("repeat_list_samenameverison: ", repeat_list_samenameverison)
        print("total_repeat_num: ", total_repeat_num)
        print("total_reduce_count: ", total_reduce_count)


        if  OTHER_dependencies_list != [] :
            num = num + 1
            dependency_num = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
            all_dependency_num = all_dependency_num + dependency_num
            all_reduce_count=all_reduce_count+total_reduce_count
            totalsize=unpacked_size

            othersize=0
            totalnum=len(TOP_dependencies_list)+len(OTHER_dependencies_list)
            otherproportion=0
            reduce_sizeproportion=0
            for top_dependencie in TOP_dependencies_list:
                top_dependenciename = top_dependencie["dep_name"]
                top_dependencieversion = top_dependencie["dep_version"]
                packedsize = get_unpackedsize(top_dependenciename, top_dependencieversion)
                if packedsize=='' or packedsize is None:
                    packedsize=0
                totalsize = totalsize + int(packedsize)

            for other_dependencie in OTHER_dependencies_list:
                other_dependenciename = other_dependencie["dep_name"]
                other_dependencieversion = other_dependencie["dep_version"]
                packedsize = get_unpackedsize(other_dependenciename, other_dependencieversion)
                if packedsize == '' or packedsize is None:
                    packedsize = 0
                totalsize = totalsize + int(packedsize)
                othersize = othersize + int(packedsize)

            if totalsize != 0:
                # OTHER_dependencies_list大小占总体积比例
                otherproportion=othersize/totalsize
                # 可减少重复依赖大小占总体积比例
                reduce_sizeproportion=total_reduce_size/totalsize

            all_size=all_size + totalsize
            all_othersize=all_othersize+othersize
            all_repeat_num = all_repeat_num + len(OTHER_dependencies_list)
            all_proportion = all_proportion + otherproportion
            all_reduce_size = all_reduce_size + total_reduce_size
            all_reduce_size_proportion=all_reduce_size_proportion+reduce_sizeproportion


            if len(OTHER_dependencies_list)<50:
                num0_50=num0_50+1
                all_size0_50 = all_size0_50 + totalsize
                all_repeat_num0_50 = all_repeat_num0_50 + len(OTHER_dependencies_list)
                all_proportion0_50 = all_proportion0_50 + otherproportion
                all_reduce_size0_50 = all_reduce_size0_50 + total_reduce_size
                all_reduce_size_proportion0_50 = all_reduce_size_proportion0_50+reduce_sizeproportion
                all_dependency_num0_50=all_dependency_num0_50+dependency_num
                all_reduce_count0_50=all_reduce_count0_50+total_reduce_count

            elif len(OTHER_dependencies_list)>=50 and len(OTHER_dependencies_list)<100:
                num50_100=num50_100+1
                all_size50_100 = all_size50_100 + totalsize
                all_repeat_num50_100 = all_repeat_num50_100 + len(OTHER_dependencies_list)
                all_proportion50_100 = all_proportion50_100 + otherproportion
                all_reduce_size50_100 = all_reduce_size50_100 + total_reduce_size
                all_reduce_size_proportion50_100 = all_reduce_size_proportion50_100 + reduce_sizeproportion
                all_dependency_num50_100 = all_dependency_num50_100 + dependency_num
                all_reduce_count50_100 = all_reduce_count50_100 + total_reduce_count

            elif len(OTHER_dependencies_list)>=100 and len(OTHER_dependencies_list)<500:
                num100_500=num100_500+1
                all_size100_500 = all_size100_500 + totalsize
                all_repeat_num100_500 = all_repeat_num100_500 + len(OTHER_dependencies_list)
                all_proportion100_500 = all_proportion100_500 + otherproportion
                all_reduce_size100_500 = all_reduce_size100_500 + total_reduce_size
                all_reduce_size_proportion100_500 = all_reduce_size_proportion100_500 + reduce_sizeproportion
                all_dependency_num100_500 = all_dependency_num100_500 + dependency_num
                all_reduce_count100_500 = all_reduce_count100_500 + total_reduce_count
            elif len(OTHER_dependencies_list) >=500:
                numup500=numup500+1
                all_size500 = all_size500 + totalsize
                all_repeat_num500 = all_repeat_num500 + len(OTHER_dependencies_list)
                all_proportion500 = all_proportion500 + otherproportion
                all_reduce_size500 = all_reduce_size500 + total_reduce_size
                all_reduce_size_proportion500 = all_reduce_size_proportion500 + reduce_sizeproportion
                all_dependency_num500 = all_dependency_num500 + dependency_num
                all_reduce_count500 = all_reduce_count500 + total_reduce_count

            with open(url, 'a', encoding='utf-8') as f:
                f.write("*****************************************************************************************************" + "\n")
                f.write("num:" + str(num) + "\n")
                f.write("projectid:" + str(projectid) + "\n")
                f.write("projectname:" + projectname + "\n")
                f.write("Version number:" + str(latestversion) + "\n")
                f.write("repeat_list_samename:" + str(repeat_list_samename) + "\n")
                f.write("repeat_list_samenameverison:" + str(repeat_list_samenameverison) + "\n")
                # f.write("TOP_dependencies_list:" + str(TOP_dependencies_list) + "\n")
                # f.write("OTHER_dependencies_list:" + str(OTHER_dependencies_list) + "\n")
                f.write("total_repeat_num:" + str(total_repeat_num) + "\n")
                f.write("otherproportion:" + str(otherproportion) + "\n")
                f.write("totalsize:" + str(totalsize) + "\n")
                f.write("total_reduce_size: "+str(total_reduce_size) + "\n")
                f.write("totalnum:" + str(totalnum) + "\n")

            print("totalnum: ", totalnum)
            print("totalsize: ", totalsize)
            print("othersize: ", othersize)
            print("otherproportion: ", otherproportion)
            print("total_reduce_size: ", total_reduce_size)
            if totalsize!=0:
                print("total_reduce_proportion: ", total_reduce_size/totalsize)
    # 平均重复依赖数
    averagenum=all_repeat_num/num
    # 平均大小
    averagesize=all_size/num
    # 重复依赖大小占总大小比例
    averageproportion=all_proportion/num
    # averageproportion=all_othersize/all_size


    average_reduce_size_proportion=all_reduce_size/all_size

    averagenum0_50 = all_repeat_num0_50 / num0_50
    averagesize0_50 = all_size0_50 / num0_50
    averageproportion0_50 = all_proportion0_50 / num0_50
    average_reduce_size_proportion0_50 = all_reduce_size0_50 / all_size0_50


    averagenum50_100 = all_repeat_num50_100 / num50_100
    averagesize50_100 = all_size50_100 / num50_100
    averageproportion50_100 = all_proportion50_100 / num50_100
    average_reduce_size_proportion50_100 = all_reduce_size50_100 / all_size50_100

    averagenum100_500 = all_repeat_num100_500 / num100_500
    averagesize100_500 = all_size100_500 / num100_500
    averageproportion100_500 = all_proportion100_500 / num100_500
    average_reduce_size_proportion100_500 = all_reduce_size100_500 / all_size100_500

    averagenum500 = all_repeat_num500 / numup500
    averagesize500 = all_size500 / numup500
    averageproportion500 = all_proportion500 / numup500
    average_reduce_size_proportion500 = all_reduce_size500 / all_size500

    with open(url, 'a', encoding='utf-8') as f:
        f.write("###########################################################################" + "\n")
        f.write("allnum:" + str(num) + "\n")
        f.write("all_dependency_num:" + str(all_dependency_num) + "\n")
        f.write("averag_dependency_num:" + str(all_dependency_num/num) + "\n")
        f.write("all_repeat_num:" + str(all_repeat_num) + "\n")
        f.write("all_size:" + str(all_size) + "\n")
        f.write("averagenum:" + str(averagenum) + "\n")
        f.write("averagesize:" + str(averagesize) + "\n")
        f.write("all_proportion:" + str(all_proportion) + "\n")
        f.write("averageproportion:" + str(averageproportion) + "\n")
        f.write("all_reduce_size:" + str(all_reduce_size) + "\n")
        # f.write("average_reduce_size_proportion:" + str(average_reduce_size_proportion) + "\n")
        f.write("average_reduce_size_proportion:" + str(all_reduce_size_proportion / num) + "\n")

        f.write("all_dependency_num:" + str(all_dependency_num) + "\n")
        f.write("all_reduce_count:" + str(all_reduce_count) + "\n")
        f.write("all_reduce_count_proportion:" + str(all_reduce_count/all_dependency_num) + "\n")


        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" + "\n")
        f.write("num0_50:" + str(num0_50) + "\n")
        f.write("all_repeat_num0_50:" + str(all_repeat_num0_50) + "\n")
        f.write("all_size0_50:" + str(all_size0_50) + "\n")
        f.write("averagenum0_50:" + str(averagenum0_50) + "\n")
        f.write("averagesize0_50:" + str(averagesize0_50) + "\n")
        f.write("all_proportion0_50:" + str(all_proportion0_50) + "\n")
        f.write("averageproportion0_50:" + str(averageproportion0_50) + "\n")
        f.write("all_reduce_size0_50:" + str(all_reduce_size0_50) + "\n")
        f.write("all_reduce_size_proportion0_50:" + str(all_reduce_size_proportion0_50) + "\n")
        # f.write("average_reduce_size_proportion0_50:" + str(average_reduce_size_proportion0_50) + "\n")
        f.write("average_reduce_size_proportion0_50:" + str(all_reduce_size_proportion0_50/num0_50) + "\n")

        f.write("all_dependency_num0_50:" + str(all_dependency_num0_50) + "\n")
        f.write("all_reduce_count0_50:" + str(all_reduce_count0_50) + "\n")
        f.write("all_reduce_count_proportion0_50:" + str(all_reduce_count0_50 / all_dependency_num0_50) + "\n")

        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" + "\n")
        f.write("num50_100:" + str(num50_100) + "\n")
        f.write("all_repeat_num:" + str(all_repeat_num50_100) + "\n")
        f.write("all_size50_100:" + str(all_size50_100) + "\n")
        f.write("averagenum50_100:" + str(averagenum50_100) + "\n")
        f.write("averagesize50_100:" + str(averagesize50_100) + "\n")
        f.write("all_proportion50_100:" + str(all_proportion50_100) + "\n")
        f.write("averageproportion50_100:" + str(averageproportion50_100) + "\n")
        f.write("all_reduce_size50_100:" + str(all_reduce_size50_100) + "\n")
        f.write("all_reduce_size_proportion50_100:" + str(all_reduce_size_proportion50_100) + "\n")
        # f.write("average_reduce_size_proportion50_100:" + str(average_reduce_size_proportion50_100) + "\n")
        f.write("average_reduce_size_proportion50_100:" + str(all_reduce_size_proportion50_100/num50_100) + "\n")

        f.write("all_dependency_num50_100:" + str(all_dependency_num50_100) + "\n")
        f.write("all_reduce_count50_100:" + str(all_reduce_count50_100) + "\n")
        f.write("all_reduce_count_proportion50_100:" + str(all_reduce_count50_100 / all_dependency_num50_100) + "\n")

        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" + "\n")
        f.write("num100_500:" + str(num100_500) + "\n")
        f.write("all_repeat_num100_500:" + str(all_repeat_num100_500) + "\n")
        f.write("all_size100_500:" + str(all_size100_500) + "\n")
        f.write("averagenum100_500:" + str(averagenum100_500) + "\n")
        f.write("averagesize100_500:" + str(averagesize100_500) + "\n")
        f.write("all_proportion100_500:" + str(all_proportion100_500) + "\n")
        f.write("averageproportion100_500:" + str(averageproportion100_500) + "\n")
        f.write("all_reduce_size100_500:" + str(all_reduce_size100_500) + "\n")
        f.write("all_reduce_size_proportion100_500:" + str(all_reduce_size_proportion100_500) + "\n")
        # f.write("average_reduce_size_proportion100_500:" + str(average_reduce_size_proportion100_500) + "\n")
        f.write("average_reduce_size_proportion100_500:" + str(all_reduce_size_proportion100_500/num100_500) + "\n")

        f.write("all_dependency_num100_500:" + str(all_dependency_num100_500) + "\n")
        f.write("all_reduce_count100_500:" + str(all_reduce_count100_500) + "\n")
        f.write("all_reduce_count_proportion100_500:" + str(all_reduce_count100_500 / all_dependency_num100_500) + "\n")

        f.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" + "\n")
        f.write("numup500:" + str(numup500) + "\n")
        f.write("all_repeat_num:" + str(all_repeat_num500) + "\n")
        f.write("all_size:" + str(all_size500) + "\n")
        f.write("averagenum:" + str(averagenum500) + "\n")
        f.write("averagesize:" + str(averagesize500) + "\n")
        f.write("all_proportion:" + str(all_proportion500) + "\n")
        f.write("averageproportion500:" + str(averageproportion500) + "\n")
        f.write("all_reduce_size500:" + str(all_reduce_size500) + "\n")
        f.write("all_reduce_size_proportion500:" + str(all_reduce_size_proportion500) + "\n")
        # f.write("average_reduce_size_proportion500:" + str(average_reduce_size_proportion500) + "\n")
        f.write("average_reduce_size_proportion500:" + str(all_reduce_size_proportion500/numup500) + "\n")

        f.write("all_dependency_num500:" + str(all_dependency_num500) + "\n")
        f.write("all_reduce_count500:" + str(all_reduce_count500) + "\n")
        f.write("all_reduce_count_proportion500:" + str(all_reduce_count500 / all_dependency_num500) + "\n")


if __name__ == '__main__':
    executor = ThreadPoolExecutor(20)
    # # main_db()
    #
    # do_main_db(1, 'wrappack')

    test("lzmtest_hhhhh")