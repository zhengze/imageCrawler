# imagecrawler
crawl images from http://www.meizitu.com

这个爬虫是多线程+多进程的示例，一个进程为一个爬虫，一个爬虫包含两个线程：收集图片url，保存到data目录；根据url下载图片，保存到download目录下

启动爬虫：
`$python crawler.py`
