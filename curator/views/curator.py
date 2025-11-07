from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.views.plugin import PluginView
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer
from uuid import uuid4
from ..models import CuratedDataset
from ..util.arches import local_api_search
from ..util.curator import is_zenodo_enabled, is_ipfs_enabled
from ..util.zip import save_zip
from ..zenodo.publish import zenodo_publish
from ..zenodo.calculate import zenodo_contributors, zenodo_keywords, zenodo_dates

import json, datetime, pytz, urllib.parse, ipfslib

@method_decorator(csrf_exempt, name="dispatch")
class Curator(View):
	"""This is the class for the main view. Its GET function simply returns a JSON object of previously created CuratedSearch instances
	assigned to the logged-in user. It's generally called from the Knockout Javascript within the Arches UI. If called with a POST,
	it creates a new curated search based on the arguments passed, and redirects to the new istance."""

	def serialize_datasets(self, user_id):
		res = [{'id': str(dataset.search_id), 'label': dataset.search_label, 'results': dataset.search_results_count} for dataset in CuratedDataset.objects.filter(search_user__id=user_id).exclude(search_label='').exclude(search_results_count=0)]
		return res

	def tidy_up(self):
		"""Remove all CuratedDataset objects that have no results and are over 48 hours old, to free up space and keep the database tidy."""
		CuratedDataset.objects.filter(search_results_count=0, updated_time__lte=pytz.utc.localize(datetime.datetime.utcnow()) - datetime.timedelta(hours=48)).delete()

	@cached_property
	def exports_enabled(self):
		ret = []
		if is_zenodo_enabled():
			ret.append('zenodo')
		if is_ipfs_enabled():
			ret.append('ipfs')
		return ret

	def get(self, request):
		user = request.user
		if not user.is_authenticated:
			return JsonResponse({"datasets": []})
		data = {"datasets": self.serialize_datasets(user.id), "exports_enabled": self.exports_enabled}
		return JsonResponse(data)

	def post(self, request):
		user = request.user
		if not user.is_authenticated:
			return JsonResponse({"id": "", "datasets": []})
		request_data = json.loads(request.body)
		if len(request_data['id']) == 0:
			ret = CuratedDataset(search_user=user, search_id=uuid4(), search_results_count=0)
		else:
			ret = get_object_or_404(CuratedDataset, search_id=request_data['id'])
		if user.id != ret.search_user.id:
			raise Http404()
		fields = []
		if 'title' in request_data:
			if len(request_data['title']) > 0:
				ret.search_label = request_data['title']
				fields.append('search_label')
		if 'results' in request_data:
			ret.search_results = int(request_data['results'])
			fields.append('search_results')
		if 'url' in request_data:
			if len(request_data['url']) > 0:
				ret.search_url = request_data['url'].replace('/export_results?', '?')
				fields.append('search_url')
		if 'geojson' in request_data:
			if len(request_data['geojson']) > 0:
				ret.search_results = {"search_url": request_data['geojson'], "features": [], "type": "FeatureCollection"}
				fields.append('search_results')
		if ((len(request_data['id']) == 0) or (len(fields) == 0)):
			ret.save()
		else:
			ret.save(update_fields=fields)

		data = {"id": ret.search_id, "datasets": self.serialize_datasets(user.id), 'exports_enabled': self.exports_enabled}
		return JsonResponse(data)

