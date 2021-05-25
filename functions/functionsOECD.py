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
    category=data['structure']['name']
    structure = data['structure']['dimensions']['series']
    
    for key in data['dataSets'][0]['series'].keys():
        pos = [
            int(re.sub(':.+$','',key)),
            int(re.sub('^.+:','',key))
            ]

        val = [
            structure[0]['values'][pos[0]],
            structure[1]['values'][pos[1]]
            ]

        dim = {
            'dataSet':ref,
            'source':'OECD',
            'category':category
            }

        for i in range(len(val)):
            name = structure[i]['name'].lower()
            posit = structure[i]['keyPosition']
            
            if name == 'country':
                name = "location"
            
            dim[name] = {
                'id':val[i]['id'],
                'name':val[i]['name'],
                'keyPosition':posit
            }

        collection.append(dim)
    return(collection)

# Retrieving a particular dataset

def oecdGetSeries(dataref,variable,location):
    if variable['keyPosition']==0:
        link = f"https://stats.oecd.org/SDMX-JSON/data/{dataref}/{variable['id']}.{location['id']}"
    else:
        link = f"https://stats.oecd.org/SDMX-JSON/data/{dataref}/{location['id']}.{variable['id']}"

    response = requests.get(link)
    return(response.json())


def oecdOutput(dataref,variable,location):
    data = oecdGetSeries(dataref,variable,location)
    # Data
    series = [obs[0] for obs in data['dataSets'][0]['series']['0:0']['observations'].values()] # Accessing data
    years = [year['id'] for year in data['structure']['dimensions']['observation'][0]['values']]#years

    #Meta data
    meta = data['structure']['attributes']['series']
    finalSet = {} 
    for i in range(len(meta)):
        if meta[i]['values']:
            finalSet[meta[i]['name'].lower()] = meta[i]['values'][0]['name']

    # Adding variable name & location
    structure = data['structure']['dimensions']['series']
    for i in range(len(structure)):
        if structure[i]['values'][0]['name'] == "country":
            tempo = "location"
        else:
            tempo = structure[i]['values'][0]['name']
        finalSet[structure[i]['name'].lower()] = tempo

    # Adding data
    finalSet['data']={}
    for pos in range(len(series)):
        finalSet['data'][years[pos]] = series[pos]

    # Adding source & dataset title
    finalSet['source']='OECD'
    finalSet['title']=data['structure']['name']
    
    return(finalSet)