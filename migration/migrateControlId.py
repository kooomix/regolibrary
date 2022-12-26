
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
    frameworks = load_frameworks()
    new_frameworks = copy.deepcopy(frameworks)
 
        
    other_controls = copy.deepcopy({k: v for k, v in controls.items() if "cis-" not in v["controlID"].lower()})
    highest_id = 0
    for key in other_controls.keys():
        controlID = other_controls[key]["controlID"]
        other_controls[key]["ordinal"] = int(controlID.lower().replace("c-", ""))
        highest_id = max(highest_id, int(controlID.lower().replace("c-", "")))
 
    
    cis_controls = copy.deepcopy({k: v for k, v in controls.items() if "cis-" in v["controlID"].lower()})
    for key in cis_controls.keys():
        controlID = cis_controls[key]["controlID"]
        cis_controls[key]["ordinal"] = convert_dotted_section_to_int(controlID.lower().replace("cis-", ""))
        
    cis_controls = {k: v for k, v in sorted(cis_controls.items(), key=lambda item: item[1]["ordinal"])}
    
    print("highest:", highest_id)
   
    current_int_controlID = highest_id + 1
    for key in cis_controls.keys():
        cis_controls[key]["old_controlID"] = cis_controls[key]["controlID"]
        cis_controls[key]["controlID"] = generate_control_id_from_int(current_int_controlID)
        new_ids_mapping [cis_controls[key]["old_controlID"]] = cis_controls[key]["controlID"]
        # print(cis_controls[key]["old_controlID"], "->", cis_controls[key]["controlID"])
        current_int_controlID = current_int_controlID + 1
    
    export_json(new_ids_mapping, "newids.json", new_ids_matching_dir_name)
    new_controls = other_controls
    new_controls.update(cis_controls)
    
    assert compare_controls(controls, new_controls) == True
    
    for key, value in new_frameworks.items():
        new_frameworks[key]["activeControls"] = build_activeControls(new_frameworks[key], new_controls)
        # export_json(frameworks[key], frameworks[key]["filename"], frameworks_output_dir_name)
        # print(key, ":", frameworks[key]["filename"])
    
    
    assert compare_frameworks(frameworks, new_frameworks)
    
    # save controls and frameworks
    for key in new_controls.keys():
        if "old_controlID" in new_controls[key]:
            del new_controls[key]["old_controlID"]
        
        filename = new_controls[key]["filename"]
        del new_controls[key]["filename"]
        del new_controls[key]["ordinal"]
        del new_controls[key]['id']
        
        export_json(new_controls[key], filename, controls_output_dir_name)
    
    
    for key in new_frameworks.keys():
        filename = new_frameworks[key]["filename"]
        del new_frameworks[key]["filename"]
        del new_frameworks[key]["controlsNames"]
        
        export_json(new_frameworks[key], filename, frameworks_output_dir_name)
        
    ## need to drop 'filename', 'ordinal', 'old_controlID' 