#importing BeautifulSoup 4 and selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
from tqdm import tqdm

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


def main(search_term, level):
    """Run Main program,
           level: 0:Search Page Results, 1 : Product Page Results"""
    # startup the webdriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    records = []
    url = get_url(search_term)

    for page in tqdm(range(1, 21)):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})

        for item in results:
            record = extract_details(item)
            if record:
                records.append(record)

    df = pd.DataFrame(records)
    df.columns = ['Title', 'Author', 'Link', 'Price', "Rating", 'Rating Count']

    if level > 0:
        # additional code for next level depth crawling and scraping product details, product description
        list_language = []
        list_book_description = []
        for i in tqdm(range(len(df['Link']))):
            try:
                driver.get(df['Link'][i])
                soup2 = BeautifulSoup(driver.page_source, 'html.parser')

                book_description = soup2.find('div', {
                    "class": "a-expander-content a-expander-partial-collapse-content"}).text.strip()
                product_details = soup2.find('div', {"id": "detailBullets_feature_div"})
                language = product_details.find_all('span', {'class': 'a-list-item'})[1].find_all('span')[1].text.strip()
            except:
                language = 'Unknown'
                book_description = 'Unknown'
            list_language.append(language)
            list_book_description.append(book_description)

        df['Langauge'] = list_language
        df['Description'] = list_book_description

    driver.close()
    df.to_csv('amazon_books_records_with_description.csv', sep=',')


if __name__ == '__main__':
    start_time = datetime.now()

    # main('Books',0) # for product search results only
    main('Books', 1)  # for product search results and individual product details

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

