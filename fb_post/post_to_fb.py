import json
import requests
from urllib import urlencode
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
import subprocess

APP_ID = "125994524515407"
APP_SECRET = "62225f04b35d0184cf2a84771b44b371"
REDIRECT_URL = "http://localhost:9999/"

HOST = "localhost"
PORT = 9999
# file to read from
file_path = "/home/navendu/work/fb_post/info.txt"
FB_PAGE_ID = "935683393225672"


def parse_file():
    line_count = 1

    photos = []
    link = ""
    desc = ""
    
    f = open(file_path, 'r')
    for line in f:
        if line_count <= 10:
            # read photos!
            if line.strip():
                photos.append(line.strip())
        elif line_count == 11:
            # read link!
            if line.strip():
                link = line.strip()
        else:
            # read description!
            desc += line

        line_count += 1

    f.close()
    return (photos, link, desc)


def make_post(page_token, photos, link, desc):
    post_url = "https://graph.facebook.com/v2.7/%s/feed" % FB_PAGE_ID
    args = {}
    if photos:
        post_url = "https://graph.facebook.com/v2.7/%s/photos" % FB_PAGE_ID
        args['url'] = photos[0]
    if desc:
        args["message"] = desc
    if link:
        args["link"] = link

    if not args:
        raise Exception("Nothing to post")
    args["access_token"] = page_token

    resp = requests.post(post_url, data=args)
    print ""
    print resp.json()


def get_page_access_token(user_token):
    page_token = None

    url = "https://graph.facebook.com/v2.7/me/accounts"
    args = {"access_token": user_token}
    args = urlencode(args)
    complete_url = url + "?" + args
    resp = requests.get(complete_url)
    resp = resp.json()

    for i in resp['data']:
        if i['id'] == FB_PAGE_ID:
            page_token = i['access_token']

    return page_token

    
def get_user_access_token(url):
    resp = requests.get(url)
    resp = resp.json()
    return resp['access_token']


class HTTPServerHandler(BaseHTTPRequestHandler, object):
    """
    HTTP Server callbacks to handle Facebook OAuth redirects
    """

    def __init__(self, request, address, server, a_id, a_secret):
        self.app_id = a_id
        self.app_secret = a_secret
        super(self.__class__, self).__init__(request, address, server)


    def do_GET(self):
        GRAPH_API_AUTH_URI = ('https://graph.facebook.com/v2.7/oauth/' + \
                              'access_token?client_id=' + self.app_id + '&redirect_uri=' + REDIRECT_URL + \
                              '&client_secret=' + self.app_secret + '&code=')

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if 'code' in self.path:
            self.auth_code = self.path.split('=')[1]
            # Display to the user that they no longer need the browser window
            self.wfile.write('<html>You may now close this window</html>')
            self.server.access_token = get_user_access_token(GRAPH_API_AUTH_URI + self.auth_code)


class TokenHandler(object):
    """
    Class used to handle Facebook oAuth
    """

    def __init__(self, a_id, a_secret):
        self._id = a_id
        self._secret = a_secret


    def get_access_token(self):
        """
        Fetches the access key using an HTTP server to handle oAuth
        """

        ACCESS_URI = ('https://www.facebook.com/dialog/oauth?' + \
                      'client_id=' + self._id + \
                      '&redirect_uri=' + REDIRECT_URL)

        p = subprocess.Popen(["firefox", ACCESS_URI])
        httpServer = HTTPServer((HOST, PORT),
                                lambda request, address, server: HTTPServerHandler(request, address, server, self._id, self._secret))

        #This function will block until it receives a request
        httpServer.handle_request()

        p.kill()
        #Return the access token
        return httpServer.access_token
    

def fb_post():
    try:
        th = TokenHandler(APP_ID, APP_SECRET)
        user_token = th.get_access_token()
        print "\n%s" % user_token
        page_token = get_page_access_token(user_token)
        print "\n%s" % page_token

        if not page_token:
            raise Exception("Page not found")

        photos, link, desc = parse_file()
        make_post(page_token, photos, link, desc)

        print "\nSuccess!"

    except Exception as e:
        print "facebook post failed: %s" % e


if __name__ == "__main__":
    fb_post()
