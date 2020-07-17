#!/usr/bin/python

import re
import os
import shutil
import tarfile
import json
import requests
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
import semantic_version

class Dependency(object):
    def __init__(self):
        self._repo_url = 'https://registry.npm.taobao.org/'
    def get_page(self,url):
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36
        # headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/74.0.3729.157 Safari/537.36'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException:
            return None

    def get_results(self,url):

        headers = {'User-Agent': 'Mozilla/5.0',
                   'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Authorization': ' token 30ad34440e1bdc0016db7ae316c3d4a1d75d18c1'
                   }
        req = Request(url, headers=headers)
        response = urlopen(req).read()
        result = json.loads(response.decode())
        return result
    def _extract_npm_meta(self, file_path):
        package_json_path = 'package/package.json'
        tar = tarfile.open(file_path)
        tar_members = tar.getmembers()
        package_present = False
        for tar_info in tar_members:
            if tar_info.name == package_json_path:
                tar.extract(tar_info)
                package_present = True
        tar.close()
        return package_present

    #needs some work - ideally sort so the latest version is used not the early
    #Also multiple x.x don't necessrily work
    def _parse_version_nums(self, v_from, v_to):

        rep = {"=": "", ">": "", "=": "", "~": "", "<": ""}
        rep = dict((re.escape(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep.keys()))
        version = pattern.sub(lambda m: rep[re.escape(m.group(0))], v_from)

        #doesnt always assume the right value - temporary solution
        if "x" in version:
            version = version.replace("x", "1")
        return version

    def parse_dependency(self, name):

        temp_list = name.split('@')
        dep_name=temp_list[0]
        dep_versionrange=temp_list[1]
        # print("dep_name:",dep_name)
        # print("dep_versionrange:", dep_versionrange)

        npm_url = "https://registry.npm.taobao.org" + '/' + dep_name
        items = self.get_results(str(npm_url))
        verioninfos = items["versions"]
        str_version=""
        true_version=""
        for verioninfo in verioninfos:
            str_version=str(verioninfo)

            if semantic_version.Version(str_version) in semantic_version.NpmSpec(dep_versionrange):
                true_version=str_version
                print("dep_name: ", dep_name,"str_version: ", str_version," dep_versionrange: ",dep_versionrange)
                break
        if true_version!="":
            dep_map = {"dep_name": dep_name, "dep_version": true_version}
            return dep_map
        else:
            print(name + " 未匹配到有效版本！")
            exit()
        # reg_obj = re.compile("^(.*)@([~^\*>]?[=]?)([0-9]{1,2}\.[0-9x]{1,2}\.[0-9x]{1,2})(.*)")
        # dep_match = reg_obj.search(name)
        #
        # if dep_match:
        #     dep_name = dep_match.group(1)
        #     dep_version_from = dep_match.group(3)
        #     dep_version_to = dep_match.group(4)
        #
        #     dep_v = self._parse_version_nums(dep_version_from, dep_version_to)
        #     dep_map = {"dep_name": dep_name, "dep_version": dep_v}
        #     return dep_map
        # else:
        #     print("Invalid dependency format agains: " + name + " use package@version")
        #     exit()

    # def download_npm(self, dep_obj, output_dir):
    #     repo_artifact_base = (self._repo_url, dep_obj['dep_name'], '/-/')
    #     target_tar = (dep_obj['dep_name'], '-', dep_obj['dep_version'], '.tgz')
    #     url_request = ''.join((repo_artifact_base + target_tar))
    #     output_file = output_dir + '\\' + ''.join(target_tar)
    #     if os.path.exists(output_file):
    #         print("File already exist\'s. Returning current file path")
    #         return output_file
    #
    #     try:
    #         session = requests.Session()
    #         response = session.get(url_request, stream=True)
    #     except requests.exceptions.RequestException as e:
    #         print("failure Attempt to get " + ''.join(target_tar) + " " + str(e.message))
    #         exit()
    #
    #     if not response.status_code == 200:
    #         print ("Failure in geting Tar", str(response.status_code))
    #         exit()
    #
    #     response.raw.decode_content = True
    #     with open(output_file, 'wb') as out_file:
    #         shutil.copyfileobj(response.raw, out_file)
    #
    #     return output_file



    def get_dependency_list(self, dep_obj):
        npm_url="https://registry.npm.taobao.org"+ '/' + dep_obj['dep_name']
        # print(str(npm_url))
        items = self.get_results(str(npm_url))

        # disttagsinfo=items["dist-tags"]
        # latestversion=disttagsinfo["latest"]
        dep_version=dep_obj['dep_version']
        verioninfo=items["versions"]
        latestversioninfo=verioninfo[dep_version]

        if "dependencies" not in latestversioninfo:
            return {}

        return latestversioninfo['dependencies']





    def get_dependencies_from_tar(self, tar_file_path):
        if not self._extract_npm_meta(tar_file_path):
            print ("Failed to extract meta from NPM for file_path")
            exit()

        end = len(tar_file_path) - tar_file_path.rfind('output')
        package_path = tar_file_path[:-end] + "\\package\\package.json"
        data = json.load(open(package_path))

        data_len = len(data)
        if data_len > 0:
            package_dir = tar_file_path[:-end] + 'package'
            shutil.rmtree(package_dir)

        if "dependencies" not in data:
            return {}

        return data['dependencies']
