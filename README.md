# Web Scraping UOC | Booking.com

## Summary

This project has been created within the framework of the subject "Typology and life cycle of data", from the Master's Degree in Data Science of Universitat Oberta de Catalunya.

The projects aims to apply web scraping techniques to extract data from Booking.com webpage and create a dataset.

## Team Members

* Gerard-Josep Alcalde Gascón (@gerard2310)

* Guillem Rochina Aguas (@guiruha)

## Files
```bash
────WebscrapingUOC
    │
    ├───dataset
    │   │
    │   └───── hotel_images
    │          │
    │          └─── "hotel_name"/image_{}.png
    │          hotels_data.csv
    ├──source
    │         BookingScraper.py
    │         runScraper.py
    │
    ├───Memoria.pdf
    │
    │
    ├───sampleDataCollection.sh
    │
    │
    ├───LICENSE.md
    │
    │
    ├───envrionment.yml       
    │
    │
    └───requirements.txt
```
- **dataset/hotels_data.csv**: Output dataset containing all the info scraped
- **dataset/hotel_images/hotel_name/image_{}.png**: Directory containing photos extracted from each hotel scraped
- **source/BookingScraper.py**: Script containing all the design and implementation of the web scraper
- **source/runScraper.py**: Script that runs all the processes designed in the BookingScraper.py script
- **Memoria.pdf**: Pdf containing answers to the questions of this practice
- **sampleDataCollection.sh**: Bash script that executes the scraper with different search parameters
- **LINCENSE.md**
- **environment.yml**: Yaml of the conda environment used in this project
- **requirements.txt**: List of all python libraries used in this project

## How to set the environment to run the project correctly

In order to be able to run this project in your machine you need to either create the next environment:

```shell
$ conda env create --file=environment.yml
```

or install all the required packages in your own environment with the following command:

```shell
$ pip install -r requirements.txt
```

In any case, a list of the libraries used in this project is presented below:

```
time
csv
collections
os
datetime
random
urllib
selenium
webdriver_manager
sys
```

## How to run the project

For the moment you can start the project from the beginning using the following command:

```shell
$ python source/runScraper.py str(checkin_date) str(checkout_date) str(city) int(nºadults) int(nºchildren) int(nº rooms)
```

To be more illustrative, the following example is given:

```shell
$ python source/runScraper.py "27-January-2023" "5-February-2023" "Valencia" 2 3 2
```

In Version 1.0 of the project the scraper starts in the first landing page of Booking.com and performs the selections of the criteria inputed when running the script. Once all criteria is filled and results are given, it starts collecting the urls of all listings in the results (page by page, until the last page is reached). For the moment, all links are stored in the file "listing_links.txt".

## License

The license of the resulting dataset is **Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

## Disclaimer

This project's goal is purely educational and for research and learning purposes. The consequences of any action in which the elements contained in this repository may be involved are the solely responisibility of its actor, that is to say, the authors will not be held responsible in case of any kind of misuse of the presnt material which may bring criminal charges against the person involved.

According to section A14.2 of Booking's terms of service no one is allowed to copy data from Booking.com with commercial intentions, including all kind of information that can be found in its webpage (hotel descriptions, photos, prices, etc.). Therefore, precaution is adviced.

## Resources

Lawson, R. (2015). Web Scraping with Python. Packt Publishing Ltd. 

Mitchel, R. (2015). Web Scraping with Python: Collecting Data from the Modern Web. O'Reilly Media, Inc.

Calvo, M. & Subirats, L. (2019). Web Scraping. Editorial UOC.