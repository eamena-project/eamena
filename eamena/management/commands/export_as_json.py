from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from arches.app.models.resource import Resource
import logging, json, os, sys, pyprind

class Command(BaseCommand):
	"""
	Command for exporting the entire database's JSON representations as one big JSONL dump
	"""
	def add_arguments(self, parser):

		parser.add_argument("-d", "--destination", action="store", required=True)
		parser.add_argument("-s", "--source", action="store", default=None, required=False)

	def handle(self, *args, **options):

		output_file = os.path.abspath(options['destination'])
		input_file = ''
		ids = []
		if 'source' in options:
			input_file = options['source']
			if input_file is not None:
				with open(input_file, 'r') as fp:
					for l in fp.readlines():
						ids.append(l.strip())
		if len(ids) == 0:
			data = Resource.objects.all()
		else:
			data = Resource.objects.filter(pk__in=ids)

		c = data.count()
		with open(output_file, 'w') as fp:
			bar = pyprind.ProgBar(c, bar_char='█', stream=self.stdout)
			for res in data:
				fp.write("{}\n".format(json.dumps(res.to_json())))
				bar.update()
