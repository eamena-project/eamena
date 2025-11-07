from django.conf import settings
import requests
import json
import os

def create_zenodo_bucket(params):

	r = requests.post(settings.ZENODO_URL, params=params, json={})
	deposition_id = r.json()['id']
	bucket_url = r.json()["links"]["bucket"]

	return deposition_id, bucket_url

def add_zenodo_data(bucket_url, params, filename):

	if os.path.exists(filename):
		zip_file_name = filename
	else:
		zip_file_name = filename + ".zip"

	with open(zip_file_name, "rb") as fp:
		r = requests.put("%s/%s" % (bucket_url, zip_file_name.split('/')[-1]), data = fp, params = params)

def add_zenodo_metadata(deposition_id, params, metadata):

	r = requests.put('%s/%s' % (settings.ZENODO_URL, deposition_id), params = params, data = json.dumps(metadata))

def zenodo_publish(title, filename, description, extra_metadata=None):

	metadata = {'metadata': settings.ZENODO_METADATA['metadata']}

	params = {'access_token': settings.ZENODO_ACCESS_TOKEN}
	deposition_id, bucket_url = create_zenodo_bucket(params)
	add_zenodo_data(bucket_url, params, filename)
	metadata['metadata']['title'] = title
	metadata['metadata']['description'] = description
	if isinstance(extra_metadata, dict):
		for k, v in extra_metadata.items():
			metadata['metadata'][str(k)] = v
	if isinstance(extra_metadata, list):
		if len(extra_metadata) > 0:
			metadata['metadata']['contributors'] = extra_metadata[0]
		if len(extra_metadata) > 1:
			metadata['metadata']['keywords'] = extra_metadata[1]
		if len(extra_metadata) > 2:
			metadata['metadata']['dates'] = extra_metadata[2]
	add_zenodo_metadata(deposition_id, params, metadata)
	r = requests.post('%s/%s/actions/publish' % (settings.ZENODO_URL, deposition_id), params={'access_token': settings.ZENODO_ACCESS_TOKEN} )
	data = r.json()

	return data['links']['html'], data['links']['doi']
