import pandas as pd
import numpy as np
import matplotlib.pyplot as pl
import sys
import json
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, RepeatedStratifiedKFold

class ResistellModel():
    def __init__(self,model):
        self.columns=sorted([i for i in model if i!='intercept'])
        self.mean=np.array([[model[i]['m'] for i in self.columns]])
        self.std=np.array([[model[i]['s'] for i in self.columns]])
        self.coef=np.array([[model[i]['c'] for i in self.columns]])
        self.intercept=np.array([model['intercept']])
        self.model=LogisticRegression()
        self.model.coef_=self.coef
        self.model.intercept_=self.intercept
        self.model.classes_=np.array([0.,1.])
    def predict(self,df):
        X=df[self.columns].values
        X=(X-self.mean)/self.std
        return self.model.predict(X)
    def score(self,df):
        X=df[self.columns].values
        X=(X-self.mean)/self.std
        return self.model.decision_function(X)

def save_json(obj,file_name: str):
    with open(file_name,'w') as file_obj:
        json.dump(obj,file_obj,indent=' ')

def load_json(file_name: str):
    with open(file_name,'r') as file_obj:
        return json.load(file_obj) 

def load_data(file_name: str):
    data={}
    with pd.ExcelFile(file_name) as file:
        for i in file.sheet_names:
            data[i]=file.parse(i)
            cols=[j for j in data[i].columns if j in ['exp_id','sample_id','reference phenotype','model_name','SP1','SP2','SP3','SP4','SP5','SP6','SP7','SP8']]
            data[i]=data[i][cols]
    return data

def sample_level_metrics(df,name):
    df.copy()
    df['phenotype']=df.groupby('sample_id')['score'].transform(lambda x: 'R' if np.median(x)<0 else 'S')
    df=df[['sample_id','reference phenotype','phenotype']].drop_duplicates()
    df['metric']='unknown'
    df.loc[df['reference phenotype'].isin(['S','I'])& df['phenotype'].isin(['S']),'metric']='true positive'
    df.loc[df['reference phenotype'].isin(['R'])& df['phenotype'].isin(['R']),'metric']='true negative'
    df.loc[df['reference phenotype'].isin(['R'])& df['phenotype'].isin(['S']),'metric']='false positive'
    df.loc[df['reference phenotype'].isin(['S','I'])& df['phenotype'].isin(['R']),'metric']='false negative'
    df=df[['sample_id','metric']].groupby('metric').agg(**{name:pd.NamedAgg('sample_id','count')})
    for i in ['true positive','true negative','false positive','false negative']:
        if i not in df.index:
            df.loc[i,name]=0
    df.loc['accuracy %',name]=np.round(100*df.loc[['true positive','true negative'],name].sum()/df[name].sum(),1)
    df.loc['sensitivity %',name]=np.round(100*df.loc['true positive',name]/df.loc[['true positive','false negative'],name].sum(),1)
    df.loc['specificity %',name]=np.round(100*df.loc['true negative',name]/df.loc[['true negative','false positive'],name].sum(),1)
    df=df.loc[['true positive','true negative','false positive','false negative','accuracy %','sensitivity %','specificity %'],:]
    return df

def recording_level_metrics(df,name):
    df.copy()
    df['phenotype']=df['score'].transform(lambda x: 'R' if x<0 else 'S')
    df['metric']='unknown'
    df.loc[df['reference phenotype'].isin(['S','I'])& df['phenotype'].isin(['S']),'metric']='true positive'
    df.loc[df['reference phenotype'].isin(['R'])& df['phenotype'].isin(['R']),'metric']='true negative'
    df.loc[df['reference phenotype'].isin(['R'])& df['phenotype'].isin(['S']),'metric']='false positive'
    df.loc[df['reference phenotype'].isin(['S','I'])& df['phenotype'].isin(['R']),'metric']='false negative'
    df=df[['exp_id','metric']].groupby('metric').agg(**{name:pd.NamedAgg('exp_id','count')})
    for i in ['true positive','true negative','false positive','false negative']:
        if i not in df.index:
            df.loc[i,name]=0
    df.loc['accuracy %',name]=np.round(100*df.loc[['true positive','true negative'],name].sum()/df[name].sum(),1)
    df.loc['sensitivity %',name]=np.round(100*df.loc['true positive',name]/df.loc[['true positive','false negative'],name].sum(),1)
    df.loc['specificity %',name]=np.round(100*df.loc['true negative',name]/df.loc[['true negative','false positive'],name].sum(),1)
    df=df.loc[['true positive','true negative','false positive','false negative','accuracy %','sensitivity %','specificity %'],:]
    return df