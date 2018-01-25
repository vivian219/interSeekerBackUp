import redis_manager
import re
import json

obj_sub=redis_manager.SpiderRedis()
redis_sub=obj_sub.subscribe()

topHostPostfix = [    '.com','.la','.io','.co','.info','.net','.org','.me','.mobi',
    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn',
    '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
    '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
    '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co',
    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
    '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
    '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
    '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
    '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk"]
parser_pub=redis_manager.ParserRedis()

def whiteJudge(whiteList,url):
    if url in whiteList:
        return "whiteURL : "+url
    else:
        return url
def genWhiteList():
    f=open(r'top-1m.csv')
    whiteList=[]
    for line in f.readlines():
        whiteList.append(line.split(",")[1])
    return whiteList
class extract_data:
    def __init__(self,_ip_list,_dom_list,_hash_list,_md5,_report_md5):
        self.md5=_md5
        self.ip_list=_ip_list
        self.dom_list=_dom_list
        self.hash_list=_hash_list
        self.report_md5=_report_md5
while True:
    print("extract bot get a data")
    spider_data=json.loads(redis_sub.parse_response()[2])
    conTex=spider_data["conTex"]
    md5=spider_data["md5"]
    report_md5=spider_data["report_md5"]
    print(spider_data["md5"])
    pat_ip = re.compile('\d{1,3}(\.\d{1,3}){3}')
    pat_dom = re.compile('([a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?)')
    #pat_hash = re.compile('[a-z|0-9|A-Z]{32,64}')
    pat_hash = re.compile('[a-f0-9]{32}|[A-F0-9]{32}')

    res_ip_list = list(pat_ip.finditer(conTex))
    res_dom_list = list(pat_dom.finditer(conTex))
    res_hash_list = pat_hash.findall(conTex)

    ip_set=set()
    dom_set=set()
    hash_set=set()
    whiteList = genWhiteList()
    for i in res_ip_list:
        if len(i.group(0)) < 15 :
            ip_set.add(i.group(0))
    for i in res_dom_list:
        wordlist = i.group(0).split('.')
        l = len(wordlist)
        if '.' + wordlist[l - 1] in topHostPostfix:
            judURL = whiteJudge(whiteList, str(i.group(0)))

            dom_set.add(judURL)
    for hash_value in res_hash_list:
        if len(hash_value) == 32 or len(hash_value) == 40 or len(hash_value) == 64:
            hash_set.add(hash_value)
    print(ip_set)
    print(dom_set)
    print(hash_set)
    _parser_res=extract_data(list(ip_set),list(dom_set),list(hash_set),md5,report_md5)
    parser_pub.public(json.dumps({"ip_list":str(_parser_res.ip_list),"dom_list":str(_parser_res.dom_list),"hash_list":str(_parser_res.hash_list),
                                  "report_md5":_parser_res.report_md5,"md5":_parser_res.md5,"url":spider_data["url"]}))
