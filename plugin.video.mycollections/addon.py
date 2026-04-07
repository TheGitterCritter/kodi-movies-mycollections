import sys
import urllib.parse
import json
import xbmcgui
import xbmcplugin
import xbmc
import xbmcvfs
import xbmcaddon
import os
from resources.lib.manager import CollectionManager
from resources.lib.utils import get_full_movie_details, get_movie_info_dict

# Setup basic paths
HANDLE = int(sys.argv[1])
MANAGER = CollectionManager()
ADDON = xbmcaddon.Addon()

def LS(id):
    return ADDON.getLocalizedString(id)

ADDON_DIR = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
CUSTOM_SEARCH_ICON = os.path.join(ADDON_DIR, 'SearchIcon.png')
CUSTOM_ADD_ICON = os.path.join(ADDON_DIR, 'AddIcon.png')
CUSTOM_IMPORT_ICON = os.path.join(ADDON_DIR, 'ImportIcon.png')
RED_CROSS_ICON = os.path.join(ADDON_DIR, 'RedCrossIcon.png')

def get_url(**kwargs):
    return sys.argv[0] + '?' + urllib.parse.urlencode(kwargs)

def find_local_movie(info):
    imdb_id = info.get('imdb_id')
    title = info.get('title')
    year = info.get('year')

    if imdb_id:
        query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", 
                 "params": {"filter": {"field": "imdbnumber", "operator": "is", "value": imdb_id}}, "id": 1}
        res = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        movies = res.get('result', {}).get('movies', [])
        if movies: return movies[0]['movieid']

    if title and year:
        query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", 
                 "params": {"filter": {"and": [
                     {"field": "title", "operator": "is", "value": title},
                     {"field": "year", "operator": "is", "value": str(year)}
                 ]}}, "id": 1}
        res = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
        movies = res.get('result', {}).get('movies', [])
        return movies[0]['movieid'] if movies else -1
    return -1

def sync_scraper_info(item, dbid):
    query = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieDetails", 
             "params": {"movieid": dbid, "properties": ["uniqueid"]}, "id": 1}
    res = json.loads(xbmc.executeJSONRPC(json.dumps(query)))
    uids = res.get('result', {}).get('moviedetails', {}).get('uniqueid', {})
    
    if 'tmdb' in uids:
        item['info']['scraper'] = 'tmdb'
        item['info']['scraper_id'] = str(uids['tmdb'])
    elif 'tvdb' in uids:
        item['info']['scraper'] = 'tvdb'
        item['info']['scraper_id'] = str(uids['tvdb'])

def list_collections():
    data = MANAGER.load_data()
    xbmcplugin.setContent(HANDLE, 'files')
    
    for name in sorted(data.keys()):
        poster = MANAGER.get_poster(name, data)
        li = xbmcgui.ListItem(label=name)
        li.setArt({'poster': poster, 'icon': poster, 'thumb': poster})
        
        commands = [
            (LS(30007), f'RunPlugin({get_url(mode="rename", name=name)})'),
            (LS(30008), f'RunPlugin({get_url(mode="set_art", name=name)})'),
            (LS(30009), f'RunPlugin({get_url(mode="clear_art", name=name)})'),
            (LS(30010), f'RunPlugin({get_url(mode="export_col", name=name)})'),
            (LS(30011), f'RunPlugin({get_url(mode="delete", name=name)})')
        ]

        has_missing = any(item.get('dbid') == -1 for item in data[name].get('items', []))
        if has_missing:
            commands.insert(0, (f'[COLOR orange]{LS(30012)}[/COLOR]', f'RunPlugin({get_url(mode="rescan_col", name=name)})'))

        li.addContextMenuItems(commands)
        xbmcplugin.addDirectoryItem(HANDLE, get_url(mode='view', name=name), li, True)

    btns = [
        (LS(30004), 'search', CUSTOM_SEARCH_ICON),
        (LS(30005), 'add_col', CUSTOM_ADD_ICON),
        (LS(30006), 'import_col', CUSTOM_IMPORT_ICON)
    ]
    for label, mode, icon in btns:
        li = xbmcgui.ListItem(label=label)
        li.setArt({'icon': icon, 'thumb': icon})
        li.addContextMenuItems([], replaceItems=True)
        li.setProperty('canfavorite', 'false')
        xbmcplugin.addDirectoryItem(HANDLE, get_url(mode=mode), li, False)
    
    xbmcplugin.endOfDirectory(HANDLE)
    xbmc.executebuiltin('Container.SetViewMode(50)')

