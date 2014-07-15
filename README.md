download-reddit-saved-images
============================

This script checks your saved links and searchs for images to automagically download them into a folder.

Instructions
---
1. Clone the repository
2. Open config.yaml and configure your data. Username and password to login, and directory to store images.
3. Run the script and see how your saved images are downloaded :)

**WARNING:**
Items downloaded **will be unsaved**. If you want to prevent this, remove all occurrences of unsave().


Changelog
---
* 2.0.2
    * Added check for existing files. If the file exists, it will not be downloaded again.
* 2.0.1
    * Bug fixes.
* 2.0.0
	* Refactor code
	* Python 3 support!
* 1.2.0
	* Move is_image_link to class
	* New method to decide download method. Cleaner code.
* 1.1.0
	* Fixed several bugs
* 1.0.2
	* Refactoring
	* Bug fixes
	* Added support for YAML
* 0.2.3.0
	* Fixed error which caused albums to save to the wrong location, on the same photo.
	* Fixed error requests loop.
	* Some refactoring.
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



**Note**: Gifs seems to not work.


**If you want to collaborate, to improve performance or to add support to another websites, please submit pull requests.**


Requirements
---
1. BeautifulSoup 4
2. Requests
3. Praw
4. PIL
5. PyYAML
