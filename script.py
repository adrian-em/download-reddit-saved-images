"""
Python script to download saved images from reddit
"""
import requests
import os
from bs4 import BeautifulSoup as bs
from zipfile import ZipFile
from PIL import Image
import praw
from StringIO import StringIO
import time


__author__ = 'Adrian Espinosa'
__version__ = '1.0.0.0'
__contributor__ = '/u/shaggorama'

IMAGE_FORMATS = ['bmp', 'dib', 'eps', 'ps', 'gif', 'im', 'jpg', 'jpe', 'jpeg',
                 'pcd', 'pcx', 'png', 'pbm', 'pgm', 'ppm', 'psd', 'tif',
                 'tiff', 'xbm', 'xpm', 'rgb', 'rast', 'svg']


def is_image_link(sub):
    """
    Takes a praw.Submission object and returns a boolean
    describing whether or not submission links to an
    image.
    """
    if sub.url.split('.')[-1] in IMAGE_FORMATS:
        return True
    else:
        return False


def check_size(filename):
    """
    Calculate file size.
    To check if file is corrupt.
    """
    stats = os.stat(filename)
    filesize = stats.st_size
    # 2 KB
    if filesize > 2048:
        return True
    else:
        return False


# user data
USERNAME = ''
PASSWORD = ''
SAVE_DIR = '/home/aesptux/tests'
ALBUM_PATH = os.path.join(SAVE_DIR, 'albums')

# to notify ERRORS
ERRORS = []
# list to append correct submissions
# at the end, iterate through the list unsaving them
# It seems that removing items just after being downloaded
# causes to fetch just the first page
CORRECT_SUBMISSIONS = []


