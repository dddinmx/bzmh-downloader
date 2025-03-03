import os,re,time,requests,img2pdf,shutil,glob,json
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from natsort import natsorted
from bs4 import BeautifulSoup

CONFIG = {
    'max_workers': 6,          # 并发线程数
    'request_timeout': 20,      # 请求超时时间
    'retry_times': 3,           # 重试次数
    'queue_buffer': 10,         # 队列缓冲数量
    'delay_range': (0.1, 0.5)   # 随机延迟范围
}

def title(url):
    response = requests.get(url,timeout=5)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find("h1", class_="comics-detail__title")
    chapter_slot = re.search(r'chapter_slot=(\d+)', html_content)
    if title_tag:
        title = title_tag.get_text(strip=True)
    if chapter_slot:
        chapter_max = chapter_slot.group(1)

    return str(title), int(chapter_max), html_content

def images_to_pdf(folder_path):
    try:
        images = []
        for fname in os.listdir(folder_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(folder_path, fname))
        
        images = natsorted(images)
        
        if not images:
            print(f"文件夹 {folder_path} 中没有图片")
            return

        # 创建PDF文件名
        pdf_name = f"{os.path.basename(folder_path)}.pdf"
        
        # 转换图片为PDF
        with open(pdf_name, "wb") as f:
            f.write(img2pdf.convert(images))
        
        print(f"成功生成PDF：{pdf_name}")

    except Exception as e:
        print(f"PDF生成失败：{str(e)}")

def download_image(session, base_url, save_dir, n, retries=3):
    img_url = base_url.format(n)
    file_path = os.path.join(save_dir, f"{n}.jpg")
    
    for attempt in range(retries):
        try:
            with session.get(img_url, stream=True, timeout=15) as response:
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(2048):
                            f.write(chunk)
                    return True, n, False  # 成功，无需停止
                else:
                    if response.status_code == 404:
                        return False, n, True  # 需要停止下载
                    else:
                        print(f"图片{n} 下载失败，状态码：{response.status_code}，第{attempt+1}次重试。")
        except Exception as e:
            print(f"图片{n} 下载失败：{str(e)}，第{attempt+1}次重试。")
        # 指数退避等待
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return False, n, False  # 失败但无需停止

