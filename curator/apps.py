from django.apps import AppConfig

class CuratorConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'curator'
	is_arches_application = True
