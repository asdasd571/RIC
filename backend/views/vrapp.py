#################################################################
## 2024. 7. 30. For GUI, ETRI RIC Backend  Version 1.0 / Console Ver 12.26 / MIMO
## 
## ETRI
## K.S. Lee
##
## Description
##
## - ETRI RIC Console / Dashboard - Backend source code 
##   - Implemented as a separated rApp 
##
##   - Standalone code
##
## - Frontend Source Code
##   /o-ran-dashboard
##
################################################################

# from . import Lib_ROSS_BK   ## Package REST GET/PUT/POST
from .Lib_sme_bk import *
#from kpm_console    import * ## For Performance Evaluation
#from kpm_compare    import * ## For Performance Evaluation
from .kpm_console import *

## <My Address:Port>
HOST_ADDRESS = "0.0.0.0"      # Run as a Docker Container
HOST_PORT = 10006 # ORG 20249        # GUI Port: 10005
    # rApp: 20240 ~
    # NonRT: 20250 ~

RAPP_URL = "http://" + ROSS_SERVER_ADDRESS + ":" + str(HOST_PORT)    # My Address

################################################################
## [0] Python 프로그램 환경 지정
################################################################
## Options

VIAVI_Direct_Mode = 'ON'


VIAVI_MODE  = "ON"   # use VIAVI data + OOMB
SIMUL_DEBUG = 'OFF'   # Only for NI/PM debug
LG_MODE     = "OFF"   # use VIAVI data

SIMUL_XMODE = 'ON'   # Only for xApps

ENABLE_RAPP_REG    = "ON"

#####################################
# DL Throughput --> Cell Metrics
# DL_SUM --> Total Throughput (DL)  
# DL_rate --> PEE.Power


ManagedElement = 1193046    # VIAVI default
    
#############################
## Program Environment 
RAPP_NAME       = "VrApp"
RAPP_VENDOR     = "ETRI"
RAPP_VERSION    = "1.0.0"
RAPP_ID         = "VrApp"
RAPP_SERVICE_TYPE = "ETRI RIC Backend"
RAPP_DESC       = "ETRI RIC Dashboard Backend (rApp)"


VENDOR_NAME     = RAPP_VENDOR
BLOCK_NAME      = RAPP_NAME
BLOCK_VERSION   = RAPP_VERSION
BLOCK_DESC      = RAPP_DESC

#################################################
## For ERIC Console operation
## rApp
RAPP_ES_URL = "http://" + ROSS_SERVER_ADDRESS + ":10005" 


#############################
# Use OOMB 

NI_URI = "/NI"
PM_URI = "/PM"
O1_URI = "/O1"

NI_API_URL = OOMB_URL + NI_URI
PM_API_URL = OOMB_URL + PM_URI

O1_API_URL = OOMB_URL + O1_URI




###############################
## 0-1. Flask Web Framework  ##


#########################################################


###############################
## General
import requests
from datetime import datetime   ## time stamp

import subprocess

import random
import os
import csv

#############################
## 0-2. Parallel processing  ##
from threading import Thread
import threading

###################################
## 0-4. Python Schedule package  ##
import schedule 
from flask import Blueprint,jsonify

################################################################
## Web Server: rApp Visualization back-end
################################################################

########################### Who am I 
bp = Blueprint('vrapp', __name__, url_prefix='/')
@bp.route('/')         ## Root 
def print_rApp_status():

    data = {
        "name": RAPP_NAME,
        "rappSchema": {
            "rAppId": RAPP_ID,
            "ServiceType": RAPP_SERVICE_TYPE
        },
        "description": RAPP_DESC,
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

        "api11": "/dashboard", # No use
            "api111": "/network-info", #
            "api112": "/cell-metrics", 
            "api113": "/cell-sum",
            "api114": "/dl-rate",
            "api115": "/ul-rate",
            "api116": "/num-ue",

            "api118": "/ric-info",
            "api119": "/value3",
                
        "api21": "/rapp",   #
        "api22": "/rblock",

        "api31": "/xapp",
        "api32": "/xblock",

        "api41": "/e2node",
        "api42": "/e2perf/<cellId>",

        "api51": "/pe/files",
        "api52": "/pe/items?type=kpi",
        "api53": "/pe/kpi",
        "api54": "/pe/kpits",
        
        "api55": "/compare",


        "api71": "/run/<block>",

        "api81": "/alarm",
        "api82": "/alarmtest/<block>",

        "api91": "/login",
        "api92": "/register",
        "api93": "/deregister",

        "api99": "/logout"        
    }


    return data


################################################################################################################################
## Global variables

Num_Cell = 26

Num_SMO = 0
Num_rApp = 0
Num_ROSS = 4
Num_RESS = 0


DL_sum = 0
Power_sum = 0 
UE_sum = 0

Map_Cell_State = []

DL_rate = []
Power_rate = []
UE_rate = []

##### Saved data
sDL_rate = []
sPower_rate = []
sUE_rate = []


################################
# Value3 Difference 

DL_diff = 0
Power_diff = 0
UE_diff = 0

