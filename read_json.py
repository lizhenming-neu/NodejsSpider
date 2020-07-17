import json
import new_redundant_dependency_02

dnum = 0
ddnum=0
dddnum=0
duplicate_dependencylist = []
no_repeat_duplicate_dependencylist = []


def readJSON():
    global dnum, duplicate_dependencylist, no_repeat_duplicate_dependencylist,ddnum,dddnum
    with open("D://npmtest//alita@2.5.2/package-lock.json", 'r') as load_f:
    # with open("D://npmtest//20200614//@backstagedev-utils/package-lock.json", 'r') as load_f:

        load_dict = json.load(load_f)
        # dependencies=load_dict['dependencies']

        dependencies_list = []
        cirl_readJSON(load_dict, 0)
        print(dnum,'/',ddnum,'/',dddnum)
        ddl_len = len(duplicate_dependencylist)
        # print(ddl_len)
        for ddl1 in range(ddl_len):
            for ddl2 in range(ddl1, ddl_len):
                if duplicate_dependencylist[ddl1][1] < duplicate_dependencylist[ddl2][1]:
                    tem_ddl = duplicate_dependencylist[ddl1]
                    duplicate_dependencylist[ddl1] = duplicate_dependencylist[ddl2]
                    duplicate_dependencylist[ddl2] = tem_ddl

        # for ddl in duplicate_dependencylist:
        #     if ddl[1]>1:
        #         print(ddl[0],ddl[1])

        for ddlno1 in range(len(no_repeat_duplicate_dependencylist)):
            for ddlno2 in range(ddlno1, len(no_repeat_duplicate_dependencylist)):
                if no_repeat_duplicate_dependencylist[ddlno1][2] < no_repeat_duplicate_dependencylist[ddlno2][2]:
                    tem_ddl_no = no_repeat_duplicate_dependencylist[ddlno1]
                    no_repeat_duplicate_dependencylist[ddlno1] = no_repeat_duplicate_dependencylist[ddlno2]
                    no_repeat_duplicate_dependencylist[ddlno2] = tem_ddl_no

        templ = []
        for ddl in no_repeat_duplicate_dependencylist:
            status = 0
            for temp in templ:
                if temp[0] == ddl[0] and temp[2] < ddl[2]:
                    temp[1] = ddl[1]
                    temp[2] = ddl[2]
                    status=1
            if status==0:
                templ.append(ddl)

        for ddl_no in templ:
            if ddl_no[2] > 1:
                print('<br/>',ddl_no[0],',', ddl_no[1],',',ddl_no[2])


def cirl_readJSON(jsoninfo, n):
    global dnum, duplicate_dependencylist, no_repeat_duplicate_dependencylist,ddnum,dddnum
    dependencies = jsoninfo['dependencies']
    n = n + 1
    for dependency in dependencies:
        dnum = dnum + 1
        project_dependency = dependency
        project_version_range = dependencies[dependency]['version']

        project_info = '\"' + project_dependency + '\"' + ': ' + '\"' + project_version_range + '\"' + ','

        str = ''
        for i in range(n):
            str = str + '-'
        # print(str, project_info)
        if n == 1:
            ddnum=ddnum+1
        if n >= 2:
            dddnum=dddnum+1
            # print(str,project_info)
            ststus = 0
            ststus_np = 0
            for ddl in duplicate_dependencylist:
                if project_info == ddl[0]:
                    ddl[1] = ddl[1] + 1
                    ststus = 1
            if ststus == 0:
                temp = []
                temp.append(project_info)
                temp.append(1)
                duplicate_dependencylist.append(temp)

            for ddl2 in no_repeat_duplicate_dependencylist:
                if project_dependency == ddl2[0] and project_version_range == ddl2[1]:
                    ddl2[2] = ddl2[2] + 1
                    ststus_np = 1
            if ststus_np == 0:
                temp = []
                temp.append(project_dependency)
                temp.append(project_version_range)
                temp.append(1)
                no_repeat_duplicate_dependencylist.append(temp)

        try:
            # print(dependencies[dependency]['dependencies'])
            cirl_readJSON(dependencies[dependency], n)
            # n = n + 1
        except:
            pass


readJSON()
