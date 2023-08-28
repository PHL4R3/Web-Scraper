import urllib





GLOBAL_DOMAIN =""
GLOBAL_DEPTH=0
#take input function
def take_input():
    GLOBAL_DOMAIN = input("Welcome to the scraper, please enter your domain: ")
    GLOBAL_DEPTH = input("Please enter the target depth: ")
    url = input("Please enter the target url: ")
    print(grab_html(url))




#Networking/api to take html from website
def grab_html(url):
    webURL = urllib.request.urlopen(url)
    data = webURL.read()
    return data




#take html and find links




#append url to list of urls after checking to see if its a dupe



#main function to set up recursion
def main():
    take_input()
main()