from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from eamena.views.resource import ResourceEditorView
from eamena.views import bulk_uploader
uuid_regex = settings.UUID_REGEX

#urlpatterns = [
#    url(r'^', include('arches.urls')),
#] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
#    url(r"^resource/(?P<resourceid>%s)$" % uuid_regex, ResourceEditorView.as_view(), name="resource_editor"),
    url(r"^bulk-upload$", bulk_uploader.index),
    url(r"^bulk-upload/excel-upload$", bulk_uploader.upload_spreadsheet, name="bulk_upload"),
    url(r"^bulk-upload/validate$", bulk_uploader.validate, name="bulk_upload_validate"),
    url(r"^bulk-upload/convert$", bulk_uploader.convert, name="bulk_upload_convert"),
    url(r"^bulk-upload/templates/(?P<graphid>%s)\.xlsx$" % uuid_regex, bulk_uploader.download_template, name="download_template"),
    url(r'^', include('arches.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#if settings.SHOW_LANGUAGE_SWITCH is True:
#    urlpatterns = i18n_patterns(*urlpatterns)
