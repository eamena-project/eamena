from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from arches.app.utils.index_database import index_resources_using_multiprocessing
from arches.app.models import models
import logging, json, sys

class Command(BaseCommand):
	"""
	Command for finding heritage places with duplicate EAMENA numbers, and changing them.

	"""
	def __init__(self):

		self.values = {x['name']['en']: x['pk'] for x in models.ResourceInstance.objects.filter(name__icontains='EAMENA-').values('pk', 'name')}
		self.eamena_tile_id = '34cfe992-c2c0-11ea-9026-02e7594ce0a0'
		self.heritage_place_id = '34cfe98e-c2c0-11ea-9026-02e7594ce0a0'
		self.start_id = 100000

	def new_id(self):

		ret = ''
		while ret == '':
			ret = f'EAMENA-{self.start_id:07}'
			self.start_id = self.start_id + 1
			if ret in self.values:
				ret = ''
		return ret

	def generate_tile(self, eamena_id=None):

		new_id = eamena_id
		if new_id is None:
			new_id = self.new_id()
		new_data = {self.eamena_tile_id: {"en": {"value": new_id, "direction": "ltr"}}}
		tile = models.TileModel(nodegroup=models.NodeGroup.objects.get(pk=self.eamena_tile_id), data=new_data)
		return tile

	def handle(self, *args, **options):

		data = {}
		max_id = 0

		for tile in models.TileModel.objects.filter(nodegroup_id=self.eamena_tile_id):
			eamena_id = tile.data[self.eamena_tile_id]
			if isinstance(eamena_id, dict):
				eamena_id = eamena_id['en']['value']
				if eamena_id is None:
					if 'ar' in eamena_id:
						eamena_id = eamena_id['ar']['value']
			if eamena_id is None:
				continue
			id = int(eamena_id.replace('EAMENA-', ''))
			if id > max_id:
				max_id = id
			if eamena_id not in data:
				data[eamena_id] = []
			data[eamena_id].append(tile)

		ids_required = 1
		for k, v in data.items():
			ids_required = ids_required + (len(v) - 1)

		available = []
		for i in range(self.start_id, max_id):
			if len(available) > ids_required:
				break
			new_id = "EAMENA-{}".format(str(i).zfill(7))
			if new_id in data:
				continue
			available.append(new_id)

		if len(available) < ids_required:
			sys.stderr.write("There are not enough spare EAMENA IDs to relabel the duplicates.\n")
			sys.exit(1)

		rid = []
		for k, v in data.items():
			if len(v) < 2:
				continue
			for x in v[1:]:
				uid = str(x.resourceinstance_id)
				new_id = available.pop(0)
				tile_data = x.data
				tile_data[self.eamena_tile_id] = {'en': {'value': new_id, 'direction': 'ltr'}, 'ar': {'value': new_id, 'direction': 'rtl'}}
				print("{} -> {}".format(k, new_id))
				x.data = tile_data
				x.save()
				if uid in rid:
					continue
				rid.append(uid)

		if len(rid) == 0:
			sys.stdout.write("Nothing to do!\n")
		else:
			index_resources_using_multiprocessing(rid, recalculate_descriptors=True)
