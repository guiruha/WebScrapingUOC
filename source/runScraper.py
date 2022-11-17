import os
import sys
import csv
import pandas as pd
from urlListingsSpider import UrlSpider

if __name__ == "__main__":
    booking = UrlSpider(checkin=sys.argv[1],
                        checkout=sys.argv[2], 
                        city=sys.argv[3],
                        adults=sys.argv[4], 
                        children=sys.argv[5], 
                        rooms=sys.argv[6])

    booking.main()

""" BORRAR   
    #Concatenate the different csv files into a unique file
    df_cols = ["city_searched", "check_in_searched", "check_out_searched", "room_config_searched", "name", "address",
               "hotel_coordinates", "hotel_score", "hotel_scores", "hotel_description", "features", "room_data",
               "count", "current_page", "in_page_count"]

    df_all_cities = pd.DataFrame(columns = df_cols)
    for file in os.listdir("cities_files/"):
        df_city = pd.read_csv("cities_files/{}".format(file))
        df_all_cities = pd.concat([df_all_cities, df_city])

    df_all_cities.to_csv("cities_files/all_cities.csv")
"""