import pandas as pd

import aim_simulations as simulations

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
