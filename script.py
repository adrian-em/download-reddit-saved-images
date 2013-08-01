import requests
import os
from bs4 import BeautifulSoup as bs
from zipfile import ZipFile
from PIL import Image
import praw
from StringIO import StringIO
import time


__author__ = 'Adrian Espinosa'
__version__ = '0.2.3.0'
__contributor__ = '/u/shaggorama'

image_formats = ['bmp', 'dib', 'eps', 'ps', 'gif', 'im', 'jpg', 'jpe', 'jpeg',
                 'pcd', 'pcx', 'png', 'pbm', 'pgm', 'ppm', 'psd', 'tif',
                 'tiff', 'xbm', 'xpm', 'rgb', 'rast', 'svg']


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
username = ''
password = ''
save_dir = '/Users/adrian/Documentos/tests'
album_path = os.path.join(save_dir, 'albums')

# to notify errors
errors = []
# list to append correct submissions
# at the end, iterate through the list unsaving them
# It seems that removing items just after being downloaded
# causes to fetch just the first page
correct_submissions = []


class Downloader(object):
    global errors

    def __init__(self, submission):
        self.submission = submission
        self.path = os.path.join(save_dir, str(submission.created) +
                                 submission.title[0:20])
        self.album_path = os.path.join(self.path, 'albums')
        print "Downloading --> %s" % (submission.title)

    def direct_link(self):
        try:
            response = requests.get(self.submission.url)
            img = Image.open(StringIO(response.content))
            img.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                                                        img.format.lower())
            correct_submissions.append(self.submission)
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def imgur_album(self):
        download_url = 'http://s.imgur.com/a/%s/zip' % \
            (os.path.split(self.submission.url)[1])
        try:
            response = requests.get(download_url)
        except Exception, e:
            response = ""

        path = os.path.join(album_path, self.submission.title[0:50])
        # extract zip
        if not os.path.exists(path):
            os.mkdir(path)
        try:
            i = open(path + '.zip', 'w')
            i.write(response.content)
            i.close()
            zipfile = ZipFile(path + '.zip')
            zipfile.extractall(path)
            correct_submissions.append(self.submission)
        except Exception, e:  # big album
            os.remove(path + '.zip')
            print e
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
                    Image.open(StringIO(response.content)).save(path + "/" +
                                                                str(counter) +
                                                                "." +
                                                                img.format
                                                                .lower())
                    correct_submissions.append(self.submission)
                except Exception, e:
                    errors.append(self.submission.title)
                    print e
            counter += 1

    def imgur_link(self):
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
            correct_submissions.append(self.submission)
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def tumblr_link(self):
        response = requests.get(self.submission.url)
        soup = bs(response.content)
        #div = soup.find("div", {'class': 'post'})
        #if not div:
        #    div = soup.find("li", {'class': 'post'})
        img_elements = soup.findAll("img")
        for l in img_elements:
            if "media.tumblr.com/tumblr_" in l.attrs['src']:
                img_url = l.attrs['src']
                #img = div.find("img")
                #img_url = img.attrs["src"]
                try:
                    response = requests.get(img_url)
                    img = Image.open(StringIO(response.content))
                    img.verify()
                    Image.open(StringIO(response.content)).save(self.path +
                                                                "." +
                                                                img.format
                                                                .lower())
                    correct_submissions.append(self.submission)
                except Exception, e:
                    errors.append(self.submission.title)
                    print e

    def flickr_link(self):
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
            correct_submissions.append(self.submission)
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def picsarus_link(self):
        try:
            response = requests.get(self.submission.url + ".jpg")
            img = Image.open(StringIO(response.content))
            img.verify()
            Image.open(StringIO(response.content)).save(self.path + "." +
                                                        img.format.lower())
            correct_submissions.append(self.submission)
        except Exception, e:
            errors.append(self.submission.title)
            print e

    def picasaurus_link(self):
        rersponse = requests.get(self.submission.url)
        soup = bs(rersponse.content)
        img = soup.find("img", {"class": "photoQcontent"})
        img_url = img.attrs['src']
        try:
            rersponse = requests.get(img_url)
            image = Image.open(StringIO(rersponse.content))
            image.verify()
            Image.open(StringIO(rersponse.content)).save(self.path + "." +
                                                         image.format.lower())
            correct_submissions.append(self.submission)
        except Exception, e:
            errors.append(self.submission.title)
            print e

r = praw.Reddit("aesptux\'s saved images downloader")

print "Logging in..."
# create session
r.login(username=username, password=password)
print "Logged in."
print "Getting data..."
# this returns a generator
saved_links = r.get_saved_links(limit=None)

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
        elif 'picasaurus' in link.domain:
            d.picasaurus_link()
        else:
            print "%s ->> Domain not supported" % (link.domain)
print "Done."

# unsave items
for submission in correct_submissions:
    print "Unsaving %s" % (submission.title)
    submission.unsave()
    time.sleep(2)  # reddit's api restriction

if len(errors) > 0:
    print "The following items have failed"
    for err in errors:
        print err
