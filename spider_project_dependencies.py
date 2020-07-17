import json
from urllib.request import Request, urlopen
import pymysql
class getoutofloop(Exception): pass
from DBUtils.PooledDB import PooledDB


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

def get_results(url):

    headers = {'User-Agent': 'Mozilla/5.0',
               'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': ' token 30ad34440e1bdc0016db7ae316c3d4a1d75d18c1'
               }
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result

def all_project_name():
    name_list = []
    # SQL 查询语句
    sql = "SELECT id,project_name FROM npm_all_project_name where id>=1269422"
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


def get_project_info(projectname):
    try:
        npm_url = "https://registry.npm.taobao.org" + '/' + projectname
        # print(str(npm_url))
        items = get_results(str(npm_url))
        # print(items)
        versionsinfo = items["versions"]
        times=items["time"]
        for versioninfo in versionsinfo:
            version=versioninfo
            count = find_releases_count(projectname,version)
            if count == 0 or count == '0':
                time = times[version]
                temp_versioninfo = versionsinfo[version]
                dependencies = []
                unpackedsize = 0
                githubStatus = 'not in github'
                try:
                    repositoryinfo = temp_versioninfo['repository']
                    repositoryurl = str(repositoryinfo['url'])
                    if 'github' in repositoryurl:
                        githubStatus = 'github'
                except Exception:
                    pass
                try:
                    distinfo = temp_versioninfo['dist']
                    unpackedsize = distinfo['size']
                except Exception:
                    pass

                # print("name: ",projectname," version: ", version,"time",time,"unpackedsize",unpackedsize,"githubStatus",githubStatus)
                try:
                    insert_releases(projectname,version,time,unpackedsize,githubStatus)
                    temp_versioninfo = versionsinfo[version]
                    dependencies=[]
                    try:
                        dependencies = temp_versioninfo['dependencies']
                    except:
                        pass
                    # versioninfo=versioninfo.dumps()
                    # temp_versioninfo=type(versioninfo)
                    # dependencies=temp_versioninfo['temp_versioninfo']
                    priority=0
                    for dependency in dependencies:
                        dependencyname=dependency
                        version_range=dependencies[dependencyname]
                        # if "github" in version_range:
                        #     version_range="github"
                        insert_dependencies(projectname, version, dependencyname, version_range,priority)
                        priority=priority+1
                        # print("dependency: ",dependency," dependency verison:",version_range)
                except Exception as e1:
                    print("error! e1", e1)
                    pass

    except Exception as e:
        print("error! ",e)


def insert_releases(projectname,version,creat_time,unpackedSize,githubStatus):
    # now = datetime.datetime.now()
    # now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_insert = "INSERT INTO npm_all_releases (project_name, package_version,creat_time,unpacked_size,repository) VALUES ('%s','%s','%s','%s','%s')" % (projectname, version,creat_time,unpackedSize,githubStatus)
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

    #
    # try:
    #     cursor_insertpypi = db.cursor()
    #     # 执行sql语句
    #     cursor_insertpypi.execute(sql_insert)
    #     # 执行sql语句
    #     db.commit()
    #     cursor_insertpypi.close()
    #     print("insert_releases  [ name:", projectname,"] FINISHED")
    #     # print("update: ", git_name, " FINISHED")
    # except Exception as e:
    #     print("sql_update:", sql_insert)
    #     print("npm_all_releases error ",e)
    #     # 发生错误时回滚
    #     db.rollback()
    # db.close()

def insert_dependencies(projectname,version,dependency,version_range,priority):
    # now = datetime.datetime.now()
    # now = now.strftime("%Y-%m-%d %H:%M:%S")
    sql_insert_dependencies = "INSERT INTO npm_project_dependencies_06 (project_name, package_version,dependency,version_range,priority) VALUES ('%s','%s','%s','%s','%s')" % (projectname,version,dependency,version_range,priority)
    # sql_update = " update  pypi_info set  github_url = '%s' ,  stars = '%s' where id = '%s'" % (html_url, stargazers_count, fileid)
    # db = pymysql.connect(host, user, password, db_name)

    try:
        db_insert_dependencies = POOL_temp.connection()
        # 执行sql语句
        dependencies_cursor = db_insert_dependencies.cursor()
        dependencies_cursor.execute(sql_insert_dependencies)
        db_insert_dependencies.commit()
    except Exception as e:
        print("sql_update:", sql_insert_dependencies)
        print("insert_dependencies error ", e)
        db_insert_dependencies.rollback()
    finally:
        db_insert_dependencies.close()

    # try:
    #     cursor_insertpypi = db.cursor()
    #     # 执行sql语句
    #     cursor_insertpypi.execute(sql_insert)
    #     # 执行sql语句
    #     db.commit()
    #     cursor_insertpypi.close()
    #     print("insert_dependencies  [ name:", projectname,"] FINISHED")
    #     # print("update: ", git_name, " FINISHED")
    # except Exception as e:
    #     print("sql_update:", sql_insert)
    #     print("npm_all_releases error ",e)
    #     # 发生错误时回滚
    #     db.rollback()
    # db.close()

#查询该html_url是否存在，返回查询数量
def find_releases_count(project_name,package_version):
    sql = "SELECT COUNT(*) FROM npm_all_releases WHERE project_name = '%s' and package_version = '%s'" % (project_name,package_version)
    try:
        # 执行sql语句
        db_v = POOL_temp.connection()
        cursor_find_versionname = db_v.cursor()
        cursor_find_versionname.execute(sql)
        nums = cursor_find_versionname.fetchone()
        cursor_find_versionname.close()
        db_v.close()
        num = nums[0]
        return num
    except Exception:
        print("find_versionname() dberror")

def main():
    project_list=all_project_name()
    for project in project_list:
        projectid=project[0]
        projectidname=project[1]
        print("id: ",projectid,"projectidname: ",projectidname)
        try:
            get_project_info(projectidname)
            print("get_npm_project_dependencies  [ id:",projectid,"projectname:",projectidname,"] FINISHED")
        except Exception as e:
            print("get_project_info error! ",e)
            pass
    # get_project_info("lzmtest_host")

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