#################################################################
## 2024. 7. 30. For GUI, ETRI RIC Backend  Version 1.0 / Console Ver 12.26
## 
## ETRI
## K.S. Lee
##
## Description
##
################################################################

#############################
from .Lib_ROSS_BK    import * ## Package REST GET/PUT/POST
from .kpm_compare    import * ## For Performance Evaluation

###############################
## 0-1. Flask Web Framework  ##
from flask import Flask, json, jsonify, request
from flask_cors import CORS     # 다른 포트 번호에 대한 보안 제거 (CORS (app) 만 해도 됨) : 최지안

from flask import Blueprint


##############################
ap = Blueprint ('pe', __name__, url_prefix='/pe')         ## openapi


###############################
## General
from datetime import datetime   ## time stamp

import os


################################################################################################################################
# Performance Evaluation Console
################################################################################################################################
    # "api51": "/files",
    # "api52": "/items",
    # "api53": "/kpi",
    # "api54": "/kpits",
    # "api55": "/compare",

#########################
KPI_csv_dir = './backend/csv'

KPI_file1 = ''
KPI_file2 = ''

KPI_config = [    
    'Average Power Usage',
    'Cell QoS Score',
    'DL Throughput',
    'Average Energy Efficiency'
    ]

KPI_config_ts = [    
    'Number of Active Cell',
    'Average Power Usage',
    'DL PRB Usage',
    'DL Volume'    
    ]

KPI_file1 = 'CellReports.csv'
KPI_file2 = 'CellReports.csv'
#KPI_file2 = 'CellReports1wk1024.csv'

#KPI_config = ['DL Throughput', 'Average Energy Efficiency']     # default
#KPI_config_ts = ['Average Power Usage', 'DL PRB Usage']  # default


#########################
KPI_items = [
    'Average Power Usage',
    'Cell QoS Score',
    'DL Throughput',
    'Average Energy Efficiency',

    'Energy Saving TBD',
    'Number of Active Cells TBD',
    'Average Cells PRB Usage TBD'
    ]

KPI_items_unit = [
    'kWatt',
    'Point',
    'Mbps',
    'kbits/Joule',

    'Point'
    'Cells',
    'PRBs'
    ]

KPI_items_desc = [
    'Average Power Usage',
    '99th percentile Cell QoS Score',
    'DL Throughput',
    'Average Energy Efficiency',

    'Energy Saving desc',
    'Number of Active Cells desc',
    'Average Cells PRB Usage desc'
    ]



KPI_items_ts = [
    'Number of Active Cell',
    'Average Power Usage',
    'DL PRB Usage',
    'DL Volume'    
    ]

KPI_items_ts_unit = [
    'Cells',
    'kWatt',
    'PRBs',
    'Mbit'
    ]

KPI_items_ts_desc = [
    'Number of Active Cell (Time Series)',
    'Average Power Usage (Time Series)',
    'DL PRB Usage (Time Series)',
    'DL Volume (Time Series)'
    ]


########################################
## 1st 
@ap.route ('/files', methods = ['GET'])    ## 1)
def files ():

    data = []

    ## 1) GET file lists
    filedir = KPI_csv_dir
    
    data = file_list (filedir)

    result = { 'filename': data }


    return result


def file_list (dir):
    
    data = []
    
    try:
        files = os.listdir (dir)
        
        data = [file for file in files if file.endswith('.csv')]
        
        
    except FileNotFoundError:
        print(f"'{dir}' Cannot find the Directory")
    except NotADirectoryError:
        print(f"'{dir}' Not a Correct Directory")
    except PermissionError:
        print(f"'{dir}' No permission to the Directory")
    
     
    return data


##############################################
# Config
@ap.route ('/items', methods = ['GET']) # /items?type=kpi
def items ():

    item_type = request.args.get ('type')

    if not item_type:
        result = { 'items': KPI_items  }


    else:
        
        if item_type == 'kpi':

            result = { 'items': KPI_items  }

        else: # kpits

            result = { 'items': KPI_items_ts  }


    return result


@ap.route ('/items', methods = ['POST'])
def items_post ():

    global KPI_config
    global KPI_config_ts

    # 1) Get from Frontend
    body = request.get_json()

    print ('items_post ()', body)

    type = body ['type']
    if type == 'kpi':
        KPI_config.copy (body ['items'])
    elif type == 'kpits':
        KPI_config_ts.copy (body ['items'])


    return body


