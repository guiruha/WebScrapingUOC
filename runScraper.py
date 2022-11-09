import sys
from urlListingsSpider import UrlSpider

if __name__ == "__main__":
    booking = UrlSpider(checkin=sys.argv[1], 
                            checkout=sys.argv[2], 
                            city=sys.argv[3],  
                            adults=sys.argv[4], 
                            children=sys.argv[5], 
                            rooms=sys.argv[6])

    booking.main()
    
    
    