download-reddit-saved-images
============================

This script checks your saved links and searchs for images to automagically download them into a folder.

Instructions
---
1. Clone the repository
2. Enter your reddit's username and password
3. Set a directory where images will be stored
4. Run the script and see how your saved images are downloaded :)

**WARNING:**
Items downloaded **will be unsaved**. If you want to prevent this, remove all occurrences of unsave()

Changelog
---
* 1.0.0.1
    * Update to newest PRAW
    * Fix bug #2, albums with slashes failed
* 1.0.0.0
    * Version 1.0.0.0! During my tests I did not found any major error
    * Bug fixes
    * If the submission.title contained '/' or '\' it failed to save
* 0.2.3.0
    * Little refactor to improve PEP8
* 0.2.2.2
    * Refactor variable names
    * Fixed bug while unsaving items.
* 0.2.2.1
    * Added support for Picasaurus
    * Show errors to the user
* 0.2.1.1
    * Improved code thanks to */u/shaggorama*
    * Now using PRAW and PIL
    * Added support for Picsarus
* 0.1.1.1
    * Initial release


Support
---
1. Direct links to images
2. Imgur links
3. Imgur albums
4. Flickr images
5. Tumblr  (not fully tested)
6. Picsarus
7. Picasaurus

**If you want to collaborate, to improve performance or to add support to another websites, please submit pull requests.**


Requirements
---
1. BeautifulSoup 4
2. Requests
3. Praw
4. PIL
