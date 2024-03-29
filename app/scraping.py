# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup

import pandas as pd 
import datetime as dt

def initBrowser():
    return Browser("chrome", headless=False)

###################################################
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page -useful when image heavy pages may take time to load
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # setup the html parser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    slide_elem = news_soup.select_one('ul.item_list li.slide')

    # Add try/except for error handling
    try:
        # begin scraping
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

        # begin scraping
        slide_elem.find("div", class_='content_title')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        return news_title, news_p
    except AttributeError:
        return None, None
###################################################

# Featured Images-Setup and visit url
def featured_image(browser):

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.find_link_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

###################################################
# Code for the mars facts table
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table in to a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # use pandas to convert dataframe back to html code
    return df.to_html() 

###################################################
# Mars Hemispheres image scraping

def mars_hemispheres(browser):

    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)

    # parse html
    hemispheres_html = browser.html
    hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')

    # create list to hold scraped hemisphere data
    hemisphere_data = []
    # find list of hemispheres using tag+class
    result_list = hemispheres_soup.find('div', class_='result-list')
    hemispheres = result_list.find_all('div', class_='item')

    # get title, text and images for each hemisphere
    for hemisphere in hemispheres:
        title = hemisphere.find('div', class_='description')
        #long_text = hemisphere.find('p',class_='')
        #long_text = browser.find_link_by_partial_text('Mosaic')

        # find elements with link by partial text, remove " Enhanced" (space + text) to find element to click on
        title_text = title.a.text.replace(' Enhanced', '')
        browser.click_link_by_partial_text(title_text)

        # parse again avoiding attrubute error. (had trouble using try except) and get each img url
        hemispheres_html = browser.html
        hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')
        image = hemispheres_soup.find('div', class_='downloads').find('ul').find('li')
        img_url = image.a['href']

        # append the hemispehere data to the list
        hemisphere_data.append({'title': title_text, 'img_url': img_url})
    return hemisphere_data

###################################################
def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    #return news_title, news_paragraph
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }
    return data

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())

# end browser session
#browser.quit()