######################
## KPI item configure
@ap.route ('/kpi', methods = ['POST', 'PATCH'])
def kpi_post ():

    global KPI_config
   
        
    # 1) Get from Frontend
    body = request.get_json()

    print ('kpi_post ()', body)

    # 2) Decode
    data = body ['items']

       
    KPI_config      = data.copy ()
    
    print ('KPI_config: ', KPI_config)

    return KPI_config


@ap.route ('/kpits', methods = ['POST', 'PATCH'])
def kpits_post ():

    global KPI_config_ts
   
        
    # 1) Get from Frontend
    body = request.get_json()

    print ('kpits_post ()', body)

    # 2) Decode
    data = body ['items']

       
    KPI_config_ts   = data.copy ()
    
    print ('KPI_config_ts: ', KPI_config_ts)

    return KPI_config_ts


######################
## KPI Compare Results
@ap.route ('/kpi', methods = ['GET'])
def kpi ():

    global KPI_file1
    global KPI_file2

    global KPI_config

    result = []

    # KPI_csv_dir = './csv/'
    print ('/kpi', KPI_file1, KPI_file2, KPI_config)

    result = compare_file (KPI_file1, KPI_file2, KPI_config)
   

    return result


def compare_file (file1, file2, kpi_config):

    result = []

    # filename1, file_extension1 = os.path.splitext (file1)
    # filename2, file_extension2 = os.path.splitext (file2)

    # if file_extension1 != 'csv':
    #     if file_extension2 != 'csv':
    #         return result   # Void File name
    #     else:
    #         file1 = file2
    # else:
    #     if file_extension2 != 'csv':
    #         file2 = file1


    lfile1 = KPI_csv_dir + '/' + file1
    lfile2 = KPI_csv_dir + '/' + file2


    for mode in kpi_config:

        index = KPI_items.index (mode)
        
        value1, value2, value3 = kpi_compare (lfile1, lfile2, mode)

        result.append ( kpi_data_gen (index, value1, value2, value3))


    return result


def kpi_data_gen (m, value1, value2, value3):
    
    print (m, value1, value2, value3)

    item = {
        'item': KPI_items [m],
        'unit': KPI_items_unit [m],

        'value1': round (value1, 2),
        'value2': round (value2, 2),
        'compare': round (value3, 2),     # %

        'desc': KPI_items_desc [m]
    }

    return item



######################
## KPI Compare Results
@ap.route ('/kpits', methods = ['GET'])
def kpits ():

    global KPI_file1
    global KPI_file2

    global KPI_config_ts

    result = []

    # KPI_csv_dir = './csv/'


    result = compare_file_ts (KPI_file1, KPI_file2, KPI_config_ts)


    return result


def compare_file_ts (file1, file2, kpi_config):

    global KPI_config_ts

    results = []


    lfile1 = KPI_csv_dir + '/' + file1
    lfile2 = KPI_csv_dir + '/' + file2

    for mode in kpi_config:
        values = []
        item = {}

        index = KPI_items_ts.index (mode)

        value1, value2, times  = timechart_compare (lfile1, lfile2, mode)

        values = kpits_data_gen (value1, value2, times)

        print ('compare_file_ts ()', mode, index, lfile1, lfile2)

        item ['item'] = KPI_items_ts [index]
        item ['unit'] = KPI_items_ts_unit [index]
        item ['desc'] = KPI_items_ts_desc [index]

        item ['valueData'] = values.copy ()

        results.append (item)

    return results


def kpits_data_gen (value1, value2, times):

    values = []

    i = 0
    for v1, v2, t in zip (value1, value2, times):
    
        dt = t.strftime ("%M:%S")
        
        if i == 0:
            print (t, 'start = ', dt)

        value = {
            'name': dt,
            'value1': round (v1, 2),
            'value2': round (v2, 2)
        }

        values.append (value)

        i += 1 

    return values


####################################

#################################
## KPI Compare Results
@ap.route ('/compare', methods = ['GET'])
def compare_files_list ():

    global KPI_file1
    global KPI_file2

    content = {
        'file1': KPI_file1,
        'file2': KPI_file2
    }

    print ('compare_files_list ()', content)


    return content


#################################
## KPI Compare Results
@ap.route ('/compare', methods = ['POST'])
def compare ():

    global KPI_file1
    global KPI_file2

    # 1) Get from Frontend
    body = request.get_json()


    # 2) Decode & Save Only
    KPI_file1 = body ['file1']
    KPI_file2 = body ['file2']

    print ('compare ()', body)

    
    return body # echo

