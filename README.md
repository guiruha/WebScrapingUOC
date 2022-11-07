# Web Scraping UOC

## Summary

This project has been created within the framework of the subject "Typology and life cycle of data", from the Master's Degree in Data Science of Universitat Oberta de Catalunya.

The projects aims to apply web scraping techniques to extract data from Booking.com webpage and create a dataset.

## Team Members

* Gerard-Josep Alcalde Gascón (@gerard2310)

* Guillem Rochina Aguas (@guiruha)

## Files

## How to set the environment to run the project correctly

In order to be able to run this project in your machine you need to either create the next environment:

``conda env create --file=environment.yml``

or install all the required packages in your own environment with the following command:

``pip install -r requirements.txt``

## How to run the project

For the moment you can start the project from the beginning using the following command:

``python runScraper.py str(day-month-year_checkin) str(day-month-year_checkout) str(city) int(number_of_adults) int(number_of_children) int(number of rooms)``

To be more illustrative, the following example is given:

``python runScraper.py "27-January-2023" "5-February-2023" "Valencia" 2 3 2``

In Version 1.0 of the project the scraper starts in the first landing page of Booking.com and performs the selections of the criteria inputed when running the script. Once all criteria is filled and results are given, it starts collecting the urls of all listings in the results (page by page, until the last page is reached). For the moment, all links are stored in the file "listing_links.txt".

## License

License to be decided

## Resources