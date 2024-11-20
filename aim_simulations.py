import pandas as pd

import aim_data_management as data
import aim_clustering as clustering

def draw_full_map(simulation_years, policies):
    full_map = pd.DataFrame(index=simulation_years, columns=policies)
    for policy in range(len(policies)):
        for year in range(len(simulation_years)):
            full_map.iloc[year,policy] = policy
    return full_map

#COMMENT Dummy cost function
def calculate_costs(yearly_max_costs, yearly_min_costs, allPolicies_df, policies, simulation_years):
    print("Calculating pathway's costs")
    for policy in range(len(policies)):
        print ("  ", policies[policy])
        policy_df = data.select_policy(policies[policy], allPolicies_df)
        for year in simulation_years:
            print ("    End of",year)
            year_df = data.select_simulation_year(year, policy_df).reset_index(drop=True)
            yearly_max_costs.loc[year,policies[policy]] = 100 #in million euros
            yearly_min_costs.loc[year,policies[policy]] = 50 #in million euros
    return yearly_max_costs, yearly_min_costs

def trigger_points_df_constructor(trigger_points_df,trigger_year_df,targets,selected_year,year,input_variables, output_variables,threshold_type,policy):
    for target in targets.columns:
        print ("            Target: {}".format(target))
        limits = clustering.find_trigger_cluster(target, selected_year, year, trigger_year_df, input_variables, output_variables, targets[target], thres_type=threshold_type.loc[target])
        limits['targetted_output'] = target
        limits['policy'] = policy
        limits['year'] = year
        trigger_points_df = pd.concat([trigger_points_df, limits])
    return trigger_points_df

def targets_and_average_results_message(year,targets,selected_year):
    target_message = "      Targets in year {}: ".format(year)
    average_results_message = "      Average results {}: ".format(year)
    for target in targets.columns:
        target_message += "{}-->{:.2f}  ".format(target, targets.loc[year,target])
        average_results_message += "{}-->{:.2f}  ".format(target, selected_year[target].mean())
    return target_message,average_results_message

