import os
import json
import zipfile
import tempfile

def save_zip(data, filename, callback=None):
	"""Simple function for creating a temporary ZIP file containing a specific set of data. The filename passed is the internal
	filename of the data within the archive. The actual filename of the ZIP file created is returned by the function."""

	# Create a ZIP file
	zip_file = tempfile.mkstemp(prefix=filename, suffix='.zip')
	zip_file_name = os.path.abspath(zip_file[1])
	zipf = zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED)

	# Create the data
	json_data = json.dumps(data, indent=4)
	json_file_name = filename + '.json'

	# Add the JSON file to the ZIP
	zipf.writestr(json_file_name, json_data)

	# Run the callback, if necessary
	if not callback is None:
		callback(zipf, data)

	zipf.close()

	return zip_file_name
