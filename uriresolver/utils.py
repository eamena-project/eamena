from django.apps import apps
from base64 import b64encode, b64decode
from uuid import UUID, uuid4

def lookup_uuid(in_uuid):

	ret = []
	for m in apps.get_models():
		if not(m.__module__.startswith('arches')):
			continue
		if m._meta.pk.get_internal_type() != "UUIDField":
			continue
		ob = m.objects.filter(pk=in_uuid)
		ret += ob

	return ret

def uuid_to_base64(id):

	if isinstance(id, str):
		return b64encode(UUID(id).bytes).decode('utf8').replace('+', '-').replace('/', '_').rstrip('=')

	if isinstance(id, UUID):
		return b64encode(id.bytes).decode('utf8').replace('+', '-').replace('/', '_').rstrip('=')

	return None

def base64_to_uuid(x):

	return UUID(bytes=b64decode(x.replace('-', '+').replace('_', '/').ljust(24, '=')))
