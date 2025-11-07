from arches.app.models import models
from arches.app.models.concept import Concept, get_preflabel_from_valueid, get_valueids_from_concept_label
from arches.app.models.system_settings import settings

class SummaryGenerator:

	def __init__(self):

		self._properties = []
		self._cached_summaries = {}

	def missing_fields(self, resourceid):
		ret = [x for x in settings.MINIMUM_DATA_STANDARD]
		for x in list(models.TileModel.objects.filter(resourceinstance_id=resourceid).values_list('data')):
			for y in x:
				for z in list(y.keys()):
					zz = str(z)
					if zz in ret:
						if not y[zz] is None:
							ret.remove(zz)
					if len(ret) == 0:
						return ret
		return ret

	def node_name(self, nodeid):
		try:
			return models.Node.objects.filter(pk=nodeid).first().name
		except:
			return nodeid

	def find_concepts(self, nodeid):

		ret = []
		node = models.Node.objects.get(nodeid=nodeid)

		if 'rdmCollection' in node.config:
			conceptid = node.config['rdmCollection']
			if not(conceptid is None):
				for item in Concept().get_e55_domain(conceptid):
					valueobj = get_preflabel_from_valueid(item['id'], 'en')
					valueid = valueobj['id']
					label = get_preflabel_from_valueid(valueid, 'en')
					ret.append({'valueid': valueid, 'conceptid': item['conceptid'], 'label': label['value']})
		return ret

	def find_objects(self, graph_id, identifier_id):

		ret = {}
		for item in models.TileModel.objects.filter(resourceinstance__graph_id=graph_id, nodegroup_id=identifier_id):
			id = str(item.resourceinstance_id)
			value = {'id': id}
			if item.data:
				if isinstance(item.data, (dict)):
					if identifier_id in item.data:
						label = item.data[identifier_id]
						if isinstance(label, dict):
							if 'en' in label:
								label = label['en']['value']
						value['label'] = label
			ret[id] = value
		return ret

	def add_property(self, label, uuid):

		self._properties.append([str(uuid), str(label)])
		self._cached_summaries = {}

	def get_summaries(self):

		if len(self._cached_summaries) > 0:
			return self._cached_summaries

		ret = {}
		for prop in self._properties:
			k = prop[0]
			label = prop[1]
			for tile in models.TileModel.objects.filter(data__icontains=k): # , nodegroup_id='34cfea2e-c2c0-11ea-9026-02e7594ce0a0'):
				rid = str(tile.resourceinstance_id)
				if not(rid in ret):
					ri = models.ResourceInstance.objects.get(resourceinstanceid=rid)
					ret[rid] = {'AddedToDatabase': ri.createdtime.strftime("%Y-%m-%d")}
				data = tile.data[k]
				if data is None:
					continue
				if isinstance(data, (list)):
					if len(data) == 0:
						continue
					data = data[0]
				if isinstance(data, (dict)):
					if 'resourceId' in data:
						data = data['resourceId']
				if label in ret[rid]:
					if isinstance(ret[rid][label], list):
						ret[rid][label].append(data)
						continue
					if isinstance(ret[rid][label], str):
						ret[rid][label] = [ret[rid][label], data]
						continue
				else:
					ret[rid][label] = data

		for kk in ret.keys():
			k = str(kk)
			if 'Date' in ret[k]:
				continue
			if 'AddedToDatabase' in ret[k]:
				ret[k]['Date'] = ret[k]['AddedToDatabase']

		self._cached_summaries = ret
		return ret

