#################################################################
## 2024. 8. 5. - For GUI Backend rApp
##
##  ROSS IF Function
##  ETRI
##  K.S. Lee
##
##  Description
##  - for requests.get/put/post
##  - for Logging (print)
##
################################################################

VENDOR_NAME     = "ETRI"
BLOCK_NAME      = "VrApp"

#############################
#Global Declaration

#############################
# ETRI ROSS Server
#RAPP_SERVER_ADDRESS = "192.168.10.112"
RAPP_SERVER_ADDRESS = "129.254.220.111"

#ROSS_SERVER_ADDRESS = "192.168.10.112"
ROSS_SERVER_ADDRESS = "129.254.220.111"
#ROSS_SERVER_ADDRESS = "127.0.0.1"

#############################
## VIAVI RIC Tester URL
VIAVI_ADDRESS = "129.254.218.96"
#VIAVI_ADDRESS = "192.168.1.196"
#VIAVI_PORT = "80"
VIAVI_PORT = "19680"


VIAVI_URL = "http://" + VIAVI_ADDRESS + ":" + VIAVI_PORT
#VIAVI_URL = "http://192.168.1.196"   # ETRI VIAVI Address


#############################
# ETRI ROSS Server
OOMB_PORT = "20250"
ODMB_PORT = "20251"
OSMB_PORT = "8090" #"9096"
OAPB_PORT = "8081" # OSC PMS

## OOMB: RIC Flatform <address:port>
OOMB_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + OOMB_PORT # Non-RT RIC Framework (OOMB)
## ODMB: RIC Flatform <address:port>
ODMB_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + ODMB_PORT # Non-RT RIC Framework (ODMB)
OSMB_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + OSMB_PORT # Non-RT RIC Framework (OSMB)
OAPB_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + OAPB_PORT # Non-RT RIC Framework (OAPB)


#############################
## EUCAST OAM address:port
OAM_FTP_PORT = "22"     # SSH Port 
OAM_REST_PORT = "21010"

OAM_ID      = "user01"
OAM_PASSWD  = "1234"

OAM_ADDRESS = "192.168.10.59"

OAM_REST_URL = "http://" + OAM_ADDRESS + ":" + OAM_REST_PORT   # ETRI VIAVI Address


############################# 
# To DM Agent - for Printout
DM_PORT = '10007'

DM_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + DM_PORT  # Non-RT RIC Framework: OOMB


import requests
import json
import time


############################################
def requests_get (target_url):
    
    data_json = []
     
    try:
        eeprint (3, "BK requests_get (target_url) = ", target_url)
       
        response = requests.get(target_url, timeout=2)
        
        if response.status_code < 500:  # 200 OK
            data_json = json.loads(response.text)

        # print ("response ", response.status_code, type (response))
        # print ("response.text ", response.text)
        pass
    except requests.ConnectionError:
        pass


    return data_json


############################################
def requests_put (target_url, body):
    
    data_json = []

    header = {
        "Content-Type": "application/json"
    }
     
    try:
        eeprint (3, "BK requests_put (target_url) ", target_url)
        
     #   time.sleep(1)

        response = requests.put(target_url, data=json.dumps(body), headers=header, timeout=10)

     #   time.sleep(1)

        if response.status_code < 500:  # 200 OK
            data_json = json.loads(response.text)

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass


    return data_json


############################################
def requests_post (target_url, body):
    
    data_json = []

    header = {
        "Content-Type": "application/json"
    }
     
    try:
        eeprint (3, "BK requests_post (target_url) ", target_url)

        response = requests.post(target_url, data=json.dumps(body), headers=header, timeout=10)

        if response.status_code < 500:  # 200 OK
            data_json = json.loads(response.text)


    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass


    return data_json


############################################
def requests_delete (target_url):
    
    data_json = []
     
    try:
        eeprint (3, "requests_delete (target_url) = ", target_url)
       
        response = requests.delete(target_url, timeout=10)

        if response.status_code < 500:  # 200 OK
            data_json = json.loads(response.text)


    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass


    return data_json     


############################################
## Printout Related Codes
##

LOG_LEVEL = [ 
    "INFO",     ## 0
    "ERROR",    ## 1
    "WARNING",  ## 2
    "Func", ## 3
    "REST +", ## 4
    "VERBOSE",  ## 5
    "MODE",     ## 6
    "DEBUG"     ## 7
]


####################################################

def eprint (level, desc):
    print (VENDOR_NAME, BLOCK_NAME, LOG_LEVEL [level], desc)


def eeprint (level, desc, value):
    print (VENDOR_NAME, BLOCK_NAME, LOG_LEVEL [level], desc, value)
