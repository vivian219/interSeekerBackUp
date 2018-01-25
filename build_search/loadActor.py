import json
import mongo_manager
import buildIndex
f=open('actortrackr_export_20171204.json')
line=f.readline()
lineDict=json.loads(line)
actorList=lineDict['actors']

for _actor in actorList:
    #print(actor)
    # print(_actor.keys())
    # print(_actor['_source'])
    # print(_actor['_source'].keys())
    actor=_actor['_source']
    # print(actor['type'])

    post=mongo_manager.stixThreatActor(
            Name=actor['name'],
            First_Sighting = actor['created_s'],
            Description = actor['description'],
            Criticality = str(actor['criticality']),
            Classification_Family = actor['classification'][0]['family'],
            Classification_ID =actor['classification'][0]['id'],
            TLP = str(actor['tlp']),
            Actor_Types = str(actor['type']),
            Motivations = str(actor['motivation']),
            Aliases = str(actor['alias']),
            Communication_Addresses =actor['communication_address'][0]['value'],
            Financial_Accounts =str(actor['financial_account'][0]['value']),
            Country_Affiliations = str(actor['country_affiliation']),
            Known_Targets = str(actor['known_target']),
            Actor_Suspected_Point_of_Origin = actor['origin'],
            Infrastructure_IPv4s = str(actor['infrastructure']['ipv4']),
            Infrastructure_FQDNs = str(actor['infrastructure']['fqdn']),
            Infrastructure_Action = actor['infrastructure']['action'],
            #Infrastructure_Ownership = actor['infrastructure_ownership'],
            Infrastructure_Status =actor['infrastructure']['status'],
            Infrastructure_Types = actor['infrastructure']['type'][0],
            Detection_Rules = actor['detection_rule'][0]['value']
        )
    post.save()
    if buildIndex.document_exist("actor", "Name",actor['name']) == False:
        rep_actor =mongo_manager.stixThreatActor.objects(Name=actor["name"])[0].to_mongo()
        rep_actor = dict(rep_actor)
        id = rep_actor['_id']
        rep_actor.pop('_id', None)
        rep_actor['Name'] = id
        res = buildIndex.post_document("actor", rep_actor)
        print(actor['name']+"is new!")
    else:
        print(actor['name']+"exist!!")

#print(lineDict['actors'])
