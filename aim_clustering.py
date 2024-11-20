import prim
import pandas as pd

import aim_data_management as data

def find_cluster(target_output, df, target_year, clust_thres, thres_type):
    if thres_type == ">":
        successful_scen = df.loc[df[target_output] > clust_thres[target_year]]
        plausible_indexes = successful_scen["scenario"].values
    elif thres_type == "<":
        successful_scen = df.loc[df[target_output] < clust_thres[target_year]]
        plausible_indexes = successful_scen["scenario"].values
    elif thres_type == "=":
        successful_scen = df.loc[df[target_output] == clust_thres[target_year]]
        plausible_indexes = successful_scen["scenario"].values
    return plausible_indexes, successful_scen

# performs PRIM for the trigger_year_df_inputs considering the target_year_outputs,
# the clustering threshold and the therhold type
def find_trigger_cluster(target_output, target_year_df, target_year, trig_year_df, input_variables, output_variables, clust_thres, thres_type):
    target_year_outputs = data.build_outputs_array(target_year_df, output_variables)
    trigger_year_inputs = data.build_inputs_dataframe(trig_year_df, input_variables)
    if (sum(data.get_truth(target_year_outputs[k,output_variables.index(target_output)], thres_type, clust_thres[target_year]) for k in range(len(target_year_outputs[:,0])))) > 0:
        pt = prim.Prim(trigger_year_inputs, target_year_outputs[:,output_variables.index(target_output)], threshold=clust_thres[target_year], threshold_type=thres_type)
        trigger_box = pt.find_box()
        if not trigger_box.limits.empty:
            df_split = trigger_box.limits.to_string().split('\n')
            for i in range(len(df_split)):
                print ("                ", df_split[i])
            print ("\n")
        else:
            print ("                Trigger box empty\n\n")
    else:
        print ("          Trigger values could not be found because policy fails in every scenario")
    return trigger_box.limits
