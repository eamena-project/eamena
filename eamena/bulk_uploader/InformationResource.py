from crossref.restful import Works
from urllib.parse import urlsplit
import json, uuid, datetime

class InformationResource():

    def __init__(self, doi, legacy_uuid=None):
        self.doi = doi
        if '://' in doi:
            u = urlsplit(doi)
            self.doi = str(u.path).lstrip('/')
        works = Works()
        self.info = works.doi(self.doi)
        self.resid = legacy_uuid
        self.graphid = '35b99cb7-379a-11ea-9989-06f597a7d5ce'
        if legacy_uuid is None:
            self.resid = str(uuid.uuid4())
        self.tiles = []
        self.crossref_type_map = {
            "journal-article": "d4e08efa-c0a2-457d-a451-99faab2989b6",
            "book": "346b87f0-b83d-4280-ba42-efa2a0168363",
            "book-chapter": "64ce1fcd-27cc-4203-ab04-df1203397b55",
        }
        self.crossref_bib_map = {
            "title": ['3d0dfc7f-5251-11ea-a3f7-02e7594ce0a0', '3d0dfc7f-5251-11ea-a3f7-02e7594ce0a0'],
            #"author": ['6c0d426a-c5aa-11ea-9026-02e7594ce0a0', '6c0d426a-c5aa-11ea-9026-02e7594ce0a0'],
            "published": ['4eaf1700-5251-11ea-a3f7-02e7594ce0a0', '4eaf16fd-5251-11ea-a3f7-02e7594ce0a0'],
            "publisher-location": ['14e4ffc3-5251-11ea-a3f7-02e7594ce0a0', '14e4ffc6-5251-11ea-a3f7-02e7594ce0a0'],
            "container-title": ['aa8a789e-5251-11ea-a3f7-02e7594ce0a0', 'aa8a789e-5251-11ea-a3f7-02e7594ce0a0'],
            "publisher": ['39bf3874-5252-11ea-a3f7-02e7594ce0a0', '39bf3874-5252-11ea-a3f7-02e7594ce0a0'],
            "volume": ['6a5d14c7-5251-11ea-a3f7-02e7594ce0a0', '6a5d14c7-5251-11ea-a3f7-02e7594ce0a0'],
            "issue": ['99e55b37-5251-11ea-a3f7-02e7594ce0a0', '99e55b37-5251-11ea-a3f7-02e7594ce0a0'],
            "page": ['363f4abf-5252-11ea-a3f7-02e7594ce0a0', '363f4abf-5252-11ea-a3f7-02e7594ce0a0']
        }

    @property
    def url(self):
        return "https://doi.org/" + self.doi

    def create_tile(self, nodegroup_id, parent_id=None, data={}):
        tile_id = str(uuid.uuid4())
        tile_data = {}
        tile_data['tileid'] = tile_id
        tile_data['nodegroup_id'] = str(nodegroup_id)
        if parent_id is None:
            tile_data['parenttile_id'] = None
        else:
            tile_data['parenttile_id'] = str(parent_id)
        tile_data['provisionaledits'] = None
        tile_data['resourceinstance_id'] = self.resid
        tile_data['sortorder'] = 0
        tile_data['data'] = data
        self.tiles.append(tile_data)
        return tile_id

    def generate_tiles(self):
        self.tiles = [] # clear any previous tiles
        bib_root = self.create_tile("49c2fb32-5250-11ea-a3f7-02e7594ce0a0")
        if 'type' in self.info:
            if self.info['type'] in self.crossref_type_map:
                type_root = self.create_tile("54c62e2e-524f-11ea-a3f7-02e7594ce0a0", data={"0800e7a9-5250-11ea-a3f7-02e7594ce0a0": self.crossref_type_map[self.info['type']]})
        url_data = {
                     "7f41dcde-518c-11ea-a3f7-02e7594ce0a0" : {
                        "en" : {
                           "direction" : "ltr",
                           "value" : self.url
                        }
                     },
                     "d25a68cc-5228-11ea-a3f7-02e7594ce0a0" : datetime.datetime.now().strftime("%Y-%m-%d")
                  }
        url_root = self.create_tile("7f41dcde-518c-11ea-a3f7-02e7594ce0a0", data=url_data)
        for k, v in self.info.items():
            if k in self.crossref_bib_map:
                rel = self.crossref_bib_map[k]
                if 'date-parts' in v:
                    v = '-'.join([str(x) for x in v['date-parts'][0]])
                self.create_tile(rel[0], parent_id=bib_root, data={rel[1]: v})

    def dump_json(self):

        if len(self.tiles) == 0:
            self.generate_tiles()
        item = {}
        item['resourceinstance'] = {
            "resourceinstanceid" : self.resid, "graph_id" : self.graphid, "legacyid" : self.resid}
        item['tiles'] = self.tiles

        business_data = {"resources": []}
        business_data['resources'].append(item)
        return json.dumps({"business_data": business_data})

    def dump_jsonl(self):

        if len(self.tiles) == 0:
            self.generate_tiles()
        item = {}
        item['resourceinstance'] = {
            "resourceinstanceid" : self.resid, "graph_id" : self.graphid, "legacyid" : self.resid}
        item['tiles'] = self.tiles

        return json.dumps(item)
