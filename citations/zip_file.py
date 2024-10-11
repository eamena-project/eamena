import os
import json
import zipfile
import tempfile
import numpy as np

# needed to export as JSON
class NpEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		if isinstance(obj, np.floating):
			return float(obj)
		if isinstance(obj, np.ndarray):
			return obj.tolist()
		return json.JSONEncoder.default(self, obj)

def save_zip(data, filename):

	# Hack to normalise a numpy JSON data structure
	json_string = json.dumps(data, cls=NpEncoder)
	json_string = json.loads(json_string)

	# Create a ZIP file using NamedTemporaryFile
	zip_file = tempfile.mkstemp(prefix=filename, suffix='.zip')
	zip_file_name = os.path.abspath(zip_file[1])
	zipf = zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED)

	# Create the JSON file and write the data to it
	with tempfile.NamedTemporaryFile(prefix=filename, suffix='.json', mode='w') as json_file:
		json.dump(json_string, json_file, indent=4)
		json_file_name = json_file.name
		# Add the JSON file to the ZIP
		zipf.write(json_file_name, filename + '.json')
		zipf.close()

	return zip_file_name
