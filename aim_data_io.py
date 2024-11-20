import glob
import pandas as pd
import numpy as np
import plotly.graph_objs as go

import aim_data_management as data
import aim_simulations as simulations

def read_inputs(path):
    allPolicies = glob.glob(path + "/*.csv")
    allPol_df = pd.DataFrame()
    temp_list_ = []
    for policy_ in allPolicies:
        temp_df = pd.read_csv(policy_, header=0, engine='python')
        temp_list_.append(temp_df)
    allPol_df = pd.concat(temp_list_)
    return allPol_df

def prepare_plotly(years_and_targets, adaptation_map, implementation_map, allPolicies_df, success_percentages, max_costs, min_costs, outputs_limits, context_factor_triggers, full_map, succesful_all_policies_df, trigger_points_df, context_factors, outputs, target_threshold_type, targets_success_percentage, impl_sequence_):
    
    outputs_limits, successful_outputs_limits, context_factor_triggers = data.prepare_hover_info(succesful_all_policies_df, trigger_points_df, allPolicies_df, allPolicies_df['policy'].unique(), years_and_targets.index, outputs_limits, context_factor_triggers)

    impl_sequence_df = pd.DataFrame(columns = ["policy", "start","end"])

    if impl_sequence_!=[]:
        for item in impl_sequence_:
            impl_sequence_df.loc[len(impl_sequence_df.index)] = "Nan"
            impl_sequence_df["policy"].loc[len(impl_sequence_df.index)-1] = item[0]
            impl_sequence_df["start"].loc[len(impl_sequence_df.index)-1] = item[1]
            impl_sequence_df["end"].loc[len(impl_sequence_df.index)-1] = item[2]
        impl_sequence_df = impl_sequence_df.set_index("policy")

    map_data = []
    pathway_data = []

    # Colour pallete: 148 colours => max 148 Candidate Policies
    colors = ["blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgrey", "darkgreen", "darkkhaki","aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond", "blue", "darkmagenta", "darkolivegreen","darkorange","darkorchid","darkred","darksalmon","darkseagreen","darkslateblue","darkslategray","darkslategrey","darkturquoise","darkviolet","deeppink","deepskyblue","dimgray","dimgrey","dodgerblue","firebrick","floralwhite","forestgreen","fuchsia","gainsboro","ghostwhite","goldenrod","gold","gray","green","greenyellow","grey","honeydew","hotpink","indianred","indigo","ivory","khaki","lavenderblush","lavender","lawngreen","lemonchiffon","lightblue","lightcoral","lightcyan","lightgoldenrodyellow","lightgray","lightgreen","lightgrey","lightpink","lightsalmon","lightseagreen","lightskyblue","lightslategray","lightslategrey","lightsteelblue","lightyellow","lime","limegreen","linen","magenta","maroon","mediumaquamarine","mediumblue","mediumorchid","mediumpurple","mediumseagreen","mediumslateblue","mediumspringgreen","mediumturquoise","mediumvioletred","midnightblue","mintcream","mistyrose","moccasin","navajowhite","navy","oldlace","olive","olivedrab","orange","orangered","orchid","palegoldenrod","palegreen","paleturquoise","palevioletred","papayawhip","peachpuff","peru","pink","plum","powderblue","purple","rebeccapurple","red","rosybrown","royalblue","saddlebrown","salmon","sandybrown","seagreen","seashell","sienna","silver","skyblue","slateblue","slategray","slategrey","snow","springgreen","steelblue","tan","teal","thistle","tomato","turquoise","violet","wheat","white","whitesmoke","yellow","yellowgreen"]

    # -------------------------- ADAPTATION MAP --------------------------- #
    # ===================================================================== #
    # The adaptation_map includes the candidate policies that exceed the success threshold
    # for the simulation years from the start of the last implemented policy and after.
    for policy in adaptation_map.columns:
        trace = go.Scatter(
            x = adaptation_map.index.values,
            y = adaptation_map[:][policy],
            hoverinfo = 'none',
            mode='lines+markers',
            opacity=0.7,
            line = dict(width=5,color=colors[adaptation_map.columns.get_loc(policy)]),
            marker={'size': 10, 'line': {'width': 0.5, 'color': 'rgb(231, 99, 250)'}},
            name=policy)
        map_data.append(trace)

    # The implementation_map includes all the implemented policies
    for policy in implementation_map.columns:
        trace = go.Scatter(
            x = implementation_map.index.values,
            y = implementation_map[:][policy],
            hoverinfo = 'none',
            mode='lines',
            opacity=0.7,
            line = dict(width=15,color=colors[implementation_map.columns.get_loc(policy)]),
            marker={'size': 10, 'line': {'width': 0.5, 'color': 'rgb(231, 99, 250)'}},
            name=policy)
        map_data.append(trace)

    for policy in full_map.columns:
        success_of_current_policy = targets_success_percentage.loc[targets_success_percentage["policy"]==policy].set_index("year")
        adapt_text="Policy: {} ".format(policy) +"- Success percentage: "+ success_percentages[:][policy].astype(str)+"<br>"
        for target in years_and_targets.columns.to_list():
            max_df, min_df = data.output_limits_df_creator(outputs_limits,target, years_and_targets.index, allPolicies_df['policy'].unique().tolist())
            adapt_text += "Target: {} ".format(target)+" "+target_threshold_type.loc[target]+" "+years_and_targets[:][target].astype(str)+",<br>     Success: " + success_of_current_policy[:][target].apply("{0:,.2f}".format).astype(str)+"%<br>"
            adapt_text += "     Output range: "+min_df[:][policy].apply("{0:,.2f}".format).astype(str)+" - "+max_df[:][policy].apply("{0:,.2f}".format).astype(str)+"<br>" #.loc[targets_success_percentage["Year"]==2025]
        # for output in outputs:
        #     if output not in years_and_targets.columns:
        #         max_df, min_df = data.output_limits_df_creator(outputs_limits,output, years_and_targets.index, allPolicies_df['policy'].unique().tolist())
        #         adapt_text += "     Non targetted output: {}: ".format(target) + min_df[:][policy].apply("{0:,.2f}".format).astype(str) + " - " + max_df[:][policy].apply("{0:,.2f}".format).astype(str)+"<br>"
        # for context_factor in context_factors:
        #     max_df, min_df = data.output_limits_df_creator(context_factor_triggers,context_factor, years_and_targets.index, allPolicies_df['policy'].unique().tolist())
        #     adapt_text += "Contextual factor {}: ".format(context_factor)+min_df[:][policy].apply("{0:,.2f}".format).astype(str)+" - "+max_df[:][policy].apply("{0:,.2f}".format).astype(str)+"<br>"
        # adapt_text += "Yearly cost: "+min_costs[:][policy].apply("{0:,.2f}".format).astype(str)+"€ - "+max_costs[:][policy].apply("{0:,.2f}".format).astype(str)+"€"
        trace = go.Scatter(
            x = full_map.index.values,
            y = full_map[:][policy],
            text =  adapt_text,
            hoverinfo = 'text',
            mode='markers',
            opacity=0.7,
            line = dict(width=2,color=colors[full_map.columns.get_loc(policy)], dash='dash'),
            marker={'size': 5, 'line': {'width': 0.5, 'color': 'rgb(231, 99, 250)'}},
            name=policy)
        map_data.append(trace)
    outputs_limits.to_excel('Total Output Limits.xlsx')
    context_factor_triggers.to_excel('Context Factor Triggers.xlsx')
    #########################################################################

    # ----------------------- OUTPUT FIGURES -------------------------------#
    # ===================================================================== #
    # ----------------------- Targets --------------------------------------#
    i_graph=0
    x_axis_list=[]
    y_axis_list=[]
    figure_width=1/len(outputs)
    for target in years_and_targets.columns:
        i_graph+=1
        max_df, min_df = data.output_limits_df_creator(successful_outputs_limits,target, years_and_targets.index, allPolicies_df['policy'].unique().tolist())
        max_df_copy = max_df.copy(deep=True)
        min_df_copy = min_df.copy(deep=True)
        trigger_factor_df = trigger_points_df.loc[trigger_points_df['targetted_output']==target]
        
        if impl_sequence_!=[]:
            years_of_implementation = [year for year in years_and_targets.index if year < impl_sequence_[-1][1]]
            for year in years_of_implementation:
                for policy in max_df.columns:
                    if policy not in impl_sequence_df.index or (year<impl_sequence_df["start"].loc[policy] or year>impl_sequence_df["end"].loc[policy]):
                        max_df_copy[policy].loc[year] = None
                        min_df_copy[policy].loc[year] = None
        
        
        for policy in adaptation_map.columns:
            selected_policy = data.select_policy(policy, allPolicies_df)
            trigger_policy_df = data.select_policy(policy, trigger_factor_df)
            adapt_text = "Policy: "+ policy + ", Year: "+ adaptation_map.index[:].astype(str) +"<br>Max " + target + ": "+max_df[:][policy].apply("{0:,.2f}".format).astype(str) + "<br>Min " + target + ": "+min_df[:][policy].apply("{0:,.2f}".format).astype(str)
            for context_factor in context_factors:
                trigger_context_factor_df = trigger_policy_df.loc[trigger_policy_df.index==context_factor]
                max_cf_df = pd.Series(index = years_and_targets.index.values)
                min_cf_df = pd.Series(index = years_and_targets.index.values)
                for year in years_and_targets.index:
                    max_value = trigger_context_factor_df.loc[trigger_context_factor_df['year']==year]['max'].tolist()
                    min_value = trigger_context_factor_df.loc[trigger_context_factor_df['year']==year]['min'].tolist()
                    if not max_value:
                        max_cf_df.loc[year] = np.NaN  
                    else:
                        max_cf_df.loc[year] = max_value[0]
                        
                    if not min_value:
                        min_cf_df.loc[year] = np.NaN
                    else:
                        min_cf_df.loc[year] = min_value[0]
                        
                adapt_text += "<br>Contectual factor {}: ".format(context_factor)+min_cf_df[:].apply("{0:,.2f}".format).astype(str)+" - "+max_cf_df[:].apply("{0:,.2f}".format).astype(str)
                
            trace_max = go.Scatter(
                x = adaptation_map.index.values,
                y = max_df_copy[:][policy],
                xaxis='x{}'.format(i_graph),
                yaxis='y{}'.format(i_graph),
                text =  adapt_text,
                hoverinfo = 'text',
                mode='lines',
                opacity=0.6,
                line = dict(width=2,color=colors[adaptation_map.columns.get_loc(policy)]),
                marker=None,
                name=policy)
            trace_min = go.Scatter(
                x = adaptation_map.index.values,
                y = min_df_copy[:][policy],
                xaxis='x{}'.format(i_graph),
                yaxis='y{}'.format(i_graph),
                text =  adapt_text,
                hoverinfo = 'text',
                mode='lines',
                opacity=0.6,
                line = dict(width=2,color=colors[adaptation_map.columns.get_loc(policy)]),
                marker=None,
                name=policy,
                #fill='tonexty',
                fillcolor=colors[adaptation_map.columns.get_loc(policy)])
            pathway_data.append(trace_max)
            pathway_data.append(trace_min)

        tracetarget = go.Scatter(
            x = adaptation_map.index.values,
            y = years_and_targets[:][target],
            xaxis='x{}'.format(i_graph),
            yaxis='y{}'.format(i_graph),
            text =  "Target: " + target + ",<br>Threshold value: "+years_and_targets[:][target].apply("{0:,.2f}".format).astype(str),
            hoverinfo = 'text',
            mode='lines',
            opacity=0.6,
            line = dict(width=3,color="rgba(255,0,0,1)", dash='dot'),
            marker=None,
            name=policy
            )
        pathway_data.append(tracetarget)

        xaxis={'type': 'linear', 'title': 'Simulation Year', 'tickvals': adaptation_map.index.values, 'domain':[figure_width*(i_graph-1), figure_width*(i_graph-0.15)]}
        if i_graph==1:
            yaxis={'title': target}
        else:
            yaxis={'title': target, 'overlaying':'y', 'anchor': 'free', 'position': figure_width*(i_graph-1)}

        x_axis_list.append(xaxis)
        y_axis_list.append(yaxis)

    # ----------------------- Rest outputs ------------------------------------#
    for output in outputs:
        if output not in years_and_targets.columns:
            i_graph+=1
            max_df, min_df = data.output_limits_df_creator(successful_outputs_limits,output, years_and_targets.index, allPolicies_df['policy'].unique().tolist())
            max_df_copy = max_df.copy(deep=True)
            min_df_copy = min_df.copy(deep=True)

            if impl_sequence_!=[]:
                years_of_implementation = [year for year in years_and_targets.index if year < impl_sequence_[-1][1]]
                for year in years_of_implementation:
                    for policy in max_df.columns:
                        if policy not in impl_sequence_df.index or (year<impl_sequence_df["start"].loc[policy] or year>impl_sequence_df["end"].loc[policy]):
                            max_df_copy[policy].loc[year] = None
                            min_df_copy[policy].loc[year] = None

            for policy in adaptation_map.columns:
                selected_policy = data.select_policy(policy, allPolicies_df)

                trace_max = go.Scatter(
                    x = adaptation_map.index.values,
                    y = max_df_copy[:][policy],
                    xaxis='x{}'.format(i_graph),
                    yaxis='y{}'.format(i_graph),
                    text = "Policy: "+ policy + ", Year: "+ adaptation_map.index[:].astype(str) +"<br>Output: "+ output +"<br>Max: " +max_df[:][policy].apply("{0:,.2f}".format).astype(str) + "<br>Min: " + min_df[:][policy].apply("{0:,.2f}".format).astype(str),
                    hoverinfo = 'text',
                    mode='lines',
                    opacity=0.6,
                    line = dict(width=2,color=colors[adaptation_map.columns.get_loc(policy)]),
                    marker=None,
                    name=policy)
                trace_min = go.Scatter(
                    x = adaptation_map.index.values,
                    y = min_df_copy[:][policy],
                    xaxis='x{}'.format(i_graph),
                    yaxis='y{}'.format(i_graph),
                    text = "Policy: "+ policy + ", Year: "+ adaptation_map.index[:].astype(str) +"<br>Output: "+ output +"<br>Max: " +max_df[:][policy].apply("{0:,.2f}".format).astype(str) + "<br>Min: " + min_df[:][policy].apply("{0:,.2f}".format).astype(str),
                    hoverinfo = 'text',
                    mode='lines',
                    opacity=0.6,
                    line = dict(width=2,color=colors[adaptation_map.columns.get_loc(policy)]),
                    marker=None,
                    name=policy,
                    #fill='tonexty',
                    fillcolor=colors[adaptation_map.columns.get_loc(policy)])
                pathway_data.append(trace_max)
                pathway_data.append(trace_min)
            xaxis={'type': 'linear', 'title': 'Simulation Year', 'tickvals': adaptation_map.index.values, 'domain':[figure_width*(i_graph-1), figure_width*(i_graph-0.15)]}
            yaxis={'title': output, 'overlaying':'y', 'anchor': 'free', 'position': figure_width*(i_graph-1)}

            x_axis_list.append(xaxis)
            y_axis_list.append(yaxis)
    ############################################################################
    # ------------------ Layout of visual environment ------------------------ #
    # ======================================================================== #
    axis_dictionary={'xaxis':x_axis_list[0],'yaxis':y_axis_list[0]}
    for i_graph in range(1,len(x_axis_list),1):
        axis_dictionary['xaxis{}'.format(i_graph+1)]=x_axis_list[i_graph]
        axis_dictionary['yaxis{}'.format(i_graph+1)]=y_axis_list[i_graph]
    pathway_graph_layout = go.Layout(
                                        **axis_dictionary,
                                        height=400,
                                        width = 450*len(outputs),
                                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                        legend={'x': 0, 'y': 1},
                                        showlegend=True,
                                        #hovermode='closest'
                                        )
    return map_data, pathway_data, pathway_graph_layout
