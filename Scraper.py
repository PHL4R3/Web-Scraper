import urllib.request
import pprint
from bs4 import BeautifulSoup
import csv
import multiprocessing
import os


#take input function
def take_input():
    global GLOBAL_DOMAIN
    global GLOBAL_DEPTH
    GLOBAL_DOMAIN = input("Welcome to the scraper, please enter your domain: ")
    GLOBAL_DEPTH = input("Please enter the target depth: ")
    url = input("Please enter the target url: ")
    pprint.pprint(grab_html(url))




#Networking/api to take html from website
def grab_html(url):
    if "https://" not in url:
        url = "https://" + url
    webURL = urllib.request.urlopen(url)
    data = webURL.read()
    pprint.pprint(get_links_from_html(data))




#take html and find links
def get_links_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    link_list = [link.get('href') for link in links]  
    valid_links = [link for link in link_list if link is not None and link.startswith('http') and GLOBAL_DOMAIN in link]
    append_to_list(valid_links)
#append url to list of urls after checking to see if its a dupe
def append_to_list(valid_links):
    global GLOBAL_DOMAIN
    global GLOBAL_DEPTH
    #try statement if the file exists
    try:
        currentlinks=None
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","r") as prevLinks:
            csv_reader=csv.reader(prevLinks)
            currentlinks= next(csv_reader,currentlinks)
            for link in valid_links:
                    if link in currentlinks:
                            valid_links.pop(link)
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","w") as prevLinks:
            csv_writer = csv.writer(prevLinks)
            for link in valid_links:
                 currentlinks.append(link)
            csv_writer.writerow(currentlinks)
    #except statement for if theres a new file
    except:
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","w") as findings:
            csv_writer = csv.writer(findings)
            csv_writer.writerow(valid_links)     



#main function to set up recursion
def main():
    take_input()
main()