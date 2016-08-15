import datetime
import urllib
import urllib2
import json
import MySQLdb
import os

import logging as log
log.basicConfig(filename='website_phone.log', level=log.DEBUG)

# filters!
keys = ["AIzaSyBaN-UeRSvrPFuHG8eOLrQp548XHlrFoYk",
        "AIzaSyD7_fcaHfLzbBjwu63ub9LXAPEYVjtOEZk"]

file_path = "/home/navendu/work/google_places/zip-lat-long2.txt"
# radius in meters, max 50000
radius = 15000
place_type = ""

# mysql config!
db_ip = "127.0.0.1"
db_port = 3306
db_name = "testdb"
db_user = "root"
db_pass = "xxxxxxxxx"

db_handle = MySQLdb.connect(host=db_ip, port=db_port, user=db_user, passwd=db_pass, db=db_name)



def insert_into_db(place_id, name, formatted_phone_number,
                   formatted_address, website, maps_url):
    try:
        log.debug("Inserting place_id: %s" % place_id)
        cursor = db_handle.cursor()

        formatted_address = formatted_address.replace("\"", "").replace("'", "")
        sql = "INSERT INTO tblPlaces (PlaceID, Name, FormattedAddress, FormattedPhoneNumber, Website, URL) " + \
              "VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\") " \
              % (place_id, name, formatted_address, formatted_phone_number, website, maps_url) + \
              "ON DUPLICATE KEY UPDATE " + \
              "Name=\"%s\", FormattedAddress=\"%s\", FormattedPhoneNumber=\"%s\", Website=\"%s\", URL=\"%s\"" \
              % (name, formatted_address, formatted_phone_number, website, maps_url)

        cursor.execute(sql)
        cursor.close()

    except Exception as e:
        log.error("Insert into db failed for place_id %s: %s" % (place_id, e))


def google_api_wrapper(url, query_args):
    try:
        global keys
        if len(keys) == 0:
            raise Exception("No keys available")

        error_status = ["OVER_QUERY_LIMIT", "REQUEST_DENIED"]

        query_args["key"] = keys[0]
        encoded_args = urllib.urlencode(query_args)
        complete_url = url + "?" + encoded_args
        resp = urllib2.urlopen(complete_url)
        data = json.load(resp)

        if data["status"] in error_status:
            # remove key and call again!
            log.info("Removing key %s" % keys[0])
            keys = keys[1:]
            google_api_wrapper(url, query_args)

        return data

    except urllib2.HTTPError as e:
        log.error("Google api call failed due to http error: %s" % e)
    except Exception as e:
        log.error("Google api call failed: %s" % e)


def call_google_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    query_args = {"placeid": place_id}

    data = google_api_wrapper(url, query_args)
    if not data:
        return
    place_detail = data["result"]

    # get place data!
    name = place_detail.get("name", "")
    formatted_phone_number = place_detail.get("formatted_phone_number", "")
    formatted_address = place_detail.get("formatted_address", "")
    website = place_detail.get("website", "")
    maps_url = place_detail.get("url", "")
    if formatted_phone_number or website:
        insert_into_db(place_id, name, formatted_phone_number,
                       formatted_address, website, maps_url)


def call_google_places(location):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    query_args = {"location": location,
                  "radius": radius}
    if place_type:
        query_args["type"] = place_type

    data = google_api_wrapper(url, query_args)
    if not data:
        return

    for place in data["results"]:
        place_id = place["place_id"]
        call_google_place_details(place_id)


def insert_website_phone():
    try:
        num_lines_ignore = 1
        lines_counter = 0
        already_processed_location = False
        set_flag = False

        # read current location
        current_location = None
        if os.path.exists("current_location.txt"):
            fr_handle = open("current_location.txt", 'r')
            current_location = fr_handle.read().strip()
            fr_handle.close()

        file_handle = open(file_path, 'r')
        for line in file_handle:
            # ignore empty lines!
            if line.strip():
                # ignore lines!
                if lines_counter < num_lines_ignore:
                    lines_counter +=1
                    continue

                # get location!
                items = line.split(",", 1)
                location = items[1].strip()

                # ignore lines till current location
                if current_location:
                    if location != current_location:
                        if set_flag:
                            already_processed_location = False
                        else:
                            already_processed_location = True
                    else:
                        # reached current location, ignore this as well.
                        already_processed_location = True
                        set_flag = True

                if already_processed_location:
                    continue

                # save current location
                fw_handle = open("current_location.txt", 'w')
                fw_handle.write(location)
                fw_handle.close()

                log.debug("\nProcessing location %s\n" % location)
                call_google_places(location)

        # delete current location
        os.remove("current_location.txt")

    except Exception as e:
        log.error("Script failed: %s" % e)
        raise
    finally:
        db_handle.close()


if __name__ == "__main__":
    log.info("Started Processing at %s\n" % datetime.datetime.now())
    insert_website_phone()
    log.info("Finished Processing at %s\n\n\n" % datetime.datetime.now())
