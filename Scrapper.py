import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from random import randint
from time import sleep
import re
import csv


base_url = "https://www.amazon.com/s?i=stripbooks&bbn=283155&rh=p_n_feature_browse-bin%3A2656022011&s=review-count-rank&page="

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}


def scrape_page(url, header):
    
    try:
        response = requests.get(url, headers=header)
    except:
        print("Connection Error: could not connect to page")
        return []
    
    soup = bs(response.content, 'html.parser')
    rev_div = []
    for a in soup.findAll("a",attrs={"class","a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"}, href = True):
        if a.text:
            rev_div.append(a['href'])

    book_id =  []
    for link in rev_div:
        attributes = link.split('/')
        book_id.append(attributes[3])

    return book_id

#print(scrape_page(base_url, header))
def get_books_id():
    book_id = []
    textFile = open("bookID.txt", "w+")
    for i in range(1,76):
        
        url = base_url + str(i)
        new_id = scrape_page(url, header)
        book_id = book_id + new_id
        for id in new_id:
            textFile.write(id + '\n')
        print("page number "+str(i) + " with " + str(len(new_id))+ " entries")
        sleep(randint(3,6))

    textFile.close()
    print(len(book_id))

def get_saved_id():
    listID = []
    textFile = open("bookID.txt", "r+")
    listID = textFile.readlines()
    textFile.close()
    return listID

def get_all_books():
    csv_headers = ["id", "title", "authors", "price", "date", "pages", "language", "rating", "num_ratings" ,"category 1", "category 2", "category 3"]
    listID = get_saved_id()
    with open('AmazonBooksDataset.csv', 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        for id in listID:
            try:
                data = get_book_data(id, header)
                if data !=  []:
                    print(data)
                    writer.writerow(data)
                sleep(randint(3,6))
            except:
                print("Error Book: " + id)
                sleep(10)

def clean_up_details(detail):
    temp = detail
    temp = temp.replace("  ", "")
    temp = temp.replace(":", "")
    temp = temp.replace("\n", "")
    temp = temp.replace("Publisher", "")
    temp = temp.replace("Language", "")
    temp = temp.replace("Hardcover", "")
    temp = temp.replace("ISBN-10", "")
    temp = temp.replace("ISBN-13", "")
    temp = temp.replace("Item Weight", "")
    temp = temp.replace("Dimensions", "")
    temp = temp.replace("\u200f\u200e", "")
    return temp

def get_cat(text):
    text = text.split(" ")
    for i in range(3):
        text.pop(0)
    # text.pop(-1)
    text = (" ").join(text)
    return text

def get_date(text):
    text = text.split(" ")
    text.pop(-1)
    new_text = []
    for i in range(3):
        new_text.append(text.pop(-1))
    temp = new_text[0]
    new_text[0] = new_text[2]
    new_text[2] = temp
    new_text = (" ").join(new_text)
    new_text = new_text[1:-1]
    new_text = new_text.replace(",","")
    return new_text


def get_rating(text):
    text = text.replace("stars", "")
    text = text.replace(",", "")
    text = text.split(" ")
    return text[2], text[6]

def get_book_data(id, header):
    url = "https://www.amazon.com/dp/" + str(id) + "/"

    try:
        response = requests.get(url, headers=header)
        soup = bs(response.content, 'html.parser')
        title = soup.find(id ="productTitle").get_text()
    except:
        print("Connection Error: could not connect to page")
        return []
    
    try:
        price = soup.find(id = "price").get_text()
        price = float(price[1:])
    except:
        price = -1
    
    try:
        author = soup.find(class_ = "author notFaded")
        authors = []
        for div in author.find_all(class_ = "a-link-normal"):
            authors.append(div.text)
        
        temp_authors = authors[:]
        for text in temp_authors:
            if "Amazon" in text or "search" in text:
                authors.remove(text)
    except:
        authors = ["None"]
    


    try:
        det = soup.find(id = "detailBullets_feature_div")
    except :
        print("No Details Avaiable for book: " + id)
        return []
    
    details = []
    
    for li in det.find_all("li"):
        temp = li.text
        temp = clean_up_details(temp)

        if "ASIN" not in temp:
            details.append(temp)


    date = get_date(details[0])
    pages = details[2]
    pages = int(re.search(r'\d+', pages).group())

    categories = []
    for i in range(3):
        category = get_cat(details[-2-i])
        if "100" not in category:
            categories.append(category)
        else:
            break
    
    language = details[1].replace(" ", "")
    
    rating, num_ratings = get_rating(details[-1])

    id = id.replace("\n", "")
    
    return [id, title, authors[0], price, date, pages, language, rating, num_ratings] + categories

# print(get_book_data("1400226759", header))
get_all_books()

#final id: 1338600834