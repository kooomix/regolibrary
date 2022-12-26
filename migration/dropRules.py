
from helpers import (load_controls, 
                     export_json, 
                     convert_dotted_section_to_int, 
                     load_frameworks)

import copy


def build_activeControls(framework: dict, controls: dict) -> dict:
    active_controls = []
    
    for control_name in framework["controlsNames"]:
        patch = {}
        if framework["name"].lower() == "cis":
            framework_control_name =  controls[control_name]["old_controlID"] + " " + control_name
        else:
            framework_control_name =  control_name
        patch["name"] = framework_control_name
        
        
        if "references" in controls[control_name]:
            patch["references"] = controls[control_name]["references"]


        active_controls.append({"controlID": controls[control_name]["controlID"],
                                "patch": patch})
        
    active_controls = sorted(active_controls, key=lambda d: d['controlID'])
    assert len(framework["controlsNames"]) == len(active_controls)    
    return active_controls

def generate_control_id_from_int(num: int) -> str:
    if num < 10:
        return "C-000" + str(num)

    if num < 100:
        return "C-00" + str(num)
    
    if num < 1000:
        return "C-0" + str(num)
    
    if num < 10000:
        return "C-" + str(num)
    raise Exception(f"num {num} must be below 10000")
        

def compare_controls(controls_a: dict, controls_b: dict) -> bool:
    assert len(controls_a) == len(controls_b)
    for key in controls_a.keys():
        for key1 in controls_a[key].keys():
            if key1 not in ["controlID"]:
                if controls_a[key][key1] != controls_b[key][key1]:
                    print(key)
                    return False
    
    return True


def compare_frameworks(frameworks_a: dict, frameworks_b: dict) -> bool:
    assert len(frameworks_a) == len(frameworks_b)
    for key in frameworks_a.keys():
        for key1 in frameworks_a[key].keys():
            if key1 not in ["controlsNames", "activeControls"]:
                if frameworks_a[key][key1] != frameworks_b[key][key1]:
                    return False
    
    return True

if __name__ == '__main__':
    # controls_output_dir_name = "1-newDesign/controls"
    # frameworks_output_dir_name = "1-newDesign/frameworks"
    # new_ids_matching_dir_name  = "1-newDesign/"
    controls_output_dir_name = "controls"
    frameworks_output_dir_name = "frameworks"
    new_ids_matching_dir_name  = "controlIDsmigration/"
    new_ids_mapping = {}
    controls = load_controls()
    
    # save controls and frameworks
    for key in controls.keys():
        # print(controls[key]["name"], ":", controls[key]["filename"], ":", controls[key].keys())
        if "rules" in controls[key]:
            del controls[key]["rules"]
        
        filename = controls[key]["filename"]
        del controls[key]["filename"]
        # print(controls[key]["name"], ":", filename, ":", controls[key].keys())
        
        export_json(controls[key], filename, controls_output_dir_name)
    
        
    ## need to drop 'filename', 'ordinal', 'old_controlID' 