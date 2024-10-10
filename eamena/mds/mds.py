##################################################################################################################
## renamed, adapted and moved to https://github.com/eamena-project/eamena-functions/tree/main/reference_data.py ##
## and																											##
## renamed, adapted and moved to https://github.com/eamena-project/eamena-functions/tree/main/business_data.py  ##
##################################################################################################################

import argparse
import pandas as pd
import numpy as np
import re
import requests
import json
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import plotly.express as px
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# argp = argparse.ArgumentParser()
# argp.add_argument('GEOJSON_URL', type=str, help='The GeoJSON URL coming from a Search in the EAMENA database', default='')
# argp.add_argument('VERBOSE', type=bool, help='Verbose, True or False', default=False)
# args = argp.parse_args()

# print(args.GEOJSON_URL)

# def db_query(GEOJSON_URL = None):
# 	"""
# 	Return a JSON file (GeoJSON) from a GeoJSON URL

# 	Use the Arches REST API with a GeoJSON URL (in Arches: Export > GeoJSON URL) to collect selected Heritage Places in a GeoJSON format

# 	:param GEOJSON_URL: The GeoJSON URL

# 	:Example: 
# 	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
# 	>> hps = mds.db_query()
# 	"""
# 	import requests

# 	resp = requests.get(GEOJSON_URL)
# 	print(resp.status_code) # 504 error on large datasets (> 1,000)
# 	return(resp.json())

# def db_export_geojson(geojson_data, output_file_path = "output.geojson"):
# 	# Save the GeoJSON data to a file
# 	import json

# 	with open(output_file_path, "w") as output_file:
# 		json.dump(geojson_data, output_file, indent=2)

# def hps_list(hps = None):
# 	"""
# 	Store the EAMENA ID in a list 

# 	:param hps: a dict() coming from reading of a JSON (GeoJSON). See the function `db_query()`

# 	:return: A list of EAMENA IDs

# 	:Example: 
# 	>> GEOJSON_URL = "https://database.eamena.org/api/search/..."
# 	>> hps = mds.db_query(GEOJSON_URL)
# 	>> selected_hp = mds.hps_list(hps)

# 	"""
# 	selected_hp = []
# 	for i in range(len(hps['features'])):
# 		selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
# 	return(selected_hp)

# def mds_template(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dbs/database.eamena/data/reference_data/rm/hp/mds/mds-template-readonly.tsv"):
# 	"""
# 	Dataframe of mds individual fields

# 	:param tsv_file: the path to the read-only TSV file of mds

# 	:return: Dataframe of mds individual fields
# 	"""
# 	df = pd.read_csv(tsv_file, delimiter = '\t', skip_blank_lines = True)
# 	df_listed = df[["level1", "level2", "level3", "Enhanced record minimum standard",'uuid_sql','color']]
# 	# df_listed = df.dropna()
# 	# if verbose:
# 	# 	print(df_listed.to_markdown())
# 	return(df_listed)

# def mds_template_levels(tsv_file = "https://raw.githubusercontent.com/eamena-project/eamena-arches-dev/main/dbs/database.eamena/data/reference_data/rm/hp/mds/mds-template-readonly.tsv", radio_button = None):
# 	"""
# 	Dataframe of mds individual or aggregated fields

# 	Taking a level of aggregation (level1, level2, etc.), group and sum mds fields (level3) into broader categories

# 	:param tsv_file: the path to the read-only TSV file of mds
# 	:param radio_button: a value coming from a Jupyter NB radio button

