

import os
import pandas as pd
import numpy as np
import requests
import bs4
import lxml


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def question1():
    """
    NOTE: You do NOT need to do anything with this function.

    """
    # Don't change this function body!
    # No python required; create the HTML file.

    return


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------




def extract_book_links(text):
    """
    :Example:
    >>> fp = os.path.join('data', 'products.html')
    >>> out = extract_book_links(open(fp, encoding='utf-8').read())
    >>> url = 'scarlet-the-lunar-chronicles-2_218/index.html'
    >>> out[1] == url
    True
    """
    book_links = []
    
    soup = bs4.BeautifulSoup(text, 'html.parser')
    
    # Find all the book listings
    book_listings = soup.find_all('article', class_='product_pod')
    
    for book_listing in book_listings:
        # Check the book's rating
        rating = book_listing.find('p', class_='star-rating')['class'][1]
        if rating == 'Four' or 'Five':
            # Check the book's price
            price = float(book_listing.find('p', class_='price_color').text[1:])
            if price < 50:
                # Extract the book URL
                book_url = book_listing.find('h3').find('a')['href']
                book_links.append('http://books.toscrape.com/catalogue/' + book_url)
    
    return book_links


def get_product_info(text, categories):
    """
    :Example:
    >>> fp = os.path.join('data', 'Frankenstein.html')
    >>> out = get_product_info(open(fp, encoding='utf-8').read(), ['Default'])
    >>> isinstance(out, dict)
    True
    >>> 'Category' in out.keys()
    True
    >>> out['Rating']
    'Two'
    """
    soup = bs4.BeautifulSoup(text, 'html.parser')
    
    # Get the product title
    title = soup.find('div', class_='product_main').find('h1').text
    
    # Get the product price
    price = soup.find('p', class_='price_color').text[1:]
    
    # Get the product availability
    availability = soup.find('p', class_='instock availability').text.strip()
    
    # Get the product rating
    rating = soup.find('p', class_='star-rating')['class'][1]
    
    # Get the product category
    category = soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
    
    # Check if the category is in the given list of categories
    if category in categories:
        # Get the book details
        upc = soup.find('th', text='UPC').find_next_sibling('td').text
        product_type = soup.find('th', text='Product Type').find_next_sibling('td').text
        price_incl_tax = soup.find('th', text='Price (incl. tax)').find_next_sibling('td').text
        price_excl_tax = soup.find('th', text='Price (excl. tax)').find_next_sibling('td').text
        tax = soup.find('th', text='Tax').find_next_sibling('td').text
        num_reviews = soup.find('th', text='Number of reviews').find_next_sibling('td').text
        category = soup.find('ul', class_='breadcrumb').find_all('a')[-1].text.strip()
        description = soup.find('article', class_='product_page').find('p', recursive=False).text.strip()
        product_info = {
                        'UPC': upc,
                        'Product Type': product_type,
                        'Price (excl. tax)': price_excl_tax,
                        'Price (incl. tax)': price_incl_tax,
                        'Tax': tax,
                        'Availability': availability,
                        'Number of reviews': num_reviews,
                        'Category': category,
                        'Rating': rating,
                        'Description': description,
                        'Title': title
                    }
        return product_info
    
    return None


