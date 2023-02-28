#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import json
from tqdm import tqdm
import os
import sys

session = requests.session()
ico = {}
root_path = ""


def exe_path():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    elif __file__:
        path = os.path.dirname(__file__)
    global root_path
    root_path = path


def get_cookie():
    cookie_path = os.path.join(root_path, "cookie")
    is_exists = os.path.exists(cookie_path)
    if is_exists:
        with open(cookie_path, "r", encoding="utf-8") as f:
            _cookie_ = f.read()
            if _cookie_:
                return _cookie_
    else:
        _cookie_ = input("请输入在浏览器获取的cookie:")
        with open(cookie_path, 'x', encoding="utf-8") as fs:
            fs.write(_cookie_)
            print("cookie 保存成功！")
            return _cookie_


def getVideData(bv, cookie):
    url = "https://api.bilibili.com/x/web-interface/view?bvid=" + bv
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55",
        "cookie": "SESSDATA=" + cookie
    }
    videoJSON = json.loads(session.get(url=url, headers=headers).text)
    ico["video"] = videoJSON["data"]["pic"]
    ico["up"] = videoJSON["data"]["owner"]["face"]
    _video = videoJSON["data"]["pages"]
    url = "https://api.bilibili.com/x/player/playurl?cid={cid}&bvid={bv}&qn={qn}".format(cid=_video[0]["cid"], bv=bv,
                                                                                         qn=80)
    res = session.get(url=url, headers=headers).text
    res = json.loads(res)
    if res["data"]["quality"] == 80:
        quality = "高清-1080P"
    else:
        quality = "其他"
    videoInfo = {
        "url": res["data"]["durl"][0]["url"],
        "title": _video[0]["part"],
        "quality": quality
    }
    return videoInfo


def downVideo(_video):
    download_path = os.path.join(root_path, "downloads")
    folder = os.path.exists(download_path)
    if not folder:
        os.makedirs(download_path)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55",
        "referer": "https://www.bilibili.com"
    }
    url = _video["url"]
    file_name = _video["title"] + " " + _video["quality"]
    response = session.get(url=url, headers=headers, stream=True)

    total_size = int(int(response.headers["Content-Length"]) / 1024 + 0.5)

    with open(download_path + "\\" + file_name + ".mp4", "wb") as f:
        print('Video info：【{}】 文件大小：【{}MB】'.format(
            file_name, round(total_size / 1024, 1)))
        for chunk in tqdm(response.iter_content(chunk_size=1024), total=total_size, unit='k', desc="Downloading"):
            if chunk:
                f.write(chunk)


if __name__ == '__main__':
    try:
        _bv = sys.argv[1].split("video")[1].replace("/", "").split("?")[0]
        _cookie = get_cookie()
        video = getVideData(_bv, _cookie)
        downVideo(video)
    except KeyboardInterrupt as e:
        exit()
