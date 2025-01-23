#################################################################
## 2024. 7.31. SME for rApp / Backend Mode / Use rApp Catalogue Only
#   8.4 For PlugFest 
#   8.21 / 9.3 Update SME
##
##  ETRI
##  K.S. Lee
##
##  Description
##
##  - rApp Catalogue-Enhanced: rApp registration
##  - CAPIF Core: rApp/Service registration
##
#################################################################

#############################
from .Lib_ROSS_BK    import * ## Package REST GET/PUT/POST
from .Lib_sme_bk     import *
#from kpm_console    import * ## For Performance Evaluation
#from kpm_compare    import * ## For Performance Evaluation
from flask import Blueprint
bp = Blueprint('sme', __name__, url_prefix='/sme')

#############################
## Program Environment 
RAPP_NAME       = "VrApp"
RAPP_VENDOR     = "ETRI"
RAPP_VERSION    = "1.0.0"
RAPP_ID         = "VrApp"
RAPP_SERVICE_TYPE = "ETRI RIC Backend"
RAPP_DESC       = "ETRI RIC Dashboard Backend (rApp)"


#############################
## rApp Catalogue <address:port>
CATALOGUE_URL = "http://" + ROSS_SERVER_ADDRESS + ":9096"    # Non-RT RIC Framework (rApp Catalogue-Enhanced)
CATALOGUE_URI = "/rappcatalogue"

#############################
## SME: RIC Framework <address:port>
SME_URL = "http://" + ROSS_SERVER_ADDRESS + ":8090"    # Non-RT RIC Framework (SME)
SME_URI = "/SME"


###############################
## 0-1. Flask Web Framework  ##

################################################################
## [1] rApp registration Functions
################################################################

##########################
# rApp.py - SME connection
def rApp_reg (name, body):
    
    rApp_Catalogue_Enhanced ()  # All Procedure
    # 1. GET 
    # 2. PUT
    # 3. GET

   

## rApp registration  module
@bp.route('/rappcatalogue')
def rApp_Catalogue ():

    ## 1) rApp Description
#    rApp_service_info = rApp_service_description (RAPP_NAME, RAPP_VERSION, RAPP_SERVICE_TYPE)

    rAppId = RAPP_NAME  ## init.

    ## 1. rApp registration
    eprint (5, "[0]:    <<R1>> rApp Catalogue-Enhanced: registration procedure")

    ## 1.1 Query
    eprint (5, "        0. GET /rappcatalogue")

    target_url = CATALOGUE_URL + "/rappcatalogue"

    rAppIds = requests_get (target_url)

    print ("        Registered rAppIds = ", rAppIds)

    return rAppIds



## rApp registration  module
@bp.route('/rappcatalogue_all')
def rApp_Catalogue_Enhanced ():

    ## 1) rApp Description
#    rApp_service_info = rApp_service_description (RAPP_NAME, RAPP_VERSION, RAPP_SERVICE_TYPE)

    rAppId = RAPP_ID  ## init.

    ## 1. rApp registration
    eprint (5, "[0]:    <<R1>> rApp Catalogue-Enhanced: registration procedure")

    ## 1.1 Query
    eprint (5, "        0. GET /rappcatalogue")

    target_url = CATALOGUE_URL + "/rappcatalogue"

    rAppIds = requests_get (target_url)

    print ("        Registered rAppIds = ", rAppIds)

 #   data_json = rApp_Catalogue_Enhanced_delete (rAppId) # for safe test

    # tric for test
    count = len (rAppIds)

    data_json = rApp_Catalogue_Enhanced_put (rAppId)

    print ("        My rApp Info (registered name) = ", data_json)


    return data_json


## rApp registration  module
@bp.route('/rappcatalogue/<rAppId>', methods=['GET'])
def rApp_Catalogue_Enhanced_get (rAppId):

    ## 1. rApp registration
    eprint (5, "[0]:    <<R1>> rApp Catalogue-Enhanced: registration procedure")

    ## 1.1 Query
    eprint (5, f"        0-1. GET /rappcatalogue/{rAppId}")

    target_url = CATALOGUE_URL + "/rappcatalogue" + "/" + rAppId

    data_json = requests_get (target_url)
 
    return data_json


## rApp registration  module
@bp.route('/rappcatalogue/<rAppId>', methods=['PUT'])
def rApp_Catalogue_Enhanced_put (rAppId):

#    rApp_info         = rApp_description (RAPP_NAME+rAppId, RAPP_VENDOR, rAppId, RAPP_SERVICE_TYPE)

    headers = {
        "Content-Type": "application/json"
    }
    
    ## 1.2 rApp registration PUT
#    body = json.dumps(rApp_info.to_dict(rAppId))
    body = {
        "name": RAPP_NAME,
        "rappSchema": {
            "rAppId": rAppId,
            "ServiceType": RAPP_SERVICE_TYPE
        },
        "description": RAPP_DESC
    }
    #print (body)

    eprint (5, f"        0-2. PUT /rappcatalogue/{rAppId}")

    target_url = CATALOGUE_URL + CATALOGUE_URI + "/" + rAppId
  
    data_json = requests_put(target_url, body)  

    ## 1-3 rApp service registration
    # GET /services/{serviceName}    
    # PUT /services/{serviceName}    
 
    return data_json


## rApp registration  module
@bp.route('/rappcatalogue/<rAppId>', methods=['DELETE'])
def rApp_Catalogue_Enhanced_delete (rAppId):

    ## 1. rApp registration
    eprint (5, "[0]:    <<R1>> rApp Catalogue-Enhanced: registration procedure")

    ## 1.1 Query
    eprint (5, f"        0-1. DELETE /rappcatalogue/{rAppId}")

    target_url = CATALOGUE_URL + "/rappcatalogue" + "/" + rAppId

    data_json = requests_delete (target_url)
 
    return data_json


################################################################
#### Essential Codes for Logging
################################################################

def eprint (level, desc):
    
    body = f"{VENDOR_NAME} {RAPP_NAME} {LOG_LEVEL [level]} {desc}"
    
#    rsend (body)


def eeprint (level, desc, value):

    body = f"{VENDOR_NAME} {RAPP_NAME} {LOG_LEVEL [level]} {desc} {value}"

#    rsend (body)
