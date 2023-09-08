import urllib.request
from bs4 import BeautifulSoup
import csv
import multiprocessing
import os
import time
from urllib.error import HTTPError, URLError
from http.client import InvalidURL


global backoff
backoff=1

#take input function
def take_input():
    global GLOBAL_DOMAIN
    global GLOBAL_DEPTH
    GLOBAL_DOMAIN = input("Welcome to the scraper, please enter your domain: ")
    GLOBAL_DEPTH = input("Please enter the target depth: ")
    url = input("Please enter the target url: ")
    recursion_handler(url,GLOBAL_DEPTH)




#Networking/api to take html from website
def grab_html(url):
    if "https://" not in url:
        url = "https://" + url
    try:
        webURL = urllib.request.urlopen(url)
        data = webURL.read()
        get_links_from_html(data)

    except HTTPError as e:
        if e.code == 429: #timeout
            exponential_backoff()
            global backoff
            print(str(backoff))
            grab_html(url)
        if e.code== 403: #forbidden
            pass
    except URLError:
         pass
    except InvalidURL:
         url = str(url).replace(" ","+")
    except UnicodeDecodeError:
        webURL = urllib.request.urlopen(url)
        data = webURL.read()
        soup = BeautifulSoup(data,'html.parser')
        meta_tag =soup.find('meta', charset = True)
        if meta_tag:
             data = data.decode(str(meta_tag))
             get_links_from_html(data)
        else:
             pass
    except:
         pass




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
        tmpCurrentLinks=None
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","r") as prevLinks:
            csv_reader=csv.reader(prevLinks)
            currentlinks= next(csv_reader,currentlinks)
            prevSet = set(currentlinks)
            validLinkSet = set(valid_links)
            currentlinks = list(prevSet.union(validLinkSet))
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","w") as prevLinks:
            csv_writer = csv.writer(prevLinks)
            for link in valid_links:
                 link= str(link).replace(" ","+")
                 link= str(link).replace("\n","")
                 currentlinks.append(link)
            csv_writer.writerow(currentlinks)
        with open("tmp.csv","r") as tmp:
                csv_reader = csv.reader(tmp)
                tmpCurrentLinks = next(csv_reader,tmpCurrentLinks)
        with open("tmp.csv","w") as tmp:
            csv_writer = csv.writer(tmp)
            for link in valid_links:
                    link= str(link).replace(" ","+")
                    link= str(link).replace("\n","")
                    tmpCurrentLinks.append(link)
            csv_writer.writerow(currentlinks)
    #except statement for if theres a new file
    except:
        with open(GLOBAL_DOMAIN + "Scrape_Depth="+str(GLOBAL_DEPTH)+ ".csv","w") as findings:
            csv_writer = csv.writer(findings)
            csv_writer.writerow(valid_links)     
        with open("tmp.csv", "w") as tmp:
            csv_writer = csv.writer(tmp)
            csv_writer.writerow(valid_links)

#set up recusion
def recursion_handler(url,depth):
     if int(depth) <0:
            return
     grab_html(url)
     row= None
     with open("tmp.csv", "r") as tmp:
          csv_reader = csv.reader(tmp)
          row = next(csv_reader)
     with open("tmp.csv", "w") as tmp:
            csv_writer = csv.writer(tmp)
            csv_writer.writerow([])
     for link in row:
        recursion_handler(link,int(depth)-1)
def exponential_backoff():
    global backoff
    backoff = backoff *2
    time.sleep(backoff)

#main function to set up recursion
def main():
    take_input()
main()