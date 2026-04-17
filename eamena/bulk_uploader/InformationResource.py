from crossref.restful import Works
from urllib.parse import urlsplit
import json, uuid

class InformationResource():

    def __init__(self, doi, legacy_uuid=None):
        self.doi = doi
        if '://' in doi:
            u = urlsplit(doi)
            self.doi = str(u.path).lstrip('/')
        works = Works()
        self.info = works.doi(self.doi)
        self.resid = legacy_uuid
        if legacy_uuid == '':
            self.resid = str(uuid.uuid4())
        self.nodes = {}
        self.tiles = []

    @property
    def url(self):
        return "https://doi.org/" + self.doi

    def dump_json(self):

        item = {}
        item['resourceinstance'] = {
            "resourceinstanceid" : self.resid, "graph_id" : self.id, "legacyid" : self.resid}
        item['tiles'] = self.tiles

        business_data = {"resources": []}
        business_data['resources'].append(item)
        return json.dumps({"business_data": business_data})

    def dump_jsonl(self):

        item = {}
        item['resourceinstance'] = {
            "resourceinstanceid" : self.resid, "graph_id" : self.id, "legacyid" : self.resid}
        item['tiles'] = self.tiles

        return json.dumps(item)
