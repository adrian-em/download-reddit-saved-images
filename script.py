import requests
import os
from bs4 import BeautifulSoup as Soup
from zipfile import ZipFile
from PIL import Image
import praw
from StringIO import StringIO


__author__ = 'Adrian Espinosa'
__version__ = '0.2.1.1'
__contributor__ = '/u/shaggorama'

image_formats = ['bmp', 'dib', 'eps', 'ps', 'gif', 'im', 'jpg', 'jpe', 'jpeg',
                  'pcd', 'pcx', 'png', 'pbm', 'pgm', 'ppm', 'psd', 'tif', 'tiff',
                  'xbm', 'xpm', 'rgb', 'rast', 'svg']


def is_image_link(submission):
    """
    Takes a praw.Submission object and returns a boolean
    describing whether or not submission links to an
    image.
    """
    if submission.url.split('.')[-1] in image_formats:
        return True
    else:
        return False


# user data
username = ''
password = ''
save_dir = ''
album_path = os.path.join(save_dir, 'albums')
# to notify errors
errors = []


class Downloader(object):
    global errors

    def __init__(self, submission):
        self.submission = submission
        self.path = os.path.join(save_dir, str(submission.created) + submission.title[0:20])
        self.album_path = os.path.join(self.path, 'albums')
        print "Downloading --> %s" % (submission.title)

    def direct_link(self):
        try:
            photo = requests.get(self.submission.url)
            image = Image.open(StringIO(photo.content))
            image.verify()
            Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
            self.submission.unsave()
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def imgur_album(self):
        download_url = 'http://s.imgur.com/a/%s/zip' % (os.path.split(self.submission.url)[1])
        filezip = requests.get(download_url)
        path = os.path.join(album_path, self.submission.title[0:50])
        # extract zip
        if not os.path.exists(path):
            os.mkdir(path)
        try:
            i = open(path + '.zip', 'w')
            i.write(filezip.content)
            i.close()
            zipfile = ZipFile(path + '.zip')
            zipfile.extractall(path)
            self.submission.unsave()
        except Exception, e:  # big album
            os.remove(path + '.zip')
            print e
            print "Album is too big, downloading images..."
            # this is the best layout
            idimage = os.path.split(self.submission.url)[1]
            if '#' in idimage:
                idimage = idimage[0:idimage.index("#")]
            url = "http://imgur.com/a/%s/layout/blog" % (idimage)
            web = requests.get(url)
            soup = Soup(web.content)
            container = soup.find("div", {"id": "image-container"})
            imgs = container.findAll("a", {"class": "zoom"})
            counter = 0
            for img in imgs:
                print counter
                p = img.attrs['href']
                try:
                    photo = requests.get(p)
                    image = Image.open(StringIO(photo.content))
                    image.verify()
                    Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
                    self.submission.unsave()
                except Exception, e:
                    errors.append(self.submission.title)
                    print e

    def imgur_link(self):
        # just a hack. i dont know if this will be a .jpg, but in order to download an
        # image data, I have to write an extension
        new_url = "http://i.imgur.com/%s.jpg" % (os.path.split(self.submission.url)[1])
        try:
            photo = requests.get(new_url)
            image = Image.open(StringIO(photo.content))
            image.verify()
            Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
            self.submission.unsave()
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def tumblr_link(self):
        photo = requests.get(self.submission.url)
        soup = Soup(photo.content)
        #div = soup.find("div", {'class': 'post'})
        #if not div:
        #    div = soup.find("li", {'class': 'post'})
        links = soup.findAll("img")
        for l in links:
            if "media.tumblr.com/tumblr_" in l.attrs['src']:
                url = l.attrs['src']
                #img = div.find("img")
                #url = img.attrs["src"]
                try:
                    photo = requests.get(url)
                    image = Image.open(StringIO(photo.content))
                    image.verify()
                    Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
                    self.submission.unsave()
                except Exception, e:
                    errors.append(self.submission.title)
                    print e

    def flickr_link(self):
        photo = requests.get(self.submission.url)
        fkr = Soup(photo.content)
        div = fkr.find("div", {"class": "photo-div"})
        photo = div.find("img")
        url = photo.attrs['src']
        try:
            photo = requests.get(url)
            image = Image.open(StringIO(photo.content))
            image.verify()
            Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
            self.submission.unsave()
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def picsarus_link(self):
        try:
            photo = requests.get(self.submission.url + ".jpg")
            image = Image.open(StringIO(photo.content))
            image.verify()
            Image.open(StringIO(photo.content)).save(self.path + "." + image.format.lower())
            self.submission.unsave()
        except Exception, e:
            errors.append(self.submission.title)
            print e

praw = praw.Reddit("aesptux\'s saved images downloader")

print "Logging in..."
# create session
praw.login(username=username, password=password)
print "Logged in."
print "Getting data..."
# this returns a generator
saved_links = praw.get_saved_links(limit=None)

# check if dir exists
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
if not os.path.exists(os.path.join(save_dir, 'albums')):
    os.mkdir(album_path)

for link in saved_links:
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
        else:
            print "%s ->> Domain not supported" % (link.domain)
print "Done."
