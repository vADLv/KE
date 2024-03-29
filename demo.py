# -*- coding: utf-8 -*-
"""script.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M5P3FNPlo1u9Wcnga_7c9EKfGKLgEvPv
"""

import numpy as np
import pandas as pd
import re

import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, confusion_matrix, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import label_binarize
from sklearn.tree import DecisionTreeClassifier


#from google.colab import drive
#drive.mount('/content/drive')

def has_cyrillic(text):
  return bool(re.search('[\u0400-\u04FF]', text))

def stem(word):
  if has_cyrillic(word):
    return stem_ru.stem(word)
  else:
    return stem_en.stem(word)

stem_en = SnowballStemmer("english")
stop_words = stopwords.words("english")
stem_ru = SnowballStemmer("russian")
stop_words.extend(stopwords.words("russian"))
#stop_words.extend(['мл','л','кг','г','мм','м'])
def preprocess(text):
  tokenized = nltk.word_tokenize(text)
  #return ' '.join([stem(w) for w in tokenized if (w not in stop_words and w.isalpha())])
  #return ' '.join([w for w in tokenized if (w not in stop_words and w.isalpha())])
  #return ' '.join([stem(w) for w in tokenized if w.isalnum()])
  return ' '.join([stem(w) for w in tokenized if w.isalpha()])

model_path = 'model.joblib'

class Model:
  def __init__(self,models,uniques_path,prod_df_prepared):
    self.models = models
    self.uniques_path = uniques_path
    self.cat_df = cat_df

# получение названия категорий
  def get_address(self, add):
    add = add.split('.')[1:]
    #add = self.cat_df[self.cat_df.category_id==cat_id].category_path.iloc[0].split('.')[1:]
    add_text = []
    for i in add:
      try:
        add_text.append(self.cat_df[self.cat_df.category_id==int(i)].category_title.iloc[0].strip())
      except:
        add_text.append('-')
    return add_text

#возврат к исходным ид
  def unfac(self, add):
    address = []
    for a in add.keys():
      if self.uniques_path[a][add[a]] != -1:
        address.append(str(self.uniques_path[a][add[a]]))
    return ".".join(address)

#проходим по дереву моделей предсказывая категорию от родительской до листовой
  def predict(self,text):
    add={}
    add['path1']=0
    for i in range(len(self.models.keys())):
      prev_path = list(self.uniques_path.keys())[i]
      next_path = list(self.uniques_path.keys())[i+1]

      add[next_path] = self.models[prev_path][add[prev_path]].predict([text])[0]
    return self.unfac(add)

loaded_model = joblib.load(model_path)

demo_text = ["Полотенце", "Маска для лица", "Колонка с блютусом"]

pr = [loaded_model.predict(preprocess(j)) for j in demo_text]
ct = ["->".join(loaded_model.get_address(i)) for i in pr]

print("------------------ Product classification model DEMO ------------------")
print('{0:20}\t{1:25}\t{2:20}'.format('Product title', 'Category path', 'Category title'))
for text, path, title in zip(demo_text,pr,ct):
  print('{0:20}\t{1:25}\t{2:20}'.format(text, path,title))

while True:
  if input("Press \"n\" to enter new product title (any key to exit): ")=='n':
    test = input("Product title: ")
    path = loaded_model.predict(preprocess(test))
    title = "->".join(loaded_model.get_address(path))
    print('\n{0:25}\t{1:20}\n'.format(path,title))
  else:
    break

#import argparse
#parser = argparse.ArgumentParser()
#parser.add_argument('--text',help="Введите наименование товара")
