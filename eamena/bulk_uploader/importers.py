from arches.app.models import models
from arches.app.utils.index_database import index_resources_using_multiprocessing
import json, logging

logger = logging.getLogger(__name__)

def append_json(data):

    no_dup = ['34cfe9b9-c2c0-11ea-9026-02e7594ce0a0', '34cfe9aa-c2c0-11ea-9026-02e7594ce0a0']
    parent_map = {}

    resources = {}
    new_tiles = []
    updated_tiles = {}
    rid = []
    if 'business_data' not in data:
        return (-1, -1)
    if 'resources' not in data['business_data']:
        return (-1, -1)
    for item in data['business_data']['resources']:
        resid = item['resourceinstance']['resourceinstanceid']
        try:
            res = models.ResourceInstance.objects.get(pk=resid)
        except:
            res = None
        if res is None:
            logger.error("Resource Instance {} doesn't exist.".format(resid))
            return (-1, -1) # Cannot append if all the resource instances don't exist
        resources[resid] = res
        for tile in item['tiles']:
            tileid = tile['tileid']
            ti = None
            if tile['nodegroup_id'] in no_dup:
                try:
                    ti = models.TileModel.objects.get(resourceinstance_id=resid, nodegroup_id=tile['nodegroup_id'])
                    parent_map[tileid] = str(ti.pk)
                except:
                    ti = None
            if ti is None:
                try:
                    ti = models.TileModel.objects.get(pk=tileid)
                except:
                    ti = None
            if ti is None:
                new_tiles.append(tileid)
            else:
                updated_tiles[tileid] = ti

    # Create new tiles

    added = 0
    for item in data['business_data']['resources']:
        resid = item['resourceinstance']['resourceinstanceid']

        for tile in item['tiles']:
            if tile['tileid'] not in new_tiles:
                continue
            parent_tile = tile['parenttile_id']
            if parent_tile in parent_map:
                parent_tile = parent_map[parent_tile]
            ti = models.TileModel(nodegroup_id=tile['nodegroup_id'], parenttile_id=parent_tile, resourceinstance_id=tile['resourceinstance_id'], sortorder=tile['sortorder'], tileid=tile['tileid'])
            ti.data = tile['data']
            try:
                ti.save()
            except Exception as e:
                logger.error("Error creating tile {}; Rolling back...".format(tile['tileid']), exc_info=e)
                models.TileModel.objects.filter(pk__in=new_tiles).delete()
                return (-1, -1)
            added = added + 1
            if resid not in rid:
                rid.append(resid)
    
    # Update existing tiles

    updated = 0
    for item in data['business_data']['resources']:
        resid = item['resourceinstance']['resourceinstanceid']

        for tile in item['tiles']:
            if tile['tileid'] not in updated_tiles:
                continue
            ti = updated_tiles[tile['tileid']]
            ti.data.update(tile['data'])
            try:
                ti.save()
            except Exception as e:
                logger.error("Error creating tile {}; Rolling back...".format(tile['tileid']), exc_info=e)
                models.TileModel.objects.filter(pk__in=new_tiles).delete()
                return (-1, -1)
            updated = updated + 1
            if resid not in rid:
                rid.append(resid)
    
    logger.info("Success! Created {} tiles, updated {} tiles.".format(added, updated))
    index_resources_using_multiprocessing(rid, recalculate_descriptors=True)
    logger.info("Reindexed {} resources.".format(len(rid)))
    return (added, updated)

def bulk_append(filename):
    with open(filename, 'r') as fp:
        return append_json(json.load(fp))
