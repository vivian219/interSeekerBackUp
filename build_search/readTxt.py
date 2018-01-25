import re
class txtStruct:

    def __init__(self,_time, _title,_abstract,_tag,_urlList):
        self.time=_time
        self.title=_title
        self.abstract=_abstract
        self.tag=_tag
        self.urlList=_urlList
def getStructData(filename):
    print("get the data")
    dataPat='(\d{8})-((\d)+)'
    f=open(filename)
    line = f.readline()  # 调用文件的 readline()方法
    txtStruList=[]
    while line:
        mat=re.match(dataPat,line)
        if not mat:
            line = f.readline()
            continue
        time=mat.group()
        line = f.readline()
        title,abs=getTitleAbs(line)
        line=f.readline()
        #print("line"+line)
        tag=line.split('TAG: ')[1].split('\n')[0]
        #print('TAG'+tag)
        line=f.readline()
        urlList=[]
        while line !='END\n':
            urlList.append(line.split('URL:')[1].split('\n')[0])
            line=f.readline()
        txt=txtStruct(time,title,abs,tag,urlList)
        print('title'+txt.title)
        print('abstract'+txt.abstract)
        print('tag'+txt.tag)
        print('urlList'+txt.urlList[0])
        txtStruList.append(txt)
        # print(line, end = '')　　　# 在 Python 3中使用
        line = f.readline()
    return txtStruList
def getTitleAbs(line):
    lineArr=line.split('】')
    title=lineArr[0].split('【')[1]
    abs=lineArr[1].split('\n')[0]
    #print(title)
    # line=line.encode('utf-8')
    # titlePat='【\w*】'
    # title=re.match(titlePat,line)
    # abs=line.split(title.group())[0]
    # print(abs)
    # wordPat='\w+'
    # title=title.group().split('【')[0].split('】')[0]
    return title,abs
#getStructData('APT_test.txt')