def crawl_chapter(chapter_url, save_prefix):
    save_dir = f"{save_prefix:02d}"
    os.makedirs(save_dir, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    with requests.Session() as session:
        try:
            response = session.get(chapter_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"章节页访问失败：{response.status_code}")
                return
            
            match = re.search(r'(https?://[^/]+/scomic/[^/]+/\d+/[^/]+/1\.jpg)', response.text)
            if not match:
                print("未找到1.jpg的图片地址")
                return
            
            base_url = match.group(1).replace("1.jpg", "{}.jpg")
            print(f"开始下载章节：{save_dir}")

            max_workers = 6
            success_count = 0
            n = 1
            stop_flag = False

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                while not stop_flag:
                    futures = []
                    for _ in range(max_workers * 2):
                        futures.append(executor.submit(download_image, session, base_url, save_dir, n))
                        n += 1

                    for future in as_completed(futures):
                        success, num, stop_download = future.result()
                        if success:
                            success_count += 1
                            #print(f"Downloaded：{save_dir}/{num}.jpg")
                        else:
                            if stop_download:
                                stop_flag = True
                                executor.shutdown(wait=False)
                                break

                    time.sleep(0.5)

            print(f"章节 {save_dir} 下载完成，开始生成PDF...")
            images_to_pdf(save_dir)

        except Exception as e:
            print(f"章节处理异常：{str(e)}")

if __name__ == "__main__":
    banner = r"""
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    bzmh                  bzmh
    bzmh  bzmh  bzmh  bzmh  bzmh
    bzmh                  bzmh
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    """
    print(banner)
    print ("auther by dddinmx"+"\n"+"Github: https://github.com/dddinmx/bzmh-downloader")
    print ("漫画地址获取: https://cn.baozimhcn.com/"+"\n"+"              https://www.baozimh.com/")
    print ("\n"+"1 整本下载"+"\n"+"2 更新")
    model = str(input("选择: "))

    if model == "1":
        input_url = str(input("\n"+"输入漫画地址: "))
        base_chapter_url = input_url.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        folder, chapter_max, html_content = title(input_url)  # 漫画主要信息获取
        new_data = {folder: input_url}
        json_file_path = "./comic.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                existing_data = json.load(json_file)
        else:
            existing_data = {}
        existing_data.update(new_data)
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        if not os.path.exists(folder):
            os.makedirs(folder)

        if any(keyword in html_content for keyword in ["已完结", "已完結", "大结局", "大結局"]):
            # 获取完结漫画最大数
            pattern = r'chapter_slot=(\d+)'
            matches = re.findall(pattern, html_content)
            if matches:
                chapter_max = max(map(int, matches))
                print ("漫画已完结,章数: "+str(chapter_max))

            for chapter_num in range(0, chapter_max):
                url = base_chapter_url.format(chapter_num)
                response = requests.head(url, headers=headers)
                if response.status_code == 200:
                    print(f"\n开始处理第 {chapter_num+1} 章")
                    crawl_chapter(url, chapter_num+1)
                    save_dir = f"{chapter_num+1:02d}"
                    shutil.rmtree(save_dir)
                    pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                    for pdf_file in pdf_files:
                        shutil.move(pdf_file, "./"+folder)
                else:
                    print(f"章节{chapter_num+1}不存在，停止检测")
                    break
        else:
            for chapter_num in range(0, chapter_max):
                url = base_chapter_url.format(chapter_num)
                response = requests.head(url, headers=headers)
                if response.status_code == 200:
                    print(f"\n开始处理第 {chapter_num+1} 章")
                    crawl_chapter(url, chapter_num+1)
                    save_dir = f"{chapter_num+1:02d}"
                    shutil.rmtree(save_dir)
                    pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                    for pdf_file in pdf_files:
                        shutil.move(pdf_file, "./"+folder)
                else:
                    print(f"章节{chapter_num+1}不存在，停止检测")
                    break

    if model == "2":
        path = './'  
        folders = []
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    folders.append(entry.name)
        for folder in sorted(folders):
            print(folder)
        comic_name = input("输入要更新的漫画名: ")
        comic_path = "./"+comic_name
        pdf_files = [f for f in os.listdir("./"+folder) if f.endswith('.pdf')]
        numbers = []
        for pdf_file in pdf_files:
            match = re.search(r'\d+', pdf_file)
            if match:
                numbers.append(int(match.group()))
        if numbers:
            max_number = max(numbers)

        # 读取 JSON 文件
        json_file_path = "./comic.json"
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        update_url = data[comic_name]

        # 更新漫画
        base_chapter_url = update_url.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        folder, chapter_max, html_content = title(update_url)

        if any(keyword in html_content for keyword in ["已完结", "已完結", "大结局", "大結局"]):
            pattern = r'chapter_slot=(\d+)'
            matches = re.findall(pattern, html_content)
            if matches:
                chapter_max = max(map(int, matches))
                print ("漫画已完结,章数: "+str(chapter_max))
            if max_number < chapter_max:
                print ("找到更新,开始下载.")
            for chapter_num in range(max_number, chapter_max):
                url = base_chapter_url.format(chapter_num)
                response = requests.head(url, headers=headers)
                if response.status_code == 200:
                    print(f"\n开始处理第 {chapter_num+1} 章")
                    crawl_chapter(url, chapter_num+1)
                    save_dir = f"{chapter_num+1:02d}"
                    shutil.rmtree(save_dir)
                    pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                    for pdf_file in pdf_files:
                        shutil.move(pdf_file, "./"+folder)
                else:
                    print(f"章节{chapter_num+1}不存在，停止检测")
                    break
        if max_number < chapter_max:
            print ("找到更新,开始下载."+"\n")
            if not os.path.exists(folder):
                os.makedirs(folder)
            for chapter_num in range(max_number, chapter_max):
                url = base_chapter_url.format(chapter_num)
                response = requests.head(url, headers=headers)
                if response.status_code == 200:
                    print(f"\n开始处理第 {chapter_num+1} 章")
                    crawl_chapter(url, chapter_num+1)
                    save_dir = f"{chapter_num+1:02d}"
                    shutil.rmtree(save_dir)
                    pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                    for pdf_file in pdf_files:
                        shutil.move(pdf_file, "./"+folder)
                else:
                    print(f"章节{chapter_num+1}不存在，停止检测")
                    break
        else:
            print ("未找到更新.")
    else:
        print ("退出.")
