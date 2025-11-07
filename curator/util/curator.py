from django.conf import settings

def is_ipfs_enabled():
	"""Checkss for presence of required values in settings, if any are absent then we return false"""

	for setting_id in ['IPFS_NODE', 'IPFS_WEB_PROXY']:
		if not hasattr(settings, setting_id):
			return False
	return True

def is_zenodo_enabled():
	"""Checks for presence of required values in settings, if any are absent then we return false"""

	for setting_id in ['ZENODO_ACCESS_TOKEN', 'ZENODO_URL', 'ZENODO_METADATA']:
		if not hasattr(settings, setting_id):
			return False
	return True
