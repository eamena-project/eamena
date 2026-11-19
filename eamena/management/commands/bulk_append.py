from django.conf import settings
from django.core.management.base import BaseCommand
from eamena.bulk_uploader.importers import bulk_append
import json, os, sys, logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
	"""
	Command for appending data into the EAMENA database

	"""
	def add_arguments(self, parser):

		parser.add_argument(
			"-s", "--source", action="store", dest="source", required=True, help="Arches JSON file for appending.",
		)

	def handle(self, *args, **options):

		filename = os.path.abspath(options['source'])
		if not os.path.exists(filename):
			sys.stderr.write("Cannot find the file {}.\n".format(filename))
			sys.exit(1)

		added, updated = bulk_append(filename)
		total = added + updated

		if total <= 0:
			sys.stderr.write("No tiles added.\n")
			sys.exit(1)

		sys.stderr.write("{} tiles added, {} tiled updated.\n".format(added, updated))
