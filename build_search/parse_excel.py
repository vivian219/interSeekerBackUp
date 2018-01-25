import mongo_manager
import buildIndex
import hashlib

class ParseExcel:

    reports = []

    def read(self, path):
        import xlrd
        file = xlrd.open_workbook(path,encoding_override='utf-8')  # 打开 excel 文件
        sheet = file.sheets()[0]  # 获取第一个sheet
        self.process(sheet)
        self.exportReportToMongo()
        return self.reports

    def process(self, sheet):
        nrows = sheet.nrows  # 获取行数
        row = []

        for i in range(1, nrows):  # 跳过标题行
            row = sheet.row_values(i)
            self.makeup(row)

    def makeup(self, row):
        report = {}
        report["report"] = [
            row[0],     # title
            row[4],     # date
            row[5]     # 来源
        ]
        report["label"] = row[2]   # labels
        report["abstract"] = row[1]     # abstract
        report["url"] = row[3].split('\n')     # split urls
        report["hash"] = row[7].split('\n')     # split spiteful hash
        report["ip"] = row[8].split('\n')  # split spiteful ip
        report["domain"] = row[9].split('\n')  # split spiteful domain
        report["urls"] = row[11].split('\n')  # split spiteful url
        # maybe others to add...

        self.reports.append( report )

    def postIndicator(self,data):
        index="indicator"
        post = mongo_manager.stixIndicator(ID=data["md5"], IOC_MD5=data["hash"],
                                           IOC_Domain=data["domain"], IOC_IPV4=data["ip"],
                                           Related_Reports=data["report_md5"], IOC_URL=data["url"])
        post.save()
        if buildIndex.document_exist(index, "md5", data['md5']) == False:
            rep_data = mongo_manager.stixIndicator.objects(ID=data["md5"])[0].to_mongo()
            rep_data = dict(rep_data)
            id = rep_data['_id']
            rep_data.pop('_id', None)
            rep_data['md5'] = id
            res = buildIndex.post_document(index, rep_data)
    def postReport(self,report):
        index="report"
        post = mongo_manager.stixReport(ID=report["md5"], Title=report["title"], Abstract=report["abstract"], Tag=report["tag"],
                                        URL=report["url"], Date=report["time"],vendors=report['vendor'])
        post.save()
        # es.index(index=index, doc_type="test-type", body={"any": "data", "timestamp": datetime.now()})
        if buildIndex.document_exist(index, "md5", report['md5']) == False:
            # print("False")
            rep_data = mongo_manager.stixReport.objects(ID=report["md5"])[0].to_mongo()
            # print("txt_ext_db",rep_data)
            rep_data = dict(rep_data)
            id = rep_data['_id']
            rep_data.pop('_id', None)
            rep_data['md5'] = id
            res = buildIndex.post_document(index, rep_data)
    def exportReportToMongo(self):
        for data in self.reports:
            report = data["report"]
            labels = data["label"]
            abstract = data["abstract"]
            url=str(data['url'])
            hash_list=str(data['hash'])
            ip=str(data['ip'])
            domain=str(data['domain'])
            urls=str(data['urls'])
            report=self.makeReport(report,labels,abstract,url)
            indicator=self.makeIndicator(ip,hash_list,domain,url,urls,report['md5'])
            print(report)
            print(indicator)
            self.postReport(report)
            self.postIndicator(indicator)

    def makeReport(self,_report,labels,abstract,url):
        report={}
        report['md5']=hashlib.md5(abstract.encode('utf-8')).hexdigest()
        report['tag']=labels
        report['title']=_report[0]
        report['time']=_report[1]
        report['vendor']=_report[2]
        report['abstract']=abstract
        report['url']=url
        return report
    def makeIndicator(self,ip,hash,domain,url,urls,report_md5):
        indicator={}
        indicator['ip']=ip
        indicator['domain']=domain
        indicator['hash']=hash
        indicator['url']=url
        indicator['report_md5']=report_md5
        indicator['md5']=hashlib.md5(url.encode('utf-8')).hexdigest()
        return indicator
if __name__=='__main__':
    import json
    reports= ParseExcel().read("CERT预警情报_20171225_20171229.xlsx")

    # print(json.dumps(
    #     ParseExcel().read("CERT预警情报_20171225_20171229.xlsx")
    # ))