# 	:return: Dataframe of mds individual or aggregated fields
# 	"""
# 	if radio_button != None:
# 		mylevel = radio_button.value
# 	else:
# 		mylevel = 'level3'
# 	df_listed = mds_template(tsv_file)
# 	df_mds = df_listed.copy()
# 	df_mds['Enhanced record minimum standard'] = df_mds['Enhanced record minimum standard'].str.contains(r'Yes', case = False, na = False, regex = True).astype(int)
# 	df_mds = df_mds[[mylevel, "Enhanced record minimum standard"]]
# 	df_mds.columns.values[0] = "field"
# 	df_mds = df_mds.groupby(['field'])['Enhanced record minimum standard'].sum()
# 	print(f'You selected: {mylevel}')
# 	df_mds = pd.DataFrame({
# 		'field': df_mds.index,
# 		'value' : df_mds.values
# 					})
# 	# print(df_mds.to_markdown(index=False))
# 	return(df_mds)


# def mds_field_colors(level = 'level1', cmap = 'Dark2'):
# 	"""
# 	Return a dataframe of colors based on one of the levels to color graph nodes

# 	:param level1: a level. Default 'level1'
# 	:param cmap: a color ramp

# 	:return: Dataframe of 'level' colors

# 	:Example:
# 	>> df_color = mds_field_colors()
# 	"""
# 	import matplotlib.pyplot as plt
# 	from matplotlib.colors import to_hex
# 	import pandas as pd

# 	mds_template_df = mds_template()
# 	mds_template_df = mds_template_df.drop('Enhanced record minimum standard', axis=1)
# 	level1_cat = mds_template_df[level].unique()
# 	my_cmap = plt.get_cmap(cmap)
# 	level1_cmap = my_cmap(np.linspace(0, 1, len(level1_cat)))
# 	level1_cmap = [to_hex(color) for color in level1_cmap]
# 	df_color = pd.DataFrame(columns=(level, 'color'))
# 	df_color[level] = level1_cat
# 	df_color['color'] = level1_cmap
# 	df_color = mds_template_df.merge(df_color, on=level, how='left')
# 	return df_color

# def hps_dict(hps = None, selected_hp = None, df_listed = None, mylevel = "level3", verbose = False):
# 	# Keys are EAMENA IDs and values are HP fields filled or not
# 	level_values = df_listed[mylevel].unique()
# 	l_mds = []
# 	dict_hps = {} 
# 	# len(selected_hp)
# 	for i in range(len(selected_hp)):
# 		a_hp = selected_hp[i]
# 		if verbose:
# 			print("read: " + a_hp)
# 		# create an empty df
# 		df_res = pd.DataFrame({'field': level_values, 
# 							'recorded': np.repeat(0, len(level_values)).tolist()})
# 		# len(df_res)
# 		for j in range(len(df_res)):
# 			a_field = df_res.iloc[j]["field"]
# 			try:
# 				a_value = hps['features'][i]['properties'][a_field]
# 				if verbose:
# 					print("field: '" + a_field + "' has value :'" + str(a_value) + "'")
# 			# TODO: change to warning?
# 			except:
# 				if verbose:
# 					print(" /!\ '" + a_field + "' listed in the mds dataframe is a level1 or level2 value, but is not a field listed in the database")
# 				a_value = None
# 			if a_value is not None:
# 				# row_num = df_res[df_res['field'] == df_field].index.tolist()
# 				df_res.at[j, 'recorded'] = df_res.loc[j]['recorded'] + 1
# 		l_mds.append(df_res)
# 		dict_hps[a_hp] = df_res
# 	return(dict_hps)


# def filter_dataframe(hps, selected_hp, selected_value):
# 	"""
# 	Filter a dataframe giving a selected value coming from a radio button

# 	:param hps: HPs in a dict shape (GeoJSON)
# 	:param selected_hp: a list of HPs IDs
# 	:param selected_value: value returned by the on_radio_button_change() function, it is a GS ID

