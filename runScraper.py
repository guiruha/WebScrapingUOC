import sys
import csv
from urlListingsSpider import UrlSpider

if __name__ == "__main__":
    with open(sys.argv[3], newline='') as f:
        reader = csv.reader(f)
        cities = list(reader)

    for city_in in cities[0]:
        booking = UrlSpider(checkin=sys.argv[1],
                            checkout=sys.argv[2], 
                            city=city_in,
                            adults=sys.argv[4], 
                            children=sys.argv[5], 
                            rooms=sys.argv[6])

        booking.main()