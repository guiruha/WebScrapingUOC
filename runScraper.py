import sys
from urlListingsSpider import UrlSpider
from dataListingsSpider import DataSpider

if __name__ == "__main__":
    booking_url = UrlSpider(checkin=sys.argv[1], 
                            checkout=sys.argv[2], 
                            city=sys.argv[3],  
                            adults=sys.argv[4], 
                            children=sys.argv[5], 
                            rooms=sys.argv[6])
    booking_url.main()
    
    with open("listing_links.txt", "r") as links:
        for ind, link in enumerate(links):
            if ind == 10:
                break
            booking_data = DataSpider(link)
            try:   
                booking_data.obtain_data()
            except:
                pass
    