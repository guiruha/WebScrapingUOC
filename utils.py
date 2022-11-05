import datetime
import sys


def generate_url(checkin, checkout, city, country, adults, children, rooms):

    # Create url
    url = "https://www.booking.com/searchresults.es.html?ss={city}&dest_type=city&checkin={checkin}&checkout={checkout}&group_adults={adults}"\
        "&group_children={children}&order=price&ss={city}%2C%20{country}&no_rooms={rooms}"\
        .format(checkin = checkin,
                checkout = checkout,
                adults = int(adults),
                children = int(children),
                city=city,
                country=country,
                rooms = rooms)
    return url