def view_collection(name):
    data_all = MANAGER.load_data()
    col_data = data_all.get(name, {"items": []})
    items = sorted(col_data['items'], key=lambda k: k.get('order', 0))

    xbmcplugin.setContent(HANDLE, 'movies')

    for index, item in enumerate(items):
        dbid = item.get('dbid', -1)
        original_label = item.get('label', 'Unknown')
        info_json = item.get('info', {})
        
        if dbid == -1:
            display_label = f"{index + 1}. [COLOR grey]{original_label}[/COLOR]"
            li = xbmcgui.ListItem(label=display_label)
            li.setArt({'poster': RED_CROSS_ICON, 'thumb': RED_CROSS_ICON, 'icon': RED_CROSS_ICON})
            
            info = li.getVideoInfoTag()
            info.setTitle(f"{original_label} ({LS(30018)})")
            info.setPlot(f"[COLOR red]{LS(30026)}[/COLOR]\n{LS(30027)}")
            if info_json.get('year'): info.setYear(int(info_json['year']))
            
            li.setProperty('IsPlayable', 'false')
            li.addContextMenuItems([(LS(30015), f'RunPlugin({get_url(mode="rescan_item", col=name, label=original_label)})')], replaceItems=True)
            url = get_url(mode='missing_notify', name=original_label)
        else:
            details = get_full_movie_details(dbid)
            year = str(details.get('year', '')) if details and details.get('year') else ""
            title = details.get('title', original_label) if details else original_label
            final_label = f"{index + 1}. {title}" + (f" ({year})" if year else "")
            
            li = xbmcgui.ListItem(label=final_label)
            info = li.getVideoInfoTag()
            info.setDbId(int(dbid))
            info.setMediaType('movie')
            info.setTitle(final_label)
            
            if details:
                info.setPlaycount(details.get('playcount', 0))
                resume = details.get('resume', {})
                if resume and resume.get('position'):
                    info.setResumePoint(resume['position'], resume.get('total', 0))
                
                info.setPlot(details.get('plot', ''))
                if year: info.setYear(int(year))
                li.setArt(details.get('art', {}))
            else:
                li.setArt({'poster': MANAGER.get_movie_poster_by_id(dbid)})
                
            li.setProperty('IsPlayable', 'true')
            li.addContextMenuItems([
                (LS(30013), f'RunPlugin({get_url(mode="move", col=name, dbid=dbid)})'),
                (LS(30003), f'RunPlugin({get_url(mode="add_to_col_context", label=original_label, dbid=dbid)})'),
                (LS(30014), f'RunPlugin({get_url(mode="remove", col=name, dbid=dbid)})')
            ])
            url = get_url(mode='play', dbid=dbid)

        xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
        
    xbmcplugin.endOfDirectory(HANDLE)
    xbmc.executebuiltin('Container.SetViewMode(50)')