# 	:return: Dataframe of existing HP is a given GS
# 	"""
# 	# nonlocal selected_hp_gs
# 	# global selected_hp_gs
# 	hps_to_keep = list()
# 	hps_gs = dict()
# 	hps_gs['features'] = []
# 	for i in range(len(selected_hp)):
# 		gs_current = hps['features'][i]['properties']['Grid ID']
# 		if gs_current == selected_value:
# 		# if gs_current ==  radio_button_1.value:
# 			hps_to_keep.append(i)
# 		feat = [hps['features'][i] for i in hps_to_keep]
# 	for i in range(len(feat)):
# 		hps_gs['features'].append(feat[i])
# 	selected_hp_gs = []
# 	for i in range(len(hps_gs['features'])):
# 		selected_hp_gs.append(hps_gs['features'][i]['properties']['EAMENA ID'])
# 	return(selected_hp_gs)

# def filter_hp_by_gs(hps, selected_hp):

# 	# NB: doesnot work when imported into Jupyter NB, so refer to the function in the Jupyter NB

# 	"""
# 	Filter a dataframe giving a selected value coming from a radio button

# 	List all GS listed in the HP. Display a radio button to show these HP by GS. Display a radio button for the selection of the GS

# 	:param hps: HPs in a dict shape (GeoJSON)
# 	:param selected_hp: a list of HPs IDs

# 	:return: Update a copy of the HP list filtered on a given GS

# 	:Example: 
# 	>> filter_hp_by_gs(hps, selected_hp) # shows the button
# 	>> filtered_hp_gs # print the list
# 	"""
# 	# global filtered_hp_gs
# 	l_GridIDs = []
# 	for i in range(len(selected_hp)):
# 		l_GridIDs.append(hps['features'][i]['properties']['Grid ID'])
# 	l_GridIDs = list(set(l_GridIDs))
# 	l_GridIDs.sort()
# 	radio_button_1 = widgets.RadioButtons(
# 		options=l_GridIDs,
# 		description='Select a Grid Square:'
# 	)
# 	output = widgets.Output()

# 	def on_radio_button_change(change):
# 		selected_value = change.new
# 		global filtered_hp_gs
# 		with output:
# 			output.clear_output()
# 			filtered_hp_gs = filter_dataframe(hps, selected_hp, selected_value)
# 			# Print or display the result
# 			print(filtered_hp_gs, end="")

# 	radio_button_1.observe(on_radio_button_change, names='value')
# 	display(radio_button_1, output)

# def hps_subset_by_gs(hps, filtered_hp_gs):
# 	"""
# 	Select the HP from the original GeoJSON/dict file after that the user has selected some GS 

# 	:param hps: HPs in a dict shape (GeoJSON). This is the original file
# 	:param filtered_hp_gs: a list of HPs IDs filtered on GS

# 	:return: GeoJSON/dict with only HP belonging to selected GS
# 	"""
# 	selected_hp_gs = {}
# 	l_new = []
# 	for i in range(len(hps['features'])):
# 	# selected_hp.append(hps['features'][i]['properties']['EAMENA ID'])
# 		for key, value in hps['features'][i]['properties'].items():
# 			# print(key)
# 			# print(value)
# 			if key == 'EAMENA ID' and value in filtered_hp_gs:
# 				filtered_foo = {}
# 				filtered_foo['geometry'] = hps['features'][i]['geometry']
# 				filtered_foo['properties'] = hps['features'][i]['properties']
# 				l_new.append(filtered_foo)
# 	# recreate the structure of the original dataset
# 	selected_hp_gs['features'] = l_new
# 	# l_new[0]
# 	# len(selected_hp_gs['features'])
# 	return(selected_hp_gs)

