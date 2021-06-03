# Dependencies
from bs4 import BeautifulSoup as soup
from splinter import Browser
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


# executable_path = {"executable_path": "\Users\meghanmulhern\Downloads\chromedriver"}
# browser = Browser("chrome", **executable_path, headless=False)

def scrape_all():

    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless= True)

    news_title, news_paragraph = mars_news(browser)

    #Run al scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()

    }

    #stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    #scrape mars news
    #visit the mars nasa news site
    url= 'https://redplanetscience.com/'
    browser.visit(url)

    #optional delay for loading page
    browser.is_element_present_by_css('div.list_text', wait_time=1)


    #convert the browser html 

    html = browser.html
    news_soup = soup(html, 'html.parser')

    #add try for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #use the parent element to find the first 'a' tag and save it as a 'news title'
        news_title = slide_elem.find("div", class_="content_title").get_text()

        #use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    #visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    #Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    #Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #add try/except for error handling
    try:
            img_url_rel = img_soup.find('img', class_ = 'fancybox-image').get('src')

    except AttributeError:
        return None

    #use base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    #add try/except for error handling
    try:
        #use 'read_html' to scrape the facts tablke into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None
    
    #assign columns and set index of dataframe 
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #convert dataframe into HTML format, add bootstrap
    return dt.to_html(classes="table table-striped")

def hemispheres(browser):
    url = 'https://marshemispheres.com/'

    browser.visit(url + 'index.html')

    #click the link, find the sample anchor, turn the href
    hemisphere_image_urls = []
    for i in range(4):
        #find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item img")[i].click()
        hemi_data = scrape_hemisphere(browser.html)
        hemi_data['img_url']= url + hemi_data['img_url']
        #append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)
        #navigate backwards
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    #parse html text
    hemi_soup = soup(html_text, "html.parser")

    #adding try/accept for error handling
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text= "Sample").get("href")

    except AttributeError:
        #Image error will return None, for better front-end handling
        title_elem = None
        sample_elem = None

    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemispheres

if __name__ == "__main__":
    #if running as script, print scraped data
    print(scrape_all())

  