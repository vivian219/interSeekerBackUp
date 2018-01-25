f=open('actortrackr_export_20171204.json')
fp=open('line.txt','w')
for line in f:
    fp.write(line)
    break