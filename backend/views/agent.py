#########################################################
## 2024. 9.19. REST version - Standalone Codes / 10.18 - 10.24 Docker
## 
## Agent for
## - Diagnostic Monitor
## - Time Sequence Diagram
##
## TS syntax
#########################################################

#############################
# Global Declaration
#############################
# ETRI ROSS Server

#RAPP_SERVER_ADDRESS = "192.168.10.111"
RAPP_SERVER_ADDRESS = "129.254.220.111"

#ROSS_SERVER_ADDRESS = "192.168.10.112"
#ROSS_SERVER_ADDRESS = "129.254.220.111"
#ROSS_SERVER_ADDRESS = "127.0.0.1"
ROSS_SERVER_ADDRESS = "0.0.0.0"      # Run as a Docker Container

## Host address:Port: Agent
#HOST_ADDRESS = "0.0.0.0"
#HOST_ADDRESS = "127.0.0.1" 
HOST_PORT = 10007       # To Jian, also for get Data
    # rApp: 20240 ~
    # NonRT: 20250 ~


## Send To Jian
DM_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + str(HOST_PORT)  

#############################
## Program Environments 
BLOCK_NAME      = "DMAgent"
BLOCK_VENDOR    = "ETRI"
BLOCK_VERSION   = "1.0.0"
BLOCK_DESC      = "ERIC Diagnostic Monitor/Sequence Diagram Agent"


#####################################
# Period
DM_Time     = 0 # For DM Time

DBuffer_Count = 0
TBuffer_Count = 0

Buffer_Limit = 2000

Data_dm = []    # Store area
Data_ts = []


#############################
import time
from datetime import datetime   ## time stamp
import os

###############################
## 0-1. Flask Web Framework  ##
from flask import Flask, json, jsonify, request,Blueprint
from flask_cors import CORS     # 다른 포트 번호에 대한 보안 제거 (CORS (app) 만 해도 됨) : 최지안

import requests

##############################
# app = Flask(__name__)   # Web Server

# ##############################
# CORS(app, supports_credentials=True) # 다른 포트 번호에 대한 보안 제거 (CORS (app) 만 해도 됨) : 최지안


#############################
## 0-2. Parallel processing  ##
from threading import Thread
import threading


###################################
## 0-4. Python Schedule package  ##
import schedule 


