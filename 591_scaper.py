import requests
from bs4 import BeautifulSoup
import json
import time 
import sys
from pymongo import MongoClient
import datetime

region='台北市'
region_num={'台北市':'1','新北市':'3'}
url='https://rent.591.com.tw/?kind=0&region='+region_num[region]

headers={
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
}

cookies={'urlJumpIp':region_num[region],
          '591_new_session':'eyJpdiI6IkdOSHMyRUl0clpFNzJDQzlVZWh5Q3c9PSIsInZhbHVlIjoid0lvZGtLc0VQSmlqQ2NpSlNMSHhuQlJPdm5nOEVpV\
         FZ1ckpxSHhaUEFSdUZvdGZSYmFzRWQ3RXlZMngzbmlmVUpLb1B3c2E2c3ZxK2NZdzZ5aDdvRnc9PSIsIm1hYyI6IjM2NzhjYWFiNmQyZjYxYWFmYmQ3Nm\
         I0MDJmOTE3OTgzOTZlNTc5NDYxNjI4Y2VhMGNhNmYxZDg1Njc5OTA3YzgifQ%3D%3D'
         }

response = requests.get(url,headers=headers,cookies=cookies)
html = BeautifulSoup(response.text)
token=html.find('meta',{'name':'csrf-token'})['content']
headers={
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
         'X-CSRF-TOKEN': token,
        'Host': 'rent.591.com.tw',
        'Referer': 'https://rent.591.com.tw/?kind=0&region=1'}

data=[]
totaldata=html.find('span',{'class':'R'}).text.replace(' ','')
totalpage=int(totaldata)//30+1
# totalpage=10
for page in range(int(totalpage)):
    
    try:
        url='https://rent.591.com.tw/home/search/rsList?is_new_list=1&type=1&kind=0&searchtype=1&region='+\
        region_num[region]+'&firstRow='+str(page*30)+'&totalRows='+totaldata

        response = requests.get(url,headers=headers,cookies=cookies)
        result = json.loads(response.text)
    except:
        print("Unexpected error:", sys.exc_info()[0] ,"at page "+ str(page))
        
    for item in result['data']['data']:
        try:
            time.sleep(0.1)
            item_data={}
            item_data['name']=item['nick_name'].split(' ')[-1]
            item_data['identification']=item['nick_name'].split(' ')[0]
            item_data['regionname']=item['regionname']
            post_id=item['post_id']

            item_url='https://rent.591.com.tw/rent-detail-'+str(post_id)+'.html'
            response = requests.get(item_url)    
            html=BeautifulSoup(response.text)
            item_infos=html.find('ul',{'class':'attr'}).find_all('li')
            for item_info in item_infos:

                if '型態' in item_info.text:
                    item_data['type']=item_info.text.split(':')[1][2:]
                elif '現況' in item_info.text:
                    item_data['state']=item_info.text.split(':')[1][2:]

            # phone 
            item_data['phone']=html.find('span',{'class':'dialPhoneNum'})['data-value']
            # sex_criteria 
            for element in html.find_all('li',{'class':'clearfix'}):

                if element.find('div',{'class':'one'}):
                    if element.find('div',{'class':'one'}).text=='性別要求':
                        sex_criteria=element.find('div',{'class':'two'}).find('em').text
                        if '男' in sex_criteria and '女' in sex_criteria:
                            item_data['sex_criteria']='all'
                        elif '女' in sex_criteria:
                            item_data['sex_criteria']='f'
                        elif '男' in sex_criteria:
                            item_data['sex_criteria']='m'
                        break
            else:
                item_data['sex_criteria']='all'
            data.append(item_data)
                
        except:    
            print("Unexpected error:", sys.exc_info()[0],"at page "+ str(page) +' '+ str(post_id))
    
    
    
now = datetime.datetime.now()
date=str(now.year)+str(now.month)+str(now.day)

# connection
conn = MongoClient("mongodb://127.0.0.1") 
collection = db[date]

collection.insert_many(data)

conn.close()
        