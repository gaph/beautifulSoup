#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import json
import io
import urllib2
import urllib

page_url = "https://www.petrol-travel.si"
locations_list = []

'''
get all subpages with list of desstinations
'''
def find_all_location_pages():
    soup = build_soup(page_url)
    for ul in soup.find_all(name="ul", attrs={'class':'sub-menu'}):
        #css selector
        #for link in ul.select("li > a"):
        for links in ul.find_all(name="a"):
            url = page_url + links.get("href")
            url = url.encode("utf-8")
            get_location_data(url)

def get_location_data(url):
    soup_list = build_soup(url)
    i = 1
    for location in soup_list.find_all(name="li", attrs={'class':'box'}):
        location_url = page_url + location.a["href"]
        location_soup = build_soup(location_url)

        country = location_soup.find(name="small", class_="l fw").text.split(",")[0]
        title = location_soup.h1.text.strip()
        termin = location_soup.find(name="span", attrs={"id":"sq_vnd"}).text + "-"+location_soup.find(name="span", attrs={"id":"sq_bsd"}).text
        offer = location_soup.find(name="div", attrs={'class':"order-content ponudba"})
        image = location_soup.find(class_="big-img").find("img")["src"]

        download_image(image)

        if offer.contents:
            offer_place = offer.contents[0].text.strip()
            offer_service = offer.contents[3].text.replace("Storitev: ","").strip()
            offer_special_price = unicode(location_soup.find(text="Akcijska cena: ").next).strip()
            offer_golden_points = location_soup.find(text="Zlate točke: ")
            offer_golden_points = offer_golden_points and re.findall(r'\d+', offer_golden_points.next)[0].strip() or ""

            location_dict = {
                'image' : "images/"+image.split("/").pop(),
                'drzava' : country,
                'url' : location_url,
                'naslov ponudbe': title,
                'kraj': offer_place,
                'termin': termin,
                'storitev': offer_service,
                'akcijska cena':offer_special_price,
                "zlate tocke": offer_golden_points
            }

            col = {}
            col["col"+str(i)] = location_dict
            i+=1
            if i == 4:
                i = 1

            locations_list.append(col)
    print locations_list

def build_soup(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page, from_encoding="utf-8")
    page.close()
    return soup

def save_to_json():
    row = {}
    row["row"] = locations_list
    with io.open('location.json', 'w', encoding='utf-8') as location_file:
        location_file.write(unicode(json.dumps(row, ensure_ascii=False, indent=4, separators=(',', ': '))))

def download_image(image):
    image_url = page_url + image
    print image_url

    if image.split("/").pop() != "nopic_.jpg":
        urllib.urlretrieve(image_url, "images/"+image.split("/").pop())


find_all_location_pages()
save_to_json()




