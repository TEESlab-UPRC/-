import pandas as pd
import operator
import aim_simulations as simulations

# policy must be a string. One from the names defined in 'policies' list
def select_policy(policy, df):
    selected_policy = df.loc[df['policy'] == policy]
    return selected_policy

# selects a specific simulation year from a selected dataframe
# year is a number
def select_simulation_year(year, df):
    selected_year_scenarios = df.loc[df['year'] == year]
    return selected_year_scenarios

# Called to investigate if multiple policies are applied simultaneously
def find_overlapping_policies(implementation_sequence,implementation):
    overlapping_policies=[]
    for previous_implementation in implementation_sequence:
        if previous_implementation[2]>implementation[1]: #if any previous policy ends after the new policy has started
            overlapping_policies.append(previous_implementation) # add it to the overlapping policies list
    return overlapping_policies

# Called when multiple policies are implimented simultaniously, this function aggregates the outcomes of all implemented policies
def aggregate_policy_outcome(overlapping_policies, full_df,selected_years,selected_policy,outputs,aggregation_technique):
                           #(overlapping_policies, allPolicies_df,years_of_implementation,implemented_policy.reset_index(drop=True), output_variables, aggregation_technique)
    if aggregation_technique =="AVE":
        count_policies_per_year = {}
        for policy in overlapping_policies:
            aggregation_years = [year for year in selected_years if year > policy[1] and year <= policy[2]]
            for year in aggregation_years:
                # If the policy_per_year exists, add one more in the count
                if year in count_policies_per_year.keys():
                    count_policies_per_year[year] += 1
                # If the policy_per_year does not exist, add two; One for the policy we implement now, and one for the overlapping policy (the policy we
                # implement now is not included in the overlapping policies variable)
                else:
                    count_policies_per_year[year] = 2 
            for i_scenario in selected_policy.index:
                if selected_policy.iloc[i_scenario]['year'] in aggregation_years:
                    for output in outputs:
                        selected_policy.loc[i_scenario,output] += select_policy(policy[0],full_df).reset_index(drop=True).loc[i_scenario,output]
        for i_scenario in selected_policy.index:
            if selected_policy.iloc[i_scenario]['year'] in aggregation_years:
                for output in outputs:
                    selected_policy.loc[i_scenario,output] /= count_policies_per_year[selected_policy.iloc[i_scenario]['year']]
    elif aggregation_technique =="MAX":
        for policy in overlapping_policies:
            aggregation_years = [year for year in selected_years if year > policy[1] and year <= policy[2]]
            for i_scenario in selected_policy.index:
                if selected_policy.iloc[i_scenario]['year'] in aggregation_years:
                    for output in outputs:
                        selected_policy.loc[i_scenario,output] = max(selected_policy.loc[i_scenario,output] , select_policy(policy[0],full_df).reset_index(drop=True).loc[i_scenario,output])
    elif aggregation_technique =="MIN":
        for policy in overlapping_policies:
            aggregation_years = [year for year in selected_years if year > policy[1] and year <= policy[2]]
            for i_scenario in selected_policy.index:
                if selected_policy.iloc[i_scenario]['year'] in aggregation_years:
                    for output in outputs:
                        selected_policy.loc[i_scenario,output] = min(selected_policy.loc[i_scenario,output] , select_policy(policy[0],full_df).reset_index(drop=True).loc[i_scenario,output])
    return selected_policy

# builds the input dataframe as required by PRIM
# df is the selected scenario DataFrame (even if only some years of the scenario are selected)
def build_inputs_dataframe(df, input_variables):
    new_df=df[input_variables]
    return new_df

# builds the output array as required by PRIM
# df is the selected scenario DataFrame (even if only some years of the scenario are selected)
def build_outputs_array(df, output_variables):
    new_df=df[output_variables]
    return new_df.values

# passes the logical operator as the 'relate' argument, and returns
# True or False according to the comparison of inp and cut
def get_truth(inp, relate, cut):
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq}
    return ops[relate](inp, cut)

# selects a specific scenario from a selected dataframe
# scenario is an index
def select_scenario(scenario, df):
    selected_scenario = df.loc[df['scenario'] == scenario]
    return selected_scenario

# requires a list of scenario indexes as input
# df is a dataframe
def select_list_of_scenarios(df, scenarios):
    temp_list_ = []
    for scenario in scenarios:
        temp_df = df.loc[df['scenario'] == scenario]
        temp_list_.append(temp_df)
    if len(scenarios)!=0:
        selected_scenarios = pd.concat(temp_list_)
    return selected_scenarios

