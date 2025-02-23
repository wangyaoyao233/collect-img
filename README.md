# collect img from website

从某网站中获取图片

## 环境命令 memo

```bash
#创建虚拟环境
python -m venv venv

#启动虚拟环境
venv\Scripts\activate

#退出虚拟环境
deactivate

#查看包安装路径
python -m site

#安装包方法1：pip直接安装
pip install <package>
#安装包方法2：使用requirements.txt
pip install -r requirements.txt

#查看安装的包
pip list
```

```bash
#安装需要的包
pip install selenium beautifulsoup4 aiohttp requests
```

## 流程

1. python collect_href.py
2. python collect_img.py
3. python download_img.py
4. python upload_to_tg.py
