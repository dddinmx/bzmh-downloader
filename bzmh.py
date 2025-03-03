import os as _0x1
import re as _0x2
import time as _0x3
import requests as _0x4
import img2pdf as _0x5
import shutil as _0x6
import glob as _0x7
import json as _0x8
from concurrent.futures import ThreadPoolExecutor as _0x9, as_completed as _0xa
from PIL import Image as _0xb
from natsort import natsorted as _0xc
from bs4 import BeautifulSoup as _0xd

_0xe = {
    'max_workers': 6,
    'request_timeout': 20,
    'retry_times': 3,
    'queue_buffer': 10,
    'delay_range': (0.1, 0.5)
}

def _0xf(_0x10):
    _0x11 = _0x4.get(_0x10, timeout=5)
    _0x12 = _0x11.text
    _0x13 = _0xd(_0x12, "html.parser")
    _0x14 = _0x13.find("h1", class_="comics-detail__title")
    _0x15 = _0x2.search(r'chapter_slot=(\d+)', _0x12)
    if _0x14:
        _0x16 = _0x14.get_text(strip=True)
    if _0x15:
        _0x17 = _0x15.group(1)
    return str(_0x16), int(_0x17), _0x12

def _0x18(_0x19):
    try:
        _0x1a = []
        for _0x1b in _0x1.listdir(_0x19):
            if _0x1b.lower().endswith(('.jpg', '.jpeg', '.png')):
                _0x1a.append(_0x1.path.join(_0x19, _0x1b))
        _0x1a = _0xc(_0x1a)
        if not _0x1a:
            print(f"文件夹 {_0x19} 中没有图片")
            return
        _0x1c = f"{_0x1.path.basename(_0x19)}.pdf"
        with open(_0x1c, "wb") as _0x1d:
            _0x1d.write(_0x5.convert(_0x1a))
        print(f"成功生成PDF：{_0x1c}")
    except Exception as _0x1e:
        print(f"PDF生成失败：{str(_0x1e)}")

def _0x1f(_0x20, _0x21, _0x22, _0x23, _0x24=3):
    _0x25 = _0x21.format(_0x23)
    _0x26 = _0x1.path.join(_0x22, f"{_0x23}.jpg")
    for _0x27 in range(_0x24):
        try:
            with _0x20.get(_0x25, stream=True, timeout=15) as _0x28:
                if _0x28.status_code == 200:
                    with open(_0x26, 'wb') as _0x29:
                        for _0x2a in _0x28.iter_content(2048):
                            _0x29.write(_0x2a)
                    return True, _0x23, False
                else:
                    if _0x28.status_code == 404:
                        return False, _0x23, True
                    else:
                        print(f"图片{_0x23} 下载失败，状态码：{_0x28.status_code}，第{_0x27+1}次重试。")
        except Exception as _0x2b:
            print(f"图片{_0x23} 下载失败：{str(_0x2b)}，第{_0x27+1}次重试。")
        if _0x27 < _0x24 - 1:
            _0x3.sleep(2 ** _0x27)
    return False, _0x23, False

def _0x2c(_0x2d, _0x2e):
    _0x2f = f"{_0x2e:02d}"
    _0x1.makedirs(_0x2f, exist_ok=True)
    _0x30 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    with _0x4.Session() as _0x31:
        try:
            _0x32 = _0x31.get(_0x2d, headers=_0x30, timeout=10)
            if _0x32.status_code != 200:
                print(f"章节页访问失败：{_0x32.status_code}")
                return
            _0x33 = _0x2.search(r'(https?://[^/]+/scomic/[^/]+/\d+/[^/]+/1\.jpg)', _0x32.text)
            if not _0x33:
                print("未找到1.jpg的图片地址")
                return
            _0x34 = _0x33.group(1).replace("1.jpg", "{}.jpg")
            print(f"开始下载章节：{_0x2f}")
            _0x35 = 4
            _0x36 = 0
            _0x37 = 1
            _0x38 = False
            with _0x9(max_workers=_0x35) as _0x39:
                while not _0x38:
                    _0x3a = []
                    for _ in range(_0x35 * 2):
                        _0x3a.append(_0x39.submit(_0x1f, _0x31, _0x34, _0x2f, _0x37))
                        _0x37 += 1
                    for _0x3b in _0xa(_0x3a):
                        _0x3c, _0x3d, _0x3e = _0x3b.result()
                        if _0x3c:
                            _0x36 += 1
                            print(f"已下载：{_0x2f}/{_0x3d}.jpg")
                        else:
                            if _0x3e:
                                _0x38 = True
                                _0x39.shutdown(wait=False)
                                break
                    _0x3.sleep(0.5)
            print(f"章节 {_0x2f} 下载完成，开始生成PDF...")
            _0x18(_0x2f)
        except Exception as _0x3f:
            print(f"章节处理异常：{str(_0x3f)}")

