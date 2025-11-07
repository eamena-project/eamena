from django.urls import re_path
from django.conf import settings
from curator.views.curator import Curator, CuratorReport, CuratorReportZenodo, CuratorReportIPFS

uuid_regex = settings.UUID_REGEX

urlpatterns = [
	re_path(r"^curator/", Curator.as_view(), name="curator"),
	re_path(r"^plugins/curator/(?P<searchid>%s)/ipfs" % uuid_regex, CuratorReportIPFS.as_view(), name="curator_report_ipfs"),
	re_path(r"^plugins/curator/(?P<searchid>%s)/zenodo" % uuid_regex, CuratorReportZenodo.as_view(), name="curator_report_zenodo"),
	re_path(r"^plugins/curator/(?P<searchid>%s)" % uuid_regex, CuratorReport.as_view(), name="curator_report"),
]

