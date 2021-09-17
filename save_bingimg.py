#!/usr/bin/python3

import json
from urllib import request
import os
import datetime


class BingWallpaper():
    """下载必应壁纸"""
    def __init__(self):
        self.filePath = "/test"
        self.hosts = "http://cn.bing.com"
        self.imgDate = ""
        self.imgUrl = ""
        self.imgFileName = "bingimg.jpg"

    def __get_json_data(self, idx = 0):
        # idx = 0是今天的，-1明天，1昨天
        json_url = self.hosts+"/HPImageArchive.aspx?format=js&n=1&idx={}".format(idx)
        try:
            data = request.urlopen(json_url).read().decode("utf-8")
            json_data = json.loads(data)
            self.imgDate = json_data["images"][0]["enddate"]
            self.imgUrl = self.hosts + json_data["images"][0]["url"]
            self.imgFileName = self.imgDate+"_"+json_data["images"][0]["url"].split("/")[4]
        except Exception as f:
            print("get_json_data:",f)

    def __down_img(self):
        with request.urlopen(self.imgUrl) as f:
            data = f.read()
            # 图片存的路径为 G:\Pictures\DesktoBackGround目录
            todayDate = datetime.datetime.now().strftime("%Y%m%d")
            fname = os.path.join(self.filePath,self.imgFileName)
            fname = self.imgFileName
            fnamebase,fnameext = os.path.splitext(fname)
            fname = fnamebase + todayDate +fnameext
            print('fname',fname)
            with open(fname, mode="wb") as f:
                f.write(data)

    def save_img(self, idx = 0):
        self.__get_json_data(idx)
        self.__down_img()
        print("{}download!".format(self.imgFileName))

if __name__ == '__main__':
    print("path:",__file__)
    print("run...")
    wall = BingWallpaper()
    wall.save_img()
    print("end!")
    #exit = input("please enter any key to exit...")