################################################################
## 1. Dashboard, Overview
################################
@bp.route('/dashboard')
def dashboard ():

    data = {
        "name": RAPP_NAME,
        "rappSchema": {
            "rAppId": RAPP_ID,
            "ServiceType": RAPP_SERVICE_TYPE
        },
        "description": RAPP_DESC,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return data


###################################################################################################################
## 1. Cell map
###################################################################################################################

# ETRI 중심 좌표: 경도, 위도
#ETRI_X_Pos=127.3655        ## 경도  longitude
#ETRI_Y_Pos=36.3817         ## 위도  latitude

# 신성동 좌표
#ETRI_X_Pos=127.349      ## 경도  longitude
#ETRI_Y_Pos=36.3859      ## 위도  latitude

# ETRI 11동 좌표
#ETRI_X_Pos=127.36311        ## 경도  longitude
#ETRI_Y_Pos=36.38275         ## 위도  latitude

# ETRI 11동 좌표 + LGU Data
ETRI_X_Pos=127.36311 #- 0.023      ## 경도  longitude
ETRI_Y_Pos=36.38275 # - 0.5        ## 위도  latitude


##########################################
@bp.route('/network-info') # map 
def network_info ():

    msg = []

    if VIAVI_MODE == "ON":

        msg = read_network_info ()

    elif LG_MODE =='ON':

        msg = lg_cell_conf ()

    else:

        msg = dummy_cell_conf ()


    return msg


def change_geo_xy (x,y):
    xy = [x, y]

    if (x > ETRI_X_Pos + 10 or x < ETRI_X_Pos - 10):
        xy[0] = ETRI_X_Pos + x
#            eeprint (7, "Location change for GUI: was ", x)      ## GUI 붙이려면 뒤집어야 함: cacao map

    if (y > ETRI_Y_Pos + 10 or y < ETRI_Y_Pos - 10):
        xy[1] = ETRI_Y_Pos + y
#            eeprint (7, "Location change for GUI: was ", y)      ## GUI 붙이려면 뒤집어야 함: cacao map


    return xy


## Read Cell Information
def read_network_info ():

    global Num_Cell
    
    results = []

    ## 1) Read NI from VIAVI Direct 
    target_url = VIAVI_URL + "/O1/CM/" + "ManagedElement"

    result = requests_get (target_url)

    cell_json, beam_json = me_to_cellinfo_new (result)

    if cell_json == None:

        print ("=====================================================================================> Please Check VIAVI is Running !!!")
        alarm_send ('VrApp', 'ERROR', 'VIAVI is not Running')
               
        return results
    
    timestamp = datetime.now().strftime("%M:%S")

    x = 0
    y = 0


    #################
    # Per Cell or Sector
    id = 0
    for cell in cell_json:

        if Map_Cell_State [id] == 'isNotEnergySaving':
            state = 1
        else:
            state = 0

        id += 1
    

        ## 1) Location Calculation
        xy = change_geo_xy (cell['longitude'], cell['latitude'])

        x = xy [0]      ### right order - for Cacao Map
        y = xy [1]


        ## 2) Power Calculation for GUI
        cellSize = cell['cellSize']
        configuredMaxTxPower = cell['configuredMaxTxPower']

        if configuredMaxTxPower < 40:
            configuredMaxTxPower *= 5   # scaling

        ssbfreq = cell['ssbFrequency']
        if ssbfreq < 1000:
            Tx_Power_value = configuredMaxTxPower * 3     # for GUI
        elif ssbfreq < 2200:
            Tx_Power_value = configuredMaxTxPower * 2    # for GUI
        else:
            Tx_Power_value = configuredMaxTxPower * 1.5   # for GUI

        if cellSize == "medium":
            Tx_Power_value = Tx_Power_value * 1.5

        else:
            Tx_Power_value = Tx_Power_value # small ?


        ## freq for Color mapping
        freqColor = 1
        if ssbfreq < 1000:
            freqColor = 1
        elif ssbfreq < 2200:
            freqColor = 2
        else:
            freqColor = 3


        result = {
            'Cell_ID': cell['cellLocalId'],
            'Cell_ID_Full': cell['cellName'],
            'MeasTimestamp': timestamp,

            'X_Pos': x + id * 0.00001,
            'Y_Pos': y, 
            'Z_Pos': cell['azimuth'],

            'State': state,
            'Tx_Power': Tx_Power_value + id, # For GUI
            'Freq_Band': freqColor      # use as a freq for Coloring
        }

        results.append(result)


    ##########################################
    # "mMIMO Beam Group" Analog Beamforming SSB
    freqColor = 6   ## For Test
    state = 1
    configuredMaxTxPower = 200  # Fixed for beamforming
    
    for bcell in beam_json:

        ## 1) Location Calculation
        xy = change_geo_xy (bcell['longitude'], bcell['latitude'])

        x = xy [0]      ### right order - for Cacao Map
        y = xy [1]


        ## 2) Power Calculation for GUI
        cellSize = bcell['cellSize']

        Tx_Power_value = configuredMaxTxPower     # for GUI


        nbeam = bcell ['nHorBeams'] # Just use Hor beam
        azimuth = bcell['azimuth']

        step = 180 / nbeam

        dangle = azimuth - 90 + step/2

        if dangle < 0:
            dangle = dangle + 360

        i = 0
        for beam in range (nbeam):

            dazimuth = dangle  + i * step
            if dazimuth >= 360:
                dazimuth -= 360

            result = {
                'Cell_ID': bcell['cellLocalId'] + (i + 1) * 0.1,
                'Cell_ID_Full': bcell['cellName'] + '-' + str (i + 1),
                'MeasTimestamp': timestamp,

                'X_Pos': x, # + i * 0.00001,
                'Y_Pos': y, 
                'Z_Pos': dazimuth,    # azimuth

                'State': 1, # No use Power Saving
                'Tx_Power': Tx_Power_value + i, # For GUI
                'Freq_Band': freqColor      # use as a freq
            }

            results.append(result)

            i += 1


    Num_Cell = id


    print ("Num_Cell = ", Num_Cell)
    print ("X = 127 x = ", x, "y = ", y)


    return results


#########################################################
## Transform ManagedElement to cell Info. : NI format + MIMO Code
def me_to_cellinfo_new (data):

    global ManagedElement #  = 1193046    # VIAVI default
    global Map_Cell_State

    cucp_cell_id = []
    du_cell_id = []
    viavi_cell = []
    beam_cell = []


    if SIMUL_DEBUG == 'ON':
        with open("./backend/viavi_ni.json", 'r') as file:
            data = json.load(file)
    
    if isinstance (data, list):
        me = data [0]  # list      # Please Check VIAVI is running !!!
    else:
        me = data


#    print ("id = ", me["id"])       ## mandatory 
#    print (me["objectInstance"])    ## mandatory

    ###################################################
    # Error Check of ManagedElement
    value = int (me["objectInstance"].split("=")[1])
#    if value != ManagedElement:
    ManagedElement = value ## Update
    eeprint (2, "ManagedElement New Value = ", value)
    alarm_send ('VrApp', 'WARNING', 'ManagedElement=' + str(value))


    # For Tx Power Only
    #print ("GnbDuFunction = ----------------> ")
    txp = []
    for du in me ["GnbDuFunction"]:
        for duc in du["NrSectorCarrier-Multiple"]:

            md2 = {}
            md2 ['id'] = duc["id"]
            md2 ['objectInstance'] = duc["objectInstance"]
           
            attributes = duc["attributes"]  # skip 1 level for simplicity
            md2 ['configuredMaxTxPower'] = attributes["configuredMaxTxPower"]

            txp.append (md2)


    #print ("GnbDuFunction = ----------------> ")
    for du in me ["GnbDuFunction"]:
        for duc in du["NrCellDu"]:  # per Cell
#       print (du["NrCellDu"])
            
            du_cell_id.append (duc["id"])  ## use as a key

#            print (duc["objectInstance"])
#            print ("attributes = ", duc["attributes"])
#            print ("viavi-attributes = ", duc["viavi-attributes"]) ## Pick NI data

            attributes = duc['attributes']

            viaviattr = duc["viavi-attributes"]
            
            ## Add Angle 
            azimuth = 360       # 0 ~ 359: angle, 360: circle
            # print ('Keys = ',  viaviattr.keys ())

            ##########################################
            ## massive MIMO - Sector
#            print ('antennaModel = ',  antennaModel.keys ())

            advancedRfModel= viaviattr ['advancedRfModel']

            if 'name' in advancedRfModel:
                aname = advancedRfModel ['name']
#                print ('name = ', aname)                

                antennaModel = advancedRfModel ['antennaModel']
                
                type = antennaModel['type'] #"mMIMO Beam Group"

                if type == "Isotropic":
                    azimuth = 360       # 0 ~ 359: angle, 360: circle

                elif type == "Cosine":
                    azimuth = antennaModel ['azimuth'] 

                elif type == "mMIMO Beam Group":

                    beamforming = antennaModel['beamforming']
                    mmtype = beamforming ['type']
                    models = beamforming ['models']

                    for model in models:
                        azimuth = model['azimuth']

                        beamConf = model['beamConf']

                       # print (model.keys ())
                        nHorBeams = beamConf ['nHorBeams']
                        nVerBeams = beamConf ['nVerBeams']

                        print ('nHorBeams = ',  nHorBeams)

                        viavi_beam = { 'cellLocalId': attributes["cellLocalId"],        ## use as a key
                                        'ssbFrequency': attributes ['ssbFrequency'],
                                        'cellSize': viaviattr["cellSize"],
                                        'cellName': viaviattr["cellName"],
                                        'siteName': viaviattr["siteName"],
                                        'longitude': viaviattr["longitude"],  ## x
                                        'latitude': viaviattr["latitude"],     ## y
                                        'nHorBeams': beamConf ['nHorBeams'],
                                        'nVerBeams': beamConf ['nVerBeams'],
                                        'azimuth': model['azimuth']
                        }

                        beam_cell.append(viavi_beam)

                elif type == "Custom":
                    
                    azimuth = antennaModel ['azimuth'] 

            else:

                azimuth = 360    ## For Error Check


            txpower = 0
            for item in txp:
                if item.get ('id') == str (attributes["cellLocalId"]):
                    txpower = item.get ('configuredMaxTxPower')

            ##################################
            ## Typical Cell
            viavi_dict = { 'cellLocalId': attributes["cellLocalId"],        ## use as a key
                            'ssbFrequency': attributes ['ssbFrequency'],
                            'cellSize': viaviattr["cellSize"],
                            'cellName': viaviattr["cellName"],
                            'siteName': viaviattr["siteName"],
                            'longitude': viaviattr["longitude"],  ## x
                            'latitude': viaviattr["latitude"],     ## y
                            'configuredMaxTxPower': txpower,
                            'azimuth': azimuth
            }

    #           print (viavi_dict)                
            viavi_cell.append(viavi_dict)


#    print ("GnbCuCpFunction = ----------------> ")
    cell_state = []

    for cp in me["GnbCuCpFunction"]:
#        print ("id = ", cp["id"])
#        print (cp["objectInstance"])
#        print ("attributes = ", cp["attributes"])

#        print (cp["NrCellCu"])

        for cpc in cp["NrCellCu"]:
    #        print (cpc)

    #        print ("id = ", cpc["id"])
    #        print (cpc["objectInstance"])
    #        print ("attributes = ", cpc["attributes"])

            cpc_att = cpc["attributes"]

    #        print ("cellLocalId = ", cpc_att["cellLocalId"])
            cucp_cell_id.append (cpc_att["cellLocalId"])

            CESManagementFunction = cpc["CESManagementFunction"]
            cat = CESManagementFunction['attributes']
            energySavingState = cat ['energySavingState']

            cell_state.append (energySavingState)

    #       print ("CESManagementFunction = ", cpc["CESManagementFunction"])
    #       print ("NRCellRelation = ", cpc["NRCellRelation"])


    ######################################
    Map_Cell_State = cell_state.copy()


#    print ("GnbCuUpFunction = ---------------->")

    # TBD: No Use Currently
    # for up in me["GnbCuUpFunction"]:

    #    print ("id = ", up["id"])
    #    print (up["objectInstance"])
    #    print ("attributes = ", up["attributes"])

    #up_json = json.dumps (me["GnbCuUpFunction"])        


#    print ("CUCP  Lists = ", cucp_cell_id)
   # print ("Cells = ", du_cell_id)

    # num_cell = i+1  ## initially use NrCellCu cellLocalId
    num_cell = len(du_cell_id)
    print ("Num DU Cell = ", num_cell)

    
    return viavi_cell, beam_cell


######################################################################################
# Define the header
LGheader = ["Site", "Frequency", "Longitude", "Latitude", "Site Height", "Azimuth", "Tilt Angle (MDT_Mechanical Down-Tilt)", "Tilt Angle (EDT_Electrical Down-Tilt)"]

# Existing data
LGdata = [
    ["Site 1", "B1_2.1G", 0.0277958, 0.50213267, 26.1, 170, 35, 14],
    ["Site 1", "B1_2.1G", 0.02779311, 0.50213266, 14.4, 90, 25, 14],
    ["Site 1", "B1_2.1G", 0.02779311, 0.50213266, 14.4, 270, 25, 14],
    ["Site 1", "B5_850M", 0.02778, 0.502198, 21.4, 320, 35, 14],
    ["Site 1", "B5_850M", 0.02778, 0.502198, 21.4, 30, 35, 14],
    ["Site 1", "n78_3.5G", 0.02779615, 0.50213079, 47, 70, 35, 14],
    ["Site 1", "n78_3.5G", 0.02779479, 0.50213347, 29.4, 260, 10, 14],
    ["Site 1", "n78_3.5G", 0.02779412, 0.50213266, 34, 250, 10, 4],
    ["Site 2", "B1_2.1G", 0.03123604, 0.50156919, 40.2, 170, 15, 10],
    ["Site 2", "B1_2.1G", 0.03123604, 0.50156919, 40.2, 260, 15, 10],
    ["Site 2", "B1_2.1G", 0.0312272, 0.50158099, 29.4, 30, 10, 14],
    ["Site 2", "B5_850M", 0.03122652, 0.50158152, 20, 270, 10, 0],
    ["Site 2", "B5_850M", 0.03122652, 0.50158152, 20, 60, 10, 0],
    ["Site 2", "B5_850M", 0.03122652, 0.50158152, 20, 170, 10, 0],
    ["Site 2", "n78_3.5G", 0.03122854, 0.50158099, 55.6, 290, 35, 14],
    ["Site 2", "n78_3.5G", 0.03123197, 0.50157294, 21.4, 90, 35, 14],
    ["Site 2", "n78_3.5G", 0.03123399, 0.50157403, 47, 180, 35, 14],
    # ["Site 3", "B1_2.1G", 0.0320957, 0.5007704, 22.7, 20, 10, 7],
    # ["Site 3", "B1_2.1G", 0.0320957, 0.5007704, 11.8, 170, 15, 14],
    # ["Site 3", "B1_2.1G", 0.0320957, 0.5007704, 21.8, 210, 25, 14],
    # ["Site 3", "B5_850M", 0.0320957, 0.5007704, 81.6, 170, 30, 4],
    # ["Site 3", "B5_850M", 0.0320957, 0.5007704, 35, 50, 15, 4],
    # ["Site 3", "B5_850M", 0.0320957, 0.5007704, 35, 100, 30, 0],
    # ["Site 3", "n78_3.5G", 0.03197625, 0.50066645, 25.9, 170, 25, 5],
    # ["Site 3", "n78_3.5G", 0.03197557, 0.50066752, 35, 50, 15, 0],
    # ["Site 3", "n78_3.5G", 0.03197525, 0.50066591, 14.4, 270, 25, 14],
    # ["Site 4", "B1_2.1G", 0.03511143, 0.50158854, 81.6, 170, 40, 12],
    # ["Site 4", "B1_2.1G", 0.03511143, 0.50158854, 81.6, 170, 30, 0],
    # ["Site 4", "B1_2.1G", 0.03511143, 0.50158854, 42.5, 220, 14, 0],
    # ["Site 4", "B5_850M", 0.03511143, 0.50158854, 12, 100, 10, 0],
    # ["Site 4", "B5_850M", 0.03511143, 0.50158854, 12, 200, 10, 0],
    # ["Site 4", "B5_850M", 0.03511143, 0.50158854, 12, 350, 10, 0],
    # ["Site 4", "n78_3.5G", 0.03511143, 0.50158854, 25.7, 230, 10, 12],
    # ["Site 4", "n78_3.5G", 0.03511143, 0.50158854, 47, 320, 35, 14],
    # ["Site 4", "n78_3.5G", 0.03511093, 0.50158854, 21.4, 30, 35, 14],
    # ["Site 5", "B1_2.1G", 0.02985927, 0.49977709, 44.6, 80, 35, 14],
    # ["Site 5", "B1_2.1G", 0.02985927, 0.49977709, 44.6, 250, 35, 14],
    # ["Site 5", "B1_2.1G", 0.02986373, 0.49977912, 29.6, 30, 35, 14],
    # ["Site 5", "B5_850M", 0.02985927, 0.49977709, 23.7, 130, 25, 12],
    # ["Site 5", "B5_850M", 0.02985927, 0.49977709, 19.8, 210, 25, 12],
    # ["Site 5", "n78_3.5G", 0.0298657, 0.49977456, 12, 200, 10, 0],
    # ["Site 5", "n78_3.5G", 0.02985778, 0.49977278, 14.4, 90, 25, 14],
    # ["Site 5", "n78_3.5G", 0.0298657, 0.49977456, 43.6, 130, 10, 5],
    # ["Site 6", "B1_2.1G", 0.03647605, 0.49908863, 14, 80, 20, 10],
    # ["Site 6", "B1_2.1G", 0.03647605, 0.49908863, 14, 160, 20, 10],
    # ["Site 6", "B1_2.1G", 0.03647596, 0.49908863, 40.2, 180, 10, 5],
    # ["Site 6", "B5_850M", 0.03647609, 0.49908853, 9.9, 60, 35, 14],
    # ["Site 6", "B5_850M", 0.03647609, 0.49908853, 9.9, 160, 35, 14],
    # ["Site 6", "B5_850M", 0.03647609, 0.49908853, 9.9, 310, 35, 14],
    # ["Site 6", "n78_3.5G", 0.03647613, 0.49908859, 61.9, 350, 35, 14],
    # ["Site 6", "n78_3.5G", 0.03647622, 0.49908859, 9.9, 60, 35, 14],
    # ["Site 6", "n78_3.5G", 0.03647613, 0.49908863, 2, 130, 10, 0],
    # ["Site 7", "B1_2.1G", 0.02619319, 0.50344055, 34, 250, 10, 0],
    # ["Site 7", "B1_2.1G", 0.02619114, 0.50344484, 12, 100, 10, 0],
    # ["Site 7", "B1_2.1G", 0.02619114, 0.50344484, 12, 330, 10, 0],
    # ["Site 7", "B5_850M", 0.0261949, 0.50343733, 21.4, 90, 35, 14],
    # ["Site 7", "B5_850M", 0.0261949, 0.50343733, 21.4, 230, 35, 14],
    # ["Site 7", "n78_3.5G", 0.02609745, 0.50325008, 47, 180, 35, 14],
    # ["Site 7", "n78_3.5G", 0.02609733, 0.50323048, 29.6, 30, 35, 14],
    # ["Site 7", "n78_3.5G", 0.02613299, 0.50324783, 37.1, 310, 5, 0],
    # ["Site 8", "B1_2.1G", 0.02617096, 0.50204578, 22.7, 20, 10, 5],
    # ["Site 8", "B1_2.1G", 0.0261696, 0.50204685, 50, 180, 35, 14],
    # ["Site 8", "B1_2.1G", 0.02588879, 0.50221845, 14, 270, 5, 0],
    # ["Site 8", "B5_850M", 0.02588895, 0.50221939, 77.6, 70, 30, 12],
    # ["Site 8", "B5_850M", 0.0261696, 0.50204685, 26.1, 170, 35, 14],
    # ["Site 8", "B5_850M", 0.0261696, 0.50204685, 26.1, 320, 35, 14],
    # ["Site 8", "n78_3.5G", 0.0259566, 0.50206024, 48.9, 300, 10, 5],
    # ["Site 8", "n78_3.5G", 0.02616688, 0.5020506, 3, 70, 35, 14],
    # ["Site 8", "n78_3.5G", 0.02617095, 0.50204686, 22, 210, 25, 0],
    # ["Site 9", "B1_2.1G", 0.02646353, 0.50114732, 46.5, 140, 10, 0],
    # ["Site 9", "B1_2.1G", 0.02646311, 0.50114779, 22.3, 57, 20, 0],
    # ["Site 9", "B1_2.1G", 0.02646344, 0.50114813, 22.7, 280, 10, 5],
    # ["Site 9", "B5_850M", 0.02646302, 0.50114779, 40.2, 170, 15, 8],
    # ["Site 9", "B5_850M", 0.02646302, 0.50114779, 40.2, 260, 15, 8],
    # ["Site 9", "B5_850M", 0.02646311, 0.50114779, 44.6, 80, 35, 14],
    # ["Site 9", "n78_3.5G", 0.02641896, 0.50124621, 55, 180, 35, 14],
    # ["Site 9", "n78_3.5G", 0.02641896, 0.50124621, 27.4, 150, 10, 10],
    # ["Site 9", "n78_3.5G", 0.02649689, 0.50106049, 26.1, 330, 35, 10],
    # ["Site 10", "B1_2.1G", 0.02864553, 0.50034916, 58.5, 100, 20, 0],
    # ["Site 10", "B1_2.1G", 0.02864622, 0.50034647, 37.1, 310, 5, 0],
    # ["Site 10", "B1_2.1G", 0.02864656, 0.5003454, 27.4, 260, 10, 10],
    # ["Site 10", "B5_850M", 0.02864689, 0.50034648, 25.7, 10, 10, 10],
    # ["Site 10", "B5_850M", 0.02864723, 0.50034621, 61.9, 140, 30, 10],
    # ["Site 10", "B5_850M", 0.02864653, 0.50035024, 42.5, 220, 14, 0],
    # ["Site 10", "n78_3.5G", 0.02863938, 0.50036096, 35, 50, 15, 0],
    # ["Site 10", "n78_3.5G", 0.02863803, 0.50036096, 34, 250, 10, 0],
    # ["Site 10", "n78_3.5G", 0.02859398, 0.50040653, 50, 320, 35, 10],
    ["Site 11", "B1_2.1G", 0.02891497, 0.49864657, 61.9, 20, 40, 10],
    ["Site 11", "B1_2.1G", 0.02882359, 0.49880666, 22, 210, 25, 10],
    ["Site 11", "B1_2.1G", 0.02891363, 0.4986487, 40.2, 260, 15, 8],
    ["Site 11", "B5_850M", 0.02891363, 0.49864445, 14.4, 270, 25, 10],
    ["Site 11", "B5_850M", 0.02891363, 0.49864445, 14.4, 300, 25, 10],
    ["Site 11", "B5_850M", 0.02891363, 0.49864445, 14.4, 90, 25, 10],
    ["Site 11", "n78_3.5G", 0.02881917, 0.49881323, 48.9, 300, 10, 5],
    ["Site 11", "n78_3.5G", 0.02879895, 0.49880885, 44.6, 80, 35, 10],
    ["Site 11", "n78_3.5G", 0.02879895, 0.49880885, 44.6, 250, 35, 10] ########
    # ["Site 12", "B1_2.1G", 0.03036081, 0.4960921, 40, 320, 17, 0],
    # ["Site 12", "B1_2.1G", 0.030349, 0.4962768, 2, 177, 5, 0],
    # ["Site 12", "B1_2.1G", 0.03036081, 0.4960921, 57, 234, 13, 0],
    # ["Site 12", "B5_850M", 0.030349, 0.4962768, 16, 205, 6, 0],
    # ["Site 12", "B5_850M", 0.030349, 0.4962768, 77, 97, 27, 0],
    # ["Site 12", "n78_3.5G", 0.03030707, 0.49606628, 32.6, 100, 20, 0],
    # ["Site 12", "n78_3.5G", 0.03030842, 0.49606736, 63, 310, 8, 0],
    # ["Site 12", "n78_3.5G", 0.03030775, 0.49606682, 22, 200, 5, 0],
    # ["Site 13", "B1_2.1G", 0.03082819, 0.49700952, 18, 20, 20, 0],
    # ["Site 13", "B1_2.1G", 0.03095069, 0.49696626, 31, 280, 9, 0],
    # ["Site 13", "B5_850M", 0.03082858, 0.49700848, 30, 180, 12, 0],
    # ["Site 13", "n78_3.5G", 0.03082841, 0.49700858, 12, 180, 8, 0],
    # ["Site 13", "n78_3.5G", 0.03082884, 0.49700798, 21.8, 230, 4, 0],
    # ["Site 13", "n78_3.5G", 0.03082824, 0.49700939, 17, 288, 8, 0],
    # ["Site 14", "B1_2.1G", 0.0244, 0.50255944, 19, 100, 20, 0],
    # ["Site 14", "B1_2.1G", 0.02444663, 0.5026413, 46, 255, 6, 0],
    # ["Site 14", "B5_850M", 0.02444528, 0.50264183, 43.6, 125, 20, 0],
    # ["Site 14", "n78_3.5G", 0.02429972, 0.50255549, 18.8, 120, 19, 0],
    # ["Site 14", "n78_3.5G", 0.02448065, 0.50254546, 17, 10, 10, 0],
    # ["Site 14", "n78_3.5G", 0.02430113, 0.50254581, 48.5, 140, 10, 0],
    # ["Site 15", "B1_2.1G", 0.02547367, 0.4992456, 60.5, 135, 14, 0],
    # ["Site 15", "B1_2.1G", 0.02558633, 0.49922751, 77, 230, 23, 0],
    # ["Site 15", "B1_2.1G", 0.02558767, 0.49922858, 25, 40, 23, 0],
    # ["Site 15", "B5_850M", 0.02542291, 0.49921618, 57, 130, 0, 0],
    # ["Site 15", "B5_850M", 0.02540578, 0.4992024, 25, 152, 20, 0],
    # ["Site 15", "n78_3.5G", 0.02551793, 0.49920517, 53, 180, 20, 0],
    # ["Site 15", "n78_3.5G", 0.02551122, 0.49922113, 15, 150, 0, 0],
    # ["Site 15", "n78_3.5G", 0.02553134, 0.49920943, 16, 115, 4, 0],
    # ["Site 16", "B1_2.1G", 0.02396115, 0.50188501, 15, 185, 0, 0],
    # ["Site 16", "B5_850M", 0.02411651, 0.50218054, 21, 10, 5, 0],
    # ["Site 16", "n78_3.5G", 0.02427425, 0.50194353, 30, 30, 9, 0],
    # ["Site 16", "n78_3.5G", 0.02427189, 0.50194218, 44, 69, 45, 0],
    # ["Site 16", "n78_3.5G", 0.02396111, 0.50189012, 30.2, 355, 10, 0],
    # ["Site 17", "B1_2.1G", 0.02656246, 0.49529922, 24, 300, 10, 0],
    # ["Site 17", "B1_2.1G", 0.02656381, 0.49529815, 25, 190, 8, 0],
    # ["Site 17", "B5_850M", 0.0265638, 0.49529976, 24, 180, 10, 0],
    # ["Site 17", "n78_3.5G", 0.02642184, 0.49516297, 17, 329, 5, 0],
    # ["Site 17", "n78_3.5G", 0.02663545, 0.49517316, 24, 350, 3, 0],
    # ["Site 17", "n78_3.5G", 0.02656448, 0.49529977, 18, 260, 19, 0]
]


################ For PF Test
def lg_cell_conf ():

    msg = []

    timestamp = datetime.now().strftime("%M:%S")

    i = 0
    x = 0
    y = 0

    LGheader = ["Site", "Frequency", "Longitude", "Latitude", "Site Height", "Azimuth", "Tilt Angle (MDT_Mechanical Down-Tilt)", "Tilt Angle (EDT_Electrical Down-Tilt)"]
    
    for cell in LGdata:
    
        xy = change_geo_xy (cell[2], cell[3])

        x = xy [0]      ### right order - for Cacao Map
        y = xy [1]


        Tx_Power_value = 30.0

        #if cell[1] == "B5_850M":
        #    Tx_Power_value *= 2    # for GUI

        ## freq 
        freqColor = 1
        if cell[1] == "B5_850M":
            freqColor = 1
        elif cell[1] == "B1_2.1G":
            freqColor = 2
        else:
            freqColor = 3


        i += 1
        result = {
            'Cell_ID': i,
            'Cell_ID_Full': cell[0] + cell[1] + str (i), 
            'MeasTimestamp': timestamp,

            'X_Pos': x,
            'Y_Pos': y,
            'Z_Pos': cell[5],

            'State': 1,
            'Tx_Power': Tx_Power_value * 4, # + i, # For GUI
            'Freq_Band': freqColor 
        }

        msg.append(result)

        Num_Cell = i
        print ("X = 127 x = ", x, "y = ", y)

    return msg


def dummy_cell_conf ():

    global Num_Cell
    
    msg = []

    for i in range (Num_Cell):

        if i < int(Num_Cell/2):
            x = ETRI_X_Pos + 0.001 * i
            y = ETRI_Y_Pos #
        else:
            x = ETRI_X_Pos + 0.001 * (i-Num_Cell/4)
            y = ETRI_Y_Pos + 0.001 * 1

        data = {            
            "Cell_ID": i+1,
            "Cell_ID_Full": "Cell" + str (i+1),
            "Freq_Band": int (random.uniform(0, 10)),
            "State": int (random.uniform(0, 2)),     # 1: ON, 0: OFF
            "Tx_Power": 30.0 * 4,
            "X_Pos": x,
            "Y_Pos": y,
            "Z_Pos": int (random.uniform(0, 36) * 10)
        }
        
        msg.append (data)

    print ("Num_Cell = ", Num_Cell)

    return msg


###################################################################################################################
## 2. Performance Data menu
###################################################################################################################
# DL throughput
# UL throughput
# DL Sum
############################

########################################
@bp.route('/cell-metrics')
def cell_metrics ():

    results = []

    if VIAVI_MODE == "ON":

        results = read_cell_metrics ()    # Use mean or sum
 
    else:

        results = dummy_cell_metrics ()


  #  print (results)

    return results


#####################################################################
def read_cell_metrics_json2 ():
    
    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum

    global DL_rate
    global Power_rate
    global UE_rate

    results = []


    ## 1) Read data from VIAVI for GUI
    series = viavi_get_pm2 ('CellReports')   ## 


    ## 2) Copy data to Me
    list_count = 0

    ## accumulate 
    dlsum = 0
    Powersum = 0
    uesum = 0

    print ('DL_rate', DL_rate)

    for data in series:     # One value per cell data

        # GET as dict.
        name    = data['name']
        columns = data['columns']
        values  = data['values']

        cindex = columns.index ('mean_Viavi.NrPci')
        if cindex < 0:
            print ("ERROR: Data Input ERROR")
            
            return results
                

    # columns =  ['time', 'PEE.AvgPower', 'PEE.Energy', 'RRC.ConnMean', 
    #               'RRU.PrbTotDl', 'RRU.PrbTotUl']

        dli     = columns.index ('mean_RRU.PrbTotDl')
        Poweri  = columns.index ('mean_PEE.AvgPower')
        uei     = columns.index ('mean_RRC.ConnMean')

        
        for value in values:        # Accumulate all

            if value [cindex] != None:
                cid = value [cindex]-1

                if cid < Num_Cell:

                    dlsum += value [dli]        # Sum
                    DL_rate [cid] += value [dli] ## per cell

                    Powersum += value [Poweri]
                    Power_rate [cid] += value [Poweri]

                    uesum += value [uei]
                    UE_rate [cid] += value [uei]
                else:
                    print ('ERRRRRRRRR')
            else:
                print ('None')

        list_count += 1


        print (cid, value [dli], value [Poweri], value [uei])

    timestamp = datetime.now().strftime("%M:%S")


    print ("        PM: Num Cell Data count = ", list_count)
    print (f"{timestamp} dl sum = {dlsum} Power sum = {Powersum} ue sum = {uesum}")
    print ('DL_rate', DL_rate)

    DL_sum = dlsum
    Power_sum = Powersum
    UE_sum = uesum
    

    # 3) Send data
    for i in range (Num_Cell):

        data = {
            "Cell_ID": i + 1, # Cell ID starts from 1
            "DL_rate": DL_rate [i],
            "UL_rate": round (Power_rate [i], 2),
            "Num_UE": UE_rate [i],
            "Timestamp": timestamp
        }

        results.append (data)

        
    return results

####################################################################

#################################
def read_cell_metrics ():
    
    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum

    global DL_rate
    global Power_rate
    global UE_rate

    global DL_diff
    global Power_diff
    global UE_diff

    # 3) Send data
    results = []

    ## 1) Read data from VIAVI for GUI
    data = viavi_get_pm ('CellReports')   ## 

    if len (data) < 1:
        print ("=====> Please Check VIAVI is Running !!!")
        alarm_send ('VrApp', 'ERROR', 'VIAVI is not Running')
        return results
   
    timestamp = datetime.now().strftime("%M:%S")

    # GET as dict.

    name    = data['name']
    columns = data['columns']
    values  = data['values']


    ## 2) Get data by Index

    cindex = columns.index ('Viavi.NrPci')
    if cindex < 0:
        print ("ERROR: Data Input ERROR")
        alarm_send ('VrApp', 'WARNING', 'PM Data Input Error')
        
        return results


    # columns =  ['time', 'PEE.AvgPower', 'PEE.Energy', 'RRC.ConnMean', 
    #               'RRU.PrbTotDl', 'RRU.PrbTotUl']

    dli     = columns.index ('QosFlow.TotPdcpPduVolumeDl') # ('RRU.PrbTotDl')
    Poweri  = columns.index ('PEE.AvgPower')
    uei     = columns.index ('RRC.ConnMean')

    
    # 10.28 Error avoidance
    Error_CellID = 0
    Error_None = 0
    Error_All_Zero = 0

    
    # init to accumulate
    data_count = 0

    dlsum = 0
    powersum = 0
    uesum = 0

    DL_rate     = [0] * (Num_Cell)
    Power_rate  = [0] * (Num_Cell)
    UE_rate     = [0] * (Num_Cell)
    
    #   print (timestamp, 'DL_rate0', DL_rate)
    for value in values:        # Accumulate all

        if value [cindex] != None:      # Cell ID : to avoid "None" values
            cid = value [cindex]-1  # cell id = index - 1

            if cid < Num_Cell:      # to avoid overrunned value

                if value [dli] != None:
                    dlsum += value [dli]        # Sum                    
                    DL_rate [cid] += value [dli] ## per cell
                else:
                    Error_None += 1
                    DL_rate [0] = -1 


                if value [Poweri] != None:
                    powersum += value [Poweri]
                    Power_rate [cid] += value [Poweri]
                else:
                    Error_None += 1
                    Power_rate [0] = -1 


                if value [uei] != None:
                    uesum += value [uei]
                    UE_rate [cid] += value [uei]
                else:
                    Error_None += 1
                    UE_rate [0] = -1 

                data_count += 1
                    
            else:
                Error_CellID += 1
                
        else:
            Error_CellID += 1



    print ("PM: Num Data count = ", data_count)

    # Error avoidance
    if Error_CellID > 0:
        DL_rate [0] = -1
        Power_rate [0] = -1
        UE_rate [0] = -1
        DL_diff += Error_CellID/100

    if Error_None > 0:
        DL_rate [0] = -1
        Power_rate [0] = -1
        UE_rate [0] = -1
        
        Power_diff += Error_None/100

    if dlsum + powersum + uesum == 0:
        Error_All_Zero = 1
        UE_diff += Error_All_Zero/100


    if Error_CellID + Error_None + Error_All_Zero > 0:

        print ('None Count ------------------------->', timestamp, Error_CellID, Error_None, Error_All_Zero)

        # print (cid, value [dli], value [Poweri], value [uei])

#         filename = './graph_data.csv'
#         fw = open (filename, 'w')  # Write File
#         writer = csv.writer (fw)

#         for i in range (Num_Cell): 
#             writer.writerows (str (DL_rate [i]))
# #            writer.writerows (Power_rate [i])
#  #           writer.writerows (UE_rate [i])


#         fr = open (filename, 'r')  # Read File
#         reader = csv.reader (fr)
#      #   writer.writerows (reader)


    #   print (timestamp, 'DL_rate1', DL_rate)

    DL_sum = dlsum
    Power_sum = powersum
    UE_sum = uesum
    

    # 3) Send data
    results = []

    for i in range (Num_Cell): 

        data = {
            "Cell_ID": i + 1, # Cell ID starts from 1
            "DL_rate": round (DL_rate [i]/5, 2),
            "UL_rate": round (Power_rate [i]/5, 2),
            "Num_UE": int (UE_rate [i]/5),
            "Timestamp": timestamp
        }

        results.append (data)
    
    return results


#################################
def read_cell_metrics_sum ():
    
    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum

    global DL_rate
    global Power_rate
    global UE_rate

    results = []


    ## 1) Read data from VIAVI for GUI
    data = viavi_get_pm ('CellReports')   ## 

    # GET as dict.

    name    = data['name']
    columns = data['columns']
    values  = data['values']


    ## 2) Copy data to Me
    data_count = 0
   
    cindex = columns.index ('Viavi.NrPci')
    if cindex < 0:
        print ("ERROR: Data Input ERROR")
        alarm_send ('VrApp', 'WARNING', 'PM Data Input Error')
        
        return results


# columns =  ['time', 'PEE.AvgPower', 'PEE.Energy', 'RRC.ConnMean', 
#               'RRU.PrbTotDl', 'RRU.PrbTotUl']

    dli     = columns.index ('QosFlow.TotPdcpPduVolumeDl') # ('RRU.PrbTotDl')
    Poweri  = columns.index ('PEE.AvgPower')
    uei     = columns.index ('RRC.ConnMean')

    ## accumulate 
    dlsum = 0
    Powersum = 0
    uesum = 0
    
    for value in values:        # Accumulate all

        if value [cindex] != None:
            cid = value [cindex]-1

            if cid < Num_Cell:

        #        print (value [index])
                dlsum += value [dli]        # Sum
                DL_rate [cid] += value [dli] ## per cell

                Powersum += value [Poweri]
                Power_rate [cid] += value [Poweri]

                uesum += value [uei]
                UE_rate [cid] += value [uei]

            data_count += 1

#        print (cid, value [dli], value [Poweri], value [uei])

    timestamp = datetime.now().strftime("%M:%S")

    print ("PM: Num Data count = ", data_count)
    print (f"{timestamp} dl sum = {dlsum} Power sum = {Powersum} ue sum = {uesum}")
    print ('DL_rate', DL_rate)

    ###############################
    # Just Write
    DL_sum = dlsum
    Power_sum = Powersum
    UE_sum = uesum
    

    # 3) Send data
    for i in range (Num_Cell): 

        data = {
            "Cell_ID": i + 1, # Cell ID starts from 1
            "DL_rate": round (DL_rate [i]/5, 2),
            "UL_rate": round (Power_rate [i]/5, 2),
            "Num_UE": int (UE_rate [i]/5),
            "Timestamp": timestamp
        }

        results.append (data)
    
    return results


#################################
DB_URI = "/sba/influx/query?q="
DB_VIAVI_URL = VIAVI_URL + DB_URI
#VIAVI_READ_VALUE = 100
VIAVI_ADD = 5

def viavi_get_pm (point):   ## Send to OAM
    
    global Num_Cell
    global VIAVI_ADD

    #### VIAVI Error Aviodance ####
    if Num_Cell * VIAVI_ADD > 130:
        VIAVI_ADD = int (130 / Num_Cell)

    data_json = []

    ## 1) Read PM data
    if VIAVI_MODE == "ON":
        
        #target_url = DB_VIAVI_URL + "SELECT+mean(%2A)+FROM+CellReports+GROUP+BY+time(5s),%22Viavi.Cell.Name%22+LIMIT+1"
        target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+ORDER+BY+time+DESC+LIMIT+" + str (Num_Cell * VIAVI_ADD) # [VIAVI_READ_VALUE)
        
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+where+time+==+now()"
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+WHERE time > now() - 30s"
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+ORDER+BY+time+DESC+LIMIT+600"
        

        fdata_json = requests_get (target_url)


    if SIMUL_DEBUG == 'ON':   # Only for NI debug
        with open('./backend/CellReports.json', 'r') as file:
            fdata_json = json.load(file)


    if len (fdata_json) < 1:
        print ("=====================================================================================> Please Check VIAVI is Running !!!")
        alarm_send ('VrApp', 'ERROR', 'VIAVI is not Running')

        return data_json

    ## 2) Transform ManagedElement to cell Info.
    data_json = db_to_perfinfo (point, fdata_json)        
       
    ## 3) Send to rApp

    return data_json


def viavi_get_pm2 (point):   ## Send to OAM
    
    global Num_Cell

    data_json = []

    ## 1) Read PM data
    if VIAVI_MODE == "ON":
        
        target_url = DB_VIAVI_URL + "SELECT+mean(%2A)+FROM+CellReports+GROUP+BY+time(5s),%22Viavi.Cell.Name%22+LIMIT+1"
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+ORDER+BY+time+DESC+LIMIT+" + str (Num_Cell * VIAVI_ADD) # [VIAVI_READ_VALUE)
        
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+where+time+==+now()"
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+WHERE time > now() - 30s"
        #target_url = DB_VIAVI_URL + "SELECT+%2A+FROM+" + point + "+ORDER+BY+time+DESC+LIMIT+600"
        

        fdata_json = requests_get (target_url)


    if SIMUL_DEBUG == 'ON':   # Only for NI debug
        with open('./backend/CellReports.json', 'r') as file:
            fdata_json = json.load(file)


    ## 2) Transform ManagedElement to cell Info.
    data_json = db_to_perfinfo2 (point, fdata_json)        
       
    ## 3) Send to rApp

    return data_json


## VIAVI DB to JSON
def db_to_perfinfo2 (point, data): 

    data_json = []

    print ("db_to_perfinfo()", point)

#    print ('Keys = ',  data.keys ())
           
    # database output --> name, columns, values 
    results = data['results']
    item = results[0]
    statement_id = item['statement_id']
    series       = item['series']       # Please Check VIAVI is Running !!!

#     pm      = series[0]
#     name    = pm['name']
#     columns = pm['columns']
#     values  = pm['values']

#     print ("name = " , name)    # point
# #    print ("columns = " , columns) # parameters
#     print ("values len = " , len (values))

# #    data_json = json.dumps (series)

    return series


## VIAVI DB to JSON
def db_to_perfinfo (point, data): 

    data_json = []

    print ("db_to_perfinfo()", point)

#    print ('Keys = ',  data.keys ())
           
    # database output --> name, columns, values 
    results = data['results']           # Please Check VIAVI !!!
    item = results[0]
    statement_id = item['statement_id']
    series       = item['series']       # Please Check VIAVI !!!

    pm      = series[0]
#     name    = pm['name']
#     columns = pm['columns']
#     values  = pm['values']

#     print ("name = " , name)    # point
# #    print ("columns = " , columns) # parameters
#     print ("values len = " , len (values))

# #    data_json = json.dumps (series)

    return pm


def dummy_cell_metrics ():
    
    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum

    global Timestamp

    DL_sum = 0
    Power_sum = 0 
    UE_sum = 0

    DL_rate = [] 
    Power_rate = []
    Num_UE  = []    

    for i in range (Num_Cell):
        r1 = 100 #random.uniform(0, 200)
        r2 = 100 #random.uniform(0, 100)
        r3 = 1 #int (random.uniform(0, 10))

        DL_rate.append(r1)
        Power_rate.append(r2)
        Num_UE.append(r3)

        DL_sum += r1
        Power_sum += r2
        UE_sum += r3

    Timestamp = datetime.now().strftime("%M:%S")


    msg = []

    for i in range (Num_Cell):

        data = {
            "Cell_ID": i + 1,
            "DL_rate": DL_rate [i] + random.uniform(0, 10),
            "UL_rate": round (Power_rate [i] + random.uniform(0, 10), 2),
            "Num_UE": Num_UE [i],
            "Timestamp": Timestamp
        }
        
        msg.append (data)

    return msg


#####################################################

@bp.route('/dl-rate')
def DL_rate_graph ():

    global Num_Cell
    
    global DL_rate
    global sDL_rate

     ############################################
    # Power_rate와 sPower_rate 의 초기화를 한 번만 처리하도록 수정
    if 'DL_rate_initialized' not in globals():  # 초기화 여부를 확인
        DL_rate = [0] * Num_Cell
        sDL_rate = [0] * Num_Cell
        global DL_rate_initialized  # 변수 추가
        DL_rate_initialized = True
    ############################################
    data = {}
    
    if VIAVI_MODE == "ON":
    
        if DL_rate [0] == -1: # Error avoidance 
    
            for i in range (Num_Cell):
                data [str (i + 1) + " Throughput"] = round (sDL_rate [i], 2)    # saved data

        else:

            for i in range (Num_Cell):
                data [str (i + 1) + " Throughput"] = round (DL_rate [i], 2)
                sDL_rate [i] = DL_rate [i]

        #    DL_rate [i] = 0 # init

    else:
        
        for i in range (Num_Cell):

            r1 = random.uniform(0, 200)
            r1 = r1 + i

            data [str (i + 1) + " Throughput"] = r1
       #     DL_rate [i] = 0 # init


#    DL_rate     = [0] * (Num_Cell)

    return data


@bp.route('/ul-rate')
def Power_rate_graph ():

    global Num_Cell
    
    global Power_rate
    global sPower_rate 

     ############################################
    # Power_rate와 sPower_rate 의 초기화를 한 번만 처리하도록 수정
    if 'Power_rate_initialized' not in globals():  # 초기화 여부를 확인
        Power_rate = [0] * Num_Cell
        sPower_rate = [0] * Num_Cell
        global Power_rate_initialized  # 변수 추가
        Power_rate_initialized = True
    ############################################

    data = {}

    if VIAVI_MODE == "ON":
        
        if Power_rate [0] == -1:
     
            for i in range (Num_Cell):
                data [str (i + 1) + " Power"] = round (sPower_rate [i], 2) # saved data

        else:

            for i in range (Num_Cell):
                data [str (i + 1) + " Power"] = round (Power_rate [i], 2)
                sPower_rate [i] = Power_rate [i]
            
    #        Power_rate [i] = 0 # init

    else:

        for i in range (Num_Cell):

            r1 = random.uniform(0, 100)
#            r1 = 100 + i  # 

            data [str (i + 1) + " Power"]= r1

#    Power_rate  = [0] * (Num_Cell)

    return data


@bp.route('/num-ue')
def Num_UE_graph ():

    global Num_Cell
    
    global UE_rate
    global sUE_rate

     ############################################
    # UE_rate와 sUE_rate의 초기화를 한 번만 처리하도록 수정
    if 'UE_rate_initialized' not in globals():  # 초기화 여부를 확인
        UE_rate = [0] * Num_Cell
        sUE_rate = [0] * Num_Cell
        global UE_rate_initialized  # 변수 추가
        UE_rate_initialized = True
    ############################################

    data = {}

    if VIAVI_MODE == "ON":

        if UE_rate [0] == -1:
            
            for i in range (Num_Cell):
                data [str (i + 1) + " Num UE"] = sUE_rate [i] # saved data

        else:

            for i in range (Num_Cell):
                data [str (i + 1) + " Num UE"] = UE_rate [i]
                sUE_rate [i] = UE_rate [i]

    #        UE_rate [i] = 0
     
    else:

        for i in range (Num_Cell):

            r1 = random.uniform(0, 10)

            data [str (i + 1) + " Num UE"] = int (r1)

#    UE_rate     = [0] * (Num_Cell)

    return data



###################################################################################################################

@bp.route('/cell-sum')
def cell_sum ():

    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum


    Timestamp = datetime.now().strftime("%M:%S")
   
    if VIAVI_MODE == "ON":

        data = {
            "Num_Cell": Num_Cell,
            "DL_rate": round (DL_sum/5, 0),
            "UL_rate": round (Power_sum/5, 2),
            "Num_UE": int (UE_sum/5),
            "Timestamp": Timestamp
        }

    else:

        data = {  
            "Num_Cell": Num_Cell,
            "DL_rate": 183,  #DL_sum,
            "UL_rate": 2344.02,
            "Num_UE": 17,    
            "Timestamp": Timestamp
        }

    return data


################################################################################################
## 2. ERIC Menu
################################################################################################

@bp.route('/ric-info')
def eric_info ():

    block = []

    if VIAVI_Direct_Mode == 'ON':
        block.append (check_oam ("SMO/OAM", "VIAVI TeraVM RIC Simulator"))
    else:
    ## Non-RT RIC Framework block check
        block.append (check_oam ("SMO/OAM", "Active SMOs"))
    block.append (check_ross ("Non-RT RIC", "Active Framework Blocks"))
    block.append (check_rapp ("Non-RT RIC rApp", "Active rApps"))
    block.append (check_cell ("E2 Nodes", "Active Cells"))


    return block


# State = ["OFF", "ON", "WARNING", "ERROR"]

def check_oam (name, desc):

    global Num_SMO


    if VIAVI_Direct_Mode == 'ON':
        burl = VIAVI_URL
    
    else:
        burl = OAM_REST_URL

    state = "OFF"
    Num_SMO = 0
     
    try:
        response = requests.get (burl, timeout=1) # RAW data use for error avoidance

        if response.status_code < 500:
            state = "ON"
            Num_SMO = 1

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass


    data = {
        "name": name,
        "state": state,
        "description": desc,
        "value": Num_SMO
    }

    return data


def check_ross (name, desc):

    if Num_ROSS == 0:    # Num ROSS = 4 Fix
        state = "OFF"
    elif Num_ROSS < 4:
        state = "WARNING"
    else:
        state = "ON"

    # state = "ON"

    data = {
        "name": name,
        "state": state,
        "description": desc,
        "value": Num_ROSS
    }

    return data


def check_rapp (name, desc):

    ids = Lib_sme_bk.rApp_Catalogue() # Get ID lists
    Num_rApp = len (ids) 

    if VIAVI_MODE == "OFF":
        Num_rApp = 3

    if Num_rApp == 0:
        state = "OFF"
    else:
        state = "ON"

    data = {
        "name": name,
        "state": state,
        "description": desc,
        "value": Num_rApp
    }

    return data


def check_cell (name, desc):

    if Num_Cell == 0:
        state = "OFF"
    else:
        state = "ON"

    data = {
        "name": name,
        "state": state,
        "description": desc,
        "value": Num_Cell
    }

    return data


################################
@bp.route('/value3')
def value3 ():

    global Num_Cell

    global DL_sum
    global Power_sum 
    global UE_sum

    block = []

    block.append (check_value ("Throughput", "Average Data Rate (Mbps)", round (DL_sum/5, 2), round (DL_diff, 2)))
    block.append (check_value ("Power", "Average Cell Power (kWatt)", round ((Power_sum/1000)/5, 3), round (Power_diff, 2)))
    block.append (check_value ("Active UE", "Average Connected UE", round (UE_sum/5, 2), round (UE_diff, 2)))

    return block


def check_value (name, desc, value, diff):

    data = {
        "name": name,
        "value": value, #int (random.uniform(0, 20)),
        "difference": diff, #round (random.uniform(-10, +10), 2),
        "description": desc
    }

    return data



################################
## 1. Overview
@bp.route('/overview')
def overview ():

    data = {
        "name": "overview",
        "rappSchema": {
            "rAppId": "overview id",
            "ServiceType": "service type"
        },
        "description": "TEST"
    }

    return data

################################
## 91. alarm

Alarm_List = []

@bp.route('/alarm')
def alarm ():

    global Alarm_List

    result = []

    # name = ['OOMB', 'ODMB', 'OSMB', 'OAPB', 'ESrApp']

    # data = {
    #     "name": "OOMB",  #name [int (random.uniform(0, 4))],
    #     "level": "INFO",
    #     "desc": "PlugFest Test Case1",
    #     "text": "OOMB description"
    # }

    # result.append (data)


    count = 0
    
    for item in Alarm_List:
        data = item

        result.append (data)
        
        count += 1

        if count > 5: 
            Alarm_List.clear ()


    return result


@bp.route('/alarmtest/<block>')
def alarmtest (block):

    result = []

    result = alarm_send (block, 'INFO', 'Alarm Test')

    return result


def alarm_send (name, level, text):

    global Alarm_List

    data = {
        "name": name,
        "level": level,
        "desc": text
#        "text": text
    }

    Alarm_List.append (data)

    return Alarm_List


################################################################################################################################
# Vertical Menus
################################################################################################################################
################################################################################################################################
## 2. Non-RT RIC Menu
################################
## rApps Menu           ## Show all rApps

@bp.route('/rapp')    ## use OSC rApp Catalogue-enhanced
def rApps ():

    global Num_rApp

    rapps = []

    ids = rApp_Catalogue()
    print("rapp_catalogue")
    
    for id in ids:
        data = rApp_Catalogue_Enhanced_get(id)
        data_trans = real_rapp (RAPP_ES_URL, data)
        rapps.append (data_trans)

    Num_rApp = len (ids)

    if VIAVI_MODE == "OFF":
        print("rapp_catalogue")

        rapps.append (dummy_rapp (RAPP_ES_URL, "ESrApp1"))
        rapps.append (dummy_rapp (RAPP_ES_URL, "ESrApp2"))
        rapps.append (dummy_rapp (RAPP_ES_URL, "ESrApp1"))

        Num_rApp = 3


    return rapps
    

def real_rapp (burl, standr):

    print (standr)
    print (standr ['rappSchema'])
    rappSchema = standr ['rappSchema']

    data = {
        "name": standr ['name'],
        "rappSchema": {
            "rAppId": rappSchema ['rAppId'],
            "version": "1.0.0",
            "vendor": "ETRI",                
            "ServiceType": rappSchema ['ServiceType']
        },
        "description": standr ['description'],
        "state": "ON",
        "open": burl
    }

    return data


def dummy_rapp (burl, bname):

    data = {
        "name": bname,
        "rappSchema": {
            "rAppId": bname,
            "version": "v1.0.0",
            "vendor": "ETRI",                
            "ServiceType": RAPP_SERVICE_TYPE
        },
        "description": "TEST",
        "state": "ON",
        "open": burl
    }

    return data


################################################################################################
## Non-RT RIC Framework Menu           ## Show all Framework blocks

@bp.route('/rblock')
def rblocks ():
    global Num_ROSS

    state_count = 0

    rbs = []
    ## Non-RT RIC Framework block check
    # 1. OOMB
    result = real_rblock (OOMB_URL, "OOMB", "RAN OAM-related Service", "O-RAN RAN OAM-related Service Block")
    rbs.append (result)

    if result ['state'] == 'ON':
        state_count += 1

    # 2. ODMB
    result = real_rblock (ODMB_URL, "ODMB", "Data Management and Exposure Service", "O-RAN Data Management and Exposure Block")
    rbs.append (result)

    if result ['state'] == 'ON':
        state_count += 1
        
    # 3. OSMB
    result = osc_rblock (OSMB_URL, "OSMB", "Service Management & Exposure Service", "O-RAN Service Management & Exposure Block")
    rbs.append (result)

    if result ['state'] == 'ON':
        state_count += 1

    # 4. OAPB
    result = pms_rblock (OAPB_URL, "OAPB", "A1 Policy Management Service", "O-RAN A1 Policy Management Block")
    rbs.append (result)

    if result ['state'] == 'ON':
        state_count += 1

#    rbs.append (dummy_rblock (OAPB_URL, "OAPB", "A1 Policy Management Service", "O-RAN A1 Policy Management Block"))

    Num_ROSS = state_count

    return rbs


def osc_rblock (burl, bid, service, desc):

    state = "OFF"

    try:
        response = requests.get (burl, timeout=1) # RAW data use for error avoidance

        if response.status_code < 500:
            state = "ON"

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass

    data = {
        "name": bid,
        "id": bid,
        "version": "1.1.0",
        "vendor": "OSC",
        "ServiceType": service,
        
        "state": state,
        "description": desc,
        "open": burl
    }

    print (bid, state)

    return data


def pms_rblock (burl, bid, service, desc):  ### 1226 Append

    state = "OFF"

    target_url = burl + '/a1-policy/v2/'

    try:
        response = requests.get (burl, timeout=1) # RAW data use for error avoidance

        if response.status_code < 500:
            state = "ON"

    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass

    data = {
        "name": bid,
        "id": bid,
        "version": "2.6.0",
        "vendor": "OSC",
        "ServiceType": service,
        
        "state": state,
        "description": desc,
        "open": burl
    }

    print (bid, state)

    return data


def real_rblock (burl, bid, service, desc):

    data = requests_get (burl)

    print (burl, data)
    if len (data) > 0:
        state = "ON"

    else:
        state = "OFF"

    data = {
        "name": bid,
        "id": bid,
        "version": "1.0.0",
        "vendor": "ETRI",
        "ServiceType": service,
        
        "state": state,
        "description": desc,
        "open": RAPP_URL + '/run/odmb'
    }

    print (bid, state)

    return data


def dummy_rblock (burl, bname, service, desc):

    state = "OFF"

    data = {
        "name": bname,
        "id": bname,
        "version": "1.0.0",
        "vendor": "OSC",
        "ServiceType": service,
        
        "state": state,
        "description": desc,
        "open": burl
    }

    print (bname, state)


    return data


################################################################
## 3. Near-RT RIC Menu
################################
## xApps Menu           ## Show all xApps
@bp.route('/xapp')    ## Pseudo code Only
def xApps ():

    block = []

    ## Non-RT RIC Framework block check
    block.append (check_xblock (OSMB_URL, "xSMB"))
    block.append (check_xblock (ODMB_URL, "xDMB"))
    block.append (check_xblock (OAPB_URL, "xAPB"))


    return block


################################
## Near-RT RIC Platform Menu           ## Show all Platform blocks
@bp.route('/xblock')
def xblocks ():

    block = []

    ## Non-RT RIC Framework block check
    block.append (check_xblock (OSMB_URL, "ESMB"))
    block.append (check_xblock (ODMB_URL, "EDMB"))
    block.append (check_xblock (OAPB_URL, "EAPB"))
    block.append (check_xblock (OOMB_URL, "EOMB"))


    return block


def check_xblock (burl, bname):

    data = []

    if SIMUL_XMODE == "OFF":

        ## 1) heartbeat
        target_url = burl

        data.append (requests_get (target_url))
    
    else:

        data = {
            "name": bname,
            "id": bname,
            "version": "v1.0.0",
            "vendor": "ETRI",
            "ServiceType": burl,
            
            "state": "ON",
            "description": "TEST",
            "open": burl
        }

        return data 


################################################################################################################################
## E2 Node : ManagedElement
@bp.route('/e2node')
def e2node ():

    if VIAVI_MODE == 'ON':

        ## 1) Read NI from VIAVI Direct 
        target_url = VIAVI_URL + "/O1/CM/" + "ManagedElement"

        data = requests.get (target_url)

    else: 

        with open("./backend/viavi_ni.json", 'r') as file:
            data = json.load(file)


    middle = me_to_items (data)
    
    result = item_to_react (middle)


    return result


@bp.route('/e2nodet')
def e2nodetest ():

    print ('e2nodetest ()')

    if VIAVI_MODE == 'ON':

        ## 1) Read NI from VIAVI Direct 
        target_url = VIAVI_URL + "/O1/CM/" + "ManagedElement"

        data = requests_get (target_url)

    else:

        with open("./backend/viavi_ni.json", 'r') as file:
            data = json.load(file)
    
    
    middle = me_to_items (data)
    

    return middle


###############################################
## Transform ManagedElement to cell Info. 
def me_to_items (data):

    result = {}

    print ('type = ', type (data))

    if isinstance (data, dict):
        me = data
    else:
        me = data [0]

    print ('Keys = ', me.keys ())

#    print ("ManagedElement = ----------------> ") 
    result ['id'] = me ["id"]
    result ['ManagedElement'] = me["objectInstance"]

#    value = int (me["objectInstance"].split("=")[1])

#    print ("GnbDuFunction = ----------------> ") 
 
    me1 = []
   
    for du in me ["GnbDuFunction"]:

        md1 = {}
        md1 ['id'] = du["id"]
        md1 ['objectInstance'] = du["objectInstance"]


        me2 = []

        for duc in du["NrSectorCarrier-Multiple"]:

            md2 = {}
            md2 ['id'] = duc["id"]
            md2 ['objectInstance'] = duc["objectInstance"]
           
            attributes = duc["attributes"]  # skip 1 level for simplicity
            md2 ['configuredMaxTxPower'] = attributes["configuredMaxTxPower"]

            me2.append (md2)

        md1 ['NrSectorCarrier'] = me2

        me1.append (md1)

    result ['GnbDuFunction'] = me1


#    print ("GnbCuCpFunction = ----------------> ")
    
    meorg = me ["GnbCuCpFunction"]

    me2  = []

    meroot = meorg [0]      # Only 1 CUCP 

#    inst = meroot["objectInstance"]

    for cpc in meroot ["NrCellCu"]:
        ced = {}
        ced ['id'] = cpc["id"]
        ced ['objectInstance'] = cpc["objectInstance"]
        
        ces = cpc["CESManagementFunction"]
        attributes = ces ['attributes']
        ced ['attributes'] = attributes

        me2.append (ced)

    result ['GnbCuCpFunction'] = me2



#    print ("GnbCuUpFunction = ---------------->")
    meorg = me ["GnbCuUpFunction"]

    me3  = []

    meroot = meorg [0]      # Only 1 CUCP 
    
    cud = {}
    cud ['id'] = meroot ["id"]
    cud ['objectInstance'] = meroot ["objectInstance"]

    me3.append (cud)

    result ['GnbCuUpFunction'] = me3


    return result


#########################
def flow_middle (id, x, y):
    nd = {}

    nd = {
        'id' : id,
        'data': { 'label': id },
        'position': { 'x': x, 'y': y },
        'sourcePosition': 'Position.Right',  # 소스 연결점은 오른쪽 (출발점)
        'targetPosition': 'Position.Left',   # 타겟 연결점은 왼쪽 (도착점)
        'type': 'customNodeType',
    }

    return nd

def flow_end (id, x, y, value):

    data =  {
        'id': id,
        'data': { 'label': id, 'value': value},
        'position': { 'x': x, 'y': y },
        'targetPosition': 'Position.Left',   # 타겟 연결점은 왼쪽 (도착점)
        'type': 'valueNodeType' # '받는' 노드 타입
    }

    return data


def flow_txpower (id, x, y, value):

    data =  {
        'id': id,
        'data': { 'label': id, 'value': value},
        'position': { 'x': x, 'y': y },
        'targetPosition': 'Position.Left',   # 타겟 연결점은 왼쪽 (도착점)
        'type': 'valueNodeType' # '받는' 노드 타입
    }

    return data

def flow_energysaving (id, x, y, value):

    data = {
        'id': id,
        'data': { 'label': id,'state': value }, # false 값을 넘겨준다. (사용자 지정 데이터)
        'position':  { 'x': x, 'y': y },
        'targetPosition': 'Position.Left',
        'type': 'stateNodeType' # 사용자 지정 상태 표시 타입
    }

    return data


################################
def line_middle (id, src, dest):

    data = { 
        'id': id, 
        'source': src, 
        'target': dest,
        'type': 'step' ,
        'animated': True #  // 선 애니메이션 효과
    }

    return data


#########################################
## transform ManagedElement to React Flow format
def item_to_react (me):

    result  = {}

    nodes = []
    edges = []

    print (me.keys())

    # 0) Root ################################ Root
    x = 0
    y = 0
    xincr = 200
    yincr = 50


    noded = {}

    # me ['ManagedElement']
    noded ['id']        = 'ManagedElement'
    noded ['data']      = { 'label': 'ManagedElement', 'type': 'input' }
    noded ['position']  = { 'x': x, 'y': y } 
    noded ['sourcePosition'] = 'Position.Right'  # 소스 연결점은 오른쪽 (출발점)
       #     // targetPosition: Position.Left,   // 타겟 연결점은 왼쪽 (도착점)
    noded ['type']      = 'customNodeType'

    nodes.append (noded)

   
    # 1) 1st Lane ################################ Mandatory
    x = 200

    nd = flow_middle ('GnbDuFunction', x, y)
    nodes.append (nd)

    ed = line_middle ('0-1', 'ManagedElement', 'GnbDuFunction')
    edges.append (ed)


    # 2) 2nd Lane ################################ Main
    x = 400 # xincr  # x = 400
    y = 0

    for du in me ["GnbDuFunction"]:

        #md1 ['objectInstance'] = du["objectInstance"]

        idm = 'GnbDuFunction-' + du["id"]
        nd = flow_middle (idm, x, y)
        nodes.append (nd)

        idx = '1-' + du["id"]
        ed = line_middle (idx, 'GnbDuFunction', idm)
        edges.append (ed)

    #    y += yincr

        # 3) Final Lane #####################################
        for duc in du["NrSectorCarrier"]:

     #       attributes = duc["attributes"]  # skip 1 level for simplicity
            value = duc["configuredMaxTxPower"]

            id = duc["id"] + '-MaxTxPower'
            nd = flow_txpower (id, x + xincr, y, value)
            nodes.append (nd)

            idx2 = idx + '-' + duc["id"]
            ed = line_middle (idx2, idm, id)
            edges.append (ed)

            y += yincr


    # 1) 1st Lane ################################ Mandatory
    x = 200

    nd = flow_middle ('GnbCuCpFunction', x, y)
    nodes.append (nd)

    ed = line_middle ('0-2', 'ManagedElement', 'GnbCuCpFunction')
    edges.append (ed)


    ############################################
    x = 400 # xincr  # x = 400

    for du in me ["GnbCuCpFunction"]:

        #md1 ['objectInstance'] = du["objectInstance"]

        idm = 'GnbCuCpFunction-' + du["id"]
        nd = flow_middle (idm, x, y)
        nodes.append (nd)

        idx = '2-' + du["id"]
        ed = line_middle (idx, 'GnbCuCpFunction', idm)
        edges.append (ed)

#        y += yincr

  
        #meorg = me ["GnbCuCpFunction"]
        #meroot = meorg [0]      # Only 1 CUCP 

        # 3) Final Lane #####################################
           
        attributes = du ['attributes']
        state = attributes ['energySavingState']

        if state == 'isEnergySaving': 
            ise = "ON"      ## Energy Saving ON , Tx Power ON
        else:
            ise = "OFF"

        id = du["id"] + '-isEnergySaving' 
        nd = flow_energysaving (id, x + xincr, y, ise)
        nodes.append (nd)

        idx2 = idx + '-' + du["id"]
        ed = line_middle (idx2, idm, id)
        edges.append (ed)

        y += yincr


    # 1) 1st Lane ################################ Mandatory
    x = 200

    nd = flow_middle ('GnbCuUpFunction', x, y)
    nodes.append (nd)

    ed = line_middle ('0-3', 'ManagedElement', 'GnbCuUpFunction')
    edges.append (ed)


    ############################################
    x = 400 # xincr  # x = 400

    for du in me ["GnbCuUpFunction"]:

        value = du["id"] #du["objectInstance"]

        idm = 'GnbCuUpFunction-' + du["id"]
        nd = flow_end (idm, x, y, value)
        nodes.append (nd)

        idx = '3-' + du["id"]
        ed = line_middle (idx, 'GnbCuUpFunction', idm)
        edges.append (ed)

        y += yincr


    result ['Node'] = nodes

    result ['Edge'] = edges


    return result


###############################
@bp.route ('/e2perf/<cellId>', methods = ['GET'])
def e2perf (cellId):

    data = []

    value1 = [ 1,2,3,4,5,6,6,7,2,5]
    value2 = [ 6,7,2,5,1,2,3,4,5,6]
    value3 = [ 1,0,1,0,0,1,0,1,1,1]
    
    # 1) ES Prediction
    #    for i in range (Num_Cell):
    # dbwrite_cell_value ('ES_Cell_Pred', i, 0.1)  # float, 5  ## ES_yp 
    # dbwrite_cell_value ('ES_Cell_In', i, 0.1)    # float, 4,  ## ES_x_in
    # dbwrite_cell_value ('Viavi.isEnergySaving', i, 0)  # float, 5  ## ES_yp     
    
    # 2) 
    
    
    
    # 3)
    data = {        
        'cellid': cellId,
        'name1': 'ES_Cell_Pred',        
        'value1': value1,
        'name2': 'ES_Cell_In',
        'value2': value2,        
        'name3': 'Viavi.isEnergySaving',
        'value3': value3,        
    }

    return data



###################################
## rApp Algorithm caller
SCHEDULE_PERIOD = 30     # sec.

def rApp_algorithm():

    schedule.every(SCHEDULE_PERIOD).seconds.do(Data_Update) # SIMUL every 5 sec.

    while True:
        schedule.run_pending()
        time.sleep(1)



###################################
## ES algorithm loop module 
def Data_Update ():

    global Num_Cell

    global DL_rate
    global Power_rate
    global UE_rate

    print ("vrapp is running ", Num_Cell)

    ## 1) init value
    #     
 #   DL_rate     = [0] * (Num_Cell)
 #   Power_rate  = [0] * (Num_Cell)
 #   UE_rate     = [0] * (Num_Cell)


    ## 2) Periodically update
    rblocks ()


############################################
# Remote execution 

@bp.route ('/rund', methods=['GET','POST'])
def run_shell ():

    print ("        POST /run.sh")

    try:
        result = subprocess.run(['./run.sh'], capture_output=True, text=True) 

        if result.returncode == 0:             
            return jsonify({"status": "success", "output": result.stdout}), 200
        else:
            return jsonify({"status": "error", "output": result.stderr}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@bp.route ('/run/<block>', methods=['GET','POST'])
def run_docker (block):

    print ("        POST /run.sh", block)

    execfile = './run-' + block + '.sh'

    try:
        result = subprocess.run([execfile], capture_output=True, text=True) 

        if result.returncode == 0:             
            return jsonify({"status": "success", "output": result.stdout}), 200
        else:
            return jsonify({"status": "error", "output": result.stderr}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

####################################################

def eprint (level, desc):
    print (VENDOR_NAME, BLOCK_NAME, LOG_LEVEL [level], desc)


def eeprint (level, desc, value):
    print (VENDOR_NAME, BLOCK_NAME, LOG_LEVEL [level], desc, value)


#######################################################
#### [1] Starting Point