if __name__ == "__main__":
    _0x40 = r"""
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    bzmh                  bzmh
    bzmh  bzmh  bzmh  bzmh  bzmh
    bzmh                  bzmh
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    """
    print(_0x40)
    print("auther by dddinmx"+"\n"+"Github: https://github.com/dddinmx/bzmh-downloader")
    print("漫画地址获取: https://www.twmanga.com/")
    print("\n"+"1 整本下载"+"\n"+"2 更新")
    _0x41 = str(input("选择: "))
    if _0x41 == "1":
        _0x42 = str(input("\n"+"输入漫画地址: "))
        _0x43 = _0x42.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        _0x44 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        _0x45, _0x46, _0x47 = _0xf(_0x42)
        _0x48 = {_0x45: _0x42}
        _0x49 = "./comic.json"
        if _0x1.path.exists(_0x49):
            with open(_0x49, "r", encoding="utf-8") as _0x4a:
                _0x4b = _0x8.load(_0x4a)
        else:
            _0x4b = {}
        _0x4b.update(_0x48)
        with open(_0x49, "w", encoding="utf-8") as _0x4c:
            _0x8.dump(_0x4b, _0x4c, ensure_ascii=False, indent=4)
        if not _0x1.path.exists(_0x45):
            _0x1.makedirs(_0x45)
        if "已完结" in _0x47 or "已完結" in _0x47:
            _0x4d = r'chapter_slot=(\d+)'
            _0x4e = _0x2.findall(_0x4d, _0x47)
            if _0x4e:
                _0x46 = max(map(int, _0x4e))
                print("漫画已完结,章数: "+str(_0x46))
            for _0x4f in range(0, _0x46):
                _0x50 = _0x43.format(_0x4f)
                _0x51 = _0x4.head(_0x50, headers=_0x44)
                if _0x51.status_code == 200:
                    print(f"\n开始处理第 {_0x4f+1} 章")
                    _0x2c(_0x50, _0x4f+1)
                    _0x52 = f"{_0x4f+1:02d}"
                    _0x6.rmtree(_0x52)
                    _0x53 = _0x7.glob(_0x1.path.join(".", "*.pdf"))
                    for _0x54 in _0x53:
                        _0x6.move(_0x54, "./"+_0x45)
                else:
                    print(f"章节{_0x4f+1}不存在，停止检测")
                    break
        else:
            for _0x4f in range(0, _0x46):
                _0x50 = _0x43.format(_0x4f)
                _0x51 = _0x4.head(_0x50, headers=_0x44)
                if _0x51.status_code == 200:
                    print(f"\n开始处理第 {_0x4f+1} 章")
                    _0x2c(_0x50, _0x4f+1)
                    _0x52 = f"{_0x4f+1:02d}"
                    _0x6.rmtree(_0x52)
                    _0x53 = _0x7.glob(_0x1.path.join(".", "*.pdf"))
                    for _0x54 in _0x53:
                        _0x6.move(_0x54, "./"+_0x45)
                else:
                    print(f"章节{_0x4f+1}不存在，停止检测")
                    break
    elif _0x41 == "2":
        _0x55 = './'
        _0x56 = []
        with _0x1.scandir(_0x55) as _0x57:
            for _0x58 in _0x57:
                if _0x58.is_dir():
                    _0x56.append(_0x58.name)
        for _0x59 in sorted(_0x56):
            print(_0x59)
        _0x5a = input("输入要更新的漫画名: ")
        _0x5b = "./"+_0x5a
        _0x5c = _0x7.glob(_0x1.path.join(_0x5b, "*.pdf"))
        _0x5d = len(_0x5c)
        _0x49 = "./comic.json"
        with open(_0x49, "r", encoding="utf-8") as _0x5e:
            _0x5f = _0x8.load(_0x5e)
        _0x60 = _0x5f[_0x5a]
        _0x43 = _0x60.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        _0x44 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        _0x45, _0x46, _0x47 = _0xf(_0x60)
        if "已完结" in _0x47 or "已完結" in _0x47:
            _0x4d = r'chapter_slot=(\d+)'
            _0x4e = _0x2.findall(_0x4d, _0x47)
            if _0x4e:
                _0x46 = max(map(int, _0x4e))
                print("漫画已完结,章数: "+str(_0x46))
            if _0x5d < _0x46:
                print("找到更新,开始下载."+"\n")
            for _0x4f in range(_0x5d, _0x46):
                _0x50 = _0x43.format(_0x4f)
                _0x51 = _0x4.head(_0x50, headers=_0x44)
                if _0x51.status_code == 200:
                    print(f"\n开始处理第 {_0x4f+1} 章")
                    _0x2c(_0x50, _0x4f+1)
                    _0x52 = f"{_0x4f+1:02d}"
                    _0x6.rmtree(_0x52)
                    _0x53 = _0x7.glob(_0x1.path.join(".", "*.pdf"))
                    for _0x54 in _0x53:
                        _0x6.move(_0x54, "./"+_0x45)
                else:
                    print(f"章节{_0x4f+1}不存在，停止检测")
                    break
        if _0x5d < _0x46:
            print("找到更新,开始下载."+"\n")
            if not _0x1.path.exists(_0x45):
                _0x1.makedirs(_0x45)
            for _0x4f in range(_0x5d, _0x46):
                _0x50 = _0x43.format(_0x4f)
                _0x51 = _0x4.head(_0x50, headers=_0x44)
                if _0x51.status_code == 200:
                    print(f"\n开始处理第 {_0x4f+1} 章")
                    _0x2c(_0x50, _0x4f+1)
                    _0x52 = f"{_0x4f+1:02d}"
                    _0x6.rmtree(_0x52)
                    _0x53 = _0x7.glob(_0x1.path.join(".", "*.pdf"))
                    for _0x54 in _0x53:
                        _0x6.move(_0x54, "./"+_0x45)
                else:
                    print(f"章节{_0x4f+1}不存在，停止检测")
                    break
        else:
            print("未找到更新.")
    else:
        print("退出.")
