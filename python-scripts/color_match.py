# -*- coding: utf-8 -*-
"""
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1l7NW5a53H125dE0zvyrMa0Q3PfOdqfXg
"""

# constants
# root address of the server. default: "/"
ROOT = "http://103.213.247.190:20233/"
# directory in which the uploaded images are stored. default: ROOT + "uploaded/"
UPLOAD_DIR = ROOT + "uploaded/"

"""# Aria and Didi's Code:"""

import io
import pandas as pd #data frame
import numpy as np #handle numebrs

#to make this notebook's output stable across runs garantees this shuffle will be same as next
np.random.seed(42)
# url = 'https://raw.githubusercontent.com/eppingera/ColorMatcher/master/ColorFakeData2.csv'

#READ in URL from Jerry and Joe's list of colors that look good together...
url = ROOT + 'data/training-data.csv'

#import data into pandas dataframe
data = pd.read_csv(url)

#View the first 5 entries
data.head()

#get data type and number of instances for all the attributes
data.info()

"""## Insert RGB Values"""

#from https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
#Converts an inputed hex code color into it's rgb values, returns a tuple
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


print(hex_to_rgb("#ffffff"), rgb_to_hex((255, 255, 255)))

#returns a dictionary (red, green, blue) values for a given column of colors in data
def rgb(column):
  red = []
  green = []
  blue = []
  for i in range(len(data)):
    value = (data[column])[i]
    array = np.asarray(hex_to_rgb(value))

    red.append(array[0])
    green.append(array[1])
    blue.append(array[2])


  return {
      "red" : red,
      "green" : green, 
      "blue" : blue
  }

#hold the rgb values for both color columns dictionaries
rgb_values1 = rgb('Color1')
rgb_values2 = rgb('Color2')

#create a new data frame to hold our modified data (that way we don't mess up the original one)
data_2 = data

#insert the RGB values for each other the colors
data_2.insert(1, "Red1", rgb_values1["red"], True)
data_2.insert(2, "Green1", rgb_values1["green"], True)
data_2.insert(3, "Blue1", rgb_values1["blue"], True)
data_2.insert(5, "Red2", rgb_values2["red"], True)
data_2.insert(6, "Green2", rgb_values2["green"], True)
data_2.insert(7, "Blue2", rgb_values2["blue"], True)
data_2.head()

"""## Insert Darkness Index"""

#darkness methods calculate the average darkness (color)

#for color1
def darkness1():
  darkness = []
  for i in range(len(data_2)):
    darkness.append((data_2['Red1'][i] + data_2['Green1'][i] + data_2['Blue1'][i])/3)
  return darkness

#for color2
def darkness2():
  darkness = []
  for i in range(len(data_2)):
    darkness.append((data_2['Red2'][i] + data_2['Green2'][i] + data_2['Blue2'][i])/3)
  return darkness

#insert darkness indexes
d1 = darkness1()
d2 = darkness2()

data_2.insert(4, "Darkness1", d1, True)
data_2.insert(9, "Darkness2", d2, True)
data_2.head()

"""## Insert Contrast Index"""

#returns the contrast (the differnce between each of the color values and the mean)

#for color1
def contrast1():
  contrast = []
  for i in range(len(data_2)):
    darkness = data_2['Darkness1'][i]
    value = (data_2['Red1'][i] - darkness)**2 + (data_2['Green1'][i] - darkness)**2 + (data_2['Blue1'][i] - darkness)**2
    contrast.append(value)
  return contrast

#for color2
def contrast2():
  contrast = []
  for i in range(len(data_2)):
    darkness = data_2['Darkness2'][i]
    value = (data_2['Red2'][i] - darkness)**2 + (data_2['Green2'][i] - darkness)**2 + (data_2['Blue2'][i] - darkness)**2
    contrast.append(value)
  return contrast

#insert contrast indexes
c1 = contrast1()
c2 = contrast2()

data_2.insert(5, "Contrast1", c1, True)
data_2.insert(11, "Contrast2", c2, True)
data_2.head()

"""## Training Model"""

#Drop what we won't use in our ML model
data_2 = data_2.drop(["Color1", "Color2"], axis=1) 
data_2.head()

#Create a test set of data to work with.
from sklearn.model_selection import train_test_split
train_set, test_set = train_test_split(data_2, test_size=0.2, random_state=42)

#create labels and features for both the training and testing sets
x_train = train_set.drop("Match", axis = 1)
y_train = train_set["Match"]

x_test = test_set.drop("Match", axis = 1)
y_test = test_set["Match"]

"""## SGD Classifier"""

#SGDClassifier (Stochastic Gradient Descent):

