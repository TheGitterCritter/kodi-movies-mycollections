# My Collections for Kodi

**My Collections** is a lightweight, manual movie collection manager for Kodi. Unlike the built-in "Movie Sets" which rely on online scrapers (like TMDB), this addon allows you to create your own custom collections using a local JSON-based storage system. 

Whether you want to organize movies by "Comfort Films", "Date Night", "Marvel Cinematic Universe" or "Obscure Indie Gems" you have total control over the order and categorization.

## ✨ Key Features

* **Custom Collections:** Create as many collections as you like with custom names.
* **Internal Library Search:** Use the built-in search tool to find any movie in your Kodi library and add it to a collection without leaving the addon.
* **Manual Ordering:** Move movies up or down within a collection to set your own preferred viewing order.
* **Custom Artwork:** Set a custom poster for each collection to personalize your library.
* **Import/Export:** Back up your collections or share them with others using the export/import functionality.
* **Multi-Language Support:** Full localization for over 15+ languages including English, Dutch, Spanish, French, German, Chinese, and more.

## 🛠 How to Use

### Adding via Context Menu
1. Navigate to your Kodi Movie Library (outside of the addon).
2. Right-click (or long-press) on a movie.
3. Select **Add to My Collection** from the context menu.

### Adding via Internal Search
1. Open the **My Collections** addon.
2. Select `# Search Movies in Library`.
3. Enter the movie title.
4. Select the movie from the results and choose which collection to add it to.

### Managing Collections
* To create a new group, select `+ Add New Collection`.
* Inside the addon, use the context menu on any collection or movie to **rename**, **reorder**, or **delete** items.

## ⚠️ Important Note
> **Global Search Compatibility:** This addon's context menu entry will **not** appear when viewing results inside the "Global Search" addon. This is because Global Search uses its own isolated context menu system that does not support third-party addon injections. Please add movies to your collections directly from your main Library, Files, Playlist views, or the addon's internal search.

## 📁 Technical Details
* **Storage:** All data is stored in a `collections.json` file within the addon's profile folder.
* **Database:** The addon cross-references your Kodi Video Database (SQL) to ensure movies are playable and metadata is accurate.

## 📄 License
This project is licensed under the **MIT License** - see the `LICENSE.txt` file for details.

---

### Installation
1. Download the ZIP file from the [Releases](https://github.com/TheGitterCritter/kodi-movies-mycollections/releases) page.
2. In Kodi, go to **Add-ons** > **Add-on Browser**.
3. Select **Install from zip file**.
4. Navigate to the downloaded file and install.