#####################################
bp = Blueprint('agent', __name__, url_prefix='/agent')
@bp.route ('/')                 ## 0) Root 
def print_block_status():
   
   data = {
        "name":     BLOCK_NAME,
        "vendor":   BLOCK_VENDOR,
        "version":  BLOCK_VERSION,
        "description": BLOCK_DESC,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

   print (data)

   return data

########################### API lists
@bp.route('/api')      ## Show all APIs
def show_api():
    print('ETRI:    Supported APIs')

    data = {
        "api0": "/api",

        "api11": "/dm", ## from jian
        "api12": "/ts", ## from jian

        "api21": "/data",   # from rApp
        
        "api51": "/clear"   # clear buffer
    }

    print (data)

    return data


#####################################
@bp.route ('/data', methods = ['PUT','POST'])                 
def Agent ():

    global DM_Time
    global DBuffer_Count
    global TBuffer_Count
    
    global Data_dm
    global Data_ts

    lines = request.get_json ()
    print ("line = ", lines)   # string

    line = lines.strip ()    # delete \n

    trans = line.split ()    # to list
    
    index = line.find (':')
    if index > 0:
        desc = line [index+2:]
    else:
        desc = line
        
    ###########################
    # DM processing - Copy all
                
    data_dm = {
        "time" : DM_Time, # trans [1], # timestamp
        "vendor":   trans [0],
        "block":    trans [1],
        "level":    trans [2],
        "description": desc
    }

    Data_dm.append (data_dm)    # Store to local
       
    with open ('./output_dm.json', 'w') as f:     # For debugging
        json.dump (Data_dm, f)
    
    
    ###########################
    # TS select
    
    index = line.find ('+')
    
    if index > 0:

        rem = line [index+2:] # OOMB ->> VIAVI : <<IN>> GET http://129.254.218.96:19680/O1/CM/ManagedElement
        indexes = [i for i, char in enumerate(rem) if char == ':']

        print (indexes)
        if len (indexes) > 1:
            last = rem[:indexes[1]-4] + rem[indexes[2]:]
        else:
            last = rem

        data_ts = {
            "time" : DM_Time, # trans [1],
            "msg": last # line [index+2:]
        }
        
        Data_ts.append (data_ts)    # Store to local

        with open ('./output_ts.json', 'w') as f:     # For debugging
            json.dump (Data_ts, f)

        print ("data_ts line = ", data_ts)
      
    DM_Time += 1    # for Local timestamp
    DBuffer_Count += 1
    TBuffer_Count += 1

    return line

############################################
# Send To DM GUI - For Simulation
SCHEDULE_PERIOD = 60

def buffer_manager ():

#    schedule.every(SCHEDULE_PERIOD).seconds.do(simul_to_gui) # SIMUL every 5 sec.
    schedule.every(SCHEDULE_PERIOD).seconds.do(buffer_check)

    while True:
        schedule.run_pending()
        time.sleep(1)


def buffer_check ():
    
    global Data_dm
    global Data_ts
    
    global DBuffer_Count
    global TBuffer_Count
    
    print ("DMAgent: Buffer_Count = ", DBuffer_Count, TBuffer_Count)
    if DBuffer_Count > Buffer_Limit:
        DBuffer_Count = 0
        Data_dm.clear ()   

    if TBuffer_Count > Buffer_Limit:
        TBuffer_Count = 0
        Data_ts.clear ()           
    
    
    
def simul_to_gui ():

    to_dm_gui ()

    jdata = to_ts_gui ()

    print ("To Jian: Data_ts = ", jdata)
    

############################################
@bp.route ('/clear')
def clear_buffer ():
    
    buffer_manager () 



############################################
@bp.route ('/dm')                 ## 0) To Frontend - Jian
def to_dm_gui ():

    global Data_dm
    global DBuffer_Count

    jdata = []

    if len (Data_dm) > 0:

        jdata = Data_dm.copy()
    
        Data_dm.clear ()
        DBuffer_Count = 0

    # print ("To Jian: DM = ", jdata)

    return jdata


@bp.route ('/ts')                 ## 0) Root 
def to_ts_gui ():

    global Data_ts
    global TBuffer_Count

    # print ("Data_ts = ", Data_ts)

    jdata = []

    if len (Data_ts) > 0:

        jdata = Data_ts.copy()

        Data_ts.clear ()
        TBuffer_Count = 0

        print ("TS Data = ", jdata)


    return jdata


############################################
# PUSH Type Codes - will not be used
def requests_put (target_url, body):
    
    data_json = []

    header = {
        "Content-Type": "application/json"
    }
     
    try:
#        print ("requests_put (target_url) ", target_url)

        response = requests.put(target_url, data=json.dumps(body), headers=header, timeout=10)
#        if response.status_code < 500:  # 200 OK#
#            data_json = json.loads(response.text)

#        else:
#            print (response.status_code)

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass


    return data_json


# ################################################################
# #### Python Program Starting Point
# ################################################################\

# if __name__ == '__main__':

#     ## 0) Environment setting - Initialize
#     print ("START", BLOCK_NAME)
#     print ("Block Name: ", BLOCK_DESC)

#     print_block_status ()
#     show_api ()

#     print ("GUI Block URL: ", DM_URL)

#     cwd = os.getcwd()
#     Working_Directory = cwd + "/backend"
#     os.chdir (Working_Directory)

#     print (BLOCK_NAME, "Directory  = ", Working_Directory)
    
#     #######################################
#     ## 1) Parallel Operation
#     print ("Wakeup Period: ", SCHEDULE_PERIOD)

#     thread1 = Thread (target=buffer_manager) ##, args=(rAppId))
#     thread1.start()
#     #######################################

#     ## 2) Web server running
#     print ("Non-RT RIC Framework Component START : ", BLOCK_NAME)
#     app.run (host=ROSS_SERVER_ADDRESS, port=HOST_PORT, debug=False, use_reloader=False)     ## Run Web Server (using Flask)
