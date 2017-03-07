import json
import urllib
import urllib2
import csv
import re

a = "https://image.tmdb.org/t/p/original/"

file = open('/Users/dan/Desktop/mypython/tmdb-image.json').read()
tmdbid=open('/Users/dan/Desktop/mypython/tmdbid.csv')

idLine = json.loads(file)

for line in csv.reader(tmdbid):
    idSite=idLine[str(line[0])].split('/')
    #print idSite
    for i in range(1,len(idSite)):
        imageurl=a+idSite[i] #get imageurl          
        name = str(line[0]) + ':' + str(i) +'.jpg'
        content=urllib2.urlopen(imageurl)
        with open(name, 'wb') as f:
            f.write(content.read())
        
        
       