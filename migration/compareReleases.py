

import json
import csv
import os
import subprocess as s
from pathlib import Path
import copy
from typing import List


"""
Export rules controls and frameworks to files in json format
"""
currDir = os.path.abspath(os.getcwd())
old_releaseDir = currDir + "/release/"
new_releaseDir = currDir + "/1-newDesign/release/"

new_control_ids_mapping = {}
with open(currDir + "/1-newDesign/newids.json", "r") as f:
    new_control_ids_mapping= json.load(f)


def compare_dicts_keys(a: dict, b:dict):
    missing_keys = []
    for key in a.keys():
        if key not in b.keys():
            missing_keys.append(key)
   
    if len(missing_keys):
        print(a.keys(), b.keys())
        raise Exception(f"missing keys: {missing_keys}")    
    
   
def compare_lists(a: dict, b:dict):
    a = sorted(a, key=lambda d: d['name']) 
    b = sorted(b, key=lambda d: d['name']) 

    if len(a) != len(b):
        raise Exception(f"list length doesnt match, {len(a)} vs {len(b)}")
    
    
    for i in range(0, len(a)):
        compare_dicts_keys(a[i], b[i])


def compare_controls_rules():
    controls_rules = "ControlID_RuleName.csv"
    old_list = {}
    new_list = {}
    with open(old_releaseDir + "/" + controls_rules, 'r', encoding='UTF8', newline='') as f1:
        old = csv.reader(f1, delimiter=",")
        for row in old:
            if row[0] != "ControlID":
                if row[0] in new_control_ids_mapping.keys():
                    row[0] = new_control_ids_mapping[row[0]]
                old_list[row[0]] = row[1]
        
    with open(new_releaseDir + "/" + controls_rules, 'r', encoding='UTF8', newline='') as f2:
        new = csv.reader(f2, delimiter=",")
        for row in new:
            if row[0] != "ControlID":
                new_list[row[0]] = row[1]
            
    for key in old_list.keys():
        if old_list[key] != new_list[key]:
            raise Exception(f"ControlID_RuleName doesn't match, see old control id {key}")
    
    print(f"comparing 'ControlID_RuleName.csv' success")
        
def compare_frameworks_values(a: dict, b:dict):
    controls_a = {}
    controls_b = {}
    for c in a["controls"]:
        controls_a[c["controlID"]] = copy.deepcopy(c)
    
    for c in b["controls"]:
        controls_b[c["controlID"]] = copy.deepcopy(c)
    
    for controlID in controls_a.keys():
        # new_controlID = new_control_ids_mapping[controlID] if controlID in new_control_ids_mapping.keys() else controlID
        compare_dicts_keys(controls_a[controlID], controls_b[controlID])  
 
        for key1 in controls_a[controlID].keys():
            if controls_a[controlID][key1] != controls_b[controlID][key1]:
                raise Exception(f"Failed to compare {controlID}/{key1}. values:{controls_a[controlID][key1]}, {controls_b[controlID][key1]}")
                    
        # for key1 in controls_a[controlID].keys():
        #     if key1 == "id" or key1 == "controlID":
        #         if controls_b[new_controlID][key1] != new_controlID:
        #             raise Exception(f"Failed to compare {controlID}/{key1}. values:{controls_a[controlID][key1]}, {controls_b[new_controlID][key1]}")
        #         else:
        #             continue
        #     elif key1 == "name":
        #         if controls_b[new_controlID][key1].replace(controlID + " ", "") != controls_a[controlID][key1]:
        #             raise Exception(f"Failed to compare {controlID}/{key1}. values:{controls_a[controlID][key1]}, {controls_b[new_controlID][key1]}")
        #     else:
        #         if controls_a[controlID][key1] != controls_b[new_controlID][key1]:
        #             raise Exception(f"Failed to compare {controlID}/{key1}. values:{controls_a[controlID][key1]}, {controls_b[new_controlID][key1]}")
               

