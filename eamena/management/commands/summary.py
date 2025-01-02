from django.contrib.auth.models import User
from django.http import HttpRequest
from arches.app.models import models
from arches.app.models.concept import Concept, get_preflabel_from_valueid, get_valueids_from_concept_label
from arches.app.views import search
from django.core.management.base import BaseCommand
from eamena.bulk_uploader import HeritagePlaceBulkUploadSheet, GridSquareBulkUploadSheet
from eamena.statistics import SummaryGenerator
from geomet import wkt
import json, os, sys, logging, re, uuid, hashlib, datetime, warnings

logger = logging.getLogger(__name__)

def relations(graphid, role=None):

	if role is None:
		ret = models.ResourceInstance.objects.filter(graph_id=graphid).distinct()
	else:
		ret = models.ResourceInstance.objects.filter(graph_id=graphid, resxres_resource_instance_ids_to__resourceinstanceidfrom__tilemodel__data__icontains=role).distinct()
	return ret

def get_roles(sg):

	nodeid = 'd2e1ab96-cc05-11ea-a292-02e7594ce0a0'
	ret = {}
	for item in sg.find_concepts(nodeid):
		id = item['valueid']
		ret[id] = item
	return ret

def get_countries(sg):

	nodeid = '34cfea43-c2c0-11ea-9026-02e7594ce0a0'
	ret = {}
	for item in sg.find_concepts(nodeid):
		id = item['valueid']
		ret[id] = item
	return ret

def get_grid_squares(sg):

	grid_id = '77d18973-7428-11ea-b4d0-02e7594ce0a0'
	grid_id_id = 'b3628db0-742d-11ea-b4d0-02e7594ce0a0'
	return sg.find_objects(grid_id, grid_id_id)

def get_people(sg):

	p_id = 'e98e1cee-c38b-11ea-9026-02e7594ce0a0'
	p_id_id = 'e98e1cfe-c38b-11ea-9026-02e7594ce0a0'
	return sg.find_objects(p_id, p_id_id)

def get_summaries():

	gen = SummaryGenerator()

	grid_lookup = get_grid_squares(gen)
	people_lookup = get_people(gen)
	country_lookup = get_countries(gen)
	role_lookup = get_roles(gen)

	properties = [
		['5297fa9f-8e16-11ea-a6a6-02e7594ce0a0', 'ID'],
		['34cfe992-c2c0-11ea-9026-02e7594ce0a0', 'ID'],
		['34cfea81-c2c0-11ea-9026-02e7594ce0a0', 'Date'],
		['947ccaa3-1ea5-11eb-af98-02e7594ce0a0', 'Date'],
		['5297faa9-8e16-11ea-a6a6-02e7594ce0a0', 'Actor'],
		['34cfea8a-c2c0-11ea-9026-02e7594ce0a0', 'Actor'],
		['d2e1ab96-cc05-11ea-a292-02e7594ce0a0', 'Role'],
		['40c49e8c-cc08-11ea-a292-02e7594ce0a0', 'Role'],
		['34cfea43-c2c0-11ea-9026-02e7594ce0a0', 'Country'],
		['61ad1129-c7f1-11ea-a292-02e7594ce0a0', 'Country'],
		['34cfea5d-c2c0-11ea-9026-02e7594ce0a0', 'Grid'],
		['61ad1121-c7f1-11ea-a292-02e7594ce0a0', 'Grid']
	]
	for prop in properties:
		gen.add_property(prop[1], prop[0])

	ret = {}
	sum = gen.get_summaries()

	for k in sum.keys():
		kk = str(k)
		item = sum[kk]
		if 'ID' in item:
			id = item['ID']
			if isinstance(id, dict):
				if 'en' in id:
					item['ID'] = id['en']['value']
		if 'Grid' in item:
			if isinstance(item['Grid'], str):
				if item['Grid'] in grid_lookup:
					id = item['Grid']
					label = grid_lookup[id]['label']
					if isinstance(label, dict):
						if 'en' in label:
							label = label['en']['value']
					item['Grid'] = {"id": id, "label": label}
			if isinstance(item['Grid'], list):
				grids = []
				for id in list(dict.fromkeys(item['Grid'])):
					if id in grid_lookup:
						label = grid_lookup[id]['label']
						if isinstance(label, dict):
							if 'en' in label:
								label = label['en']['value']
						grids.append({"id": id, "label": label})
				if len(grids) == 1:
					item['Grid'] = grids[0]
				else:
					item['Grid'] = grids
		if 'Actor' in item:
			if isinstance(item['Actor'], str):
				if item['Actor'] in people_lookup:
					id = item['Actor']
					label = people_lookup[id]['label']
					if isinstance(label, dict):
						if 'en' in label:
							label = label['en']['value']
					item['Actor'] = {"id":id, "label": label}
			if isinstance(item['Actor'], list):
				actors = []
				for id in list(dict.fromkeys(item['Actor'])):
					if id in people_lookup:
						if isinstance(label, dict):
							if 'en' in label:
								label = label['en']['value']
						label = people_lookup[id]['label']
						actors.append({"id":id, "label": label})
				if len(actors) == 1:
					item['Actor'] = actors[0]
				else:
					item['Actor'] = actors
		if 'Country' in item:
			if isinstance(item['Country'], str):
				if item['Country'] in country_lookup:
					id = item['Country']
					label = country_lookup[id]['label']
					if isinstance(label, dict):
						if 'en' in label:
							label = label['en']['value']
					item['Country'] = {"id": id, "label": label}
			if isinstance(item['Country'], list):
				countries = []
				for id in list(dict.fromkeys(item['Country'])):
					if id in country_lookup:
						label = country_lookup[id]['label']
						if isinstance(label, dict):
							if 'en' in label:
								label = label['en']['label']
						countries.append({"id": id, "label": label})
				if len(countries) == 1:
					item['Country'] = countries[0]
				else:
					item['Country'] = countries
		if 'Role' in item:
			if isinstance(item['Role'], str):
				if item['Role'] in role_lookup:
					id = item['Role']
					label = role_lookup[id]['label']
					if isinstance(label, dict):
						if 'en' in label:
							label = label['en']['value']
					item['Role'] = {"id": id, "label": label}
			if isinstance(item['Role'], list):
				roles = []
				for id in list(dict.fromkeys(item['Role'])):
					if id in role_lookup:
						label = role_lookup[id]['label']
						if isinstance(label, dict):
							if 'en' in label:
								label = label['en']['value']
						roles.append({"id": id, "label": label})
				if len(roles) == 1:
					item['Role'] = roles[0]
				else:
					item['Role'] = roles
		ret[kk] = item
	return ret

class Command(BaseCommand):
	"""
	Command for extracting information useful for reporting purposes.

	"""

	def handle(self, *args, **options):

		marea = '270e5b36-4d18-4b6e-a7ee-c49e3d301620'
		eamena = 'b3c1325c-e837-46ab-9e71-514b42de3cba'

		summary = get_summaries()
		print(json.dumps(summary))

