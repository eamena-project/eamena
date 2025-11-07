from citations.zenodo import zenodo_map, zenodo_statistics_hp
from tempfile import mkstemp
import os

def zip_callback(zipf, data):

	image_file = mkstemp()
	image_filename = image_file[1]
	suffixes = ['_map_local.png', '_map_national.png', '_map_eamena_scope.png', '_stat_hp_conditions.png', '_stat_hp_functions.png']

	zenodo_map(image_filename, data)
	zenodo_statistics_hp(image_filename, data)
	for item in suffixes:
		filename = image_filename + item
		zip_filename = "eamena" + item
		if os.path.exists(filename):
			zipf.write(filename, zip_filename)
			os.unlink(filename)