# def plot_spidergraphs(dict_hps = None, df_mds = None, mylevel = "level3", ncol = 3, verbose = False):
# 	ncol = 3
# 	nrow = math.ceil(len(dict_hps.keys()) / ncol)
# 	fig = make_subplots(rows=nrow, cols=ncol, specs=[[{'type': 'polar'}]*ncol]*nrow, subplot_titles=tuple(dict_hps.keys()))
# 	df_mds_1 = df_mds.copy() # to add +1 later
# 	df_mds_1.loc[df_mds_1['value'] == 0, 'value'] = -1
# 	current_column, current_row = 1, 1
# 	for a_hp in dict_hps.keys():
# 		df = dict_hps[a_hp]
# 		if verbose:
# 			print(a_hp)
# 			print(str(current_row) + " " + str(current_column))
# 		if mylevel == 'level3':
# 			fig.add_trace(go.Scatterpolar(
# 			name =  "  mds",
# 			r = df_mds_1['value'],
# 			theta = df_mds_1['field'],
# 			fill='toself',
# 			fillcolor='red',
# 			line_color='red',
# 			hovertemplate="<br>".join([
# 			"value: %{r}",
# 			"field: %{theta}"]),
# 			showlegend=False), 
# 			current_row, current_column)		
# 			fig.add_trace(go.Scatterpolar(
# 			name = a_hp,
# 			r = df['recorded'],
# 			theta = df['field'],
# 			mode = 'markers',
# 			# marker=dict(color = melted_df_color),
# 			marker_color = "blue",
# 			hovertemplate="<br>".join([
# 			"value: %{r}",
# 			"field: %{theta}"])
# 			), 
# 			current_row, current_column)
# 		else:
# 			fig.add_trace(go.Scatterpolar(
# 			name = a_hp,
# 			r = df['recorded'],
# 			theta = df['field'],
# 			mode = 'markers',
# 			marker_color = "blue",
# 			hovertemplate="<br>".join([
# 			"value: %{r}",
# 			"field: %{theta}"]),
# 			showlegend=False,
# 			text="None"), 
# 			current_row, current_column)
# 		current_column = current_column + 1
# 		# end of line..
# 		if current_column > ncol:
# 			current_row = current_row + 1
# 			current_column = 1
# 	fig.update_layout(
# 		autosize=False,
# 		width=(ncol*700) + 200,
# 		height=(nrow*300) + 100,
# 	)
# 	fig.update_layout(
# 		polar=dict(
# 			radialaxis=dict(
# 				# showline=False,
# 				range=[-1, 1],  # Set the range for the radial axis
# 				tickvals=[0, 1],  # Specify the tick values
# 				ticktext=['0', '1'],  # Specify the corresponding labels
# 			),
# 			# hide labels
# 			angularaxis=dict(
# 				showline=False,          # Set to False to hide the angular axis line
# 				showticklabels=False,    # Set to False to hide the angular axis labels
# 			)
# 		),
# 		showlegend=True
# 	)
# 	fig.show()

# def plot_spidergraphs(dict_hps=None, df_mds=None, mylevel="level3", ncol=3, verbose=False):
#     # ncol = 3
#     nrow = math.ceil(len(dict_hps.keys()) / ncol)
#     fig = make_subplots(rows=nrow, cols=ncol, specs=[[{'type': 'polar'}] * ncol] * nrow, subplot_titles=tuple(dict_hps.keys()))
#     df_mds_1 = df_mds.copy()  # to add +1 later
#     df_mds_1.loc[df_mds_1['value'] == 0, 'value'] = -1
#     current_column, current_row = 1, 1
#     for a_hp in dict_hps.keys():
#         df = dict_hps[a_hp]
#         if verbose:
#             print(a_hp)
#             print(str(current_row) + " " + str(current_column))
#         if mylevel == 'level3':
# 			# mds
#             fig.add_trace(go.Scatterpolar(
#                 name="  mds",
#                 r=df_mds_1['value'],
#                 theta=df_mds_1['field'],
#                 fill='toself',
#                 fillcolor='red',
#                 line_color='red',
#                 hovertemplate="<br>".join([
#                     "value: %{r}",
#                     "field: %{theta}"]),
#                 showlegend=False),
#                 current_row, current_column)
#             fig.add_trace(go.Scatterpolar(
#                 r=df_mds_1['value'],
#                 theta=df_mds_1['field'],
#                 mode='markers',
#                 marker_color="red",
#                 hovertemplate="<br>".join([
#                     "value: %{r}",
#                     "field: %{theta}"]),
#                 name='Markers',  # Provide a name for the marker trace
#                 showlegend=False,  # Show the legend for the marker trace
#             ), current_row, current_column)
#             fig.add_trace(go.Scatterpolar(
#                 name=a_hp,
#                 r=df['recorded'],
#                 theta=df['field'],
#                 mode='markers',
#                 marker_color="blue",
#                 hovertemplate="<br>".join([
#                     "value: %{r}",
#                     "field: %{theta}"])
#             ),
#                 current_row, current_column)
#         else:
#             fig.add_trace(go.Scatterpolar(
#                 name=a_hp,
#                 r=df['recorded'],
#                 theta=df['field'],
#                 mode='markers',
#                 marker_color="blue",
#                 hovertemplate="<br>".join([
#                     "value: %{r}",
#                     "field: %{theta}"]),
#                 showlegend=False,
#                 text="None"),
#                 current_row, current_column)
#         current_column = current_column + 1
#         # end of line..
#         if current_column > ncol:
#             current_row = current_row + 1
#             current_column = 1

