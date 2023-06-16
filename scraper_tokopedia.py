#|----------------------------------------------------------------------------------|  
#  Info 
#|----------------------------------------------------------------------------------|  

"""
- Make sure selenium version is 4.0 or above
- It is using chromedriver, so make sure chromedriver is in the correct path
"""

#|----------------------------------------------------------------------------------|  
#  Dependecies 
#|----------------------------------------------------------------------------------|  

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import numpy as np

#|----------------------------------------------------------------------------------|  
#  Config chromedriver
#|----------------------------------------------------------------------------------|  

options=webdriver.ChromeOptions()
#options.add_argument("--incognito")
options.add_argument("--start-maximized")
driver = webdriver.Chrome("chromedriver.exe",options=options)

#|----------------------------------------------------------------------------------|  
#  Classes
#|----------------------------------------------------------------------------------|  

#tokped scrapper class
class tokopedia_scraper() :
    def __init__(self,key_search,number_of_page) :
        self.key_search=key_search
        self.number_of_page=number_of_page
        
    #method to go to tokped page
    def get_to_tokopedia_page(self) :
        driver.get('https://www.tokopedia.com/')
    
    #method to send value in search bar and enter it
    def search_product_button(self,product) :
        elem=driver.find_element(By.CSS_SELECTOR,'.css-3017qm')
        elem.send_keys(product)
        elem.send_keys(Keys.ENTER)
    
    #method to extract product name from a webdriver object
    def extract_product_name(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-3um8ox').text
        except :
            val=None
        return val

    #method to extract product price from a webdriver object
    def extract_price(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-1ksb19c').text
        except :
            val=None
        return val

    #method to extract product name from an webdriver object
    def extract_place(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-1ktbh56').text.split('\n')[0]
        except :
            val=None
        return val

    #method to extract merchant name from an webdriver object
    def extract_merchant_name(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-1ktbh56').text.split('\n')[1]
        except :
            val=None
        return val
    
    #method to extract rating product from an webdriver object
    def extract_rating(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-t70v7i').text
        except :
            val=None
        return val

    #method to extract total product sale name from an webdriver object
    def extract_sales(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-q9wnub span:last-child').text
        except :
            val=None
        return val
    
    #method to extract all data from webdriver object then store it in dict
    def extract_data(self,elem) :
        data={'product_name' : self.extract_product_name(elem),
            'product_price' : self.extract_price(elem),
            'place': self.extract_place(elem),
            'store_name': self.extract_merchant_name(elem),
            'rating':self.extract_rating(elem),
            'total_sales' :self.extract_sales(elem)
             }
        return data
    
    #method to handling errors such as (product not found and next button doesnt apper)
    def error_handling(self) :
        val=None
        #check if result result none
        if len(driver.find_elements(By.CSS_SELECTOR,'.css-1852zva')) > 0 :
            val=f"-- {driver.find_element(By.CSS_SELECTOR,'.css-1852zva').text} --"
        #check if next button deosn apper
        if len(driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')) > 0:
            if driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')[1].is_enabled()==False :
                val='--Next button doesnt appear or its the end on of page--'
        return val

    #method to scroll down the page
    def scroll_down(self) :
        catcher=None
        body = driver.find_element(By.CSS_SELECTOR,'body')
        while driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item') == [] :
            
            #create catcher variable to handle error
            catcher=self.error_handling()
            if catcher != None :
                print(catcher)
                break
            time.sleep(2)
            body.send_keys(Keys.PAGE_DOWN)
        return catcher

    #method to clik next page
    def next_page(self) :
        btn=driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')
        btn[1].click()
                                     
    #method run scraper looper which include (visiting tokped's page, scrolling, extracting, and paginating)
    def run_scraper(self) :
        
        #visit tokped page and seach product
        self.get_to_tokopedia_page()
        self.search_product_button(self.key_search)
        
        data=[]        
        page=0
        
        while page < self.number_of_page :
            
            print(f'#### Scrapper Running at Page : {page+1} ####')
            
            #scroll down
            self.scroll_down()
            if self.scroll_down() !=None :
                break 
                
            #loop to extract data
            for i in driver.find_elements(By.CSS_SELECTOR,'.css-llwpbs') :
                data.append(self.extract_data(i))
            
            page+=1
            self.next_page()
        df=pd.DataFrame.from_dict(data)
        try :
            df=df[~df.product_name.isnull()]
        except :
            df
        return df
    
class data_visualization() :
    def __init__(self,data,plt) :
        self.data=data
    
    def cleanse_data(self) :
        self.data=self.data.fillna(0)
        self.data['product_price']=[int(i.replace('Rp','').replace('.','')) if type(i)!=int else i for i in self.data['product_price']]
        self.data['rating']=self.data['rating'].astype(float)
        
    def chart_pie(self,x) :
        img=self.data.groupby(x).size().reset_index()
        img.columns=[x,'total']
        plt.pie(img['total'],labels=img[x])
        
    def bar_chart_count(self,col,agg_val) :
        img=self.data[col].groupby(agg_val).count().reset_index()
        img=img.sort_values(col,ascending=True)
        img.plot.barh(x=agg_val, y=col.remove(agg_val))
    
    def bar_chart_mean(self,col,agg_val) :
        img=self.data.groupby(agg_val).mean().reset_index()
        img=img.sort_values(col,ascending=True)
        img.plot.barh(x=agg_val, y=col)

#|----------------------------------------------------------------------------------|  
#  Scraping process
#|----------------------------------------------------------------------------------|  

# tokopedia scraper objct requeuires 2 input (product_to_search,and number of page that wanna be scraped)
scrapper=tokopedia_scraper('ps5',5)
df=scrapper.run_scraper()
df

#initiat object and use few visulztion method
data=data_visualization(df,plt)
data.cleanse_data()
data.chart_pie('place')
data.bar_chart_count(['product_price','place'],'place')
data.bar_chart_mean('rating','place')


