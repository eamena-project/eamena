from django.http import HttpResponse, Http404
from django.shortcuts import render
from .utils import lookup_uuid, uuid_to_base64, base64_to_uuid
import json

def resolver(request, uri_id):

	data = []
	ret = []

	input_string = uri_id.rstrip('/')

	if len(input_string) > 0:

		if len(input_string) < 32:
			data = lookup_uuid(base64_to_uuid(input_string))

		elif len(input_string) <= 36:
			data = lookup_uuid(input_string)

	if len(data) == 0:
		raise Http404()

	for item in data:
		v = [str(item.__module__), str(item.__class__.__name__)]
		if hasattr(item, 'value'):
			v.append(str(item.value))
		ret.append(v)

	return HttpResponse(json.dumps(ret), content_type='application/json')