def import_collection():
    path = xbmcgui.Dialog().browse(1, LS(30006), 'files', '.json')
    if not path: 
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    if not xbmcvfs.exists(path):
        xbmcgui.Dialog().ok(LS(30017), "File error.")
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    try:
        f = xbmcvfs.File(path)
        content = f.read()
        f.close()
        import_data = json.loads(content)
    except Exception as e:
        xbmcgui.Dialog().ok(LS(30017), str(e))
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    existing_data = MANAGER.load_data()
    for col_name, col_content in import_data.items():
        if col_name in existing_data and not xbmcgui.Dialog().yesno(LS(30019), f"{LS(30019)} {col_name}?"):
            continue

        processed = []
        for item in col_content.get('items', []):
            local_id = find_local_movie(item.get('info', {}))
            item['dbid'] = local_id
            if local_id != -1: sync_scraper_info(item, local_id)
            processed.append(item)

        existing_data[col_name] = {"items": processed, "custom_poster": col_content.get('custom_poster', "")}

    MANAGER.save_data(existing_data)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True)
    xbmc.executebuiltin('Container.Refresh')

params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
mode = params.get('mode')

if not mode:
    list_collections()
elif mode == 'view':
    view_collection(params.get('name'))
elif mode == 'import_col':
    import_collection()
elif mode == 'rescan_col':
    col_name = params.get('name')
    data = MANAGER.load_data()
    found_count = 0
    if col_name in data:
        for item in data[col_name]['items']:
            if item.get('dbid') == -1:
                new_id = find_local_movie(item.get('info', {}))
                if new_id != -1:
                    item['dbid'] = new_id
                    sync_scraper_info(item, new_id)
                    found_count += 1
    if found_count > 0:
        MANAGER.save_data(data)
        xbmc.executebuiltin("Container.Refresh")
        xbmcgui.Dialog().notification(LS(30016), f"{LS(30016)}: {found_count}", xbmcgui.NOTIFICATION_INFO, 3000)
    else:
        xbmcgui.Dialog().ok(LS(30012), LS(30024))
elif mode == 'rescan_item':
    col_name, label = params.get('col'), params.get('label')
    data = MANAGER.load_data()
    found = False
    for item in data[col_name]['items']:
        if item['label'] == label and item['dbid'] == -1:
            new_id = find_local_movie(item.get('info', {}))
            if new_id != -1:
                item['dbid'] = new_id
                sync_scraper_info(item, new_id)
                found = True
    if found:
        MANAGER.save_data(data)
        xbmc.executebuiltin("Container.Refresh")
        xbmcgui.Dialog().notification(LS(30016), f"{LS(30016)}: {label}", xbmcgui.NOTIFICATION_INFO, 2000)
    else:
        xbmcgui.Dialog().notification(LS(30017), LS(30024), xbmcgui.NOTIFICATION_WARNING, 2000)
elif mode == 'search_results':
    query = params.get('query')
    xbmcplugin.setContent(HANDLE, 'movies')
    rpc = {"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", 
           "params": {"filter": {"field": "title", "operator": "contains", "value": query}, 
           "properties": ["title", "year", "art", "playcount", "resume"]}, "id": 1}
    resp = json.loads(xbmc.executeJSONRPC(json.dumps(rpc)))
    if 'result' in resp and 'movies' in resp['result']:
        for m in resp['result']['movies']:
            li = xbmcgui.ListItem(label=m['label'])
            li.setArt(m.get('art', {}))
            info = li.getVideoInfoTag()
            info.setDbId(int(m['movieid']))
            info.setPlaycount(m.get('playcount', 0))
            res = m.get('resume', {})
            if res and res.get('position'):
                info.setResumePoint(res['position'], res.get('total', 0))
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(HANDLE, get_url(mode='play', dbid=m['movieid']), li, False)
    xbmcplugin.endOfDirectory(HANDLE)
elif mode == 'play':
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=False)
    xbmc.executebuiltin(f'PlayMedia("videodb://movies/titles/{params["dbid"]}")')
elif mode == 'missing_notify':
    xbmcgui.Dialog().notification(LS(30018), f"{params.get('name')} {LS(30018)}", xbmcgui.NOTIFICATION_INFO, 3000)
elif mode == 'search':
    kb = xbmc.Keyboard('', LS(30004))
    kb.doModal()
    if kb.isConfirmed() and kb.getText():
        xbmc.executebuiltin(f"Container.Update({get_url(mode='search_results', query=kb.getText())})")