class Downloader(object):
    """
    Downloader class.
    Define here all methods to download images from different hosts or
    even direct link to image
    """
    #global ERRORS

    def __init__(self, submission):
        self.submission = submission
        self.path = os.path.join(SAVE_DIR, str(submission.created) +
            submission.title[0:20].replace("/", "_").replace("\\", "_"))
        self.album_path = os.path.join(self.path, 'albums')
        print "Downloading --> %s" % (submission.title)

    def direct_link(self):
        """
        Direct link to image
        """
        try:
            response = requests.get(self.submission.url)
            img = Image.open(StringIO(response.content))
            img.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                img.format.lower())
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:
            ERRORS.append(self.submission.title)
            print ex

    def imgur_album(self):
        """
        Album from imgur
        """
        download_url = 'http://s.imgur.com/a/%s/zip' % \
            (os.path.split(self.submission.url)[1])
        response = requests.get(download_url)
        path = os.path.join(ALBUM_PATH, self.submission.title[0:50])
        # extract zip
        if not os.path.exists(path):
            os.mkdir(path)
        try:
            i = open(path + '.zip', 'w')
            i.write(response.content)
            i.close()
            zipfile = ZipFile(path + '.zip')
            zipfile.extractall(path)
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:  # big album
            os.remove(path + '.zip')
            print ex
            print "Album is too big, downloading images..."
            # this is the best layout
            idimage = os.path.split(self.submission.url)[1]
            if '#' in idimage:
                idimage = idimage[0:idimage.index("#")]
            url = "http://imgur.com/a/%s/layout/blog" % (idimage)
            response = requests.get(url)
            soup = bs(response.content)
            container_element = soup.find("div", {"id": "image-container"})
            imgs_elements = container_element.findAll("a", {"class": "zoom"})
            counter = 0
            for img in imgs_elements:
                print counter
                img_url = img.attrs['href']
                try:
                    response = requests.get(img_url)
                    img = Image.open(StringIO(response.content))
                    img.verify()
                    Image.open(StringIO(response.content)).save(self.path +
                        "." + img.format.lower())
                    CORRECT_SUBMISSIONS.append(self.submission)
                except Exception, ex:
                    ERRORS.append(self.submission.title)
                    print ex

    def imgur_link(self):
        """
        Image from imgur
        """
        # just a hack. i dont know if this will be a .jpg, but in order to
        # download an image data, I have to write an extension
        new_url = "http://i.imgur.com/%s.jpg" % \
            (os.path.split(self.submission.url)[1])
        try:
            response = requests.get(new_url)
            img = Image.open(StringIO(response.content))
            img.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                img.format.lower())
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:
            ERRORS.append(self.submission.title)
            print ex

    def tumblr_link(self):
        """
        Tumblr image link
        """
        response = requests.get(self.submission.url)
        soup = bs(response.content)
        #div = soup.find("div", {'class': 'post'})
        #if not div:
        #    div = soup.find("li", {'class': 'post'})
        img_elements = soup.findAll("img")
        for img in img_elements:
            if "media.tumblr.com/tumblr_" in img.attrs['src']:
                img_url = img.attrs['src']
                #img = div.find("img")
                #img_url = img.attrs["src"]
                try:
                    response = requests.get(img_url)
                    img = Image.open(StringIO(response.content))
                    img.verify()
                    Image.open(StringIO(response.content)).save(self.path +
                        "." + img.format.lower())
                    CORRECT_SUBMISSIONS.append(self.submission)
                except Exception, ex:
                    ERRORS.append(self.submission.title)
                    print ex

    def flickr_link(self):
        """
        Flickr image link
        """
        response = requests.get(self.submission.url)
        soup = bs(response.content)
        div_element = soup.find("div", {"class": "photo-div"})
        img_element = div_element.find("img")
        img_url = img_element.attrs['src']
        try:
            response = requests.get(img_url)
            image = Image.open(StringIO(response.content))
            image.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                image.format.lower())
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:
            ERRORS.append(self.submission.title)
            print ex

    def picsarus_link(self):
        """
        Picsarus image link
        """
        try:
            response = requests.get(self.submission.url + ".jpg")
            img = Image.open(StringIO(response.content))
            img.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                img.format.lower())
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:
            ERRORS.append(self.submission.title)
            print ex

    def picasaurus_link(self):
        """
        Picasaurus image link
        """
        response = requests.get(self.submission.url)
        soup = bs(response.content)
        img = soup.find("img", {"class": "photoQcontent"})
        img_url = img.attrs['src']
        try:
            response = requests.get(img_url)
            image = Image.open(StringIO(response.content))
            image.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                image.format.lower())
            CORRECT_SUBMISSIONS.append(self.submission)
        except Exception, ex:
            ERRORS.append(self.submission.title)
            print ex

R = praw.Reddit("aesptux\'s saved images downloader")

print "Logging in..."
# create session
R.login(username=USERNAME, password=PASSWORD)
print "Logged in."
print "Getting data..."
# this returns a generator
SAVED_LINKS = R.user.get_saved(limit=None)

# check if dir exists
if not os.path.exists(SAVE_DIR):
    os.mkdir(SAVE_DIR)
if not os.path.exists(os.path.join(SAVE_DIR, 'albums')):
    os.mkdir(ALBUM_PATH)

for link in SAVED_LINKS:
    # create object per submission. Trusting garbage collector!
    d = Downloader(link)

    if is_image_link(link):
        d.direct_link()
    else:
        # not direct, read domain
        if 'imgur' in link.domain:
            # check if album
            if '/a/' in link.url:
                d.imgur_album()
            else:
                d.imgur_link()
        elif 'tumblr' in link.domain:
            d.tumblr_link()
        elif 'flickr' in link.domain:
            d.flickr_link()
        elif 'picsarus' in link.domain:
            d.picsarus_link()
        elif 'picasaurus' in link.domain:
            d.picasaurus_link()
        else:
            print "%s ->> Domain not supported" % (link.domain)
print "Done."

# unsave items
for c_submission in CORRECT_SUBMISSIONS:
    print "Unsaving %s" % (c_submission.title)
    c_submission.unsave()
    time.sleep(2)  # reddit's api restriction

if len(ERRORS) > 0:
    print "The following items have failed:"
    for err in ERRORS:
        print err
    print "Perhaps you should check if the images still exist."
