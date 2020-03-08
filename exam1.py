import pandas as pd
pd.set_option('max_columns',200)
pd.set_option('max_rows',2000)
df_a=pd.read_csv('a_lvr_land_a.csv').drop(index=0)
df_b=pd.read_csv('b_lvr_land_a.csv').drop(index=0)
df_e=pd.read_csv('e_lvr_land_a.csv').drop(index=0)
df_f=pd.read_csv('f_lvr_land_a.csv').drop(index=0)
df_h=pd.read_csv('h_lvr_land_a.csv').drop(index=0)
df_all=pd.concat([df_a,df_b,df_e,df_f,df_h],ignore_index=True)

# filter_a

# 條件一: 【主要用途】為【住家用】
condition1=(df_all['主要用途']=='住家用')
# 條件二: 【建物型態】為【住宅大樓】
condition2=(df_all['建物型態'].apply(lambda s:'住宅大樓' in s))

def chineseNum2Num(s):
    
    table={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    num=0
    
    if s[0]=='十':
        num=1
    for i in s:
        if i == '十':
            num*=10
        elif i in table:
            num+=table[i]
        else:
            continue
    return num

# 條件三: 【總樓層數】需【大於等於十三層】
condition3=df_all['總樓層數'].fillna('0').apply(lambda i: True if chineseNum2Num(i)>=13 else False)

filter_a=df_all.loc[condition1&condition2&condition3,:]
filter_a.to_csv('filter_a.csv',index=False)

# filter_b

count=df_all.shape[0]
berthNum=df_all['交易筆棟數'].apply(lambda s:int(s.split('車位')[-1])).sum()
price=df_all['總價元'].astype('int32').mean()
berthprice=df_all['車位總價元'].astype('int32').mean()
filter_b=pd.DataFrame({'總件數':[count],'總車位數':[berthNum],'平均總價元':[price],'平均車位總價元':[berthprice]})
filter_b.to_csv('filter_b.csv',index=False)