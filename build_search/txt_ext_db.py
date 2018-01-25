from mongoengine import *
import redis_manager
import json
import mongo_manager
import buildIndex

connect('monoengine_test',host='localhost',port=27017)
index="report"
obj_sub=redis_manager.TxtRedis()
redis_sub=obj_sub.subscribe()
'''
msg format
        self.md5=_md5
        self.content=_content
        self.time = _txt.time
        self.title = _txt.title
        self.abstract = _txt.abstract
        self.tag = _txt.tag
        self.urlList = _txt.urlList
'''
def listen():
    while True:
        msg=json.loads(redis_sub.parse_response()[2])
        #print(msg)

        post=mongo_manager.stixReport(ID=msg["md5"],Title=msg["title"],Abstract=msg["abstract"],Tag=msg["tag"],URL=msg["urlList"],Date=msg["time"])
        post.save()
        #es.index(index=index, doc_type="test-type", body={"any": "data", "timestamp": datetime.now()})
        if buildIndex.document_exist(index,"md5",msg['md5'])==False:
            #print("False")
            rep_data = mongo_manager.stixReport.objects(ID=msg["md5"])[0].to_mongo()
            #print("txt_ext_db",rep_data)
            rep_data=dict(rep_data)
            id=rep_data['_id']
            rep_data.pop('_id', None)
            rep_data['md5']=id
            res=buildIndex.post_document(index, rep_data)

        #print('save')
listen()
def getAllData():
    alldata=mongo_manager.stixReport.objects.all()
    for data in alldata:
        print(data.to_mongo())
        #print("title",data.ID,"abstract",data.Abstract)
#getAllData()
# class Post(Document):
#     title=StringField(required=True,max_length=200)
#     content=StringField(required=True)
#     author=StringField(required=True)
#     published=DateTimeField(default=datetime.datetime.now)
# class Post_doc(Document):
#     url=StringField(required=True,unique=True)
#     content=StringField(required=True)
# class Post_fileContxt(Document):
#     url=StringField(required=True,unique=True)
#     content=StringField(required=True)
# def contentToFile(url,content):
#     try:
#         post=Post_fileContxt(url,content)
#         post.save()
#     except:
#         print(url)

#post2=Post_doc(url='127.0.0.1',content='djifjdi')
# post3=Post_doc(url='url1',content='url1-content')
# post4=Post_doc(url='url2',content='url2-content')
# post5=Post_doc(url='url3',content='url3-content')
# post1=Post(
#     title='Sample Post',
#     content='Some engaging content',
#     author='Scott'
# )
#post2.save()
# post3.save()
# post4.save()
# post5.save()
# #print(post2.url)
# for post in Post_fileContxt.objects:
#     print('url'+post.url)
#     print('content'+post.content)
    #print('content'+post.content.strip())
# doc2=Post_doc.objects(url='url1')
# for post in doc2:
#     print(post.content)
# print(doc2.content)
# post1.title='A Better Post Title'
# post1.save()
# print(post1.title)
# post3=Post_doc(
#     url='127.0.0.1',
#     content='djifjdifdf'
# )
# post3.save()

# print(post3.url)