import  hashlib
f1=open("conTxt/0aff5913f5619279c7a82c3264910a98",encoding='utf-8')
f2=open("conTxt/0e1fafb21b919c7fdae346a1dff71643",encoding='utf-8')
md5=hashlib.md5(f1.read().encode('utf-8')).hexdigest()
md5_=hashlib.md5(f2.read().encode('utf-8')).hexdigest()
print(md5)
print(md5_)