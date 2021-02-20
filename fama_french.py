# %%
import pandas as pd
import statsmodels.api as sm
import numpy as np
from functools import reduce
# %%
merge_all = lambda x,y: pd.merge(x,y,on=['code','date'],how='outer')
wmean = lambda x,y: np.average(x,weights=y)
weight_style = 'eq'
# %%
ipo_date = pd.read_excel('data\上市首日日期.xlsx')
ipo_date.columns = ['code','name','ipo_date']
ipo_date = ipo_date.drop('name',axis=1)
ipo_date['ipo_date'] = ipo_date['ipo_date'].astype('datetime64[ns]')
ipo_date['code'] = ipo_date['code'].astype(str).str.zfill(6)
dprice = pd.read_excel('data\行情数据-only data周度.xlsx')
dprice = dprice[1:]
dprice = pd.melt(dprice,id_vars='日期',var_name='code',value_name='price')
dprice = dprice[dprice['price'] != 0 ]
dprice['code'] = dprice['code'].astype(str).str.zfill(6)
dprice['dret'] = dprice.groupby('code')['price'].pct_change(1)
# dprice = dprice[dprice['日期'] > '2018-01-01']
dprice = dprice.rename({'日期':'date'},axis=1)
dprice['ym'] = dprice['date'].apply(lambda x:x.year*100 + 6 if x.month > 6 else  (x.year - 1)*100 + 6)
dprice = dprice.merge(ipo_date,on=['code'])
dprice['ipo_diff'] = (dprice['date']-dprice['ipo_date']).dt.days
# 剔除上市小于60天的收盘价
dprice = dprice[dprice['ipo_diff'] > 60]
# %%
rf = pd.read_excel('data\定期存款利率3个月.xls', header=1)
exf = pd.ExcelFile('data\股票样本因子数据20210219.xlsx')
ext_fin = pd.read_excel('data\非金融企业股票样本.xlsx')
# 剔除金融股
# ext_fin = ext_fin.iloc[:,1:]
# ext_fin.columns=['code','name']
# ext_fin['code'] = ext_fin['code'].astype(str).str.zfill(6)
# dprice = dprice[dprice['code'].isin(ext_fin['code'])]

# ofactor = pd.read_excel('data\股票样本因子数据20210212.xlsx')
ofacts_list = []
for sn in exf.sheet_names:
    ofact = exf.parse(sheet_name=sn,header=1)
    ofact = ofact.drop(['股票名称','Unnamed: 0'],axis=1)
    ofact = pd.melt(ofact,id_vars='股票代码',var_name='date',value_name=sn)
    ofact = ofact.rename({'股票代码':'code'},axis=1)
    ofacts_list.append(ofact)
ofacts = reduce(merge_all,ofacts_list)
# ofacts['ym'] = (ofacts['date']-1)*100 + 6
ofacts['ym'] = ofacts['date']*100 + 6
ofacts = ofacts.drop('date',axis=1)
ofacts['code'] = ofacts['code'].astype(str).str.zfill(6)
# %%
# 数据清洗
ofacts.columns=['code','size','bp','op','inv','esg','ym']
ofacts = ofacts[ofacts['bp'] != 0]
ofacts = ofacts[ofacts['size'] != 0]
ofacts = ofacts[ofacts['op'] != 0]
ofacts = ofacts[ofacts['inv'] != 0]
ofacts = ofacts[ofacts['esg'] != 0]
ofacts = ofacts.dropna()
# 剔除市值最小的百分之10
# ofacts['size_sort'] = ofacts.groupby('ym')['size'].transform(pd.qcut,10,labels=[1,2,3,4,5,6,7,8,9,10])
# ofacts = ofacts[ofacts['size_sort'] != 1]
# 分组
ofacts['g1'] = ofacts.groupby('ym')[['size']].transform(pd.qcut,[0,0.5,1],labels=['S','B'])
ofacts['g2'] = ofacts.groupby('ym')[['bp']].transform(pd.qcut,[0,0.3,0.7,1],labels=['L','N','H'])
ofacts['g3'] = ofacts.groupby('ym')[['op']].transform(pd.qcut,[0,0.3,0.7,1],labels=['W','N','R'])
ofacts['g4'] = ofacts.groupby('ym')[['inv']].transform(pd.qcut,[0,0.3,0.7,1],labels=['A','N','C'])
ofacts['g5'] = ofacts.groupby('ym')[['esg']].transform(pd.qcut,[0,0.3,0.7,1],labels=['B','N','G'])
ofacts['SMB_BM'] = ofacts['g1']+ofacts['g2']
ofacts['SMB_OP'] = ofacts['g1']+ofacts['g3']
ofacts['SMB_INV'] = ofacts['g1']+ofacts['g4']
ofacts['SMB_ESG'] = ofacts['g1']+ofacts['g5']
ffdf = dprice.merge(ofacts,on=['code','ym'])
ffdf = ffdf.fillna(method='backfill')
# ffdf['SMB_ESG'] = ffdf['SMB_ESG'].fillna('SG')
# %% 
# SMB
if weight_style == 'eq':
    smb_bmdf = ffdf.groupby(['date','SMB_BM'])['dret'].mean().unstack().sort_index()
    smb_opdf = ffdf.groupby(['date','SMB_OP'])['dret'].mean().unstack().sort_index()
    smb_invdf = ffdf.groupby(['date','SMB_INV'])['dret'].mean().unstack().sort_index()
    smb_esgdf = ffdf.groupby(['date','SMB_ESG'])['dret'].mean().unstack().sort_index()
