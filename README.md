# AUTOSAR文档收集与下载工具

这个项目包含多个脚本，用于从AUTOSAR官方网站收集和下载不同平台（AP和CP）的文档。


![image](https://github.com/user-attachments/assets/bfa4bc26-0388-482b-85b8-a304b0b82f23)

## 功能

1. **文档收集**：从AUTOSAR网站搜索并收集文档信息，包括标题、URL和其他元数据。
2. **文档下载**：下载收集到的所有文档，并保存到本地。
3. **多平台支持**：支持AUTOSAR AP（Adaptive Platform）和CP（Classic Platform）两个平台的文档。

## 脚本说明

### 1. AP平台文档收集与下载

#### autosar_ap_document_collector.py

这个脚本用于从AUTOSAR网站收集AP平台的文档信息。

**主要功能**：
- 爬取AUTOSAR网站上的AP平台文档列表
- 处理分页，确保收集所有文档
- 提取文档标题、URL和其他元数据
- 将收集到的信息保存为TXT和JSON格式到output文件夹

**使用方法**：
```bash
python autosar_ap_document_collector.py
```

**输出文件**：
- `output/autosar_ap_documents.txt` - 包含所有AP文档信息的文本文件
- `output/autosar_ap_documents.json` - 包含所有AP文档信息的JSON文件，用于下载脚本

#### autosar_ap_document_downloader.py

这个脚本用于下载收集到的AP平台文档。

**主要功能**：
- 从output文件夹的JSON文件加载文档信息
- 下载所有文档并保存到download_ap目录
- 显示下载进度
- 处理错误和重试
- 记录下载结果

**使用方法**：
```bash
python autosar_ap_document_downloader.py
```

**输出**：
- `download_ap/` - 下载的AP文档保存在这个目录中
- `download_ap/download_ap_log.txt` - 下载日志，记录每个文档的下载结果

### 2. CP平台文档收集与下载

#### autosar_cp_document_collector.py

这个脚本用于从AUTOSAR网站收集CP平台的文档信息。

**主要功能**：
- 爬取AUTOSAR网站上的CP平台文档列表
- 处理分页，确保收集所有文档
- 提取文档标题、URL和其他元数据
- 将收集到的信息保存为TXT和JSON格式到output文件夹

**使用方法**：
```bash
python autosar_cp_document_collector.py
```

**输出文件**：
- `output/autosar_cp_documents.txt` - 包含所有CP文档信息的文本文件
- `output/autosar_cp_documents.json` - 包含所有CP文档信息的JSON文件，用于下载脚本

#### autosar_cp_document_downloader.py

这个脚本用于下载收集到的CP平台文档。

**主要功能**：
- 从output文件夹的JSON文件加载文档信息
- 下载所有文档并保存到download_cp目录
- 显示下载进度
- 处理错误和重试
- 记录下载结果

**使用方法**：
```bash
python autosar_cp_document_downloader.py
```

**输出**：
- `download_cp/` - 下载的CP文档保存在这个目录中
- `download_cp/download_cp_log.txt` - 下载日志，记录每个文档的下载结果

## 依赖项

运行这些脚本需要以下Python库：
- requests
- beautifulsoup4

可以使用以下命令安装依赖：
```bash
pip install -r requirements.txt
```

## 注意事项

1. 请合理使用这些脚本，避免对AUTOSAR网站造成过大负担。
2. 脚本中已添加随机延迟，以减轻对服务器的压力。
3. 下载的文档仅供个人学习和研究使用，请遵守AUTOSAR的版权和使用条款。
4. 如果网站结构发生变化，脚本可能需要更新。

## 完整流程

### AP平台文档

1. 运行AP收集脚本收集文档信息：
   ```bash
   python autosar_ap_document_collector.py
   ```

2. 运行AP下载脚本下载文档：
   ```bash
   python autosar_ap_document_downloader.py
   ```

### CP平台文档

1. 运行CP收集脚本收集文档信息：
   ```bash
   python autosar_cp_document_collector.py
   ```

2. 运行CP下载脚本下载文档：
   ```bash
   python autosar_cp_document_downloader.py
   ```

3. 查看各自下载目录中的结果和日志。

