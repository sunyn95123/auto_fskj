
# -*- coding: utf-8 -*-
try:
    import os
    import re
    import ujson
    import time
    from time import sleep
    import requests
    import  platform
    import eventlet
    import os, subprocess
except ImportError as e:
    print("{}库没有安装".format(e.name))


class iosDeployServer():

    def __init__(self):
        self.fild_ipa = None
        self.info = None

    def iosDeploy(self, file_path):
        "执行安装"
        cmd="/usr/local/bin/ios-deploy –uninstall –debug --bundle %s" % file_path
        print(cmd)
        install_app = os.popen(cmd) #执行该命令
        sleep(4)
        self.info = install_app.readlines()  #读取命令行的输出到一个list
        print(self.info[-1])
        self.fild_ipa = file_path.split('/')[-1]

        try:
            if "Installed package" in self.info[-1]:
                print(f"'{self.fild_ipa}'正常安装")
            elif "VerifyingApplication" in self.info[-1]:
                print("↑️无法安装:%s" % file_path)
                assertion = f"'{self.fild_ipa}'相关包已掉签，请注意!"
                self.getDingMes(assertion)
            else:
                print(f"'{self.fild_ipa}'异常安装")
        except Exception as e:
            erroyMessage = str(e)
            print(erroyMessage)


    def detectDevice(self):
        "检查设备连接"
        cmd = "/usr/local/bin/ios-deploy -c"
        print(cmd)
        deviec = os.popen(cmd)  # 执行该命令
        self.info = deviec.readlines()  # 读取命令行的输出到一个list
        print(self.info[-1])
        if "connected through USB" in self.info[-1]:
            assertion = '设备已连接'
            print(assertion)
        else:
            assertion = "'设备连接异常,请检查设备'"
            self.getDingMes(assertion)

    def testing(self, assertion):
        "test"
        if '设备连接异常,请检查连接设备' in assertion:
            exit()

    def getDingMes(self, assertion):
        """发送钉钉信息"""
        URL = 'https://oapi.dingtalk.com/robot/send?access_token=edaf153b163eccc4e0dc6c3e6831570234749e35026bbe639db4dfb21bf3b2a8'
        HEADERS = {
            "Content-Type": "application/json ;charset=utf-8 "
        }
        # content = f"'{self.fild_ipa}'相关包已掉签，请注意!"
        stringBody = {
            "msgtype": "text",
            "text": {"content": assertion},
            "at": {
                "atMobiles": ["17621458930"],
                "isAtAll": True
            }
        }
        result = requests.post(url=URL, data=ujson.dumps(stringBody), headers=HEADERS)
        if result.status_code == 200:
            if '设备连接异常,请检查连接设备' in assertion:
                exit()
            elif '设备连接异常,请检查设备' in assertion:
                os.remove(file_path)  # 删除已掉包路径
            else:
                return result.text



if __name__ == '__main__':
    app = iosDeployServer()
    work_dir = '/Users/sunyn/Desktop/appList'
    app.detectDevice()
    for parent, dirnames, filenames in os.walk(work_dir, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            if file_path.endswith("DS_Store"):
                continue
            print('file_path：%s' % file_path)
            app.iosDeploy(file_path)