#     # Update polar settings for all subplots
#     fig.update_polars(
#         radialaxis=dict(
#             # showline=False,
#             range=[-1, 1],  # Set the range for the radial axis
#             tickvals=[0, 1],  # Specify the tick values
#             ticktext=['0', '1'],  # Specify the corresponding labels
#         ),
#         angularaxis=dict(
#             showline=False,  # Set to False to hide the angular axis line
#             showticklabels=False,  # Set to False to hide the angular axis labels
#         )
#     )
#     fig.update_layout(
#       autosize=False,
#       width=(ncol*500),
#       height=(nrow*300),
#     )
#     fig.show()



# Not Run
# filtered_data = filter_hp_by_gs(selected_hp)

# foo = {'f': {'a': 10, 'b': 'red'}, 'u': {'a': 20, 'b': 'blue'}, 'c': {'a': 30, 'b': 'green'}, 'k': {'a': 40, 'b': 'yellow'}}
# l = ['red', 'yellow']

# aa = db_query("https://database.eamena.org/api/search/export_results?paging-filter=1&tiles=true&format=geojson&reportlink=false&precision=6&total=1567&language=*&advanced-search=%5B%7B%22op%22%3A%22and%22%2C%2234cfea78-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22~%22%2C%22lang%22%3A%22en%22%2C%22val%22%3A%22Sistan%22%7D%2C%2234cfea87-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22e6e6abc5-3470-45c0-880e-8b29959672d2%22%7D%7D%2C%7B%22op%22%3A%22or%22%2C%2234cfea78-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22~%22%2C%22lang%22%3A%22en%22%2C%22val%22%3A%22South%20Khorasan%22%7D%2C%2234cfea87-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22e6e6abc5-3470-45c0-880e-8b29959672d2%22%7D%7D%2C%7B%22op%22%3A%22or%22%2C%2234cfea69-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%2C%2234cfea5d-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%2C%2234cfea73-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%2C%2234cfea43-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%224ed99706-2d90-449a-9a70-700fc5326fb1%22%7D%2C%2234cfea95-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22~%22%2C%22lang%22%3A%22en%22%2C%22val%22%3A%22%22%7D%7D%2C%7B%22op%22%3A%22and%22%2C%2234cfea81-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22gt%22%2C%22val%22%3A%222023-08-01%22%7D%2C%2234cfea4d-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%2C%22d2e1ab96-cc05-11ea-a292-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%2C%2234cfea8a-c2c0-11ea-9026-02e7594ce0a0%22%3A%7B%22op%22%3A%22%22%2C%22val%22%3A%22%22%7D%7D%5D&resource-type-filter=%5B%7B%22graphid%22%3A%2234cfe98e-c2c0-11ea-9026-02e7594ce0a0%22%2C%22name%22%3A%22Heritage%20Place%22%2C%22inverted%22%3Afalse%7D%5D")