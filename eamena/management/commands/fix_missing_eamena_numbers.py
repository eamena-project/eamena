from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from arches.app.utils.index_database import index_resources_using_multiprocessing
from arches.app.models import models
import logging, json, sys

class Command(BaseCommand):
	"""
	Command for finding heritage places missing EAMENA numbers, and assigning them.

	"""
	def __init__(self):

		self.values = {x['name']['en']: x['pk'] for x in models.ResourceInstance.objects.filter(name__icontains='EAMENA-').values('pk', 'name')}
		self.eamena_tile_id = '34cfe992-c2c0-11ea-9026-02e7594ce0a0'
		self.heritage_place_id = '34cfe98e-c2c0-11ea-9026-02e7594ce0a0'
		self.start_id = 100000

	def generate_id_tile(self, eamena_id):

		new_data = {self.eamena_tile_id: {"en": {"value": eamena_id, "direction": "ltr"}, "ar": {"value": eamena_id, "direction": "rtl"}}}
		tile = models.TileModel(nodegroup=models.NodeGroup.objects.get(pk=self.eamena_tile_id), data=new_data)
		return tile

	def handle(self, *args, **options):

		data = []
		max_id = 0

		# Remove ID tiles that have no EAMENA number
		models.TileModel.objects.filter(nodegroup_id=self.eamena_tile_id).exclude(data__icontains='EAMENA-').delete()

		rid = []
		for res in models.ResourceInstance.objects.filter(graph_id=self.heritage_place_id):
			if 'EAMENA-' not in res.name.value:
				rid.append(res.pk)
				continue
			eamena_id = json.loads(res.name.value)
			if isinstance(eamena_id, dict):
				if not isinstance(eamena_id['en'], dict):
					eamena_id = eamena_id['en']
				else:
					eamena_id = eamena_id['en']['value']
				if eamena_id is None:
					if 'ar' in eamena_id:
						eamena_id = eamena_id['ar']['value']
			if eamena_id is None:
				rid.append(res.pk)
				continue
			data.append(eamena_id)
			id = int(eamena_id.replace('EAMENA-', ''))
			if id > max_id:
				max_id = id

		ids_required = len(rid) + 1

		available = []
		for i in range(self.start_id, max_id):
			if len(available) > ids_required:
				break
			new_id = "EAMENA-{}".format(str(i).zfill(7))
			if new_id in data:
				continue
			available.append(new_id)

		if len(available) < ids_required:
			sys.stderr.write("There are not enough spare EAMENA IDs to assign.\n")
			sys.exit(1)

		for res in models.ResourceInstance.objects.filter(pk__in=rid):
			new_id = available.pop(0)

			# If an ID tile exists, it's just not being indexed, so leave this record alone.
			if models.TileModel.objects.filter(resourceinstance=res, nodegroup_id='34cfe992-c2c0-11ea-9026-02e7594ce0a0').count() > 0:
				continue

			print("{} -> {}".format(res.pk, new_id))
			new_tile = self.generate_id_tile(new_id)
			new_tile.resourceinstance = res
			new_tile.save()

		if len(rid) == 0:
			sys.stdout.write("Nothing to do!\n")
		else:
			index_resources_using_multiprocessing(rid, recalculate_descriptors=True)

