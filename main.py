#importing BeautifulSoup 4 and selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def get_url(search_term):
    """Generates a URL from the search term."""
    generic_url = 'https://www.amazon.in/s?k={}'
    # conforming to the amazon's url format for search terms
    search_term = search_term.replace(' ', '+')

    # added page query
    url = generic_url.format(search_term)
    url += '&page={}'
    return url


def extract_details(item):
    """Extracts details of a single record"""
    atag = item.h2.a
    title = atag.text.strip()

    product_url = "https://amazon.in" + atag.get('href')
    price_parent = item.find('span', 'a-price')
    # Error Handling
    try:  # used try block for errors due to missing values
        price = price_parent.find('span', 'a-offscreen').text[1:]
        author = item.find('a', {
            'class': 'a-size-base a-link-normal s-underline-text s-underline-link-text s-link-style'}).text.strip()
        rating = item.i.text
        rating_count = item.find('span', {"class": "a-size-base s-underline-text"}).text
    except AttributeError:
        price = 'unkown'
        author = 'unknown'
        rating = 'unknown'
        rating_count = 'unknown'

    output = (title, author, product_url, price, rating, rating_count)
    return output


def main(search_term):
    """Run Main program"""
    # startup the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    records = []
    url = get_url(search_term)

    for page in range(1, 21):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in results:
            record = extract_details(item)
            if record:
                records.append(record)

    driver.close()
    df = pd.DataFrame(records)
    df.columns = ['Title', 'Author', 'Link', 'Price', "Rating", 'Rating Count']
    df.to_csv('amazon_books_records.csv', sep=',')



if __name__ == '__main__':
    main('Books')
