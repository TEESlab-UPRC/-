# TODOs
# - Add a reset button
import os
import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import plotly.graph_objs as go

import aim_data_io as io
import aim_simulations as simulations
import aim_data_management as data

class Main:

    def __init__(self):

        # variable initiation
        cwd = os.getcwd()
        data_path = cwd + '/input_data/'   # path from which the code reads the input data
        inputs_file_name = 'inputs.xlsx'   # Contextual Factors
        outputs_file_name = 'outputs.xlsx' # Output to be printed
        targets_file_name = 'targets.xlsx' # Targets

        # success_threshold: percentage of uncertainty scenarios above which a policy is successful. It varies from 0 to 100 %.
        self.success_threshold = 70
        # how many years before policy failure to check for triggers
        self.trigger_point_offset = 0 # 1 entry back from the simulation years list. Should be positive or 0
        # aggregation_technique => When multiple policies are applied simultaneously, aggregation_technique variable indicates how their outcomes will be combined.
        # Possible values for aggregation_technique variable: "AVE" for average value, "MAX" for maximum value, "MIN" for minimum value
        self.aggregation_technique = "AVE"

        # data read
        self.allPolicies_df = io.read_inputs(data_path) # read all policy and scenario CSVs in given path and build an input DataFrame
        self.allPolicies_df.rename(columns = {self.allPolicies_df.columns[0]:"Original_Index"}, inplace=True)
        self.input_variables = pd.read_excel(data_path + inputs_file_name).columns.tolist()   # List with Contextual Factors
        self.output_variables = pd.read_excel(data_path + outputs_file_name).columns.tolist() # List with quantities to be printed
        self.targets_input = pd.read_excel(data_path + targets_file_name, index_col=0, header=0)
        self.years_and_targets = self.targets_input.iloc[:-1,:].copy(deep=True) # Years vs targets Dataframe
        self.target_threshold_type = self.targets_input.iloc[-1,:].copy(deep=True) # Dataframe with the threshold type of each target
        
        self.year_to_start_aim_assessment = self.years_and_targets.index.tolist().index(self.years_and_targets.index[0]) # index of the first simulation year
        self.policies = self.allPolicies_df.policy.unique() # Array with each policy
        self.num_scenarios = len(self.allPolicies_df.scenario.unique()) # total number of scenarios per policy
        
        self.full_map, self.adaptation_map, self.implementation_map, self.success_percentages, self.yearly_max_costs, self.yearly_min_costs, self.outputs_limits, self.context_factor_triggers = data.df_initialisation(self.years_and_targets, self.policies, self.input_variables, self.output_variables)
        self.impl_sequence_ = [] # sequence of policy implementations
        self.final_year_of_implementation = -1 # index of the last year a policy is implemented
        # the updated allPolicies_df which is used when implementing a policy
        self.allPolicies_df_updated = self.allPolicies_df.copy(deep=True).reset_index(drop=True)
        # The simulation years step (self.year_step) is used for the visualisation of the policy adaptation map.
        self.year_step = self.years_and_targets.index.max() - self.years_and_targets.index.min()
        for i_year in range(1,len(self.years_and_targets.index.tolist())):
            self.year_step = min(self.year_step,self.years_and_targets.index.tolist()[i_year]-self.years_and_targets.index.tolist()[i_year-1])
        
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    def draw_initial_map(self):
        adaptation_map = self.adaptation_map.copy(deep=True) # I want to keep the original DataFrames so I make new copies here
        implementation_map = self.implementation_map.copy(deep=True)
        allPolicies_df = self.allPolicies_df.copy(deep=True)
        success_percentages = self.success_percentages.copy(deep=True)

        adaptation_map, success_percentages, succesful_all_policies_df, trigger_points_df, targets_success_percentage = simulations.perform_AIM(adaptation_map, allPolicies_df, self.policies, success_percentages, self.success_threshold, self.input_variables, self.output_variables, self.num_scenarios, self.years_and_targets, self.target_threshold_type, self.year_to_start_aim_assessment, self.trigger_point_offset)
        #Creates copies of yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers dataframes
        yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers = data.copy(self.yearly_max_costs, self.yearly_min_costs, self.outputs_limits, self.context_factor_triggers)
        #Calculate the costs of the candidate policies
        max_costs, min_costs  = simulations.calculate_costs(yearly_max_costs, yearly_min_costs, allPolicies_df, allPolicies_df['policy'].unique(), self.years_and_targets.index)
        #visualize
        visualization_data, pathway_data, pathway_graph_layout = io.prepare_plotly(self.years_and_targets, adaptation_map, implementation_map, allPolicies_df, success_percentages, max_costs, min_costs, outputs_limits, context_factor_triggers, self.full_map, succesful_all_policies_df, trigger_points_df, self.input_variables, self.output_variables, self.target_threshold_type, targets_success_percentage,  self.impl_sequence_)
        allPolicies_df.to_excel('All policies df updated.xlsx')
        return visualization_data, pathway_data, pathway_graph_layout

    def model_policy_implementation(self, implementation_sequence):
        adaptation_map = self.adaptation_map.copy(deep=True) # I want to keep the original DataFrames so I make new copies here
        implementation_map = self.implementation_map.copy(deep=True)
        allPolicies_df = self.allPolicies_df.copy(deep=True)
        success_percentages = self.success_percentages.copy(deep=True)

        year_to_start_aim_assessment = adaptation_map.index.tolist().index(implementation_sequence[-1][1]) #from the year the last policy started to be implemented, because in the meanwhile another policy may be implemeneted during the same period

        self.allPolicies_df_updated, implementation_map = simulations.implement_policy(implementation_sequence, implementation_map, allPolicies_df, self.allPolicies_df_updated, self.policies, self.num_scenarios, self.output_variables, self.years_and_targets.index, self.aggregation_technique)
        self.allPolicies_df_updated.to_excel('All policies df updated.xlsx')
        adaptation_map, success_percentages, succesful_all_policies_df, trigger_points_df, targets_success_percentage = simulations.perform_AIM(adaptation_map, self.allPolicies_df_updated, self.policies, success_percentages, self.success_threshold, self.input_variables, self.output_variables, self.num_scenarios, self.years_and_targets, self.target_threshold_type, year_to_start_aim_assessment, self.trigger_point_offset)

        #Creates copies of yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers dataframes
        yearly_max_costs, yearly_min_costs, outputs_limits, context_factor_triggers = data.copy(self.yearly_max_costs, self.yearly_min_costs, self.outputs_limits, self.context_factor_triggers)
        #Calculate the costs of the candidate policies
        max_costs, min_costs  = simulations.calculate_costs(yearly_max_costs, yearly_min_costs, self.allPolicies_df_updated, self.allPolicies_df_updated['policy'].unique(), self.years_and_targets.index)
        # visualize
        visualization_data, pathway_data, pathway_graph_layout = io.prepare_plotly(self.years_and_targets, adaptation_map, implementation_map, self.allPolicies_df_updated, success_percentages, max_costs, min_costs, outputs_limits, context_factor_triggers, self.full_map, succesful_all_policies_df, trigger_points_df, self.input_variables, self.output_variables, self.target_threshold_type, targets_success_percentage, self.impl_sequence_)

        return visualization_data, pathway_data, pathway_graph_layout

    def plot_plotly(self, app, data, pathway_data, pathway_graph_layout):
        dropdown_options=[]
        for policy in self.policies:
            dropdown_options.append({'label': ('Policy: '+policy), 'value': policy})
        app.layout = html.Div(children=[
            html.Div([
                dcc.Graph(id='adaptation map',
                          figure={'data': (data),
                                  'layout': go.Layout(
                                            xaxis={'type': 'linear', 'title': 'Simulation Year', 'tickvals': self.years_and_targets.index.values},
                                            yaxis={'title': 'Policy Packages', 'tickvals': [i_pol for i_pol in range(len(self.policies))], 'ticktext': self.policies},
                                            height=600,
                                            width = 1500,
                                            margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                                            # legend={'x': 0, 'y': 1},
                                            showlegend=False,
                                            hovermode='closest'
                                            )
                                  },
                            ),
                    ]),
            html.Div([
                dcc.Graph(id='pathway',
                          figure={'data': (pathway_data),
                                  'layout': (pathway_graph_layout)
                                  },
                            ),
                    ]),
            html.Div([
                    dcc.Dropdown(id='policy',
                                style={'height': '30px', 'width': '400px'},
                                options=dropdown_options,
                                value=''
                                ),
                    #dcc.Input(id="Number_of_policies_to_imply" ,  type="number", placeholder="", min=1, max=len(self.policies), step=1),
                    ]),
            html.Br(),
            html.Div([
                    dcc.Input(id="start_date", type="number", placeholder="", min=self.years_and_targets.index.min(), max=self.years_and_targets.index.max(), step=self.year_step),
                    dcc.Input(id="end_date" ,  type="number", placeholder="", min=self.years_and_targets.index.min(), max=self.years_and_targets.index.max(), step=self.year_step),
                    html.Button('Submit', id='submit_button', n_clicks=0),
                    html.Div(id="output"),
                    ])
        ])
        @app.callback(
            Output('adaptation map', 'figure'),
            Output('pathway', 'figure'),
            Input('submit_button', 'n_clicks'),
            State('policy', 'value'),
            State('start_date', 'value'),
            State('end_date', 'value'))
        def update_map(n_clicks, policy, start_date, end_date):
            if policy != '':
                # Multiple policy implementation: The new policy must start after the start and before the end of the previous policy, and end after the end of the previous policy
                if self.final_year_of_implementation < 0 or (start_date >= main.impl_sequence_[-1][1] and end_date >= main.impl_sequence_[-1][2] and start_date <= main.impl_sequence_[-1][2]): 
                    main.impl_sequence_.append([policy, start_date, end_date])
                    main.final_year_of_implementation = self.years_and_targets.index.tolist().index(end_date) #In this implementation we do not use this variable because we allow for multiple policy implementations
                    print (main.impl_sequence_)
                    callback_data, callback_pathway_data, callback_pathway_graph_layout = main.model_policy_implementation(main.impl_sequence_)
                elif start_date < main.impl_sequence_[-1][1]:
                    print ("Please select a year to start", policy, "implementation later than the year the previous policy's implementation started")
                    callback_data, callback_pathway_data, callback_pathway_graph_layout = data, pathway_data, pathway_graph_layout
                elif end_date < main.impl_sequence_[-1][2]:
                    print ("Please select a year to terminate", policy, "implementation later than the year the previous policy's implementation ended")
                    callback_data, callback_pathway_data, callback_pathway_graph_layout = data, pathway_data, pathway_graph_layout
                elif start_date > main.impl_sequence_[-1][2]:
                    print ("Please select a year to start", policy, "implementation earlier than the year the previous policy's implementation ended")
                    callback_data, callback_pathway_data, callback_pathway_graph_layout = data, pathway_data, pathway_graph_layout
            else:
                callback_data, callback_pathway_data, callback_pathway_graph_layout = data, pathway_data, pathway_graph_layout

            adaptation_figure={'data': (callback_data),
                               'layout': go.Layout(
                                         xaxis={'type': 'linear', 'title': 'Simulation Year', 'tickvals': self.years_and_targets.index.values},
                                         yaxis={'title': 'Policy Packages', 'tickvals': [i_pol for i_pol in range(len(self.policies))], 'ticktext': self.policies},
                                         height=600,
                                         width = 1500,
                                         margin={'l': 100, 'b': 40, 't': 10, 'r': 10},
                                         # legend={'x': 0, 'y': 1},
                                         showlegend=False,
                                         hovermode='closest'
                                         )
                              }
            pathway_figure={'data': (callback_pathway_data),
                            'layout': (callback_pathway_graph_layout)
                           }
            return adaptation_figure, pathway_figure

#order of execution
main = Main()
plotly_data, plotly_pathway_data, plotly_pathway_graph_layout = main.draw_initial_map()
main.plot_plotly(main.app, plotly_data, plotly_pathway_data, plotly_pathway_graph_layout)
if __name__ == '__main__':
    main.app.run_server()