else:
    smb_bmdf = ffdf.groupby(['date','SMB_BM']).apply(lambda x:wmean(x['dret'],x['size'])).unstack().sort_index()
    smb_opdf = ffdf.groupby(['date','SMB_OP']).apply(lambda x:wmean(x['dret'],x['size'])).unstack().sort_index()
    smb_invdf = ffdf.groupby(['date','SMB_INV']).apply(lambda x:wmean(x['dret'],x['size'])).unstack().sort_index()
    smb_esgdf = ffdf.groupby(['date','SMB_ESG']).apply(lambda x:wmean(x['dret'],x['size'])).unstack().sort_index()

smb_bm = smb_bmdf.loc[:,smb_bmdf.columns.str.contains('S')].mean(axis=1) - smb_bmdf.loc[:,smb_bmdf.columns.str.contains('B')].mean(axis=1)
smb_op = smb_opdf.loc[:,smb_opdf.columns.str.contains('S')].mean(axis=1) - smb_opdf.loc[:,smb_opdf.columns.str.contains('B')].mean(axis=1)
smb_inv = smb_invdf.loc[:,smb_invdf.columns.str.contains('S')].mean(axis=1) - smb_invdf.loc[:,smb_invdf.columns.str.contains('B')].mean(axis=1)
smb_esg = smb_esgdf.loc[:,smb_esgdf.columns.str.contains('S')].mean(axis=1) - smb_esgdf.loc[:,smb_esgdf.columns.str.contains('B')].mean(axis=1)

# %%
ffact = pd.DataFrame(index=smb_bmdf.index)
ffact['SMB'] = (smb_bm+smb_op+smb_esg+smb_inv)/4
ffact['HML'] = smb_bmdf[['SH','BH']].mean(axis=1)-smb_bmdf[['SL','BL']].mean(axis=1)
ffact['RMW'] = smb_opdf[['SR','BR']].mean(axis=1)-smb_opdf[['SW','BW']].mean(axis=1)
ffact['CMA'] = smb_invdf[['SC','BC']].mean(axis=1)-smb_invdf[['SA','BA']].mean(axis=1)
ffact['ESG'] = smb_esgdf[['SG','BG']].mean(axis=1)-smb_esgdf[['SB','BB']].mean(axis=1)
ffact.to_csv(f'ffact_{weight_style}.csv')
# %%
mkt_rf = pd.read_excel('data\市值溢价因子.xlsx')
mkt_rf = mkt_rf[['交易日期','市场风险溢价因子(流通市值加权)']]
mkt_rf.columns = ['date','MKT_RF']
ffact = pd.read_csv(f'ffact_{weight_style}.csv')
ffact = ffact.merge(mkt_rf,on=['date'])
ffact.to_csv(f'ffact_{weight_style}.csv', index=False)

# %%