class CuratorReport(PluginView):
	"""This is an HTML view for an actual CuratedSearch instance. It foregoes any deep Arches/KO integration and opts instead
	for Django's templating system, mainly because I'm not too experienced with Knockout, but also because KO is being
	dropped in favour of Vue.js."""

	@cached_property
	def exports_enabled(self):
		ret = []
		if is_zenodo_enabled():
			ret.append('zenodo')
		if is_ipfs_enabled():
			ret.append('ipfs')
		return ret

	def get(self, request, searchid=None):

		plugin = models.Plugin.objects.get(slug='curator')
		user = request.user
		if not user.is_authenticated:
			raise Http404()
		dataset = get_object_or_404(CuratedDataset, search_id=searchid)
		if user.id != dataset.search_user.id:
			raise Http404()
		resource_graphs = (
			models.GraphModel.objects.exclude(
				pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
			)
			.exclude(isresource=False)
			.exclude(publication=None)
		)
		widgets = models.Widget.objects.all()
		card_components = models.CardComponent.objects.all()
		datatypes = models.DDataType.objects.all()
		map_markers = models.MapMarker.objects.all()
		geocoding_providers = models.Geocoder.objects.all()
		templates = models.ReportTemplate.objects.all()
		plugins = models.Plugin.objects.all()

		context = self.get_context_data(
			plugin=plugin,
			plugin_json=JSONSerializer().serialize(plugin),
			plugins_json=JSONSerializer().serialize(plugins),
			main_script="views/plugin",
			resource_graphs=resource_graphs,
			widgets=widgets,
			widgets_json=JSONSerializer().serialize(widgets),
			card_components=card_components,
			card_components_json=JSONSerializer().serialize(card_components),
			datatypes_json=JSONSerializer().serialize(
				datatypes, exclude=["iconclass", "modulename", "classname"]
			),
			map_markers=map_markers,
			geocoding_providers=geocoding_providers,
			report_templates=templates,
			templates_json=JSONSerializer().serialize(
				templates, sort_keys=False, exclude=["name", "description"]
			),
		)

		context["nav"]["title"] = ""
		context["nav"]["menu"] = False
		context["nav"]["icon"] = plugin.icon
		context["nav"]["title"] = plugin.name

		context['dataset'] = dataset
		context['exports_enabled'] = self.exports_enabled

		return render(request, "views/curator.htm", context)

	def post(self, request, searchid=None):

		user = request.user
		if not user.is_authenticated:
			raise Http404()
		dataset = get_object_or_404(CuratedDataset, search_id=searchid)
		if user.id != dataset.search_user.id:
			raise Http404()

		try:
			data = local_api_search(dataset.search_results['search_url'], user)
		except:
			data = {}
		if len(data) == 0:
			raise Http404()
		if not 'features' in data:
			raise Http404()
		result_count = len(data['features'])
		if result_count == 0:
			raise Http404()

		dataset.search_results = data
		dataset.search_results_count = result_count
		dataset.search_label = request.POST['datasetname']
		dataset.save(update_fields=['search_results', 'search_results_count', 'search_label'])

		return HttpResponseRedirect(request.path)

@method_decorator(csrf_exempt, name="dispatch")
class CuratorReportZenodo(View):
	"""This is a view for Zenodo exports. It returns a 404 if the user is not logged in, or the required Django settings
	are not set."""

	def post(self, request, searchid=None):

		if not is_zenodo_enabled():
			raise Http404()

		user = request.user
		if not user.is_authenticated:
			raise Http404()
		dataset = get_object_or_404(CuratedDataset, search_id=searchid)
		if user.id != dataset.search_user.id:
			raise Http404()
		if not dataset.saved:
			raise Http404()

		if not dataset.zenodo_url is None:
			# If this dataset is already on Zenodo, don't publish it again, just return a link to it
			return HttpResponseRedirect(dataset.zenodo_url)

		filename = slugify(dataset.search_label)
		data = dataset.search_results
		zip_filename = save_zip(data, filename, callback=getattr(settings, 'CURATOR_CALLBACK', None))
		try:
			zd = zenodo_dates(data)
		except:
			zd = []
		zenodo_calculated_fields = [zenodo_contributors(data), zenodo_keywords(data, additional=[]), zd]
		url, doi = zenodo_publish(dataset.search_label, zip_filename, dataset.search_label, zenodo_calculated_fields)

		dataset.zenodo_url = url
		dataset.zenodo_doi = doi
		dataset.save(update_fields=['zenodo_url', 'zenodo_doi'])

		return HttpResponseRedirect(url)

@method_decorator(csrf_exempt, name="dispatch")
class CuratorReportIPFS(View):
	"""This is a view for adding IPFS files. It returns a 404 if the user is not logged in, or the required Django settings
	are not set."""

	def post(self, request, searchid=None):

		if not is_ipfs_enabled():
			raise Http404()

		user = request.user
		if not user.is_authenticated:
			raise Http404()
		dataset = get_object_or_404(CuratedDataset, search_id=searchid)
		if user.id != dataset.search_user.id:
			raise Http404()
		if not dataset.saved:
			raise Http404()

		if not dataset.ipfs_cid is None:
			# If this dataset is already on IPFS, don't publish it again, just return a link to it
			return HttpResponseRedirect(dataset.ipfs_url)

		conn_data = settings.IPFS_NODE
		if len(conn_data) != 2:
			raise Http404()

		filename = slugify(dataset.search_label)
		data = dataset.search_results
		zip_filename = save_zip(data, filename)

		ipfs_api = ipfslib.Connect(conn_data[0], conn_data[1])
		cid = ipfslib.IPFS.add(ipfs_api, zip_filename, mode='b')

		dataset.ipfs_cid = cid
		dataset.save(update_fields=['ipfs_cid'])

		return HttpResponseRedirect(dataset.ipfs_url)

