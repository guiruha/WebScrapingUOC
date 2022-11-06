import sys
from urlListingsSpider import BookingSpider

if __name__ == "__main__":
    booking = UrlSpider(checkin=sys.argv[1], 
                            checkout=sys.argv[2], 
                            city=sys.argv[3], 
                            country=sys.argv[4], 
                            adults=sys.argv[5], 
                            children=sys.argv[6], 
                            rooms=sys.argv[7])
    booking.main()
    
    
    