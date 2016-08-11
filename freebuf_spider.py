#/usr/bin/env python
#!encoding=UTF-8
'''
   采集freebuf知识库文章的脚本。
   修改时间：2016-08-09
   修改作者:
'''
import urllib2
import requests
import re
import sys
import hashlib
import math
import threading
import time
import os
reload(sys)
sys.setdefaultencoding("utf-8" )

#默认保存文件夹
FileName = "paper"
#默认使用30个线程
ThreadNum  = 30
#采集网站地址
SiteUrl = "http://www.freebuf.com/"+FileName+"/page"
#线程队列
threads = []
#总页数
TotalPage = 0
#所有列表页面URL
PageListUrls = []
#所有文章URL
PageUrls = []
#文章内容
Articles = []

#获取总页数
def two(left,right,url):
    mid=(left+right)/2
    print mid,left
    if mid==left:
        return left
    patt=re.compile(r"<h1>.*?</h1>")
    url_real=url+("/%d" % mid)
    content=requests.get(url_real)
    if (patt.findall(content.text)):
        right=mid
    else:
        left=mid
    return two(left,right,url)

def get_total_page_number(url):
    totle_number=two(1,1000,url)
    return totle_number

#所有列表页面URL
def get_page_list_url(TotalPage):
    global FileName
    PageListUrls = []
    for i in range(TotalPage):
        PageListUrls.append("http://www.freebuf.com/%s/page/%d" %(FileName,i))
    return PageListUrls

#采集文章链接
def get_article_url(PageListUrls):
    PageUrls = []
    for url in PageListUrls:
        patt = re.compile(r"<div class=\"news-img\"><a target=\"_blank\" href=\"(.*?)\">")
        content = requests.get(url)
        article = patt.findall(content.text)
        for aurl in article:
            PageUrls.append(aurl)
    return PageUrls




#将采集数据缓存本地 \/:*?"><|
def cache_Articles(url,create_time,title, author, content):
    global FileName
    filename= title+create_time+".html"

#这里替换文章名中一些不能写做文件名的特殊符号
    filename = filename.replace("\\",".")
    filename = filename.replace("&nbsp;"," ")
    filename = filename.replace("/",".")
    filename = filename.replace(":",".")
    filename = filename.replace("*",".")
    filename = filename.replace("?",".")
    filename = filename.replace("\"",".")
    filename = filename.replace("<",".")
    filename = filename.replace(">",".")
    filename = filename.replace("|",".")
    filename = filename.replace("'","\\'")
#保存在当前目录的freebuf文件夹下面
    filename = FileName+"/"+filename
    print "Successed Downloading >> "+filename
    try:
        fw = open(filename,"w+")
    except Exception,e:
    	#用文章的名字创建文件失败时，使用当前时间创建html文件
        Fname =FileName+"/"+str(int(time.time()))+create_time+".html"
        fw = open(Fname,'w+')
    try:
        text = '''
        <html>
			<head>
			     <title>${title}$ - ${author}$</title>
				 <meta http-equiv="content-type" content="text/html; charset=UTF-8">
			</head>
			<body>
				<h1>原文地址:<a href="${url}$">${url}$</a></h1>
				${content}$
			</body>
		</html>
        '''
        s = text.replace('${url}$',str(url)).replace('${title}$',str(title)).replace('${author}$',str(author)).replace('${content}$',str(content))
        fw.write(s)
    except Exception,e:
        #print e
        print "here"
    finally:
        fw.close()

#采集文章内容并且缓存本地
def get_article_content(PageUrls):
    for url in PageUrls:
        #抓取页面
        req = requests.get(url)
        content = req.text
        #获取标题
        patt_title = re.compile(r"<h2>(.*?)</h2>")
        title = patt_title.findall(content)
        #获取作者
        path_author = re.compile(r"rel=\"author\">(.*?)</a>")
        author = path_author.findall(content)
        #获取文章内容
        path_section = re.compile(r"<head>([\w\W]*?)<div class=\"article-oper\">")
        section = path_section.findall(content)

        #time
        patt_time=re.compile(r"<span class=\"time\">(.*?)</span>")
        time=patt_time.findall(content)
        #将采集数据缓存本地
        cache_Articles(url,time[0],title[0],author[0],section[0])


def main():
    global ThreadNum
    global SiteUrl
    global threads
    global TotalPage
    global PageListUrls
    global PageUrls
    global Articles
    global FileName
    try:
        os.makedirs(FileName)
    except:
        print u"文件夹已存在！"
        #FileName = str(int(time.time()))
        #print u"创建目录"
        #os.makedirs(FileName)



    #获取总页数
    TotalPage = get_total_page_number( SiteUrl )

    #构建列表页面URL
    print "构建列表页面URL..."
    PageListUrls = get_page_list_url(TotalPage)

    #采集文章链接
    print "采集文章链接..."
    if os.path.exists(FileName+"/cache"):
        fr=open(FileName+"/cache","r")
        PageUrls=fr.read().split(",")
        del PageUrls[-1]
        fr.close()
    else:
        fw = open(FileName+"/cache","w+")
        PageUrls = get_article_url(PageListUrls)
        for i in range(len(PageUrls)):
            fw.write(str(PageUrls[i])+",")
        fw.close()

    #获取每个线程执行条数
    ThreadExceNum = math.ceil( len(PageUrls) / ThreadNum  )
    print  "线程执行条数%d" % ThreadExceNum
    #分组
    PageUrlGroup = []
    #创建目录



    j = 0

    for i in range(0,len(PageUrls)):

        if j % ThreadExceNum == 0:
            #加入线程
            t1 = threading.Thread(target=get_article_content,args=(PageUrlGroup,))
            threads.append(t1)
            PageUrlGroup = []
        else:
            PageUrlGroup.append(PageUrls[i])
        j = j + 1

    for t in threads:
        try:
            t.setDaemon(True)
            t.start()
        except Exception,ex:
            print "something error!"

    t.join()
    print "All Done!!!"
if __name__ == '__main__':
    main()