def perform_AIM(adaptation_map, allPolicies_df, policies, success_percentages, success_threshold, input_variables, output_variables, num_scenarios, targets, threshold_type, year_to_start_aim_assessment, trigger_point_offset):
    simulation_years = targets.index
    succesful_policies_df = pd.DataFrame()
    targets_success_percentage_columns = targets.columns.tolist()
    targets_success_percentage_columns.append("policy")
    targets_success_percentage_columns.append("year")
    targets_success_percentage = pd.DataFrame(columns=targets_success_percentage_columns)
    trigger_points_df = pd.DataFrame(columns=["min", "max", "qp values", "targetted_output", "policy", "year"])
    print ("Performing AIM")
    for i_policy in range(len(policies)):
        selected_policy = data.select_policy(policies[i_policy], allPolicies_df)
        print("\n  Evaluating policy " + policies[i_policy])
        for year in simulation_years:
            selected_year = data.select_simulation_year(year, selected_policy).reset_index(drop=True)
            print ("    Target Year:" + str(year))
            targets_success_percentage.loc[len(targets_success_percentage.index)] = "NaN"
            targets_success_percentage["policy"].loc[len(targets_success_percentage.index)-1] = policies[i_policy]
            targets_success_percentage["year"].loc[len(targets_success_percentage.index)-1] = year
            # For the first target use selected_year. Use successful_scenarios for every other target
            for target in targets.columns:
                if target == targets.columns[0]:
                    plausible_scenarios_index, successful_scenarios = clustering.find_cluster(target, selected_year, year, targets[target], thres_type=threshold_type.loc[target])
                    targets_success_percentage[target].loc[len(targets_success_percentage.index)-1] = len(plausible_scenarios_index)/num_scenarios*100
                else:
                    plausible_scenarios_index, successful_scenarios = clustering.find_cluster(target, successful_scenarios, year, targets[target], thres_type=threshold_type.loc[target])
                    plausible_scenarios_index_current_target = clustering.find_cluster(target, selected_year, year, targets[target], thres_type=threshold_type.loc[target])[0]
                    targets_success_percentage[target].loc[len(targets_success_percentage.index)-1] = len(plausible_scenarios_index_current_target)/num_scenarios*100
            succesful_policies_df = pd.concat([succesful_policies_df, successful_scenarios]).reset_index(drop=True)
            success_percentages.loc[year, policies[i_policy]] = (len(plausible_scenarios_index)/num_scenarios)*100


            if success_percentages.loc[year, policies[i_policy]] >= success_threshold:
                print ("      Policy {} is plausible! It achieves the {} objectives in {:.1f} % of the contextual scenarios".format(policies[i_policy], year, success_percentages.loc[year, policies[i_policy]]))
                target_message, average_results_message = targets_and_average_results_message(year,targets,selected_year)
                print(target_message)
                print(average_results_message)
                # Draw map
                if len(simulation_years[year_to_start_aim_assessment:]) != 0: #checks if the list is not empty
                    if year >= simulation_years[year_to_start_aim_assessment:][0]:
                        adaptation_map.loc[year, policies[i_policy]] = i_policy
                # Calculate triggers
                if success_percentages.loc[year, policies[i_policy]] < 100:
                    # Triggers
                    trigger_year_index = simulation_years.tolist().index(year)-trigger_point_offset
                    trigger_year = simulation_years[trigger_year_index]
                    if trigger_year in simulation_years and trigger_year_index >= 0:
                        trigger_year_df = data.select_simulation_year(trigger_year, selected_policy).reset_index(drop=True)
                        print ("        The trigger values for the year", trigger_year, "are the following:")
                        trigger_points_df = trigger_points_df_constructor(trigger_points_df,trigger_year_df,targets,selected_year,year,input_variables, output_variables,threshold_type,policies[i_policy])
                    elif year == simulation_years[0]:
                        trigger_year_df = data.select_simulation_year(year, selected_policy).reset_index(drop=True)
                        print ("        The trigger values for the same year are the following:")
                        trigger_points_df = trigger_points_df_constructor(trigger_points_df,trigger_year_df,targets,selected_year,year,input_variables, output_variables,threshold_type,policies[i_policy])
                    else:
                        print("        Trigger points cannot be found for year {} because it is not in the simulated years list".format(trigger_year))
            elif len(plausible_scenarios_index) == 0:
                print ("      A policy change is needed! Policy {} failed in every scenario development!".format(policies[i_policy]))
                target_message, average_results_message = targets_and_average_results_message(year,targets,selected_year)
                print(target_message)
                print(average_results_message)
            else:
                print ("      A policy change is needed! Policy {} succeeds in only {:.1f} % of the contextual scenarios".format(policies[i_policy], success_percentages.loc[year, policies[i_policy]]))
                target_message, average_results_message = targets_and_average_results_message(year,targets,selected_year)
                print(target_message)
                print(average_results_message)
                # Triggers
                trigger_year_index = simulation_years.tolist().index(year)-trigger_point_offset
                trigger_year = simulation_years[trigger_year_index]
                if trigger_year in simulation_years and trigger_year_index >= 0:
                    trigger_year_df = data.select_simulation_year(trigger_year, selected_policy).reset_index(drop=True)
                    print ("        The trigger values for the year", trigger_year, "are the following:")
                    trigger_points_df = trigger_points_df_constructor(trigger_points_df,trigger_year_df,targets,selected_year,year,input_variables, output_variables,threshold_type,policies[i_policy])
                elif year == simulation_years[0]:
                     trigger_year_df = data.select_simulation_year(year, selected_policy).reset_index(drop=True)
                     print ("        The trigger values for the same year are the following:")
                     trigger_points_df = trigger_points_df_constructor(trigger_points_df,trigger_year_df,targets,selected_year,year,input_variables, output_variables,threshold_type,policies[i_policy])
                else:
                    print("        Trigger points cannot be found for year {} because it is not in the simulated years list".format(trigger_year))
    return adaptation_map, success_percentages, succesful_policies_df, trigger_points_df, targets_success_percentage

