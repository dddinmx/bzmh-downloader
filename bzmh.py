import os, re, time, requests, img2pdf, shutil, glob, json
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from natsort import natsorted
from bs4 import BeautifulSoup

_0xC0NF = {
    'max_workers': 6,
    'request_timeout': 20,
    'retry_times': 3,
    'queue_buffer': 10,
    'delay_range': (0.1, 0.5)
}

def _0xT1(_0xU):
    _0xR = requests.get(_0xU, timeout=5)
    _0xH = _0xR.text
    _0xS = BeautifulSoup(_0xH, "html.parser")
    _0xT = _0xS.find("h1", class_="comics-detail__title")
    _0xCS = re.search(r'chapter_slot=(\d+)', _0xH)
    if _0xT:
        _0xTT = _0xT.get_text(strip=True)
    if _0xCS:
        _0xCM = _0xCS.group(1)
    return str(_0xTT), int(_0xCM), _0xH

def _0xP2(_0xFP):
    try:
        _0xL = []
        for _0xF in os.listdir(_0xFP):
            if _0xF.lower().endswith(('.jpg', '.jpeg', '.png')):
                _0xL.append(os.path.join(_0xFP, _0xF))
        _0xL = natsorted(_0xL)
        if not _0xL:
            print(f"文件夹 {_0xFP} 中没有图片")
            return
        _0xPDF = f"{os.path.basename(_0xFP)}.pdf"
        with open(_0xPDF, "wb") as _0xO:
            _0xO.write(img2pdf.convert(_0xL))
        print(f"成功生成PDF：{_0xPDF}")
    except Exception as _0xE:
        print(f"PDF生成失败：{str(_0xE)}")

def _0xDWN(_0xS, _0xBU, _0xSD, _0xN, _0xRT=3):
    _0xIU = _0xBU.format(_0xN)
    _0xFP = os.path.join(_0xSD, f"{_0xN}.jpg")
    for _0xA in range(_0xRT):
        try:
            with _0xS.get(_0xIU, stream=True, timeout=15) as _0xR:
                if _0xR.status_code == 200:
                    with open(_0xFP, 'wb') as _0xW:
                        for _0xC in _0xR.iter_content(2048):
                            _0xW.write(_0xC)
                    return True, _0xN, False
                else:
                    if _0xR.status_code == 404:
                        return False, _0xN, True
                    else:
                        print(f"图片{_0xN} 下载失败，状态码：{_0xR.status_code}，第{_0xA+1}次重试。")
        except Exception as _0xE:
            print(f"图片{_0xN} 下载失败：{str(_0xE)}，第{_0xA+1}次重试。")
        if _0xA < _0xRT - 1:
            time.sleep(2 ** _0xA)
    return False, _0xN, False

def _0xCRWL(_0xCU, _0xSP):
    _0xSD = f"{_0xSP:02d}"
    os.makedirs(_0xSD, exist_ok=True)
    _0xHDS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    with requests.Session() as _0xS:
        try:
            _0xR = _0xS.get(_0xCU, headers=_0xHDS, timeout=10)
            if _0xR.status_code != 200:
                print(f"章节页访问失败：{_0xR.status_code}")
                return
            _0xM = re.search(r'(https?://[^/]+/scomic/[^/]+/\d+/[^/]+/1\.jpg)', _0xR.text)
            if not _0xM:
                print("未找到1.jpg的图片地址")
                return
            _0xBU = _0xM.group(1).replace("1.jpg", "{}.jpg")
            print(f"开始下载章节：{_0xSD}")
            _0xMW = 4
            _0xSC = 0
            _0xN = 1
            _0xSF = False
            with ThreadPoolExecutor(max_workers=_0xMW) as _0xE:
                while not _0xSF:
                    _0xFuts = []
                    for _ in range(_0xMW * 2):
                        _0xFuts.append(_0xE.submit(_0xDWN, _0xS, _0xBU, _0xSD, _0xN))
                        _0xN += 1
                    for _0xFut in as_completed(_0xFuts):
                        _0xRes, _0xNum, _0xStop = _0xFut.result()
                        if _0xRes:
                            _0xSC += 1
                            print(f"已下载：{_0xSD}/{_0xNum}.jpg")
                        else:
                            if _0xStop:
                                _0xSF = True
                                _0xE.shutdown(wait=False)
                                break
                    time.sleep(0.5)
            print(f"章节 {_0xSD} 下载完成，开始生成PDF...")
            _0xP2(_0xSD)
        except Exception as _0xE:
            print(f"章节处理异常：{str(_0xE)}")

