from django.conf import settings
from datetime import datetime
from collections import Counter
import pandas as pd
import pytz

def summed_values(data, fieldname = None):
	"""
	Creates a dataframe summing the number of occurences for a given field

	::param data: dictionary of Heritage Places (JSON)
	"""

	l = list()
	for i in range(len(data['features'])):
		l.append(data['features'][i]['properties'][fieldname])
	split_names = [name.strip() for item in l if item is not None for name in item.split(',')]
	name_counts = Counter(split_names)
	df = pd.DataFrame.from_dict(name_counts, orient='index').reset_index()
	df = df.rename(columns={'index': 'name', 0: 'n_hp'})
	df = df.sort_values('n_hp', ascending=False)
	return df

def zenodo_contributors(data):
	"""
	Creates dictionary of contributors, filling a dictionary layout (`contributors_layout_*`). Contributors are sorted according to the total number of their name occurences in the selected `fieldname`.

	:param data: dictionary of Heritage Places (JSON)
	"""
	values = {}
	for fieldname in settings.ZENODO_METADATA['contributors']['fields']:
		for feature in data['features']:
			if fieldname in feature['properties']:
				if feature['properties'][fieldname] is None:
					continue
				for name in feature['properties'][fieldname].strip().split(','):
					name_s = name.strip()
					if name_s == '':
						continue
					if name_s == 'None':
						continue
					if not name_s in values:
						values[name_s] = 0
					values[name_s] = values[name_s] + 1
	ret = []
	for item in list(x[0] for x in sorted(list([k, v] for k, v in values.items()), key=lambda x: x[1], reverse=True)):
		v = settings.ZENODO_METADATA['contributors']['layout'].copy()
		v['name'] = item
		ret.append(v)
	return ret

def zenodo_keywords(data, additional = None):
	"""
	Creates a list of keywords with a constant basis (`constant`) and parsed supplementary `fields` (for space-time keywords)

	:param data: dictionary of Heritage Places (JSON)
	:param additional: additional keywords provided by the user
	"""
	try:
		constant = settings.ZENODO_METADATA['keywords']['static']
	except:
		constant = []
	try:
		fields = settings.ZENODO_METADATA['keywords']['fields']
	except:
		fields = []
	KEYWORDS = list()
	KEYWORDS = KEYWORDS + constant + additional
	if all(elem in list(data['features'][0]['properties'].keys()) for elem in fields):
	# HPs
		for fieldname in fields:
			df = summed_values(data, fieldname)
			KEYWORDS = KEYWORDS + df['name'].tolist()
		try:
			KEYWORDS.remove('Unknown')
		except ValueError:
			pass
		try:
			KEYWORDS.remove('')
		except ValueError:
			pass
	return KEYWORDS

def zenodo_dates(data):
	"""
	Get the min and the max of dates recorded in `fields`

	:param data: dictionary of Heritage Places (JSON)
	"""
	try:
		fields = settings.ZENODO_METADATA['dates']['fields']
	except:
		fields = []
	if all(elem in list(data['features'][0]['properties'].keys()) for elem in fields):
	# HPs
		ldates = list()
		for fieldname in fields:
			df = summed_values(data, fieldname)
			ldates = ldates + df['name'].tolist() 
		if 'None' in ldates:
			ldates.remove('None')
		date_objects = [datetime.strptime(date, '%Y-%m-%d') for date in ldates]
		min_date = min(date_objects)
		max_date = max(date_objects)
		min_date_str = min_date.strftime('%Y-%m-%d')
		max_date_str = max_date.strftime('%Y-%m-%d')
		DATES = [{'type': 'created', 'start': min_date_str, 'end': max_date_str}]
		return DATES
	else:
	# not HPs (GS, ...)
		now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone(settings.TIME_ZONE))
		DATES = [{'type': 'created', 'start': now.strftime("%Y-%m-%d"), 'end': now.strftime("%Y-%m-%d")}]
		return DATES
