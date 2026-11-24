from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from arches.app.utils.index_database import index_resources_using_multiprocessing
from arches.app.models import models
import logging, json, sys, pyprind

class Command(BaseCommand):
	"""
	Command for fixing the identifier tiles of heritage places.

	"""
	def handle(self, *args, **options):

		hpid = '34cfe98e-c2c0-11ea-9026-02e7594ce0a0'
		tile_ngid = '34cfe992-c2c0-11ea-9026-02e7594ce0a0'
		reindex = []

		resources = models.ResourceInstance.objects.filter(graph_id=hpid)
		bar = pyprind.ProgBar(resources.count(), bar_char="█", stream=sys.stdout)
		for res in resources:

			bar.update(item_id=res)

			tiles = models.TileModel.objects.filter(resourceinstance=res, nodegroup_id=tile_ngid)
			if tiles.count() > 1:

				dbid = str(res.name).strip()
				if tiles.filter(data__icontains=dbid).count() == 1:
					tiles.exclude(data__icontains=dbid).delete()
				continue

			if tiles.count() == 0:

				continue

			dbid = str(res.name).strip()
			ttid = str(tiles.first().data[tile_ngid]['en']['value']).strip()
			if dbid == ttid:
				continue

			if models.ResourceInstance.objects.filter(name=ttid).count() > 0:
				print("{} has inconsistent EAMENA IDs ({}/{})".format(res, dbid, ttid))
				print("...but another resource with the ID {} already exists!".format(ttid))
				sys.exit(1)
				continue

			res.name = ttid
			res.save(update_fields=['name'])
			reindex.append(res.pk)

		index_resources_using_multiprocessing(reindex, recalculate_descriptors=True)