if __name__ == "__main__":
    _0xB = r"""
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    bzmh                  bzmh
    bzmh  bzmh  bzmh  bzmh  bzmh
    bzmh                  bzmh
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    """
    print(_0xB)
    print("auther by dddinmx"+"\n"+"Github: https://github.com/dddinmx/bzmh-downloader")
    print("漫画地址获取: https://www.twmanga.com/")
    print("\n"+"1 整本下载"+"\n"+"2 更新")
    _0xM = str(input("选择: "))
    if _0xM == "1":
        _0xIU = str(input("\n"+"输入漫画地址: "))
        _0xBCU = _0xIU.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        _0xHDS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        _0xF, _0xCM, _0xHC = _0xT1(_0xIU)
        _0xND = {_0xF: _0xIU}
        _0xJFP = "./comic.json"
        if os.path.exists(_0xJFP):
            with open(_0xJFP, "r", encoding="utf-8") as _0xJF:
                _0xED = json.load(_0xJF)
        else:
            _0xED = {}
        _0xED.update(_0xND)
        with open(_0xJFP, "w", encoding="utf-8") as _0xJF:
            json.dump(_0xED, _0xJF, ensure_ascii=False, indent=4)
        if not os.path.exists(_0xF):
            os.makedirs(_0xF)
        if "已完结" in _0xHC or "已完結" in _0xHC:
            _0xPTN = r'chapter_slot=(\d+)'
            _0xMs = re.findall(_0xPTN, _0xHC)
            if _0xMs:
                _0xCM = max(map(int, _0xMs))
                print("漫画已完结,章数: "+str(_0xCM))
            for _0xCN in range(0, _0xCM):
                _0xU = _0xBCU.format(_0xCN)
                _0xR = requests.head(_0xU, headers=_0xHDS)
                if _0xR.status_code == 200:
                    print(f"\n开始处理第 {_0xCN+1} 章")
                    _0xCRWL(_0xU, _0xCN+1)
                    _0xSD = f"{_0xCN+1:02d}"
                    shutil.rmtree(_0xSD)
                    _0xPFS = glob.glob(os.path.join(".", "*.pdf"))
                    for _0xPF in _0xPFS:
                        shutil.move(_0xPF, "./"+_0xF)
                else:
                    print(f"章节{_0xCN+1}不存在，停止检测")
                    break
        else:
            for _0xCN in range(0, _0xCM):
                _0xU = _0xBCU.format(_0xCN)
                _0xR = requests.head(_0xU, headers=_0xHDS)
                if _0xR.status_code == 200:
                    print(f"\n开始处理第 {_0xCN+1} 章")
                    _0xCRWL(_0xU, _0xCN+1)
                    _0xSD = f"{_0xCN+1:02d}"
                    shutil.rmtree(_0xSD)
                    _0xPFS = glob.glob(os.path.join(".", "*.pdf"))
                    for _0xPF in _0xPFS:
                        shutil.move(_0xPF, "./"+_0xF)
                else:
                    print(f"章节{_0xCN+1}不存在，停止检测")
                    break
    if _0xM == "2":
        _0xP = './'
        _0xFD = []
        with os.scandir(_0xP) as _0xENT:
            for _0xEN in _0xENT:
                if _0xEN.is_dir():
                    _0xFD.append(_0xEN.name)
        for _0xFDN in sorted(_0xFD):
            print(_0xFDN)
        _0xCNM = input("输入要更新的漫画名: ")
        _0xCP = "./"+_0xCNM
        _0xPFS = [f for f in os.listdir("./"+_0xCNM) if f.endswith('.pdf')]
        _0xNums = []
        for _0xPF in _0xPFS:
            _0xMch = re.search(r'\d+', _0xPF)
            if _0xMch:
                _0xNums.append(int(_0xMch.group()))
        if _0xNums:
            _0xMaxN = max(_0xNums)
        with open(_0xJFP, "r", encoding="utf-8") as _0xJF:
            _0xED = json.load(_0xJF)
        _0xUpURL = _0xED[_0xCNM]
        _0xBCU = _0xUpURL.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        _0xHDS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        _0xF, _0xCM, _0xHC = _0xT1(_0xUpURL)
        if "已完结" in _0xHC or "已完結" in _0xHC:
            _0xPTN = r'chapter_slot=(\d+)'
            _0xMs = re.findall(_0xPTN, _0xHC)
            if _0xMs:
                _0xCM = max(map(int, _0xMs))
                print("漫画已完结,章数: "+str(_0xCM))
            if _0xMaxN < _0xCM:
                print("找到更新,开始下载."+"\n")
            for _0xCN in range(_0xMaxN, _0xCM):
                _0xU = _0xBCU.format(_0xCN)
                _0xR = requests.head(_0xU, headers=_0xHDS)
                if _0xR.status_code == 200:
                    print(f"\n开始处理第 {_0xCN+1} 章")
                    _0xCRWL(_0xU, _0xCN+1)
                    _0xSD = f"{_0xCN+1:02d}"
                    shutil.rmtree(_0xSD)
                    _0xPFS = glob.glob(os.path.join(".", "*.pdf"))
                    for _0xPF in _0xPFS:
                        shutil.move(_0xPF, "./"+_0xF)
                else:
                    print(f"章节{_0xCN+1}不存在，停止检测")
                    break
        if _0xMaxN < _0xCM:
            print("找到更新,开始下载."+"\n")
            if not os.path.exists(_0xF):
                os.makedirs(_0xF)
            for _0xCN in range(_0xMaxN, _0xCM):
                _0xU = _0xBCU.format(_0xCN)
                _0xR = requests.head(_0xU, headers=_0xHDS)
                if _0xR.status_code == 200:
                    print(f"\n开始处理第 {_0xCN+1} 章")
                    _0xCRWL(_0xU, _0xCN+1)
                    _0xSD = f"{_0xCN+1:02d}"
                    shutil.rmtree(_0xSD)
                    _0xPFS = glob.glob(os.path.join(".", "*.pdf"))
                    for _0xPF in _0xPFS:
                        shutil.move(_0xPF, "./"+_0xF)
                else:
                    print(f"章节{_0xCN+1}不存在，停止检测")
                    break
        else:
            print("未找到更新.")
    else:
        print("退出.")