def prepare_hover_info(succesful_all_policies_df, trigger_points_df, allPolicies_df, policies, simulation_years,outputs_limits, context_factor_triggers):
    successful_outputs_limits = outputs_limits.copy(deep=True)
    for policy in policies:
        successful_policy_df = select_policy(policy, succesful_all_policies_df)
        all_policy_df = select_policy(policy, allPolicies_df)
        trigger_policy_df = select_policy(policy, trigger_points_df)
        for year in simulation_years:
            successful_year_df = select_simulation_year(year, successful_policy_df)
            all_year_df = select_simulation_year(year, all_policy_df)
            trigger_policy_year_df = select_simulation_year(year, trigger_policy_df)
            for column in context_factor_triggers.columns:
                context_factor = column[:-4]
                if column.split("-")[-1] == 'max':
                    context_factor_triggers.loc[policy+"-"+str(year)][column] = trigger_policy_year_df.loc[trigger_policy_year_df.index==context_factor]['max'].min()
                elif column.split("-")[-1] == 'min':
                    context_factor_triggers.loc[policy+"-"+str(year)][column] = trigger_policy_year_df.loc[trigger_policy_year_df.index==context_factor]['min'].max()
            if not(successful_year_df.empty):
                for column in outputs_limits.columns:
                    output = column[:-4]
                    if column.split("-")[-1] == 'max':
                        successful_outputs_limits.loc[policy+"-"+str(year)][column] = successful_year_df[output].max()
                    elif column.split("-")[-1] == 'min':
                        successful_outputs_limits.loc[policy+"-"+str(year)][column] = successful_year_df[output].min()
            for column in outputs_limits.columns:
                output = column[:-4]
                if column.split("-")[-1] == 'max':
                    outputs_limits.loc[policy+"-"+str(year)][column] = all_year_df[output].max()
                elif column.split("-")[-1] == 'min':
                    outputs_limits.loc[policy+"-"+str(year)][column] = all_year_df[output].min()
    return outputs_limits, successful_outputs_limits, context_factor_triggers

def df_initialisation(years_and_targets,policies, context_factors_list, output_variables):
    # Dataframes for hover info
    # this map is used to print mouse-hover information
    full_map = simulations.draw_full_map(years_and_targets.index, policies)
    # map showing feasible policies
    adaptation_map = pd.DataFrame(index=years_and_targets.index, columns=policies)
    # map showing implemented policies
    implementation_map = adaptation_map.copy(deep=True)
    success_percentages = adaptation_map.copy(deep=True)
    yearly_max_costs = pd.DataFrame(index=years_and_targets.index, columns=policies)
    yearly_min_costs = yearly_max_costs.copy(deep=True)
    ####################################### Contextual factors
    column_list=[]
    for context_factor in context_factors_list:
        column_list.append(context_factor+"-max")
        column_list.append(context_factor+"-min")
    index_list = []
    for year in  years_and_targets.index:
        for policy in policies:
            index_list.append(policy+"-"+str(year))
    context_factor_triggers = pd.DataFrame(index=index_list, columns=column_list)
    ######################################## Outputs
    column_list=[]
    for output_var in output_variables:
        column_list.append(output_var+"-max")
        column_list.append(output_var+"-min")
    outputs_limits = pd.DataFrame(index=index_list, columns=column_list)
    return full_map, adaptation_map, implementation_map, success_percentages, yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers

def copy(yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers):
    def_yearly_max_costs = yearly_max_costs.copy(deep=True)
    def_yearly_min_costs = yearly_min_costs.copy(deep=True)
    ######################################## Contextual factors
    def_context_factor_triggers   = context_factor_triggers.copy(deep=True)
    ######################################## Outputs
    def_outputs_limits   = outputs_limits.copy(deep=True)

    return def_yearly_max_costs, def_yearly_min_costs, def_outputs_limits, def_context_factor_triggers

def output_limits_df_creator(full_df,target, years, policies):
    output_max_df = pd.DataFrame(index=years, columns=policies)
    output_min_df = pd.DataFrame(index=years, columns=policies)
    for year in years:
        for policy in policies:
            output_max_df.loc[year][policy] = full_df.loc[policy+'-'+str(year)][target+'-max']
            output_min_df.loc[year][policy] = full_df.loc[policy+'-'+str(year)][target+'-min']

    return output_max_df, output_min_df
