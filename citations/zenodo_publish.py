from django.conf import settings
import requests
import json
import os

METADATA = {
	 'metadata': {
		 'title': '',
		 'description': '',
		 'upload_type': 'dataset',
		 'license': 'cc-by',
		 'subjects': [{"term": "Cultural property", "identifier": "https://id.loc.gov/authorities/subjects/sh97000183.html", "scheme": "url"}],
		 'method': 'EAMENA data entry methodology',
		 'creators': [{'name': "EAMENA database",
					   'affiliation': "University of Oxford, University of Southampton"}],
		 'contributors': [],
		 'keywords': [],
		 'dates': {}
		#  'communities': "[{'identifier': 'eamena'}]",
		#  'related_identifiers': zn.zenodo_related_identifiers()
	 }
 }

def create_zenodo_bucket(params): 
	r = requests.post(settings.ZENODO_URL,
					params=params,
					json={})
		
	deposition_id = r.json()['id']
	bucket_url = r.json()["links"]["bucket"]
	return deposition_id, bucket_url

def add_zenodo_data(bucket_url, params, filename):
	if os.path.exists(filename):
		zip_file_name = filename
	else:
		zip_file_name = filename + ".zip"
	with open(zip_file_name, "rb") as fp:
		r = requests.put(
			"%s/%s" % (bucket_url, zip_file_name.split('/')[-1]),
			data = fp,
			params = params,
		)

def add_zenodo_metadata(deposition_id, params, metadata):
	r = requests.put('%s/%s' % (settings.ZENODO_URL, deposition_id),
					params = params,
					data = json.dumps(metadata))

def zenodo_publish(title, filename, description, zenodo_calculated_fields):
	params = {'access_token': settings.ZENODO_ACCESS_TOKEN}
	deposition_id, bucket_url = create_zenodo_bucket(params)
	add_zenodo_data(bucket_url, params, filename)
	METADATA['metadata']['title'] = title
	METADATA['metadata']['description'] = description
	METADATA['metadata']['contributors'] = zenodo_calculated_fields[0]
	METADATA['metadata']['keywords'] = zenodo_calculated_fields[1]
	METADATA['metadata']['dates'] = zenodo_calculated_fields[2]
	add_zenodo_metadata(deposition_id, params, METADATA)
	r = requests.post('%s/%s/actions/publish' % (settings.ZENODO_URL, deposition_id),
						params={'access_token': settings.ZENODO_ACCESS_TOKEN} )

	r = requests.get(settings.ZENODO_URL,
				  params={'access_token': settings.ZENODO_ACCESS_TOKEN})
	print(r.json()[0]['links']['html'])
	return r.json()[0]['links']['html']
