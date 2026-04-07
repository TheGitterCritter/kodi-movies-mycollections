import xbmc
import xbmcgui
import xbmcaddon
from resources.lib.manager import CollectionManager
from resources.lib.utils import get_full_movie_details, get_movie_info_dict

ADDON = xbmcaddon.Addon()

def LS(id):
    return ADDON.getLocalizedString(id)

def main():
    movie_id = xbmc.getInfoLabel('ListItem.DBID')
    movie_title = xbmc.getInfoLabel('ListItem.Title')
    
    if not movie_id or movie_id == "":
        return

    manager = CollectionManager()
    data = manager.load_data()
    col_names = sorted(data.keys())

    if not col_names:
        xbmcgui.Dialog().ok(LS(30000), LS(30023))
        return

    sel = xbmcgui.Dialog().select(f"{LS(30003)}: {movie_title}", col_names)
    if sel != -1:
        target = col_names[sel]
        
        if any(item['dbid'] == int(movie_id) for item in data[target]['items']):
            xbmcgui.Dialog().notification(LS(30000), LS(30021), xbmcgui.NOTIFICATION_INFO, 2000)
            return

        details = get_full_movie_details(int(movie_id))
        info_obj = get_movie_info_dict(details)
            
        movie_entry = {
            "label": movie_title,
            "dbid": int(movie_id),
            "order": len(data[target]['items']),
            "info": info_obj
        }
        
        data[target]['items'].append(movie_entry)
        manager.save_data(data)
        xbmcgui.Dialog().notification(LS(30016), f"{LS(30016)}: {target}", xbmcgui.NOTIFICATION_INFO, 2000)

if __name__ == '__main__':
    main()