#Import the SGDClassifier
from sklearn.linear_model import SGDClassifier

#Import the cross_val_score
from sklearn.model_selection import cross_val_predict

#Define the classifier with max_iter = 5, tol = -np.infty, random_state = 42
sgd_clf = SGDClassifier(max_iter = 5, tol = -np.infty, random_state = 42)

#Fit the sgd classifer
sgd_clf.fit(x_train, y_train)

#hold the sgd predictions
sgd_train_pred = cross_val_predict(sgd_clf, x_train, y_train, cv = 8)

#SGD F1 Score
from sklearn.metrics import f1_score

f1_score(y_train, sgd_train_pred)

#SGD ROC AUC
from sklearn.metrics import roc_auc_score

roc_auc_score(y_train, sgd_train_pred)

"""## SVC Classifier"""

#SVCClassifier (Support Vector Classification)
from sklearn.svm import SVC

svm_clf = SVC(gamma="auto")
svm_clf.fit(x_train, y_train)
svm_train_pred = cross_val_predict(svm_clf, x_train, y_train, cv=8)

#SVC F1 Score
f1_score(y_train, svm_train_pred)

#SVC ROC AUC Score
roc_auc_score(y_train, svm_train_pred)

"""## Random Forest Classifier"""

#Random Forest:

#Import the RandomForestClassifier:
from sklearn.ensemble import RandomForestClassifier

#Define the classifier with n_estimators = 100 and random_state = 42 and
forest_clf = RandomForestClassifier(n_estimators = 100, random_state = 42)

#Fit the classifier to X_train and y_train
forest_clf.fit(x_train, y_train)

#Get scores for the random forest classifier, cv = 10 and scoring 
forest_train_pred = cross_val_predict(forest_clf, x_train, y_train, cv=8)

#Forest F1 Score
f1_score(y_train, forest_train_pred)

#Fores ROC AUC
roc_auc_score(y_train, forest_train_pred)

"""## Acutally using model to predict now"""

#returns the mL feature values needed assuming the input is two hex code colors
def get_feature_values(color1, color2):
  #for color 1:
  rgb1 = np.asarray(hex_to_rgb(color1))   #add rgb values
  darkness1 = (rgb1[0] + rgb1[1] + rgb1[2])/3 #add darkness score
  contrast1 = (rgb1[0]-darkness1)**2 + (rgb1[1]-darkness1)**2 + (rgb1[2]-darkness1)**2  #add contrast

  #now for color 2:
  rgb2 = np.asarray(hex_to_rgb(color2))   #add rgb values
  darkness2 = (rgb2[0] + rgb2[1] + rgb2[2])/3 #add darkness score
  contrast2 = (rgb2[0]-darkness2)**2 + (rgb2[1]-darkness2)**2 + (rgb2[2]-darkness2)**2  #add contrast

  return np.concatenate((rgb1, darkness1, contrast1, rgb2, darkness2, contrast2), axis=None)

#an example to see if this works
#put two color pairs into a pandas dataframe
value = get_feature_values('#424B5A', '#F1E0C5')
value2 = get_feature_values('#CB863E', '#58CACA')

values = np.concatenate((value, value2), axis=0)
values = np.reshape(values, (2,10))
values

values_dataFrame = pd.DataFrame(values)
values_dataFrame.columns = ['Red1',	'Green1',	'Blue1',	'Darkness1',	'Contrast1',	'Red2',	'Green2',	'Blue2',	'Darkness2',	'Contrast2']
values_dataFrame.head()

#test Random Forest classifier on the test data set
y_test_pred = forest_clf.predict(values_dataFrame)
y_test_pred

"""This means that it thinks both these colors will go well together"""

#returns the necessary features for the ml model assuming the input is rgb values not hexcode
def get_feature_values_array(color1, color2):
  #for color 1:
  rgb1 = np.asarray(color1)   #add rgb values
  darkness1 = (rgb1[0] + rgb1[1] + rgb1[2])/3 #add darkness score
  contrast1 = (rgb1[0]-darkness1)**2 + (rgb1[1]-darkness1)**2 + (rgb1[2]-darkness1)**2  #add contrast

  #now for color 2:
  rgb2 = np.asarray(color2)   #add rgb values
  darkness2 = (rgb2[0] + rgb2[1] + rgb2[2])/3 #add darkness score
  contrast2 = (rgb2[0]-darkness2)**2 + (rgb2[1]-darkness2)**2 + (rgb2[2]-darkness2)**2  #add contrast

  return np.concatenate((rgb1, darkness1, contrast1, rgb2, darkness2, contrast2), axis=None)

"""## Image Upload"""

