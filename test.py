import semantic_version
import pymysql
# import grab_npm_tars
# import npmdependency
from DBUtils.PooledDB import PooledDB
import semantic_version
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import json
POOL_temp = PooledDB(
    creator=pymysql,  # 使用链接数据库的模块
    maxconnections=None,  # 连接池允许的最大连接数，0和None表示没有限制
    mincached=10,  # 初始化时，连接池至少创建的空闲的连接，0表示不创建
    maxcached=0,  # 连接池空闲的最多连接数，0和None表示没有限制
    maxshared=0,
    # 连接池中最多共享的连接数量，0和None表示全部共享，ps:其实并没有什么用，因为pymsql和MySQLDB等模块中的threadsafety都为1，所有值无论设置多少，_maxcahed永远为0，所以永远是所有链接共享
    blocking=True,  # 链接池中如果没有可用共享连接后，是否阻塞等待，True表示等待，False表示不等待然后报错
    setsession=[],  # 开始会话前执行的命令列表
    ping=0,  # ping Mysql 服务端，检查服务是否可用
    # host='localhost',
    host = '219.216.64.227',
    port=3306,
    user='root',
    password='12345678',
    database='npmspider',
    charset='utf8'
)

def main():

    # list=[]
    # listb=['d','e']
    # b=['b',listb]
    #
    # lista=[b,'c']
    # list=['a',lista]
    # print(list)
    # buildtree(list)
    # #['a', [['b', ['d', 'e']], 'c']]
    version="5.6.0"
    strversionRange="2 || 3 || 4 || 5"


    print(semantic_version.Version(version) in semantic_version.NpmSpec(strversionRange))

def buildtree(list):
    if len(list) ==2:
        buildtree(list[1])
        # print(list)
    elif len(list) ==1:
        print(list[0])

def tese():
    dependencyname='a'
    dp_temp_top_name='a'
    dp_temp_top_verison='2.0.0'
    version_range='^1.0.0'
    if dependencyname == dp_temp_top_name and check_version_range(dp_temp_top_verison,
                                                                  version_range) is not True:
        # top层有同名但版本范围不兼容
        print('aaaa')
        dp_top_status = 1

def check_version_range(version, versionrange):
    try:
        return semantic_version.Version(version) in semantic_version.NpmSpec(versionrange)
    except:
        return False


def select_project():
    pnamelist=[]
    sql = "select project_name from npm_statistical_data_duplicate GROUP BY project_name"
    try:
        db_select_project = POOL_temp.connection()
        # 执行sql语句
        select_project_cursor = db_select_project.cursor()
        select_project_cursor.execute(sql)
        select_project_datas = select_project_cursor.fetchall()  # 获取所有的数据
        if select_project_datas is not None:
            for project_data in select_project_datas:
                pname = project_data[0]
                pnamelist.append(pname)
        select_project_cursor.close()
        db_select_project.close()
    except:
        print("select_project()  dberror")

    return pnamelist


def select_project_info(project_name):
    pnamelist=[]
    sql = "select project_name,dedup_times,total_dependencies_num,dependencies_num,duplicate_dependencies_num,duplicate_dependencies_proportion," \
                 "reduce_duplicate_depnum,reduce_count,reduce_duplicate_count_proportion from npm_statistical_data_duplicate where project_name ='%s' ORDER BY reduce_duplicate_depnum DESC" %(project_name)
    try:
        db_select_project = POOL_temp.connection()
        # 执行sql语句
        select_project_cursor = db_select_project.cursor()
        select_project_cursor.execute(sql)
        select_project_datas = select_project_cursor.fetchone()  # 获取所有的数据
        if select_project_datas is not None:

            project_name= select_project_datas[0]
            dedup_times= select_project_datas[1]
            total_dependencies_num= select_project_datas[2]
            dependencies_num= select_project_datas[3]
            duplicate_dependencies_num= select_project_datas[4]
            duplicate_dependencies_proportion= select_project_datas[5]
            reduce_duplicate_depnum= select_project_datas[6]
            reduce_count= select_project_datas[7]
            reduce_duplicate_count_proportion= select_project_datas[8]

            pnamelist.append(project_name)
            pnamelist.append(dedup_times)
            pnamelist.append(total_dependencies_num)
            pnamelist.append(dependencies_num)
            pnamelist.append(duplicate_dependencies_num)
            pnamelist.append(duplicate_dependencies_proportion)
            pnamelist.append(reduce_duplicate_depnum)
            pnamelist.append(reduce_count)
            pnamelist.append(reduce_duplicate_count_proportion)
        select_project_cursor.close()
        db_select_project.close()
    except:
        print("select_project()  dberror")

    return pnamelist


def insert_statistical_data(project_name,dedup_times,total_dependencies_num,dependencies_num,duplicate_dependencies_num,duplicate_dependencies_proportion,
                            reduce_duplicate_depnum,reduce_count,reduce_duplicate_count_proportion):
    # now = datetime.datetime.now()
    # now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_insert = "INSERT INTO npm_statistical_data_duplicate_max (project_name,dedup_times,total_dependencies_num,dependencies_num,duplicate_dependencies_num,duplicate_dependencies_proportion," \
                 "reduce_duplicate_depnum,reduce_count,reduce_duplicate_count_proportion) " \
                 "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (project_name,dedup_times,total_dependencies_num,
                                                                                 dependencies_num,duplicate_dependencies_num,duplicate_dependencies_proportion,
                                                                                 reduce_duplicate_depnum,reduce_count,reduce_duplicate_count_proportion)
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


def statistical_data():
    pnamelist = select_project()
    for pname in pnamelist:
        project_data=select_project_info(pname)
        print(project_data)
        project_name = project_data[0]
        dedup_times = project_data[1]
        total_dependencies_num = project_data[2]
        dependencies_num = project_data[3]
        duplicate_dependencies_num = project_data[4]
        duplicate_dependencies_proportion = project_data[5]
        reduce_duplicate_depnum = project_data[6]
        reduce_count = project_data[7]
        reduce_duplicate_count_proportion = reduce_duplicate_depnum/duplicate_dependencies_num
        insert_statistical_data(project_name, dedup_times, total_dependencies_num, dependencies_num,
                                duplicate_dependencies_num, duplicate_dependencies_proportion,
                                reduce_duplicate_depnum, reduce_count, reduce_duplicate_count_proportion)

if __name__ == '__main__':
    statistical_data()