elif mode == 'add_to_col_context':
    movie_name, movie_dbid = params.get('label'), params.get('dbid')
    data = MANAGER.load_data()
    col_names = sorted(data.keys())
    sel = xbmcgui.Dialog().select(f"{LS(30003)}: {movie_name}", col_names)
    if sel != -1:
        target_col = col_names[sel]
        details = get_full_movie_details(int(movie_dbid))
        item = {'label': movie_name, 'dbid': int(movie_dbid), 'order': len(data[target_col]['items'])}
        item['info'] = get_movie_info_dict(details) if details else {}
        data[target_col]['items'].append(item)
        MANAGER.save_data(data)
        xbmcgui.Dialog().notification(LS(30016), f"{LS(30016)}: {target_col}", xbmcgui.NOTIFICATION_INFO, 2000)
elif mode == 'add_col':
    name = xbmcgui.Dialog().input(LS(30005))
    if name:
        data = MANAGER.load_data()
        if name not in data:
            data[name] = {"items": [], "custom_poster": ""}
            MANAGER.save_data(data)
            xbmc.executebuiltin("Container.Refresh")
elif mode == 'rename':
    old_name = params['name']
    new_name = xbmcgui.Dialog().input(LS(30007), defaultt=old_name)
    if new_name and new_name != old_name:
        data = MANAGER.load_data()
        data[new_name] = data.pop(old_name)
        MANAGER.save_data(data)
        xbmc.executebuiltin("Container.Refresh")
elif mode == 'delete':
    if xbmcgui.Dialog().yesno(LS(30020), f"{LS(30011)} '{params['name']}'?"):
        data = MANAGER.load_data()
        data.pop(params['name'], None)
        MANAGER.save_data(data)
        xbmc.executebuiltin("Container.Refresh")
elif mode == 'move':
    col_name, target_dbid = params['col'], int(params['dbid'])
    data = MANAGER.load_data()
    items = data[col_name]['items']
    idx = next((i for i, item in enumerate(items) if item['dbid'] == target_dbid), None)
    if idx is not None:
        pos = xbmcgui.Dialog().input(LS(30022), type=xbmcgui.INPUT_ALPHANUM)
        if pos:
            try:
                new_idx = max(0, min(int(pos)-1, len(items)-1))
                items.insert(new_idx, items.pop(idx))
                for i, itm in enumerate(items): itm['order'] = i
                MANAGER.save_data(data)
                xbmc.executebuiltin("Container.Refresh")
            except: pass
elif mode == 'remove':
    data = MANAGER.load_data()
    data[params['col']]['items'] = [i for i in data[params['col']]['items'] if i['dbid'] != int(params['dbid'])]
    MANAGER.save_data(data)
    xbmc.executebuiltin("Container.Refresh")
elif mode == 'set_art':
    path = xbmcgui.Dialog().browse(1, LS(30008), 'files', '.jpg|.png')
    if path:
        data = MANAGER.load_data()
        data[params['name']]['custom_poster'] = path
        MANAGER.save_data(data)
        xbmc.executebuiltin("Container.Refresh")
elif mode == 'clear_art':
    data = MANAGER.load_data()
    data[params['name']]['custom_poster'] = ""
    MANAGER.save_data(data)
    xbmc.executebuiltin("Container.Refresh")
elif mode == 'export_col':
    col_name = params['name']
    data = MANAGER.load_data()
    col_data = data.get(col_name)
    if col_data:
        path = xbmcgui.Dialog().browse(3, LS(30010), 'files')
        if path:
            if not path.endswith('.json'):
                path = os.path.join(path, f"{col_name}.json")
            with xbmcvfs.File(path, 'w') as f:
                f.write(json.dumps({col_name: col_data}, indent=4))
            xbmcgui.Dialog().notification(LS(30016), LS(30025), xbmcgui.NOTIFICATION_INFO, 2000)