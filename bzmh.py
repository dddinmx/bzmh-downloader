# -*- coding: utf-8 -*-
# auther by lmx
import os, re, time, requests, shutil, glob, json, img2pdf, random
from concurrent.futures import ThreadPoolExecutor, as_completed
import zipfile
from PIL import Image
from natsort import natsorted
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm

CONFIG = {
    'max_workers': 2,
    'request_timeout': 20,
    'retry_times': 3,
    'queue_buffer': 10,
    'delay_range': (0.1, 0.5)  # 延迟范围（秒）
}

green = "\033[1;32m"
red =  "\033[1;31m"
dark_gray = "\033[1;30m"
light_red = "\033[1;31m"
reset = "\033[0;0m"

def safe_print(message, end="\n", flush=False):
    tqdm.write(message, end=end)

def title(url):
    response = requests.get(url, timeout=5)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find("h1", class_="comics-detail__title")
    chapter_slot = re.search(r'chapter_slot=(\d+)', html_content)
    if title_tag:
        title = title_tag.get_text(strip=True)
    if chapter_slot:
        chapter_max = chapter_slot.group(1)
    return str(title), int(chapter_max), html_content

def images_to_cbz(folder_path):
    try:
        images = []
        for fname in os.listdir(folder_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(folder_path, fname))
        # 排序
        images = natsorted(images)
        if not images:
            safe_print(f"文件夹 {folder_path} 中没有图片")
            return
        cbz_name = f"{os.path.basename(folder_path)}.cbz"
        with zipfile.ZipFile(cbz_name, 'w') as cbz_file:
            for image_path in images:
                cbz_file.write(
                    image_path,
                    arcname=os.path.basename(image_path),
                    compress_type=zipfile.ZIP_STORED
                )
        safe_print(f"成功生成CBZ：{cbz_name}")
    except Exception as e:
        safe_print(f"CBZ生成失败：{str(e)}")

def images_to_pdf(folder_path):
    try:
        images = []
        for fname in os.listdir(folder_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(folder_path, fname))
        images = natsorted(images)
        if not images:
            safe_print(f"文件夹 {folder_path} 中没有图片")
            return
        pdf_name = f"{os.path.basename(folder_path)}.pdf"
        valid_images = []
        for image_path in images:
            with Image.open(image_path) as img:
                width, height = img.size
                if width < 3 or height < 3 or width > 14400 or height > 14400:
                    safe_print(f"图片 {image_path} 的尺寸不在允许范围内（{width}x{height}），跳过该图片")
                    continue
                valid_images.append(image_path)
        if not valid_images:
            safe_print("没有有效的图片可以生成PDF")
            return
        with open(pdf_name, "wb") as f:
            f.write(img2pdf.convert(valid_images))
        safe_print(f"成功生成PDF：{pdf_name}")
    except Exception as e:
        safe_print(f"PDF生成失败：{str(e)}")

def download_image(session, base_url, save_dir, n, retries=CONFIG['retry_times']):
    # 模拟阅读行为，在下载前随机延迟
    img_url = base_url.format(n)
    file_path = os.path.join(save_dir, f"{n}.jpg")
    for attempt in range(retries):
        time.sleep(random.uniform(*CONFIG['delay_range']))
        try:
            with session.get(img_url, stream=True, timeout=15) as response:
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(2048):
                            f.write(chunk)
                    return True, n, False
                else:
                    if response.status_code == 404:
                        return False, n, True
                    else:
                        safe_print(f"图片{n} " + red + "下载失败" + reset + f"，第{attempt+1}次重试。")
        except Exception as e:
            safe_print(f"图片{n} " + red + "下载失败" + reset + f"，第{attempt+1}次重试。")
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    return False, n, False