# implements the selected policy from start date to end date
def implement_policy(implementation_sequence, implementation_map, allPolicies_df, allPolicies_df_updated, policies, num_scenarios, output_variables, simulation_years, aggregation_technique):
    for implementation in implementation_sequence:
        print("Implementing policy {} from {} until {}:".format(implementation[0], implementation[1], implementation[2]))
        years_of_implementation = [year for year in simulation_years if year >= implementation[1] and year <= implementation[2]]
        # Update the implementation map
        for year in years_of_implementation:
            implementation_map.loc[year, implementation[0]] = policies.tolist().index(implementation[0])
        # select the implemented policy
        # I use allPolicies_df because during implemenetation, I update allPolicies_df_updated with the outcome of the implemented policy.
        # So when I want to make a new aggregation, I use the original dataframe
        implemented_policy = data.select_policy(implementation[0], allPolicies_df)
        # Aggregate the policy outcome of previous policies implemented in periods overlapping period implementation[1]-implementation[2]
        overlapping_policies = data.find_overlapping_policies(implementation_sequence[:implementation_sequence.index(implementation)],implementation)
        if overlapping_policies!=[]:
            implemented_policy = data.aggregate_policy_outcome(overlapping_policies, allPolicies_df,years_of_implementation,implemented_policy.reset_index(drop=True), output_variables, aggregation_technique)
        # update each policy's output during years_of_implementation to be equal to the output of the implemented policy
        # Update after implementation[1] if it is not the initial timestep of the simulation (simulation_years[0])
        if simulation_years[0] not in years_of_implementation:
            years_of_implementation.pop(0)
        for policy in policies.tolist():
            selected_policy = data.select_policy(policy, allPolicies_df_updated)
            for year in years_of_implementation:
                selected_year = data.select_simulation_year(year, selected_policy)
                if year != simulation_years[0]:
                    previous_selected_year = data.select_simulation_year(simulation_years[simulation_years.values.tolist().index(year)-1], selected_policy)
                    previous_implemented_year = data.select_simulation_year(simulation_years[simulation_years.values.tolist().index(year)-1], implemented_policy)
                implemented_year = data.select_simulation_year(year, implemented_policy)
                # iterates between all scenarios of each NOT implemented policy
                for scenario in range(num_scenarios):
                    selected_scenario_index = data.select_scenario(scenario, selected_year).index
                    if year != simulation_years[0]:
                        previous_selected_scenario_index = data.select_scenario(scenario, previous_selected_year).index
                        previous_implemented_scenario = data.select_scenario(scenario, previous_implemented_year)
                    implemented_scenario = data.select_scenario(scenario, implemented_year)
                     
                    for output in output_variables:
                        if year != simulation_years[0]:
                            allPolicies_df_updated.loc[selected_scenario_index, output] = allPolicies_df_updated.loc[previous_selected_scenario_index, output].values[0] + (implemented_scenario[output].values[0] - previous_implemented_scenario[output].values[0])    
                        else:
                            allPolicies_df_updated.loc[selected_scenario_index, output] = implemented_scenario[output].values
                        
                        ''' POLIZERO SPECIFIC'''
                        if output not in ['CO2 EMISSIONS IN ELECTRICITY MtCO2', 'DIRECT AIR CAPTURE MtCO2', 'CO2 EMISSIONS IN OTHER SECTORS MtCO2'] and  allPolicies_df_updated.loc[selected_scenario_index, output].values[0]<0:
                            allPolicies_df_updated.loc[selected_scenario_index, output] = 0
                        if output == 'NON-HYDRO ELECTRICITY PRODUCTION TWh' and  allPolicies_df_updated.loc[selected_scenario_index, output].values[0] > allPolicies_df_updated['Solar PV potential (TWh)'].max() + allPolicies_df_updated['Wind potential (TWh)'].max():
                            allPolicies_df_updated.loc[selected_scenario_index, output] = allPolicies_df_updated['Solar PV potential (TWh)'].max() + allPolicies_df_updated['Wind potential (TWh)'].max()
            
                    allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS BY SECTOR (TOTAL) MtCO2'] = allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN ELECTRICITY MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN INDUSTRY MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN RESIDENTIAL MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN SERVICES MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN DOMESTIC TRANSPORT MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN OTHER SECTORS MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'DIRECT AIR CAPTURE MtCO2'] 
                    
                       
        if implementation == implementation_sequence[-1]:
            years_of_non_implementation = [year for year in simulation_years if year > implementation[2]]
            if years_of_non_implementation != []:
                for policy in policies.tolist():
                    selected_policy = data.select_policy(policy, allPolicies_df_updated)
                    selected_policy_original = data.select_policy(policy, allPolicies_df)
                    for year in years_of_non_implementation:
                        selected_year = data.select_simulation_year(year, selected_policy)
                        selected_year_original = data.select_simulation_year(year, selected_policy_original)
                        if year != simulation_years[0]:
                            previous_selected_year = data.select_simulation_year(simulation_years[simulation_years.values.tolist().index(year)-1], selected_policy)
                            previous_selected_year_original = data.select_simulation_year(simulation_years[simulation_years.values.tolist().index(year)-1], selected_policy_original)
                        # iterates between all scenarios of each NOT implemented policy
                        for scenario in range(num_scenarios):
                            selected_scenario_index = data.select_scenario(scenario, selected_year).index
                            selected_scenario_original = data.select_scenario(scenario, selected_year_original)
                            if year != simulation_years[0]:
                                previous_selected_scenario_index = data.select_scenario(scenario, previous_selected_year).index
                                previous_selected_scenario_original = data.select_scenario(scenario, previous_selected_year_original)
                            for output in output_variables:
                                if year != simulation_years[0]:
                                    allPolicies_df_updated.loc[selected_scenario_index, output] = allPolicies_df_updated.loc[previous_selected_scenario_index, output].values[0] + (selected_scenario_original[output].values[0] - previous_selected_scenario_original[output].values[0])    
                                else:
                                    allPolicies_df_updated.loc[selected_scenario_index, output] = selected_scenario_original[output].values[0]
                                
                                ''' POLIZERO SPECIFIC'''
                                if output not in ['CO2 EMISSIONS IN ELECTRICITY MtCO2', 'DIRECT AIR CAPTURE MtCO2', 'CO2 EMISSIONS IN OTHER SECTORS MtCO2'] and  allPolicies_df_updated.loc[selected_scenario_index, output].values[0]<0:
                                    allPolicies_df_updated.loc[selected_scenario_index, output] = 0
                                if output == 'NON-HYDRO ELECTRICITY PRODUCTION TWh' and  allPolicies_df_updated.loc[selected_scenario_index, output].values[0] > allPolicies_df_updated['Solar PV potential (TWh)'].max() + allPolicies_df_updated['Wind potential (TWh)'].max():
                                    allPolicies_df_updated.loc[selected_scenario_index, output] = allPolicies_df_updated['Solar PV potential (TWh)'].max() + allPolicies_df_updated['Wind potential (TWh)'].max()
                    
                            allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS BY SECTOR (TOTAL) MtCO2'] = allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN ELECTRICITY MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN INDUSTRY MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN RESIDENTIAL MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN SERVICES MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN DOMESTIC TRANSPORT MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'CO2 EMISSIONS IN OTHER SECTORS MtCO2'] + allPolicies_df_updated.loc[selected_scenario_index, 'DIRECT AIR CAPTURE MtCO2'] 
    
    return allPolicies_df_updated, implementation_map