def convert_framework_old_to_new(framework: dict) -> dict:
    for control in framework["controls"]:
        controlID = control["controlID"]
        new_controlID = new_control_ids_mapping[controlID] if controlID in new_control_ids_mapping.keys() else controlID
        if controlID != new_controlID:
            control["name"] = controlID + " " + control["name"]
            control["id"] = new_controlID
            control["controlID"] = new_controlID
    
    return framework
        

def compare_frameworks():
    frameworks = ["allcontrols.json", "armobest.json", "cis.json", "devopsbest.json", "mitre.json", "nsa.json"]
    
    for filename in frameworks:
        with open(old_releaseDir + "/" + filename, "r") as f:
            old = json.load(f)
            
        with open(new_releaseDir + "/" + filename, "r") as f:
            new = json.load(f)
    
        try:
            compare_dicts_keys(old, new)
            compare_frameworks_values(convert_framework_old_to_new(old), new)
        except Exception as e:
            print(f"Failed to compare {filename}: {e}")
            exit(0)
        print(f"comparing {filename} success")
     

def compare_controls():
    with open(old_releaseDir + "/controls.json", "r") as f:
        old = json.load(f)
            
    with open(new_releaseDir + "/controls.json", "r") as f:
        new = json.load(f)
        
    compare_lists(old, new)    
    print(f"comparing 'controls.json' success")

 
def compare_frameworks_list():
    filename = "frameworks.json"
    
    old_dict = {}
    new_dict = {}
    with open(old_releaseDir + "/" + filename, "r") as f:
        old = json.load(f)
        for item in old:
            old_dict[item["name"]] = item
            
    with open(new_releaseDir + "/" + filename, "r") as f:
        new = json.load(f)
        for item in new:
            new_dict[item["name"]] = item

    for key in old_dict:
        try:
            compare_dicts_keys(old_dict[key], new_dict[key])
            compare_frameworks_values(old_dict[key], new_dict[key])
        except Exception as e:
            print(f"Failed to compare {filename}, framework: {key}: {e}")
            raise Exception(e)
        print(f"comparing {filename}: {key} success")
    


def compare_frameworks_controls():
    frameworks_controls = "FWName_CID_CName.csv"
    old_list = {}
    new_list = {}
    with open(old_releaseDir + "/" + frameworks_controls, 'r', encoding='UTF8', newline='') as f1:
        old = csv.reader(f1, delimiter=",")
        for row in old:
            if row[1] != "ControlID":
                if row[1] in new_control_ids_mapping.keys():
                    
                    #matching id and name of control for easier comparison
                    row[2] = row[1] + " " + row[2]
                    row[1] = new_control_ids_mapping[row[1]]
                old_list[(row[0], row[1])] = row[2]
        
    with open(new_releaseDir + "/" + frameworks_controls, 'r', encoding='UTF8', newline='') as f2:
        new = csv.reader(f2, delimiter=",")
        for row in new:
            if row[1] != "ControlID":
                new_list[(row[0], row[1])] = row[2]

    for key in old_list.keys():
        if old_list[key] != new_list[key]:
            print( old_list[key], new_list[key])
            raise Exception(f"{frameworks_controls} doesn't match, see old control id {key}")
    
    print(f"comparing '{frameworks_controls}' success")
    

if __name__ == '__main__':
    
    oldFiles = os.listdir(old_releaseDir)
    newFiles = os.listdir(new_releaseDir)
    
    assert len(oldFiles) == len(newFiles)
    
    frameworks = ["allcontrols.json", "armobest.json", "cis.json", "devopsbest.json", "mitre.json", "nsa.json"]
    controls = "controls.json"
    rules = "rules.json"
    controls_rules = "ControlID_RuleName.csv"
    
    
    compare_frameworks()
    compare_controls()
    compare_controls_rules()
    compare_frameworks_list()
    compare_frameworks_controls()
            
                
            
    
    