def scrape_books(k, categories):
    """
    :param k: number of book-listing pages to scrape.
    :returns: a dataframe of information on (certain) books
    on the k pages (as described in the question).
    :Example:
    >>> out = scrape_books(1, ['Mystery'])
    >>> out.shape
    (1, 11)
    >>> out['Rating'][0] == 'Four'
    True
    >>> out['Title'][0] == 'Sharp Objects'
    True
    """
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    books = []
    
    for page in range(1, k+1):
        url = base_url.format(page)
        response = requests.get(url)
        html_content = response.content
        soup = bs4.BeautifulSoup(html_content, 'html.parser')
        
        product_list = soup.find_all('article', class_='product_pod')
        
        for product in product_list:
            # Get the product rating
            rating = product.find('p', class_='star-rating')['class'][1]
            
            # Get the product price
            price = float(product.find('p', class_='price_color').text[1:])
            
            # Check if the book meets the criteria
            if (rating == 'Four' or 'Five') and price < 50: 
                # Get the book-specific URL
                book_url = product.find('h3').find('a')['href']
                book_response = requests.get('http://books.toscrape.com/catalogue/' + book_url)
                book_soup = bs4.BeautifulSoup(book_response.content, 'html.parser')
                
                # Get the product category from the book-specific page
                category = book_soup.find('ul', class_='breadcrumb').find_all('a')[2].text.strip()
                if category in categories:
                    # Get the product title
                    title = product.find('h3').find('a')['title']
                    
                    # Get the product availability
                    availability = product.find('p', class_='instock availability').text.strip()
                    # Get the book details
                    upc = book_soup.find('th', text='UPC').find_next_sibling('td').text
                    product_type = book_soup.find('th', text='Product Type').find_next_sibling('td').text
                    price_incl_tax = book_soup.find('th', text='Price (incl. tax)').find_next_sibling('td').text
                    price_excl_tax = book_soup.find('th', text='Price (excl. tax)').find_next_sibling('td').text
                    tax = book_soup.find('th', text='Tax').find_next_sibling('td').text
                    num_reviews = book_soup.find('th', text='Number of reviews').find_next_sibling('td').text
                    category = book_soup.find('ul', class_='breadcrumb').find_all('a')[-1].text.strip()
                    description = book_soup.find('article', class_='product_page').find('p', recursive=False).text.strip()
                    books.append({
                        'UPC': upc,
                        'Product Type': product_type,
                        'Price (excl. tax)': price_excl_tax,
                        'Price (incl. tax)': price_incl_tax,
                        'Tax': tax,
                        'Availability': availability,
                        'Number of reviews': num_reviews,
                        'Category': category,
                        'Rating': rating,
                        'Description': description,
                        'Title': title
                    })
    
    return pd.DataFrame(books)


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def stock_history(ticker, year, month):
    """
    Given a stock code and month, return the stock price details for that month
    as a DataFrame.

    >>> history = stock_history('BYND', 2019, 6)
    >>> history.shape == (20, 13)
    True
    >>> history.label.iloc[-1]
    'June 03, 19'
    """
    # Format the URL with the provided parameters
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={year}-{month:02d}-01&to={year}-{month:02d}-31&apikey=DLUYKxazfmrvrjEpbRuUlCyPuscLQWwn"
    
    # Send a GET request to the API
    response = requests.get(url)
    
    # Extract the JSON data from the response
    data = response.json()
    print(data)
    # Extract the historical prices from the JSON data
    historical_prices = data['historical']
    
    # Create a DataFrame from the historical prices
    df = pd.DataFrame(historical_prices)
    
    return df


def stock_stats(history):
    """
    Given a stock's trade history, return the percent change and transactions
    in billions of dollars.

    >>> history = stock_history('BYND', 2019, 6)
    >>> stats = stock_stats(history)
    >>> len(stats[0]), len(stats[1])
    (7, 6)
    >>> float(stats[0][1:-1]) > 30
    True
    >>> float(stats[1][:-1]) > 1
    True
    >>> stats[1][-1] == 'B'
    True
    """
    # Calculate the percent change
    start_price = history.iloc[0]['open']
    end_price = history.iloc[-1]['close']
    percent_change = ((end_price - start_price) / start_price) * 100
    
    # Calculate the estimated total transaction volume
    history['average_price'] = (history['high'] + history['low']) / 2
    total_volume = (history['volume'] * history['average_price']).sum() / 1e9
    
    # Format the results as strings with two decimal places
    percent_change_str = f"{percent_change:.2f}%"
    total_volume_str = f"{total_volume:.2f}B"
    
    return percent_change_str, total_volume_str



