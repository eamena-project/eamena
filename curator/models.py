from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class CuratedDataset(models.Model):
	"""This is a class representing a curated dataset, which is effectively a saved search
	that a user can create. It keeps a record of the search performed, which user performed
	the search and when, as well as a GeoJSON representation of the results, because these
	may change if the user or time is different."""
	search_id = models.UUIDField(primary_key=True)
	search_label = models.CharField(max_length=128, default='', blank=True, null=False)
	search_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='curated_datasets')
	"""The user who was logged in when this search was performed."""
	search_url = models.URLField(max_length=2048)
	"""The URL called in order to instigate this search."""
	search_results = models.JSONField(default=dict)
	"""A GeoJSON object representing the results of this search, as they would have been presented to the user."""
	search_results_count = models.IntegerField()
	"""The number of results in this dataset, stored so it can be queried later without needing a re-count."""
	created_time = models.DateTimeField(auto_now_add=True)
	"""A datetime representing the time this Event object was created."""
	updated_time = models.DateTimeField(auto_now=True)
	"""A datetime representing the time this Event object was last modified."""

	zenodo_url = models.URLField(max_length=512, null=True, blank=True)
	"""The URL at which this dataset appears on Zenodo."""
	zenodo_doi = models.URLField(max_length=128, blank=True, null=True)
	"""The DOI referring to this dataset on Zenodo."""

	ipfs_cid = models.SlugField(max_length=128, null=True, blank=True)
	"""The CID referring to this dataset on IPFS."""

	@property
	def saved(self):
		"""Returns true if the search has actually been carried out, false if the object has been created but not finalised.
		This is necessary because creating a CuratedDataset from the UI is a two-step process."""
		return not('search_url' in self.search_results)

	@property
	def ipfs_url(self):
		"""Returns a web URL from which the IPFS dataset is available. Requres the IPFS_WEB_PROXY setting to be set."""
		url = ''
		if self.ipfs_cid:
			try:
				url = settings.IPFS_WEB_PROXY.replace('%CID%', self.ipfs_cid)
			except:
				url = ''
		if url == '':
			return 'https://ipfs.tech/'
		return url

	def table_headers(self):
		"""Returns the headings row of a tabular representation of the data."""
		if not self.saved:
			return []
		if not 'features' in self.search_results:
			return []
		ret = []
		for feature in self.search_results['features']:
			if not 'properties' in feature:
				continue
			for kk in feature['properties'].keys():
				k = str(kk)
				if k in ret:
					continue
				if feature['properties'][k] is None:
					continue
				ret.append(k)
		return ret

	def table_data(self):
		"""Returns the data in the saved CuratedDataset in a tabular form, for display as an HTML table."""
		headers = self.table_headers()
		if len(headers) == 0:
			return []
		ret = []
		for feature in self.search_results['features']:
			if not 'properties' in feature:
				continue
			row = []
			for k in headers:
				if k in feature['properties']:
					if feature['properties'][k] is None:
						row.append('')
					else:
						row.append(feature['properties'][k])
				else:
					row.append('')
			ret.append(row)
		return ret

	class Meta:

		db_table = "curated_dataset"
		managed = True
		verbose_name = 'curated dataset'
		verbose_name_plural = 'curated datasets'