# Commented out IPython magic to ensure Python compatibility.
#Have to install the colorthief package manually
# %pip install colorthief

#Can get a single dominant color
from colorthief import ColorThief

"""## Combining Image with ML"""

#random color generator from https://stackoverflow.com/questions/28999287/generate-random-colors-rgb
def random_color():
  color = list(np.random.choice(range(256), size=3))
  return color

def make_colors(n):
  #make an array of random colors
  colors = []
  for i in range(n):
    colors.append(random_color())
  return colors

#make data frame
def make_data_frame(colors, palette):
  #get the features for all combinations of the random colors and pallet in a data frame 
  vals = []
  for i in range(len(palette)):
    for j in range(len(colors)):
      vals = np.concatenate((vals, get_feature_values_array(palette[i], colors[j])), axis=0)

  vals = np.reshape(vals, (len(colors)*6,10))

  dataFrame = pd.DataFrame(vals)
  dataFrame.columns = ['Red1',	'Green1',	'Blue1',	'Darkness1',	'Contrast1',	'Red2',	'Green2',	'Blue2',	'Darkness2',	'Contrast2']

  return dataFrame

def pred(dataFrame, colors):
  #test Random Forest classifier on the random colors
  y_test_pred = forest_clf.predict(dataFrame)
  #rows will be the palette colors, columns will be the randomly generated colors
  return np.reshape(y_test_pred, (6, len(colors)))

#store the hex codes of the new colors that match the palette
def matches(predictions, colors):
  matches = []
  for j in range(len(predictions[0])):
    colorWorks = True
    for i in range(len(predictions)):
      if (predictions[i][j] == 0):
        colorWorks = False
    if (colorWorks):
      matches.append((colors[j]))
  return matches

def colors_to_hex(colors):
  hexs = []
  for i in range(len(colors)):
    red = '%02X' % colors[i][0]
    green = '%02X' % colors[i][1]
    blue = '%02X' % colors[i][2]
    hexs.append('#' + red + green + blue)
  return hexs

"""# Scott and Jacob's Code:"""

# install chromium, its driver, and selenium
# !apt-get update
# !apt install chromium-chromedriver
# !pip install selenium
# !pip install colorthief
import math
from colorthief import ColorThief
import time
import requests
# set options to be headless, ..
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

import io
from urllib.request import urlopen

class Product:

  color_palette = []

  def __init__(self, link, image_link):
    self.link = link
    self.image_link = image_link
    self.color_palette = []

  def set_color_palette(self):
    try:
      fd = urlopen(self.image_link)
    except:
      print(self.link + " cannot be accessed")
    else:
      f = io.BytesIO(fd.read())
      color_thief = ColorThief(f)
      self.color_palette = color_thief.get_palette(color_count=6)

#webdriver mimics a human interacting with the website, it can click things, scroll and extract data
wd = webdriver.Chrome('chromedriver',options=options)

#Source: https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d
#returns a set of products (a product is made up of two links an image source and link to that products page)
#parameter are the string (in this case its "paintings for sale"), the number of products, webdriver, and an int that tells the webdriver how long to wait inbetween clicks
def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
  def scroll_to_end(wd):
      wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
      time.sleep(sleep_between_interactions)    
  
  # build the google query
  search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

  # load the page
  wd.get(search_url.format(q=query))

  image_urls = set()
  image_count = 0
  results_start = 0
  while image_count < max_links_to_fetch:
    scroll_to_end(wd)

    # get all image thumbnail results
    thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
    number_results = len(thumbnail_results)
    
    print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
    
    for img in thumbnail_results[results_start:number_results]:
      # try to click every thumbnail such that we can get the real image behind it
      try:
        img.click()
        time.sleep(sleep_between_interactions)
      except Exception:
        continue
        
      product_link = ""
      image_link = ""

      # extract product page url of the next image
      actual_products = wd.find_elements_by_css_selector('a.Beeb4e')
      for actual_product in actual_products:
        if actual_product.get_attribute('href') and 'http' in actual_product.get_attribute('href'):
          product_link = actual_product.get_attribute('href')
                
      # extracts the next image url 
      actual_images = wd.find_elements_by_css_selector('img.n3VNCb')

      for actual_image in actual_images:
        if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
          image_link = actual_image.get_attribute('src')

      # save the link and the image 
      image_urls.add(Product(product_link,image_link))

      image_count = len(image_urls)

      if image_count % 50 == 0: 
        print("Retrieved " + str(image_count) + " images") 

      if len(image_urls) >= max_links_to_fetch:
        print(f"Found: {len(image_urls)} image links, done!")
        break
    else:
      print("Found:", len(image_urls), "image links, looking for more ...")
      time.sleep(30)
      load_more_button = wd.find_element_by_css_selector(".mye4qd")
      btn_attr = load_more_button.get_attribute('style')
      if load_more_button and btn_attr and not 'display: none' in btn_attr:
        wd.execute_script("document.querySelector('.mye4qd').click();")

    # move the result startpoint further down
    results_start = len(thumbnail_results)

  return image_urls

