import json
import os
import xbmc
import xbmcvfs
import xbmcgui

class CollectionManager:
    def __init__(self):
        self.profile_path = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.mycollections/')
        if not xbmcvfs.exists(self.profile_path):
            xbmcvfs.mkdir(self.profile_path)
        self.file_path = os.path.join(self.profile_path, 'collections.json')
        if not xbmcvfs.exists(self.file_path):
            self.save_data({})

    def load_data(self):
        try:
            with xbmcvfs.File(self.file_path) as f:
                return json.loads(f.read())
        except:
            return {}

    def save_data(self, data):
        with xbmcvfs.File(self.file_path, 'w') as f:
            f.write(json.dumps(data, indent=4))

    def get_movie_poster_by_id(self, dbid):
        try:
            rpc = '{"jsonrpc":"2.0","method":"VideoLibrary.GetMovieDetails","params":{"movieid":%d,"properties":["art"]},"id":1}' % int(dbid)
            result = xbmc.executeJSONRPC(rpc)
            res_json = json.loads(result)
            details = res_json.get('result', {}).get('moviedetails', {})
            return details.get('art', {}).get('poster', 'DefaultVideo.png')
        except:
            return 'DefaultVideo.png'

    def get_poster(self, collection_name, data):
        col = data.get(collection_name, {})
        if col.get('custom_poster'):
            return col['custom_poster']
        items = col.get('items', [])
        if items:
            sorted_items = sorted(items, key=lambda x: x.get('order', 0))
            return self.get_movie_poster_by_id(sorted_items[0]['dbid'])
        return 'DefaultVideo.png'