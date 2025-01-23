## SJ 2024. 12.05

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import matplotlib
from datetime import datetime, timedelta,timezone
import time
import csv

per_cell = False
cell_idx = 0


def kpi_compare(file1, file2, kpi):

    
        ## kpm
        # ['DRB.UEThpDl', 'DRB.UEThpUl', 'RRU.PrbUsedDl', 'RRU.PrbUsedUl', 'RRU.PrbAvailDl',
        #    'RRU.PrbAvailUl', 'RRU.PrbTotUl', 'RRU.PrbTotDl','RRC.ConnMean',
        #    'RRC.ConnMax', 'QosFlow.TotPdcpPduVolumeUl',
        #    'QosFlow.TotPdcpPduVolumeDl', 'PEE.AvgPower', 
        #    'PEE.Energy','Viavi.QoS.Score']
  
    df1 = pd.read_csv(file1, index_col=['Viavi.NrPci','time (ms)'])
    df2 = pd.read_csv(file2, index_col=['Viavi.NrPci','time (ms)'])
    

    df1.sort_index(inplace=True)
    df2.sort_index(inplace=True)

    s_len1 = len(df1.index.levels[1])
    s_len2 = len(df2.index.levels[1])

    value1_s = np.zeros(len(df1.index.levels[0]))
    value2_s = np.zeros(len(df2.index.levels[0]))
    
    if kpi == 'Average Power Usage':
        col_name = 'PEE.AvgPower'
        if per_cell == False:
           value1 = df1[col_name].mean()
           value2 = df2[col_name].mean()
        else:
           for i in range(len(df1.index.levels[0])):
               value1_s[i] = df1[col_name][s_len1*i:s_len1*(i+1)].mean()
           for i in range(len(df2.index.levels[0])):
               value2_s[i] = df2[col_name][s_len2*i:s_len2*(i+1)].mean()
           
           value1 = value1_s[cell_idx]
           value2 = value2_s[cell_idx]
           
    elif kpi == 'Cell QoS Score':  
        col_name = 'Viavi.QoS.Score'
        if per_cell == False:
           value1 = df1[col_name].mean()  # mean() /median()/quantile([0.25,0.5,0.75])
           value2 = df2[col_name].mean()
        else:
           for i in range(len(df1.index.levels[0])):
               value1_s[i] = df1[col_name][s_len1*i:s_len1*(i+1)].mean()
           for i in range(len(df2.index.levels[0])):
               value2_s[i] = df2[col_name][s_len2*i:s_len2*(i+1)].mean()
           
           value1 = value1_s[cell_idx]
           value2 = value2_s[cell_idx]

    elif kpi == 'DL Throughput':
        col_name = 'DRB.UEThpDl'
        if per_cell == False:
           value1 = df1[col_name].sum() 
           value2 = df2[col_name].sum()
        else:
           for i in range(len(df1.index.levels[0])):
               value1_s[i] = df1[col_name][s_len1*i:s_len1*(i+1)].sum()
           for i in range(len(df2.index.levels[0])):
               value2_s[i] = df2[col_name][s_len2*i:s_len2*(i+1)].sum()
           
           value1 = value1_s[cell_idx]
           value2 = value2_s[cell_idx]


    elif kpi == 'Average Energy Efficiency':
        col_name1 = 'DRB.UEThpDl'
        col_name2 = 'PEE.Energy'

        if per_cell == False:
           value1 = df1[col_name1].sum() / df1[col_name2].sum()
           value2 = df2[col_name1].sum() / df2[col_name2].sum() 
        else:
           for i in range(len(df1.index.levels[0])):
               value1_s[i] = df1[col_name1][s_len1*i:s_len1*(i+1)].sum() / df1[col_name2][s_len1*i:s_len1*(i+1)].sum()
           for i in range(len(df2.index.levels[0])):
               value2_s[i] = df2[col_name1][s_len2*i:s_len2*(i+1)].sum() / df2[col_name2][s_len2*i:s_len2*(i+1)].sum()
           
           value1 = value1_s[cell_idx]
           value2 = value2_s[cell_idx]

    else:
        print('select other kpi')

        value1 = 0
        value2 = 0
    
    
    result_value =( (value1 - value2)/ value2 )*100

    
    return value1, value2, result_value


