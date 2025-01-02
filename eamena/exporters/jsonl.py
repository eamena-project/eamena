import os
import sys
import csv
import json
import uuid
import datetime
from tempfile import TemporaryFile
from time import time
from copy import deepcopy
from os.path import isfile, join
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resource_graphs.importer import import_graph as resourceGraphImporter
from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.resource import Resource
from arches.app.models.models import ResourceInstance
from arches.app.models.models import FunctionXGraph
from arches.app.models.models import Node
from arches.app.models.models import NodeGroup
from arches.app.models.models import GraphModel
from arches.app.models.system_settings import settings
from django.core.exceptions import ValidationError
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.formats.format import Writer
from arches.app.utils.data_management.resources.formats.format import Reader
from arches.app.utils.data_management.resources.formats.format import ResourceImportReporter


class JsonLWriter(Writer):
        def __init__(self, **kwargs):
                self.type_cache = {}
                super(JsonLWriter, self).__init__(**kwargs)

        def nodetype(self, id):
                sid = str(id)
                if sid in self.type_cache:
                        return self.type_cache[sid]
                try:
                        node = Node.objects.get(nodeid=sid)
                except:
                        self.type_cache[sid] = ''
                        return ''
                self.type_cache[sid] = str(node.datatype)
                return self.type_cache[sid]

        def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
                super(JsonLWriter, self).write_resources(graph_id=graph_id, resourceinstanceids=resourceinstanceids, **kwargs)

                json_for_export = []
                resources = []
                relations = []
                export = {}
                export["business_data"] = {}

                if str(self.graph_id) != settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                        json_name = os.path.join("{0}.{1}".format(self.file_name, "jsonl"))
                else:
                        json_name = os.path.join("{0}".format(os.path.basename(settings.SYSTEM_SETTINGS_LOCAL_PATH)))

                dest = TemporaryFile(mode='w+', suffix='.jsonl')

                for resourceinstanceid, tiles in self.resourceinstances.items():
                        resourceinstanceid = uuid.UUID(str(resourceinstanceid))
                        resource = {}
                        resource["tiles"] = tiles
                        resource["resourceinstance"] = ResourceInstance.objects.get(resourceinstanceid=resourceinstanceid)
                        jl = JSONDeserializer().deserialize(JSONSerializer().serialize(JSONSerializer().serializeToPython(resource)))

                        json.dump(jl, dest)
                        dest.write('\n')

                json_for_export.append({"name": json_name, "outputfile": dest})

                return json_for_export

