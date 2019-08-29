# 网络字体(石头字体/web font) 识别器 识别率 99%

## 实现:

先抓取到字体文件
再将字体文件绘制成字体
然后用ocr识别绘制的图片      
最后生成映射关系      
之所以这样 而不是直接使用[字体文件查看工具](http://fontstore.baidu.com)      
直接查找并写出映射 是因为 大部分网站每次请求加载的字体文件是不断变化的      
导致之前生成的映射关系不能使用 同时也不确定究竟要手工映射多少字体文件      
如 例子所示，没多大功夫抓取到的字体文件就达到几十个      
该脚本优先使用已经生成的映射文件 自动维护一个映射文件池      
如此可以大大降低使用 ocr 的频率 因为ocr 识别结果仍具有不可控性      
ocr 识别采用多次 shuffer 识别结果对比 一致则认为识别成功      
当返回为 空字典时 认为解析失败      
可根据需求调整 limit_count, check_count      
当前参数基本可以保证映射结果的正确性      
识别的结果还和绘制字体参数，以及merge 图片字符排列顺序有关      
所以作 shuffer 并 check 以掌控识别精度      

## 使用:

使用时只需要将 font_parser.py 文件放置在项目根目录下      
首先使用 font_store 方法将字体文件内容 放入 该项目默认目录      
接下来使用 parse() 默认参数 解析上一步生成的 font 文件      
以测试环境是否可用      
若不可用 根据错误安装相关函数库      

## 环境:

该脚本依赖 tesseract 环境，请配置相关环境并下载中文模型      


## 使用:

参考 58job_resume_crawler.py      


## 中间文件:

该脚本会自动生成 web_font 文件夹      
用于放置中间生成文件      

web_font/font_merge.jpg      字体图片合并后的文件名      
web_font/result.txt  识别到的文字存放位置      
web_font/stonefont.woff  当前抓取到的字体文件名 由 font_store 方法生成      
web_font//image/* 解析字体文件绘制的字体图像      
web_font/json/* 根据parse 传入的 唯一序列生成的 md5 格式映射文件      

# 如有疑问 QQ:691420417 联系      