def timechart_compare(file1, file2, kpi):

    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
   

             ## kpm
        # ['DRB.UEThpDl', 'DRB.UEThpUl', 'RRU.PrbUsedDl', 'RRU.PrbUsedUl', 'RRU.PrbAvailDl',
        #    'RRU.PrbAvailUl', 'RRU.PrbTotUl', 'RRU.PrbTotDl','RRC.ConnMean',
        #    'RRC.ConnMax', 'QosFlow.TotPdcpPduVolumeUl',
        #    'QosFlow.TotPdcpPduVolumeDl', 'PEE.AvgPower', 
        #    'PEE.Energy','Viavi.QoS.Score']

    group_key = 'time (ms)'   #'time'
  
    if kpi =='Number of Active Cell':
        
        g1 = df1.groupby(group_key,sort=True)['Viavi.isEnergySaving'].sum()  # kpim #'Viavi.isEnergySaving'
        g2 = df2.groupby(group_key,sort=True)['Viavi.isEnergySaving'].sum()

        # print(g1)
   
        total_num1= len(df1['Viavi.NrPci'].unique()) 
        total_num2= len(df2['Viavi.NrPci'].unique())

        # print(total_num1)

        value1= total_num1 * 1.0 - g1
        value2= total_num2 * 1.0 - g2

    elif kpi == 'Average Power Usage':

       value1 = df1.groupby(group_key,sort=True)['PEE.AvgPower'].mean()  # kpm  #'PEE.AvgPower'
       value2 = df2.groupby(group_key,sort=True)['PEE.AvgPower'].mean()

    elif kpi == 'DL PRB Usage':  

       value1 = df1.groupby(group_key,sort=True)['RRU.PrbTotDl'].mean()  # kpm  #RRU.PrbTotDl
       value2 = df2.groupby(group_key,sort=True)['RRU.PrbTotDl'].mean()

    elif kpi == 'DL Volume':
       value1 = df1.groupby(group_key,sort=True)['DRB.UEThpDl'].mean()  # kpm  #'DRB.UEThpDl' or 'QosFlow.TotPdcpPduVolumeDl'
       value2 = df2.groupby(group_key,sort=True)['DRB.UEThpDl'].mean()

    else:   ## Unknown 

        value1 = []
        value2 = []


    print ('timechart_compare ()', kpi)

    ## Time calculation
    utc_timezone = timezone.utc

    x1 = np.array(df1['time (ms)']/1000)
    x2 = np.array(df2['time (ms)']/1000)

    dt1 = []
    if x1[0]==x2[0]:    # start time
        if len(x1)>=len(x2):
            for i in range(len(x1)):
                dd = datetime.fromtimestamp(x1[i],utc_timezone)
                dt1.append(dd) 
                # print(dd,'type:',type(dd))
        else:
            for i in range(len(x2)):
                dd = datetime.fromtimestamp(x2[i],utc_timezone)
                dt1.append(dd) 

    elif x1[0]<x2[0]:
         ext = x2[-1] - x1[-1]
         for i in range(len(x1)):
                dd = datetime.fromtimestamp(x1[i],utc_timezone)
                dt1.append(dd) 
         for j in range(ext):
                dd = datetime.fromtimestamp(x2[-ext:],utc_timezone)
                dt1.append(dd)
                
    else:
        ext = x1[-1] - x2[-1]
        for i in range(len(x2)):
                dd = datetime.fromtimestamp(x2[i],utc_timezone)
                dt1.append(dd) 
        for j in range(ext):
                dd = datetime.fromtimestamp(x1[-ext:],utc_timezone)
                dt1.append(dd)

    # print ('ext', dt1)

#    value3 = dt1
    

    return np.array(value1), np.array(value2), dt1 # np.array(dt1)



def main():                   
                   
   v1,v2,v3 =kpi_compare('CellReports1wk1024.csv', 'CellReports1wk1025.csv','Average Energy Efficiency' )
   print(v1, v2, v3)

   s1,s2,s3 = timechart_compare('CellReports1wk1024.csv', 'CellReports1wk1025.csv','DL Volume' )
   
   plt.figure(figsize=(20,10))
   plt.plot(s3[:len(s1)], s1,'r')
   plt.plot(s3[:len(s2)], s2,'b')
   plt.show()
        


if __name__ == '__main__':
    main()