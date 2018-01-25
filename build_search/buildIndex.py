# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 20:25:56 2017

@author: Vivian
"""
import requests
from elasticsearch import Elasticsearch
import json

type_name = "fulltext"

es=Elasticsearch()
def buildIndex():
    # 使用PUT请求创建一个索引
    print("build index")
    #es.indices.create(index="report")
    index_name="actor"
    res = requests.put("http://localhost:9200/{0}".format(index_name))
    print(res.content.decode('utf8'))
    # 设置分词
    data = {
        type_name: {
            "_all": {
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
                "term_vector": "no",
                "store": "false"
            },
            "properties": {
                "Abstract": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_max_word",
                    "include_in_all": "true",
                    "boost": 8
                },
                "Title": {
                    "type": "text",
                    "analyzer": "ik_max_word",
                    "search_analyzer": "ik_max_word",
                    "include_in_all": "true",
                    "boost": 8
                }
            }
        }
    }
    res = requests.post("http://localhost:9200/{0}/{1}/_mapping".format(index_name,"fulltext"), json=data)
    print(res.content.decode('utf8'))


def document_exist(index_name,colName,colValue):
    http_template='http://localhost:9200/{0}/{1}/_search?q={2}:{3}'.format(index_name,type_name,colName,colValue)
    res = json.loads(requests.get(http_template).content.decode('utf8'))
    if "hits" in res.keys():
        if res["hits"]["total"] == 0:
            return False
        else:
            return True
    return False


def post_document(index_name,docDict):
    """
    docDict:ip,domain,hashValue,url
    """
    data=docDict
    #print("Doc posted:{0}".format(data))
    # 使用PUT请求将所有文档存入该索引
    res = requests.post("http://localhost:9200/{0}/fulltext".format(index_name),
                  json=data)
    print(res.content.decode('utf8'))
    return res
"""
初始化搜索引擎里的索引,仅需要运行一次即可
"""
def initial():       
    buildIndex()

def queryIndicator(queryStr):
    res=es.search(index="report", body={"query": {"match": {"_all":queryStr}}})
def queryActor(queryStr):
    res=es.search(index="report", body={"query": {"match": {"_all": queryStr}}})
def queryReport(queryStr):
    res=es.search(index="report", body={"query": {"match": {"_all": queryStr}}})
def queryIndex(index,con,queryStr):
    res = es.search(index=index, body={"query": {"match": {con:queryStr}}})
    resList=[]
    for hit in res['hits']['hits']:
        resList.append(hit["_source"])
    return resList
def queryReport(sourceItem,index,queryStr,res):
    for item in sourceItem:
        item_res=queryIndex("report",index,queryStr)
        for _res in item_res:
            res.append(_res)
    return res
def indexDict(dict,index):
    try:
        res=dict[index]
    except:
        res=""
        #print(dict)
    return res
def prep_sea_res(queryStr):
    res={}
    #res['draw']=2
    res['recordTotal']=1
    res['recordsFiltered']=1
    resList=queryAll(queryStr)
    data=[]
    for item in resList:
        item_list=[]
        item_list.append(indexDict(item,'md5'))
        item_list.append(indexDict(item,'Title'))
        item_list.append(indexDict(item,'Date'))
        item_list.append(indexDict(item,'vendors'))
        item_list.append(indexDict(item,'Status'))
        item_list.append(indexDict(item,'TLP'))
        data.append(item_list)
    res['data']=data
    return res
def searchActor(queryStr):
    res={}
    res['recordTotal']=1
    res['recordsFiltered'] = 1
    _res = es.search(index="actor", body={"query": {"match": {"_all": queryStr}}})
    resList = []
    for hit in _res['hits']['hits']:
        itemList=[]
        hitRes=hit["_source"]
        itemList.append(hitRes['Name'])
        itemList.append(hitRes['First_Sighting'])
        itemList.append(hitRes['Criticality'])
        itemList.append(hitRes['Classification_Family'])
        itemList.append(hitRes['TLP'])
        resList.append(itemList)
        #print(hit['_source'])
    res['data']=resList
    return res
def queryAll(queryStr):
    res=queryIndex("report","_all",queryStr)
    #print(res)
    ind=queryIndex("indicator","_all",queryStr)
    #print(ind)
    res=queryReport(ind,"'report_md5",queryStr,res)
    #print(res)
    # act=queryIndex("actor","_all",queryStr)
    # res=queryReport(act,"")
    return res
def updateReportData(md5,data):
    json_data=data
    #print(json_data)
    res=es.search(index="report", body = {'query':{'match':{'md5':md5}}})
    hit=res['hits']['hits']
    if hit==[]:
        return
    id=hit[0]['_id']
    type=hit[0]['_type']

    es.delete(index="report", doc_type =type, id =id)
    json_data.pop('_id', None)
    json_data['md5'] = md5
    post_document("report",json_data)
    print(json_data)
def deleteSpecData(index_name,colName,colData):
    res = es.search(index=index_name, body={'query': {'match': {colName: colData}}})
    hit = res['hits']['hits']
    if hit == []:
        return
    id = hit[0]['_id']
    type = hit[0]['_type']
    es.delete(index=index_name, doc_type=type, id=id)
def updateActorData(data):
    name=data['_id']
    print(name)
    res = es.search(index="actor", body={'query': {'match': {'Name': name}}})
    hit = res['hits']['hits']
    if hit==[]:
        print("es update actor data failed")
        return
    for _hit in hit:
        id=_hit['_id']
        type=_hit['_type']
        es.delete(index="actor", doc_type =type, id =id)
    data.pop('_id', None)
    data['Name'] = name
    post_document("actor",data)
def queryAllInfo(index):
    res = es.search(index=index, body={"query": {"match_all": {}}})
    for hit in res['hits']['hits']:
        print(hit['_source'])
def queryActorNameList(queryStr):
    res = es.search(index="actor", body={"query": {"match": {"_all": queryStr}}})
    resList = []
    resDict={}
    for hit in res['hits']['hits']:
        _res=hit["_source"]
        itemDict={}
        itemDict['name']=_res['Name']
        itemDict['first_sighting'] = _res['First_Sighting']
        resList.append(itemDict)
        #print(hit['_source'])
    resDict['items'] = resList
    print(resDict)
    return resDict
def deleteAllData():
    index_list=['actor']
    for index in index_list:
        res = es.search(index=index, body={"query": {"match_all": {}}})
        for hit in res['hits']['hits']:
            id = hit['_id']
            type = hit['_type']
            es.delete(index=index, doc_type=type, id=id)

if __name__ == "__main__":
    #initial()
    #deleteAllData()
    #deleteSpecData("actor",'Name','Wekby')
    queryActorNameList("Wekby")
    #queryAllInfo("actor")
    #res=queryAll("20170710-4")
    #print(res)
    print(searchActor("APT"))