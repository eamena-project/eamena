from django.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from eamena.bulk_uploader.views import upload_spreadsheet, validate, convert, download_template, landing_page

uuid_regex = settings.UUID_REGEX

urlpatterns = [
	re_path(r"^$", landing_page, name="bulk_upload"),
	re_path(r"^excel-upload$", upload_spreadsheet, name="bulk_upload"),
	re_path(r"^validate$", validate, name="bulk_upload_validate"),
	re_path(r"^convert$", convert, name="bulk_upload_convert"),
	re_path(r"^templates/(?P<graphid>%s)\.xlsx$" % uuid_regex, download_template, name="download_template"),
]
