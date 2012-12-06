import requests
import json
import os
from bs4 import BeautifulSoup as Soup
from zipfile import ZipFile
import time


__author__ = 'Adrian Espinosa'


def detect_ext(content):
    """
    Detect image extension
    """
    if content.startswith('\xff'):
        return ".jpg"
    elif content.startswith("GIF89a"):
        return ".gif"
    elif content.startswith("\x89PNG"):
        return ".png"
    else:
        return ".jpg"


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
save_dir = '/path/to/store/imgs/'
album_path = os.path.join(save_dir, 'albums')
saved_url = ''
login_payload = {'user': username, 'passwd': password, 'api_type': 'json'}
headers = {'user-agent': 'aesptux\'s saved images downloader'}
login_url = 'http://www.reddit.com/api/login'
unsave_url = 'http://www.reddit.com/api/unsave'

print "Logging in..."
# create session
client = requests.session()
r = client.post(login_url, data=login_payload)
print "Logged in."

# convert to python dict
login_response = json.loads(r.text)
# grab modhash
client.modhash = login_response['json']['data']['modhash']
# get all saved links
print "Getting data..."
s = requests.get(saved_url)
s = s.content
s = json.loads(s)

# check if dir exists
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
if not os.path.exists(os.path.join(save_dir, 'albums')):
    os.mkdir(album_path)

# to delete
names = []
# to notify errors
errors = []

while s['data']['children']:
    for x in s['data']['children']:
        print "Downloading ---> %s" % (x['data']['title'])
        try:
            path = os.path.join(save_dir, str(x['data']['created']) + x['data']['title'][0:15])
            photo = requests.get(x['data']['url'])
            # direct link to image
            if os.path.splitext(photo.url)[1] in ['.jpg', '.gif', '.png', '.jpeg']:
                try:
                    i = open(path + os.path.splitext(photo.url)[1], 'w')
                    i.write(photo.content)
                    i.close()
                    if check_size(path + os.path.splitext(photo.url)[1]):
                        names.append(x['data']['name'])
                    else:
                        errors.append(x['data']['title'])
                except Exception, e:
                    print e
            else:
            # link to imgur
                if "imgur" in x['data']['domain']:
                    # its album
                    if "/a/" in x['data']['url']:
                        print "It is an imgur album"
                        download_url = 'http://s.imgur.com/a/%s/zip' % (os.path.split(x['data']['url'])[1])
                        filezip = requests.get(download_url)
                        path = os.path.join(album_path, x['data']['title'][0:50])
                        # extract zip
                        if not os.path.exists(path):
                            os.mkdir(path)
                        try:
                            i = open(path + '.zip', 'w')
                            i.write(filezip.content)
                            i.close()
                            zipfile = ZipFile(path + '.zip')
                            zipfile.extractall(path)
                            names.append(x['data']['name'])
                        except Exception, e:  # big album
                            os.remove(path + '.zip')
                            print "Album is too big, downloading images..."
                            # this is the best layout
                            idimage = os.path.split(x['data']['url'])[1]
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
                                photo = requests.get(p)
                                ext = detect_ext(photo.content[0:10])
                                i = open(path + "/" + str(counter) + ext, 'w')
                                i.write(photo.content)
                                i.close()
                                counter += 1

                            names.append(x['data']['name'])
                    # imgur image
                    else:
                        # just a hack. i dont know if this will be a .jpg, but in order to download an
                        # image data, I have to write an extension
                        new_url = "http://i.imgur.com/%s.jpg" % (os.path.split(x['data']['url'])[1])
                        photo = requests.get(new_url)
                        ext = detect_ext(photo.content[0:10])
                        i = open(path + ext, 'w')
                        i.write(photo.content)
                        i.close()
                        if check_size(path + ext):
                            names.append(x['data']['name'])
                        else:
                            errors.append(x['data']['title'])
                elif "tumblr" in x['data']['domain']:
                    soup = Soup(photo.content)
                    #div = soup.find("div", {'class': 'post'})
                    #if not div:
                    #    div = soup.find("li", {'class': 'post'})
                    links = soup.findAll("img")
                    for l in links:
                        if l.attrs['src']:
                            url = l.attrs['src']
                    #img = div.find("img")
                    #url = img.attrs["src"]
                    photo = requests.get(url)
                    ext = detect_ext(photo.content[0:10])
                    print path
                    print ext
                    i = open(path + ext, 'w')
                    i.write(photo.content)
                    i.close()
                    if check_size(path + ext):
                        names.append(x['data']['name'])
                    else:
                        errors.append(x['data']['title'])
                elif "flickr" in x['data']['domain']:
                    fkr = Soup(photo.content)
                    div = fkr.find("div", {"class": "photo-div"})
                    photo = div.find("img")
                    url = photo.attrs['src']
                    photo = requests.get(url)
                    ext = detect_ext(photo.content[0:10])
                    i = open(path + ext, 'w')
                    i.write(photo.content)
                    i.close()
                    if check_size(path + ext):
                        names.append(x['data']['name'])
                    else:
                        errors.append(x['data']['title'])
                else:
                    print "%s Domain not supported" % (x['data']['domain'])

        except Exception, e:
            print "Could not get photo"

    # read data
    if s['data']['after']:
        print "Loading next page."
        s = requests.get(saved_url + '&after=' + s['data']['after'])
        s = s.content
        s = json.loads(s)
    else:
        print "No more pages."
        s['data']['children'] = None

unsave_payload = {'id': '', 'uh': client.modhash}

######### unsaving block ########
for name in names:
    unsave_payload['id'] = name
    print "Unsaving %s" % (unsave_payload['id'])
    # reddit's api restriction. One request per two seconds
    time.sleep(2)
    u = client.post(unsave_url, data=unsave_payload, headers=headers)
################################

for e in errors:
    print "There was an error with -> %s" % (e)

# check if there are remaining items, to warn the user
s = requests.get(saved_url)
s = s.content
s = json.loads(s)

if s['data']['children']:
    print "There are still items in your saved links"
