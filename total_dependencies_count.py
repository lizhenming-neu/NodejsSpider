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


def all_project_name():
    name_list = []
    # SQL 查询语句
    sql = "SELECT id,project_name FROM npm_all_project_name where id<=20"
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
    except :
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


def get_dep(projectname,version,dep_num,tp_dependencies_list):
    new_tp_dependencies_list = []
    # 为了不对tp_dependencies_list造成修改
    for nl in tp_dependencies_list:
        new_tp_dependencies_list.append(nl)
    global TOP_dependencies_list, OTHER_dependencies_list
    # 1为直接依赖
    if dep_num==0:
        direct_dependency = 1
    else:
        direct_dependency=0
    if dep_num>20:
        return
    # stra = '-'
    # for numa in range(dep_num):
    #     stra = stra + '-'
    # print(stra, projectname, version)

    temp_dependencies_list=[]
    dep_list=[]
    dependencies_list = get_dependencies(projectname, version)
    for dependency in dependencies_list:
        # 依赖项
        dependencyname = dependency[0]
        # 依赖版本范围
        version_range = dependency[1].replace("< ", "<").replace("<= ", "<=").replace("> ", ">").replace(">= ", ">=")
        # print(projectname, version,dependencyname,version_range)
        dp_top_status = 0
        # 循环top层依赖
        for dp_temp_top in TOP_dependencies_list:
            dp_temp_top_name = dp_temp_top["dep_name"]
            dp_temp_top_verison = dp_temp_top["dep_version"]
            if dependencyname==dp_temp_top_name and check_version_range(dp_temp_top_verison, version_range) is not True:
                # top层有同名但版本范围不兼容
                dp_top_status=1
            elif dependencyname==dp_temp_top_name and check_version_range(dp_temp_top_verison, version_range):
                # top层有同名且版本范围兼容
                dp_top_status=2


        # top层没有同名
        if dp_top_status==0:
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
        # top层有同名但版本范围不兼容
        elif dp_top_status==1:

            dp_tp_status = 0
            # 循环上级沙箱中是否包含该版本依赖
            for dp_temp_sandbox in tp_dependencies_list:
                dp_temp_sandbox_name = dp_temp_sandbox["dep_name"]
                dp_temp_sandbox_verison = dp_temp_sandbox["dep_version"]
                if dependencyname == dp_temp_sandbox_name and check_version_range(dp_temp_sandbox_verison,version_range):
                    # sandbox有同名且版本范围兼容
                    dp_tp_status = 1

            # 上级沙箱中不包含该版本依赖
            if dp_tp_status==0:
                version_list = get_version_list(dependencyname)
                try:
                    for temp_version in version_list:
                        if check_version_range(temp_version, version_range):
                            # print(dependencyname,temp_version, version_range)
                            dep_obj = {"dep_name": dependencyname, "dep_version": temp_version,"dep_version_range": version_range,"direct_dependency":direct_dependency}
                            OTHER_dependencies_list.append(dep_obj)
                            new_tp_dependencies_list.append(dep_obj)
                            dep_list.append(dep_obj)
                            raise getoutofloop()
                except getoutofloop:
                    pass
    # 第二次深度优先，递归遍历每项依赖
    dep_num = dep_num + 1
    for dependencytemp_02 in dep_list:
        tempname = dependencytemp_02["dep_name"]
        tempversion = dependencytemp_02["dep_version"]
        get_dep(tempname, tempversion, dep_num,new_tp_dependencies_list)


def check_version_range(version,versionrange):
    try:
        return semantic_version.Version(version) in semantic_version.NpmSpec(versionrange)
    except:
        return False



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


# 更新依赖数量
def update_dependencies_num(id,dependencies_num,duplicate_dependencies_num,
                            duplicate_dependencies_proportion,dependencies_size,
                            duplicate_dependencies_size,reduce_count,reduce_size,
                            reduce_duplicate_count_proportion,reduce_duplicate_size_proportion,latest_version):
    sql_update_unpackedsize = "update  npm_all_project_name " \
                              "set dependencies_num='%s',duplicate_dependencies_num='%s'," \
                              "latest_version='%s',duplicate_dependencies_proportion='%s', " \
                              "dependencies_size='%s',duplicate_dependencies_size='%s', " \
                              "reduce_count='%s',reduce_size='%s', " \
                              "reduce_duplicate_count_proportion='%s',reduce_duplicate_size_proportion='%s' " \
                              "where id='%s'" % (dependencies_num,duplicate_dependencies_num,latest_version,duplicate_dependencies_proportion,dependencies_size,
                            duplicate_dependencies_size,reduce_count,reduce_size,
                            reduce_duplicate_count_proportion,reduce_duplicate_size_proportion,id)
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




def main():
    project_list = all_project_name()
    for project in project_list:
        projectid = project[0]
        projectname = project[1]
        try:
            global TOP_dependencies_list, OTHER_dependencies_list
            TOP_dependencies_list = []
            OTHER_dependencies_list = []
            latestversion, unpacked_size = latest_version(projectname)
            print("*********************************************************** ")
            print("项目名: ", projectname, " 最新版本: ", latestversion)
            get_dep(projectname, latestversion, 0,[])
            # print("TOP_dependencies_list: ",TOP_dependencies_list)
            # print("OTHER_dependencies_list: ", OTHER_dependencies_list)
            duplicate_dependencies_num = len(OTHER_dependencies_list)
            # 可减少的总体积
            total_reduce_size = 0
            total_reduce_count = 0
            total_reduce_size, total_reduce_count = reduce_size(TOP_dependencies_list, OTHER_dependencies_list)
            # (repeat_list_samename, repeat_list_samenameverison) = statistic(OTHER_dependencies_list)
            dependencies_num,duplicate_dependencies_proportion,reduce_duplicate_count_proportion,reduce_duplicate_size_proportion=0,0,0,0
            totalsize = unpacked_size
            othersize = 0
            dependencies_num=len(TOP_dependencies_list)
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
            update_dependencies_num(projectid, dependencies_num, duplicate_dependencies_num,
                                    duplicate_dependencies_proportion, totalsize,
                                    othersize, total_reduce_count, total_reduce_size,
                                    reduce_duplicate_count_proportion, reduce_duplicate_size_proportion, latestversion)
        except Exception as e:
            print("main error ", e)
            pass

#
#
# def main():
#     project_list = all_project_name()
#     for project in project_list:
#         projectid = project[0]
#         projectname = project[1]
#         global TOP_dependencies_list,OTHER_dependencies_list
#         TOP_dependencies_list=[]
#         OTHER_dependencies_list=[]
#         latestversion, id = latest_version(projectname)
#         get_dep(projectname, latestversion, 0)
#         dependencies_num = len(TOP_dependencies_list) + len(OTHER_dependencies_list)
#         duplicate_dependencies_num=len(OTHER_dependencies_list)
#         # print("projectname",projectname,"projectid:",projectid,"dependencies_num:",dependencies_num,"duplicate_dependencies_num:",duplicate_dependencies_num)
#         update_dependencies_num(projectid,dependencies_num,duplicate_dependencies_num,latestversion)
#         print("update_dependencies_num [ projectname",projectname,"projectid:",projectid,"dependencies_num:",dependencies_num,"duplicate_dependencies_num:",duplicate_dependencies_num," ]")


if __name__ == "__main__":
    main()