from mongoengine import *
import redis_manager
import json
import mongo_manager
import buildIndex

connect('monoengine_test', host='localhost', port=27017)
index="indicator"

obj_sub = redis_manager.ParserRedis()
redis_sub = obj_sub.subscribe()
def listen():
    while True:

        msg = json.loads(redis_sub.parse_response()[2])

        #print(msg)#print(redis_sub.parse_response())
        post = mongo_manager.stixIndicator(ID=msg["md5"],IOC_MD5=msg["hash_list"],
                             IOC_Domain=msg["dom_list"],IOC_IPV4=msg["ip_list"],
                             Related_Reports=msg["report_md5"],IOC_URL=msg["url"])
        post.save()
        if buildIndex.document_exist(index,"md5",msg['md5']) == False:

            rep_data = mongo_manager.stixIndicator.objects(ID=msg["md5"])[0].to_mongo()
            rep_data = dict(rep_data)
            id = rep_data['_id']
            rep_data.pop('_id', None)
            rep_data['md5'] = id
            res=buildIndex.post_document(index, rep_data)

def getAllData():
    alldata=mongo_manager.stixIndicator.objects.all()
    #for data in alldata:
        #print(data.to_mongo())
        #print("ID",data.ID,"ip list",data.IOC_IPV4,"related report",data.Related_Reports)
def deleteData():
    alldata = mongo_manager.stixIndicator.objects.all()
    for data in alldata:
        mongo_manager.stixIndicator.delete(data)
        #print("ID", data.ID, "ip list", data.IOC_IPV4, "related report", data.Related_Reports)
listen()
#getAllData()
#deleteData()