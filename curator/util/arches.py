from django.test import RequestFactory
from arches.app.views.api import SearchExport
import json

def local_api_search(url, user):
	"""Uses the RequestFactory from Django's test framework to make a local call to the Arches API. This ensures all HTTP
	traffic is kept local, ensures a logged in user, and prevents any cross-site nonsense, making it more secure than
	simply doing an HTTP call, as with the EAMENA Citation plugin."""

	rf = RequestFactory()
	view = SearchExport.as_view()
	r = rf.get(url)
	r.user = user

	try:
		return json.loads(view(r).content)
	except:
		return {}