def crawl_chapter(chapter_url, save_prefix, comic_format):
    save_dir = f"{save_prefix:02d}"
    os.makedirs(save_dir, exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    with requests.Session() as session:
        try:
            response = session.get(chapter_url, headers=headers, timeout=10)
            if response.status_code != 200:
                safe_print(f"章节页访问失败：{response.status_code}")
                return
            match = re.search(r'(https?://[^/]+/scomic/[^/]+/\d+/[^/]+/1\.jpg)', response.text)
            if not match:
                safe_print(red + "未找到1.jpg的图片地址" + reset)
                return
            base_url = match.group(1).replace("1.jpg", "{}.jpg")
            safe_print(f"开始下载章节：{save_dir}")

            max_workers = CONFIG['max_workers']
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
                        else:
                            if stop_download:
                                stop_flag = True
                                executor.shutdown(wait=False)
                                break
                    # 批次处理后随机延迟，模拟人阅读时的间隔
                    time.sleep(random.uniform(*CONFIG['delay_range']))
            if comic_format == 1:
                safe_print(f"章节 {save_dir} 下载完成，开始生成PDF...")
                images_to_pdf(save_dir)
            elif comic_format == 2:
                safe_print(f"章节 {save_dir} 下载完成，开始生成CBZ...")
                images_to_cbz(save_dir)
        except Exception as e:
            safe_print(f"章节处理异常：{str(e)}")

def pdf_cbz_update(chapter_max, max_number_pdf, folder, base_chapter_url, headers, comic_format):
    now_1 = datetime.now().strftime("%H:%M:%S")
    safe_print(green + "[" + now_1 + "]" + "  Start  " + folder + reset)
    with tqdm(
        total=chapter_max - max_number_pdf,
        desc="进度",
        unit="章",
        position=0,
        leave=True,
        dynamic_ncols=True
    ) as main_pbar:
        for chapter_num in range(max_number_pdf, chapter_max):
            url = base_chapter_url.format(chapter_num)
            response = requests.head(url, headers=headers)
            if response.status_code == 200:
                safe_print("\033[s", end="", flush=True)
                safe_print(f"开始处理第 {chapter_num+1} 章")
                crawl_chapter(url, chapter_num+1, comic_format)
                time.sleep(40)
                safe_print("\033[u\033[J", end="", flush=True)
                save_dir = f"{chapter_num+1:02d}"
                try:
                    shutil.rmtree(save_dir)
                except FileNotFoundError:
                    safe_print(f"目录 {save_dir} 不存在，无需删除")
                except Exception as e:
                    safe_print(f"删除目录时发生错误: {e}")
                cbz_files = glob.glob(os.path.join(".", "*.cbz"))
                for cbz_file in cbz_files:
                    shutil.move(cbz_file, os.path.join(".", folder))
                pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                for pdf_file in pdf_files:
                    shutil.move(pdf_file, "./" + folder)
            else:
                safe_print(f"章节{chapter_num+1}不存在，停止检测")
                break
            main_pbar.update(1)
            main_pbar.set_postfix_str(f"当前章节 {chapter_num+1}")
    return now_1

def main(model, comic_format):
    if model == "1":
        input_url = str(input("\n" + "输入漫画地址: "))
        base_chapter_url = input_url.replace("/comic/", "/comic/chapter/") + "/0_{}.html"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        folder, chapter_max, html_content = title(input_url)  # 漫画信息
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

        # 获取完结漫画最大数
        pattern = r'chapter_slot=(\d+)'
        matches = re.findall(pattern, html_content)
        if matches:
            chapter_max = max(map(int, matches))
            safe_print("漫画章数: " + str(chapter_max))
        now_1 = datetime.now().strftime("%H:%M:%S")
        safe_print(green + "[" + now_1 + "]" + "  Start  " + folder + reset)
        with tqdm(
            total=chapter_max - 0,
            desc="进度",
            unit="章",
            position=0,
            leave=True,
            dynamic_ncols=True
        ) as main_pbar:
            for chapter_num in range(0, chapter_max):
                url = base_chapter_url.format(chapter_num)
                response = requests.head(url, headers=headers)
                if response.status_code == 200:
                    safe_print("\033[s", end="", flush=True)
                    safe_print(f"开始处理第 {chapter_num+1} 章")
                    crawl_chapter(url, chapter_num+1, comic_format)
                    # 每章处理后随机延迟
                    time.sleep(40)
                    safe_print("\033[u\033[J", end="", flush=True)
                    save_dir = f"{chapter_num+1:02d}"
                    try:
                        shutil.rmtree(save_dir)
                    except FileNotFoundError:
                        safe_print(f"目录 {save_dir} 不存在，无需删除")
                    except Exception as e:
                        safe_print(f"删除目录时发生错误: {e}")
                    cbz_files = glob.glob(os.path.join(".", "*.cbz"))
                    for cbz_file in cbz_files:
                        shutil.move(cbz_file, os.path.join(".", folder))
                    pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                    for pdf_file in pdf_files:
                        shutil.move(pdf_file, "./" + folder)
                else:
                    safe_print(f"章节{chapter_num+1}不存在，停止检测")
                    break
                main_pbar.update(1)  # 每完成一个章节更新
                main_pbar.set_postfix_str(f"当前章节 {chapter_num+1}")
            now_2 = datetime.now().strftime("%H:%M:%S")
            safe_print("\n" + green + "[" + now_2 + "]" + "  End" + reset)
            time_format = "%H:%M:%S"
            time_1 = datetime.strptime(now_1, time_format)
            time_2 = datetime.strptime(now_2, time_format)
            time_diff = time_2 - time_1
            safe_print("总耗时: " + str(time_diff))
            for i in range(1): 
                safe_print("\033[F\033[J", end="")
    elif model == "2":
        path = './'
        folders = []
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    folders.append(entry.name)
        for folder in sorted(folders):
            safe_print(folder)
        comic_name = input("输入要更新的漫画名: ")
        comic_path = "./" + comic_name
        cbz_files = [f for f in os.listdir(comic_path) if f.endswith('.cbz')]
        pdf_files = [f for f in os.listdir(comic_path) if f.endswith('.pdf')]
        numbers = []
        pdf_numbers = []
        for cbz_file in cbz_files:
            match = re.search(r'\d+', cbz_file)
            if match:
                numbers.append(int(match.group()))
        if numbers:
            max_number = max(numbers)

        for pdf_file in pdf_files:
            match = re.search(r'\d+', pdf_file)
            if match:
                pdf_numbers.append(int(match.group()))
        if pdf_numbers:
            max_number_pdf = max(pdf_numbers)

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

        pattern = r'chapter_slot=(\d+)'
        matches = re.findall(pattern, html_content)
        if matches:
            chapter_max = max(map(int, matches))
            safe_print("漫画章数: " + str(chapter_max))
        if comic_format == 1:
            now_1 = pdf_cbz_update(chapter_max, max_number_pdf, folder, base_chapter_url, headers, comic_format)
            now_2 = datetime.now().strftime("%H:%M:%S")
            safe_print(green + "[" + now_2 + "]" + "  End" + reset)
            time_format = "%H:%M:%S"
            time_1 = datetime.strptime(now_1, time_format)
            time_2 = datetime.strptime(now_2, time_format)
            time_diff = time_2 - time_1
            safe_print("总耗时: " + str(time_diff))
            for i in range(1): 
                safe_print("\033[F\033[J", end="")
        if comic_format == 2:
            now_1 = pdf_cbz_update(chapter_max, max_number, folder, base_chapter_url, headers, comic_format)
            now_2 = datetime.now().strftime("%H:%M:%S")
            safe_print(green + "[" + now_2 + "]" + "  End" + reset)
            time_format = "%H:%M:%S"
            time_1 = datetime.strptime(now_1, time_format)
            time_2 = datetime.strptime(now_2, time_format)
            time_diff = time_2 - time_1
            safe_print("总耗时: " + str(time_diff))
            for i in range(1): 
                safe_print("\033[F\033[J", end="")
        if max_number < chapter_max:
            safe_print("找到更新,开始下载." + "\n")
            if not os.path.exists(folder):
                os.makedirs(folder)
            now_1 = datetime.now().strftime("%H:%M:%S")
            safe_print(green + "[" + now_1 + "]" + "  Start  " + folder + reset)
            with tqdm(
                total=chapter_max - max_number,
                desc="进度",
                unit="章",
                position=0,
                leave=True,
                dynamic_ncols=True
            ) as main_pbar:
                for chapter_num in range(max_number, chapter_max):
                    url = base_chapter_url.format(chapter_num)
                    response = requests.head(url, headers=headers)
                    if response.status_code == 200:
                        safe_print(f"开始处理第 {chapter_num+1} 章")
                        crawl_chapter(url, chapter_num+1, comic_format)
                        time.sleep(20)
                        save_dir = f"{chapter_num+1:02d}"
                        try:
                            shutil.rmtree(save_dir)
                        except FileNotFoundError:
                            safe_print(f"目录 {save_dir} 不存在，无需删除")
                        except Exception as e:
                            safe_print(f"删除目录时发生错误: {e}")
                        cbz_files = glob.glob(os.path.join(".", "*.cbz"))
                        for cbz_file in cbz_files:
                            shutil.move(cbz_file, os.path.join(".", folder))
                        pdf_files = glob.glob(os.path.join(".", "*.pdf"))
                        for pdf_file in pdf_files:
                            shutil.move(pdf_file, "./" + folder)
                    else:
                        safe_print(f"章节{chapter_num+1}不存在，停止检测")
                        break
                    main_pbar.update(1)
                    main_pbar.set_postfix_str(f"当前章节 {chapter_num+1}")
            now_2 = datetime.now().strftime("%H:%M:%S")
            safe_print(green + "[" + now_2 + "]" + "  End" + reset)
            time_format = "%H:%M:%S"
            time_1 = datetime.strptime(now_1, time_format)
            time_2 = datetime.strptime(now_2, time_format)
            time_diff = time_2 - time_1
            safe_print("总耗时: " + str(time_diff))
            for i in range(1): 
                safe_print("\033[F\033[J", end="")
        else:
            safe_print("未找到更新.")
    else:
        safe_print("退出.")

#-------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = dark_gray + r"""
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    bzmh                  bzmh
    bzmh  bzmh  bzmh  bzmh  bzmh
    bzmh                  bzmh
    bzmhbzmhbzmhbzmhbzmhbzmhbzmh
    """ + reset
    safe_print(banner)
    safe_print("      auther by " + light_red + "dddinmx" + reset + "\n" + dark_gray + "      Github: https://github.com/dddinmx/bzmh-downloader" + reset)
    safe_print(dark_gray + "漫画地址获取: https://cn.baozimhcn.com/" + "\n" + "              https://www.baozimh.com/" + reset)
    safe_print("\n" + "[1] 整本下载    [2] 更新")
    model = str(input("选择: "))
    safe_print("[1] PDF    [2] CBZ")
    comic_format = input("选择保存格式: ")
    main(model, int(comic_format))
