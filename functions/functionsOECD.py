import requests
import re
import json as json

def oecdGetAllData(ref):
    link = f'https://stats.oecd.org/SDMX-JSON/data/{ref}'
    response = requests.get(link)
    return(response.json())

def oecdGetDimensions(ref):
    data = oecdGetAllData(ref)
    collection = []
    structure = data['structure']['dimensions']['series']
    named0 = structure[0]['name']
    named1 = structure[1]['name']
    posit0 = structure[0]['keyPosition']
    posit1 = structure[1]['keyPosition']
    for key in data['dataSets'][0]['series'].keys():
        pos0 = int(re.sub(':.+$','',key))
        val0 = structure[0]['values'][pos0]

        pos1 = int(re.sub('^.+:','',key))
        val1 = structure[1]['values'][pos1]

        dim = {
            'dataSet':ref,
            'source':'OECD',
            named0.lower():{
                'id':val0['id'],
                'name': val0['name'],
                'keyPosition':posit0
            },
            named1.lower():{
                'id':val1['id'],
                'name':val1['name'],
                'keyPosition':posit1
            }
            }
        collection.append(dim)
    return(collection)

# Retrieving a particular dataset

def oecdGetSeries(dataref,variable,country):
    if variable['keyPosition']==0:
        link = f"https://stats.oecd.org/SDMX-JSON/data/{dataref}/{variable['id']}.{country['id']}"
    else:
        link = f"https://stats.oecd.org/SDMX-JSON/data/{dataref}/{country['id']}.{variable['id']}"

    response = requests.get(link)
    return(response.json())


def oecdOutput(dataref,variable,country):
    data = oecdGetSeries(dataref,variable,country)
    # Data
    series = [obs[0] for obs in data['dataSets'][0]['series']['0:0']['observations'].values()] # Accessing data
    years = [year['id'] for year in data['structure']['dimensions']['observation'][0]['values']]#years

    #Meta data
    meta = data['structure']['attributes']['series']
    finalSet = {} 
    for i in range(len(meta)):
        if meta[i]['values']:
            finalSet[meta[i]['name'].lower()] = meta[i]['values'][0]['name']

    # Adding variable name & country
    structure = data['structure']['dimensions']['series']
    for i in range(len(structure)):
        finalSet[structure[i]['name'].lower()] = structure[i]['values'][0]['name']

    # Adding data
    finalSet['data']={}
    for pos in range(len(series)):
        finalSet['data'][years[pos]] = series[pos]

    # Adding source & dataset title
    finalSet['source']='OECD'
    finalSet['title']=data['structure']['name']
    
    return(finalSet)