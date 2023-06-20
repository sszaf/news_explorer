from dotenv import load_dotenv
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from newspaper import Article, ArticleException
from googletrans import Translator
import os
from requests.exceptions import RequestException


TRANSLATION_FAILURE = 0
TRANSLATION_SUCCESS = 1
CONTENT_FONT_SIZE = 10
EMPTY_STRING = ''
AUTO_TEXT_CELL_WIDTH = 0
TEXT_CELL_HEIGHT = 10
FILE_NAME_SIZE = 25


class ArticleObtainer:
    def __init__(self):
        load_dotenv()
        self.newsapi = NewsApiClient(api_key=os.getenv('newsapiKey'))
        self.loaded_content = None

    def search_by_keyword(self, keyword):
        try:
            self.loaded_content = self.newsapi.get_everything(q=keyword, language='en', 
                                                              sort_by='relevancy')['articles']
        except RequestException:
            self.loaded_content = None
            

    def search_trending(self):
        try:
            self.loaded_content = self.newsapi.get_top_headlines(language='en')['articles']
        except RequestException:
            self.loaded_content = None

        
    def search_by_category(self, category):
        try:
            self.loaded_content = self.newsapi.get_top_headlines(category=category, language='en')['articles']
        except RequestException:
            self.loaded_content = None

        
    def get_urls(self):
        if self.loaded_content is not None:
            return [article['url'] for article in self.loaded_content]
        return []
    
    def get_titles(self):
        if self.loaded_content is not None:
            return [article['title'] for article in self.loaded_content]
        return []
    
    def get_articles_with_titles(self):
        if self.loaded_content is not None:
            articles_list = map(lambda url: Article(url),self.get_urls())
            articles_list = list(zip(self.get_titles(),articles_list))
            not_empty_articles = []
            for article in articles_list:
                if article[1] is not None: not_empty_articles.append(article)
            return not_empty_articles
        return []
    


class ArticleWrapper:
    def __init__(self, article):
        self.article = article
        self.is_generated = False
    
    def generate_article(self):
        if self.is_generated: return self.article

        try:
            self.article.download()
            self.article.parse()
        except ArticleException:
            return None
        
        self.is_generated = True
        return self.article
    

    def translate(self,lang):
        translator = Translator()
        try:
            translation_text = translator.translate(self.article.text, src='en',dest=lang)
        except Exception:
            return (TRANSLATION_FAILURE,EMPTY_STRING)
        return (TRANSLATION_SUCCESS,translation_text.text)           



            
   
    