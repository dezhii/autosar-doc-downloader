import requests
import json
import os
import time
import random
from urllib.parse import urlparse, unquote
from pathlib import Path

class AutosarCPDocumentDownloader:
    def __init__(self):
        # 从output文件夹读取JSON文件
        self.output_dir = "output"
        self.documents_file = os.path.join(self.output_dir, "autosar_cp_documents.json")
        # 使用download_cp作为下载目录
        self.download_dir = "download_cp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
        }
        self.max_retries = 3
        self.download_log = os.path.join(self.download_dir, "download_cp_log.txt")
        
        # 创建下载目录
        os.makedirs(self.download_dir, exist_ok=True)

    def load_documents(self):
        """从JSON文件加载文档信息"""
        try:
            with open(self.documents_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载文档信息时出错: {e}")
            return []

    def get_filename_from_url(self, url):
        """从URL中提取文件名"""
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = os.path.basename(path)
        return filename

    def download_document(self, doc, index, total):
        """下载单个文档"""
        url = doc["url"]
        title = doc["title"]
        filename = self.get_filename_from_url(url)
        
        # 如果URL中没有文件名，使用标题作为文件名
        if not filename or filename == "":
            # 移除标题中的非法字符
            filename = "".join(c for c in title if c.isalnum() or c in " ._-").strip()
            filename = filename.replace(" ", "_")
            
            # 根据URL判断文件类型
            if url.endswith(".pdf"):
                filename += ".pdf"
            elif url.endswith(".zip"):
                filename += ".zip"
            else:
                filename += ".pdf"  # 默认为PDF
        
        save_path = os.path.join(self.download_dir, filename)
        
        # 检查文件是否已存在
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            if file_size > 0:
                print(f"[{index}/{total}] 文件已存在，跳过: {filename}")
                return True
        
        print(f"[{index}/{total}] 正在下载: {title}")
        print(f"URL: {url}")
        print(f"保存为: {filename}")
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, stream=True, timeout=60)
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                
                # 写入文件
                with open(save_path, 'wb') as f:
                    if total_size == 0:
                        f.write(response.content)
                    else:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                # 打印下载进度
                                progress = int(50 * downloaded / total_size)
                                print(f"\r进度: [{('#' * progress) + (' ' * (50 - progress))}] {downloaded / total_size:.1%}", end="")
                        print()  # 换行
                
                # 检查下载的文件大小
                if os.path.getsize(save_path) > 0:
                    print(f"下载成功: {filename}")
                    # 记录下载日志
                    self.log_download(doc, True)
                    return True
                else:
                    print(f"下载的文件大小为0，重试中...")
                    os.remove(save_path)  # 删除空文件
            except Exception as e:
                print(f"下载出错 (尝试 {attempt+1}/{self.max_retries}): {e}")
            
            # 如果不是最后一次尝试，则等待后重试
            if attempt < self.max_retries - 1:
                delay = random.uniform(2.0, 5.0)
                print(f"等待 {delay:.2f} 秒后重试...")
                time.sleep(delay)
        
        # 所有尝试都失败
        print(f"下载失败: {filename}")
        self.log_download(doc, False)
        return False

    def log_download(self, doc, success):
        """记录下载结果到日志文件"""
        status = "成功" if success else "失败"
        with open(self.download_log, 'a', encoding='utf-8') as f:
            f.write(f"{status}: {doc['title']} | {doc['url']}\n")

    def download_all(self):
        """下载所有文档"""
        documents = self.load_documents()
        if not documents:
            print("没有找到文档信息，请先运行收集脚本")
            return
        
        print(f"开始下载 {len(documents)} 个AUTOSAR CP文档...")
        
        # 初始化下载日志
        with open(self.download_log, 'w', encoding='utf-8') as f:
            f.write(f"AUTOSAR CP文档下载日志 (共 {len(documents)} 个)\n")
            f.write("=" * 80 + "\n\n")
        
        success_count = 0
        for i, doc in enumerate(documents, 1):
            # 添加随机延迟，避免被网站封锁
            if i > 1:
                delay = random.uniform(1.0, 3.0)
                print(f"等待 {delay:.2f} 秒...")
                time.sleep(delay)
            
            if self.download_document(doc, i, len(documents)):
                success_count += 1
        
        print(f"\n下载完成: 成功 {success_count}/{len(documents)}")


if __name__ == "__main__":
    downloader = AutosarCPDocumentDownloader()
    downloader.download_all() 