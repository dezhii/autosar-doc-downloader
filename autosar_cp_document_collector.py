import requests
from bs4 import BeautifulSoup
import time
import random
import os
import re
import json

class AutosarCPDocumentCollector:
    def __init__(self):
        self.base_url = "https://www.autosar.org/search"
        self.params = {
            "tx_solr[filter][0]": "category:R24-11",
            "tx_solr[filter][1]": "platform:CP",
            "tx_solr[q]": ""
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Referer": "https://www.autosar.org/search"
        }
        self.documents = set()  # 使用集合避免重复
        # 创建output文件夹
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = os.path.join(self.output_dir, "autosar_cp_documents.txt")
        self.json_output_file = os.path.join(self.output_dir, "autosar_cp_documents.json")
        self.target_count = 234
        self.max_retries = 3
        self.max_pages = 20  # 设置一个较大的最大页数，以防分页信息不准确

    def get_page(self, page_number=1, retries=0):
        """获取指定页码的内容，支持重试"""
        if retries >= self.max_retries:
            print(f"获取第 {page_number} 页失败，已达到最大重试次数")
            return None
        
        params = self.params.copy()
        if page_number > 1:
            params["tx_solr[page]"] = page_number
        
        try:
            print(f"正在获取第 {page_number} 页...")
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 保存页面内容用于调试（仅保存第一页和有问题的页面）
            if page_number == 1 or len(self.parse_documents(response.text)) == 0:
                debug_file = os.path.join(self.output_dir, f"autosar_cp_page_{page_number}.html")
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"已保存页面内容到 {debug_file}")
            
            return response.text
        except requests.RequestException as e:
            print(f"获取第 {page_number} 页时出错: {e}")
            # 增加延迟并重试
            delay = random.uniform(2.0, 5.0)
            print(f"等待 {delay:.2f} 秒后重试...")
            time.sleep(delay)
            return self.get_page(page_number, retries + 1)

    def parse_documents(self, html_content):
        """解析HTML内容，提取文档信息"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找文档列表
        document_elements = soup.select('.results-entry')
        
        page_documents = []
        for doc_element in document_elements:
            try:
                # 获取文档标题和链接
                title_element = doc_element.select_one('.results-topic a')
                if title_element:
                    title = title_element.text.strip()
                    url = title_element.get('href', '')
                    if url and not url.startswith('http'):
                        url = f"https://www.autosar.org/{url}"
                    
                    # 获取额外信息（如版本、平台等）
                    extra_info = []
                    info_elements = doc_element.select('.extra-info span')
                    for info in info_elements:
                        info_text = info.text.strip()
                        if info_text:
                            extra_info.append(info_text)
                    
                    extra_info_str = " | ".join(extra_info) if extra_info else ""
                    
                    document_info = f"{title} | {url} | {extra_info_str}"
                    page_documents.append(document_info)
            except Exception as e:
                print(f"解析文档时出错: {e}")
                continue
        
        return page_documents

    def get_total_pages(self, html_content):
        """从HTML内容中获取总页数"""
        if not html_content:
            return 0
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找分页信息
        pagination = soup.select('.pagination li a')
        if pagination:
            try:
                # 获取最后一个页码
                page_numbers = []
                for page_link in pagination:
                    page_text = page_link.text.strip()
                    if page_text.isdigit():
                        page_numbers.append(int(page_text))
                
                if page_numbers:
                    return max(page_numbers)
            except (ValueError, IndexError) as e:
                print(f"解析分页信息时出错: {e}")
        
        # 如果找不到分页信息，尝试从结果数量估算
        results_counter = soup.select_one('.results_counter')
        if results_counter:
            try:
                counter_text = results_counter.text.strip()
                # 提取数字
                match = re.search(r'(\d+)', counter_text)
                if match:
                    total_results = int(match.group(1))
                    # 假设每页20个结果
                    return (total_results + 19) // 20
            except (ValueError, AttributeError) as e:
                print(f"解析结果计数器时出错: {e}")
        
        return self.max_pages  # 如果无法确定页数，返回最大页数

    def get_total_documents(self, html_content):
        """从HTML内容中获取文档总数"""
        if not html_content:
            return 0
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results_counter = soup.select_one('.results_counter')
        
        if results_counter:
            try:
                counter_text = results_counter.text.strip()
                # 提取数字
                match = re.search(r'(\d+)', counter_text)
                if match:
                    return int(match.group(1))
            except (ValueError, AttributeError) as e:
                print(f"解析结果计数器时出错: {e}")
        
        return self.target_count  # 如果无法确定文档总数，返回目标数量

    def collect_documents(self):
        """收集所有文档"""
        print(f"开始收集AUTOSAR文档，目标数量: {self.target_count}")
        
        page_number = 1
        first_page_html = self.get_page(page_number)
        
        # 获取文档总数
        total_documents = self.get_total_documents(first_page_html)
        if total_documents > 0:
            self.target_count = total_documents
            print(f"从网页检测到文档总数: {self.target_count}")
        
        # 获取总页数
        total_pages = self.get_total_pages(first_page_html)
        print(f"检测到总页数: {total_pages}")
        
        # 处理第一页
        first_page_docs = self.parse_documents(first_page_html)
        for doc in first_page_docs:
            self.documents.add(doc)
        
        print(f"第 {page_number} 页: 找到 {len(first_page_docs)} 个文档，当前总数: {len(self.documents)}")
        
        # 处理剩余页面
        page_number += 1
        consecutive_empty_pages = 0
        max_consecutive_empty_pages = 3
        
        while (page_number <= total_pages or page_number <= self.max_pages) and len(self.documents) < self.target_count:
            # 如果连续多个页面没有找到文档，可能是已经到达末尾
            if consecutive_empty_pages >= max_consecutive_empty_pages:
                print(f"连续 {consecutive_empty_pages} 个页面没有找到文档，停止搜索")
                break
            
            # 添加随机延迟，避免被网站封锁
            delay = random.uniform(2.0, 5.0)
            print(f"等待 {delay:.2f} 秒...")
            time.sleep(delay)
            
            html_content = self.get_page(page_number)
            page_docs = self.parse_documents(html_content)
            
            if not page_docs:
                consecutive_empty_pages += 1
                print(f"第 {page_number} 页: 未找到文档，连续空页数: {consecutive_empty_pages}")
            else:
                consecutive_empty_pages = 0
                for doc in page_docs:
                    self.documents.add(doc)
                print(f"第 {page_number} 页: 找到 {len(page_docs)} 个文档，当前总数: {len(self.documents)}")
            
            page_number += 1
        
        # 如果还没有收集到足够的文档，可能需要调整搜索参数或重试
        if len(self.documents) < self.target_count:
            print(f"警告: 只找到 {len(self.documents)} 个文档，少于目标数量 {self.target_count}")
            
            # 尝试使用不同的搜索参数
            if len(self.documents) < self.target_count / 2:
                print("尝试使用不同的搜索参数...")
                self.try_alternative_search()
        else:
            print(f"成功收集到 {len(self.documents)} 个文档")
        
        # 保存结果
        self.save_documents()
        
        # 保存文档信息到JSON文件，便于后续处理
        self.save_documents_json()

    def try_alternative_search(self):
        """尝试使用不同的搜索参数"""
        # 保存原始参数
        original_params = self.params.copy()
        
        try:
            # 尝试不同的搜索参数组合
            alternative_params = [
                {"tx_solr[filter][0]": "category:R24-11", "tx_solr[q]": ""},
                {"tx_solr[filter][0]": "platform:CP", "tx_solr[q]": ""},
                {"tx_solr[q]": "AUTOSAR CP R24-11"}
            ]
            
            for params in alternative_params:
                print(f"尝试使用参数: {params}")
                self.params = params
                
                page_html = self.get_page(1)
                page_docs = self.parse_documents(page_html)
                
                if page_docs:
                    for doc in page_docs:
                        self.documents.add(doc)
                    print(f"使用新参数找到 {len(page_docs)} 个文档，当前总数: {len(self.documents)}")
                    
                    # 如果找到了足够的文档，就不再尝试其他参数
                    if len(self.documents) >= self.target_count:
                        break
                
                # 添加随机延迟
                time.sleep(random.uniform(2.0, 5.0))
        
        finally:
            # 恢复原始参数
            self.params = original_params

    def save_documents(self):
        """将收集到的文档保存到文件"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(f"AUTOSAR CP文档列表 (共 {len(self.documents)} 个)\n")
            f.write("=" * 80 + "\n\n")
            
            for i, doc in enumerate(self.documents, 1):
                f.write(f"{i}. {doc}\n\n")
        
        print(f"文档列表已保存到 {self.output_file}")

    def save_documents_json(self):
        """将文档信息保存为JSON格式"""
        docs_list = list(self.documents)
        docs_parsed = []
        
        for doc in docs_list:
            parts = doc.split(" | ", 2)
            if len(parts) >= 2:
                title = parts[0]
                url = parts[1]
                info = parts[2] if len(parts) > 2 else ""
                
                docs_parsed.append({
                    "title": title,
                    "url": url,
                    "info": info
                })
        
        with open(self.json_output_file, 'w', encoding='utf-8') as f:
            json.dump(docs_parsed, f, ensure_ascii=False, indent=2)
        
        print(f"文档信息已保存为JSON格式到 {self.json_output_file}")


if __name__ == "__main__":
    collector = AutosarCPDocumentCollector()
    collector.collect_documents() 