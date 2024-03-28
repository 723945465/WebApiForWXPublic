import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
from io import BytesIO
import os

# 设置 tesseract 的安装路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



def extract_text_from_image(image_url):

    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        text = pytesseract.image_to_string(img, lang='chi_sim')

        # 去除换行符
        text = text.replace('\n', ' ')
        # 去掉中文文字之间的空格
        text = ''.join([c if c.strip() or ord(c) > 127 else '' for c in text])
        # 保留连续空格中的一个空格
        text = ' '.join(text.split())

        return text.strip()

    except Exception  as e:
        print(f"Error while extract_text_from_image in parse_WXPublic_webpage: {e}")
        return ""



def parse_WXPublic_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取网页中的所有文字
    all_text = soup.get_text()
    all_image_text = ""
    # 查找网页中的所有图片标签
    images = soup.find_all('img')
    for image in images:
        # 检查图片的类名，如果包含特定类名，则跳过该图片
        if 'rich_pages' not in image.get('class', []):
            continue

        # 获取图片链接
        image_url = image.get('data-src') or image.get('src')  # 尝试获取 data-src 属性，如果为空则获取 src 属性
        if image_url:
            # 使用 OCR 识别图片中的文本
            image_text = extract_text_from_image(image_url)
            if len(image_text) > 0:
                all_image_text = all_image_text + image_text

    if len(all_image_text) > 0:
        all_text = all_text + "插图文字：" + all_image_text

    return all_text


if __name__ == "__main__":
    webpage_url = 'https://mp.weixin.qq.com/s?__biz=Mzg5NjY2NjQ4Mg==&mid=2247484629&idx=1&sn=eaef8ed0556042288d6c33f5601a11c1&chksm=c07cdac8f70b53de4bb48bf3abdf6534354f0b0b7604910fdbee76b2cad9c6b1ce2b6e388d42&token=935428064&lang=zh_CN#rd'  # 你要解析的网页链接
    parsed_text = parse_WXPublic_webpage(webpage_url)
    print(parsed_text)
