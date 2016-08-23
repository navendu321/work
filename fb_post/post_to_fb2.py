import json
import requests
from urllib import urlencode

APP_ID = "125994524515407"
APP_SECRET = "62225f04b35d0184cf2a84771b44b371"
REDIRECT_URL = "https://www.facebook.com/connect/login_success.html"

# file to read from
file_path = "/home/navendu/work/fb_post/info.txt"
FB_PAGE_ID = "935683393225672"

# token file!
token_file_path = "/home/navendu/work/fb_post/token.txt"


def parse_file():
    line_count = 1

    photo = ""
    link = ""
    desc = ""
    
    f = open(file_path, 'r')
    for line in f:
        if line_count == 1:
            # read photo!
            if line.strip():
                photo = line.strip()
        elif line_count == 2:
            # read link!
            if line.strip():
                link = line.strip()
        else:
            # read description!
            desc += line

        line_count += 1

    f.close()
    return (photo, link, desc)


def make_post(page_token, photo, link, desc):
    post_url = "https://graph.facebook.com/v2.7/%s/feed" % FB_PAGE_ID
    args = {}
    if photo:
        post_url = "https://graph.facebook.com/v2.7/%s/photos" % FB_PAGE_ID
        args['url'] = photo
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


def refresh_token(token):

    # Fetch code!
    code_url = 'https://graph.facebook.com/oauth/client_code'
    args = {'access_token': token,
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'redirect_uri': REDIRECT_URL}

    args = urlencode(args)
    complete_url = code_url + "?" + args
    resp = requests.get(complete_url)
    resp = resp.json()
    print ""
    print resp
    code = resp['code']

    # Fetch new token
    token_url = 'https://graph.facebook.com/oauth/access_token'
    args = {'client_id': APP_ID,
            'code': code,
            'redirect_uri': REDIRECT_URL}

    args = urlencode(args)
    complete_url = token_url + "?" + args
    resp = requests.get(complete_url)
    resp = resp.json()
    print ""
    print resp
    new_token = resp['access_token']

    # Write new token to file
    f = open(token_file_path, 'w')
    f.write(new_token)
    f.close()

    return new_token


def fb_post():
    try:
        # read token from file!
        f = open(token_file_path, 'r')
        user_access_token = f.read().strip()
        f.close()

        user_token = refresh_token(user_access_token)        
        page_token = get_page_access_token(user_token)
        print ""
        print page_token

        if not page_token:
            raise Exception("Page not found")

        photo, link, desc = parse_file()
        make_post(page_token, photo, link, desc)

        print "\nSuccess!"

    except Exception as e:
        print "facebook post failed: %s" % e


if __name__ == "__main__":
    fb_post()