#the second input is the number of images to fetch
products = fetch_image_urls('paintings for sale', 10, wd, 1)

for product in products:
  print("Product page: " + product.link + ", Image url: " + product.image_link)
  print()
for product in products:
  product.set_color_palette()

#converts hex to rgb
def hex_converter(hex_color):
  red = int(hex_color[1:3],16)
  green = int(hex_color[3:5],16)
  blue = int(hex_color[5:7],16)
  return [red,green,blue]

#finds a matching product based on color palette
#inputs a list of colors (as hex colors)
def find_match(color_palette,products):
  #converts color palette to rgb
  rgb_color_palette = []
  for color in color_palette:
    rgb_color_palette.append(hex_converter(color))
  #finds the min palette distance
  match = Product("","")
  min_dif = float('inf')
  for product in products:
    dif = palette_distance(rgb_color_palette,product.color_palette)
    if dif< min_dif:
      min_dif =dif
      match = product
  return match

#compares each color in one palette to every color in the other palette...
#finds colors that are most similar and takes the distance
def palette_distance(p1, p2):
  if p1==[] or p2==[]:
    return float('inf')
  total_distance = 0
  for color1 in p1:
    min = float('inf')
    for color2 in p2:
      dist = color_distance(color1,color2)
      if dist< min:
        min = dist
    total_distance+=min
  return total_distance

#computes color distance based off of a weighted distance formula
#I think this formula is weighted to account for the way the human eye sees different colors
#source: https://en.wikipedia.org/wiki/Color_difference
def color_distance(rgb1, rgb2):
  r = (rgb1[0]+rgb2[0])/2
  dr = rgb1[0]-rgb2[0]
  dg = rgb1[1]-rgb2[1]
  db = rgb1[2]-rgb2[2]
  return math.sqrt((2+r/256)*dr*dr + 4*dg*dg + (2+(255-r)/256)*db*db)

"""# Jerry and Joe's Code: 
*Modified from above*
"""

# !pip install -U flask-cors

# import requests
import flask
import os
import logging
from flask import request, jsonify
from flask_cors import CORS
# from google.colab.output import eval_js

# message to be displayed when request is invalid
INVALID_DATA = {
    "success": False, 
    "error": {
        "code": 400, 
        "message": "Request is invalid! "
    }
}

app = flask.Flask(__name__) 
CORS(app)

# a new "GET" API at the url "/api/" 
@app.route('/api/process/', methods=['GET'])
# method for this API
def process(): 
  # return the invalid message when there is no arguement
  if len(request.args) == 0: 
    return jsonify(INVALID_DATA) 

  # return the invalid message when there is an unexpected arguement 
  for arg in request.args: 
    if not (arg == 'id' or arg == 'ext'): 
      return jsonify(INVALID_DATA) 

  # store the values of the arguements in variables
  id = request.args['id'] 
  ext = request.args['ext'] 

  image = id + "." + ext
  image_path = UPLOAD_DIR + image

  # url = image_path
  # myfile = requests.get(url)
  # open(image, 'wb').write(myfile.content)

  color_thief = ColorThief(image_path) #used a picture of flower

  # Get a complete color palette for that image
  palette = color_thief.get_palette(color_count=6)
  # print(palette)

  colors = make_colors(10) #select 10 random colors
  dataFrame = make_data_frame(colors, palette) #make a dataframe with these random colors and the palette
  predictions = pred(dataFrame, colors) #print out the predictions whether these colors will go well together

  match = find_match(colors_to_hex(matches(predictions, colors)), products)

  result = {
      "success": True, 
      "data": {
          "link": match.link, 
          "image": match.image_link
      }
  }

  # os.remove(image) 

  return jsonify(result)

# prints the url for accessing the root directory
# print(eval_js("google.colab.kernel.proxyPort(5000)"))

# start listening for API call
app.run()

"""Problems to solve: 
* Access Control Allow Origin: *
  * Maybe banned feature on colab notebook

Planning: 
* Host this somewhere else for testing
  * Problematic; will have to install all required libraries

API call from browser works perfectly, but when called from JS, return CORS error. 

I will have to look into the problem. 

--Jerry 2020.05.19 03:40

(recorded so I don't forget)
"""

