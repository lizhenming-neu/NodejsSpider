#!/usr/bin/python

import argparse
import os
import npmdependency

def initialise():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dependency", help="the target top level dependency to install", type=str)
    args = parser.parse_args()
    return args

#
# def get_dep(nameversion):
#
#     dep = npmdependency.Dependency()
#     dep_obj = dep.parse_dependency(nameversion)
#     print(dep_obj)
#
#     name=dep_obj["dep_name"]
#     version=dep_obj["dep_version"]
#
#
#     status = 0
#     for temp_top in top_list:
#         if name == temp_top["dep_name"] :
#             status = 1
#
#     if status == 0:
#         top_list.append(dep_obj);
#     else:
#         other_list.append(dep_obj)
#
#     dependency_list=dep.get_dependency_list(dep_obj)
#     print(dependency_list)
#     for dependency in dependency_list:
#         next_level_dep = dependency + '@' +  dependency_list[dependency].replace("^", "")
#         get_dep(next_level_dep)
#     # dep = npmdependency.Dependency()
#     # dep_obj = dep.parse_dependency(name)
#     # output_file_path = dep.download_npm(dep_obj)
#     # if output_file_path:
#     #     print("get dependencies from ", output_file_path)
#     #     artifact_dep = dep.get_dependencies_from_tar(output_file_path)
#     #     for dependency in artifact_dep:
#     #         next_level_dep = dependency + '@' + \
#     #             artifact_dep[dependency].replace("^", "")
#     #         get_dep(next_level_dep, output_dir)
#
#     return False


def main():
    global top_list,other_list
    top_list = []
    other_list=[]
    # list_top=
    # args = initialise()
    # outpath = ''.join((os.getcwd(), '\\', 'output'))
    # get_dep("lzmtest_host@3.0.0")
    print(top_list)
    print(other_list)
    # get_dep(args.dependency, outpath)


if __name__ == "__main__":
    main()
