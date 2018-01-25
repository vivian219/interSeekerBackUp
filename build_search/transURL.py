# -*- coding: utf-8 -*-
'''
获得目前已经爬取的URL列表
通过白名单对URL进行筛选，得到新的URL
利用爬虫爬取页面内容并匹配IP,Domain等信息
导入buildIndex
利用buildIndex中的相关函数将新匹配到的信息录入ES
'''
import re
from enum import Enum

from bs4 import BeautifulSoup
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser, PDFDocument
import readTxt
import redis_manager
import hashlib
import json
class ExtractMode(Enum):
    PDFMode = 1
    HTMLMode = 2

"""
从url爬取内容并返回，当无法爬取或超时，返回为空
"""

def spider(url):
    import requests
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive'}
    try:
        r=requests.get(url,headers=headers).content.decode('utf-8','ignore')
    except Exception:
        r=""
    return r.strip()


"""
从给定的路径读取白名单,返回白名单
"""
def genWhiteList():
    f=open(r'top-1m.csv')
    whiteList=[]
    for line in f.readlines():
        whiteList.append(line.split(",")[1])
    return whiteList


"""
白名单判断函数,判断 url 是否在白名单列表内
"""
def whiteJudge(whiteList,url):
    if url in whiteList:
        return "whiteURL : "+url
    else:
        return url

def parse_html(url):
    """
    从 url 对应的网页中抽取内容
    :param url: 要爬取的网页链接
    :return: 抽取到的文本内容
    """
    content = spider(url)
    if content == "":
        return content
    soup = BeautifulSoup(content)
    conTex = soup.get_text()
    return conTex


def parse_pdf(url):
    """
    从pdf中抽取内容
    :param filename: 要抽取的 pdf路径
    :return: 抽取到的pdf的内容
    """
    get_pdf(url)
    fp = open('1.pdf', 'rb') # 以二进制读模式打开
    #用文件对象来创建一个pdf文档分析器
    praser = PDFParser(fp)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 连接分析器 与文档对象
    praser.set_document(doc)
    doc.set_parser(praser)

    content = ""

    # 提供初始化密码
    # 如果没有密码 就创建一个空的字符串
    doc.initialize()

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        content = ""
    else:
        # 创建PDf 资源管理器 来管理共享资源
        rsrcmgr = PDFResourceManager()
        # 创建一个PDF设备对象
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        # 创建一个PDF解释器对象
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # 循环遍历列表，每次处理一个page的内容
        for page in doc.get_pages(): # doc.get_pages() 获取page列表
            interpreter.process_page(page)
            # 接受该页面的LTPage对象
            layout = device.get_result()
            # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
            for x in layout:
                if (isinstance(x, LTTextBoxHorizontal)):
                    results = x.get_text()
                    content += results
    content = " ".join(content.replace("\n", "").strip().split())
    return content
def contxtToFile(conTxt,md5):
    f=open("conTxt/"+str(md5),'w',encoding='utf-8')
    f.write(conTxt)
def spider_bot(txt,redis_obj,report_md5):
    urlList=txt.urlList
    for url in urlList:
        m=re.match('.+pdf$',url)
        if m is None:
            conTex=parse_html(url)
            md5ConTex=url
        else:
            conTex=parse_pdf(url)
            md5ConTex=conTex
        if conTex=="":
            continue
        md5 = hashlib.md5(md5ConTex.encode('utf-8')).hexdigest()
        redis_obj.public(json.dumps({"md5":md5,"conTex":conTex,"report_md5":report_md5,"url":url}))
        contxtToFile(conTex,md5)
""" HTML 爬取部分 """
def addNewHTMLDoc(filename,txt_pub,spider_pub):
    """
    从filename中读取 url,并进行爬取
    :param filename: url 存储文件
    """

    txtStruList =readTxt.getStructData(filename)

    for item in txtStruList:
        md5 = hashlib.md5(item.abstract.encode('utf-8')).hexdigest()
        spider_bot(item,spider_pub,md5)

        txt_pub.public(json.dumps({"md5":md5,"title":item.title,"tag":item.tag,"abstract":item.abstract,"time":item.time,"urlList":str(item.urlList)}))
        #res_list = parser(newURL, ExtractMode.HTMLMode)
    # 为文档建立索引
    #[FIX]buildDoc(res_list)


""" PDF 爬取部分 """
# def addNewPDFDoc(filename):
#     """
#     从filename中读取 pdf文件的路径,并遍历进行爬取
#     :param filename: url 存储文件
#     """
#     # 获取PDF文件路径
#     with open(filename, 'r') as fp:
#         fileList = fp.readlines()
#     res_list = parser(fileList, ExtractMode.PDFMode)
#     print(res_list)
#     # 为文档建立索引
#     buildDoc(res_list)
def get_pdf(url):
    # soup=BeautifulSoup(r)
    # print(soup.contents)
    # f=open('test_pdf.txt','w')
    # f.write(r)
    import requests

    # url = 'https://www2.trustwave.com/rs/815-RFM-693/images/2017%20Trustwave%20Global%20Security%20Report-FINAL-6-20-2017.pdf'
    r = requests.get(url)
    with open('1.pdf', 'wb') as f:
        f.write(r.content)

if __name__ == "__main__":
    spider_pub=redis_manager.SpiderRedis()
    txt_pub=redis_manager.TxtRedis()
    #addNewHTMLDoc(r"F:\实验室\安管中心-暑期项目\APT Feeds_v0.txt",spider_pub)
    addNewHTMLDoc("APT_test.txt", txt_pub,spider_pub)
