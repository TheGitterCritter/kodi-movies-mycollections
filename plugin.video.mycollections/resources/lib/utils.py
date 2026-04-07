import json
import xbmc

def get_full_movie_details(dbid):
    """Official RPC call to get movie year and premiered date."""
    try:
        rpc = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovieDetails",
            "params": {
                "movieid": int(dbid),
                "properties": ["title", "year", "premiered", "plot", "genre", "rating", "runtime", "director", "art", "cast", "votes", "tagline", "originaltitle", "mpaa", "imdbnumber", "playcount", "resume", "uniqueid"]
            },
            "id": 1
        }
        result = xbmc.executeJSONRPC(json.dumps(rpc))
        return json.loads(result).get('result', {}).get('moviedetails', {})
    except:
        return None

def get_movie_info_dict(details):
    """Extract info dict from movie details."""
    if not details:
        return {"year": 0, "title": "", "scraper": "", "scraper_id": "", "imdb_id": ""}

    info = {
        "year": details.get('year', 0),
        "title": details.get('title', ''),
        "scraper": "",
        "scraper_id": "",
        "imdb_id": details.get('imdbnumber', '')
    }

    uniqueid = details.get('uniqueid', {})
    if isinstance(uniqueid, dict):
        if 'tmdb' in uniqueid:
            info["scraper"] = "tmdb"
            info["scraper_id"] = str(uniqueid['tmdb'])
        elif 'tvdb' in uniqueid:
            info["scraper"] = "tvdb"
            info["scraper_id"] = str(uniqueid['tvdb'])

    return info