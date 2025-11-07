import re
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(re.sub(r"_", r"-", r"eamena"), "eamena.urls", name="eamena"),
)
