import sqlite3
import json
import os
import re
import bcrypt
from pdf import PDF


DB_FILE_NAME = 'usersdb.db'
TABLE_EXISTANCE_QUERY = """CREATE TABLE IF NOT EXISTS Users
                         (uid INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT, surename TEXT)"""
USER_EXISTANCE_QUERY = """SELECT EXISTS(SELECT 1 FROM Users WHERE username=?)"""
USER_INFO_QUERY = """SELECT * FROM Users WHERE username=? LIMIT 1;"""
INSERT_QUERY = """INSERT OR IGNORE INTO Users (username, password, name, surename)
                            VALUES (?,?,?,?)"""
GENERAL_SELECT_QUERY = """SELECT * FROM Users"""
SIGNUP_QUERY = """SELECT username FROM Users"""
SIGNUP_TEMPLATE = {'username': None,
                    'password': None,
                    'password_rep': None,
                    'name': None,
                    'surename': None}

CATEGORY_TEMPLATE = {'users':{
                         'root': []
                                }
                     }
QUERY_RESULT = 0
CATEGORIES_LIBRARY = 'cat_lib.json'

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
USERNAME_REGEX = r'[a-zA-Z][a-zA-Z0-9#$%*_@]{2,30}'

SIGNUP_SUCCESSS = 1
PASSWORD_CORRECTNESS_FAILURE = 2
PASSWORD_COMPLIANCE_FAILURE = 3
USERNAME_NOT_ALLOWED = 4

LOGIN_SUCCESS = 1
USER_DOESNT_EXIST = 2
INCORRECT_LOGIN_PASSWD = 3

PMKEY_INDEX = 0
USERNAME_INDEX = 1
PASSWORD_INDEX = 2
NAME_INDEX = 3
SURENAME_INDEX = 4


TRANSLATION_FAILURE = 0
TRANSLATION_SUCCESS = 1
NOT_FORMATTED_TEXT = ''
CONTENT_FONT_SIZE = 12
EMPTY_STRING = ''
AUTO_TEXT_CELL_WIDTH = 0
TEXT_CELL_HEIGHT = 10


class DBManager:
    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE_NAME)
        self.cursor = self.connection.cursor()
        self.cursor.execute(TABLE_EXISTANCE_QUERY)
    


    def end_connection(self):
        self.connection.close()


    def sign_up(self, attr):
        if  not self.passwd_compliance(attr['password'],attr['password_rep']): return PASSWORD_COMPLIANCE_FAILURE
        if self.user_exists(attr['username']) or not self.username_allowed(attr['username']): return USERNAME_NOT_ALLOWED
        if not self.passwd_corectness(attr['password']): return PASSWORD_CORRECTNESS_FAILURE
        self.create_infrastructure(attr)
        return SIGNUP_SUCCESSS
    
    def log_in(self,username,passwd):
        if not self.user_exists(username): return (USER_DOESNT_EXIST,User)

        userdata = self.user_info(username)
        saved_hash = userdata[PASSWORD_INDEX]

        if not self.compare_hash(passwd,saved_hash): return (INCORRECT_LOGIN_PASSWD,User)


        return LOGIN_SUCCESS, User(userdata)

    def username_allowed(self,username):
        return re.match(USERNAME_REGEX, username)

    def user_info(self,username):
        if self.user_exists(username):
            self.cursor.execute(USER_INFO_QUERY,(username,))
            return self.cursor.fetchone()
        return tuple()
      

    def passwd_compliance(self,passwd1,passwd2):
        return passwd1 == passwd2 


    def passwd_corectness(self,passwd):
        return re.match(PASSWORD_REGEX,passwd)    

    
    def create_infrastructure(self,attr):
        if not self.user_exists(attr['username']):
            hash_passwd = self.passwd_hash(attr['password'])

            self.cursor.execute(INSERT_QUERY,(attr['username'],hash_passwd,attr['name'],attr['surename']))
            self.connection.commit()
            
            self.create_home_directory(attr['username'])
            self.create_cat_lib(attr['username'])

    

    def passwd_hash(self,passwd):
        return bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt())
    
    def compare_hash(self,passwd,hash):
        return bcrypt.checkpw(passwd.encode("utf-8"), hash)

    
    def user_exists(self, user):
        self.cursor.execute(USER_EXISTANCE_QUERY,(user,))
        return bool(self.cursor.fetchone()[QUERY_RESULT])


    def create_home_directory(self, username):
         if not os.path.exists(username):
            os.mkdir(username)

    def create_cat_lib(self, username):
        c_manage = CategoryManager()
        c_manage.new_user_cat(username=username)         
    




class User:
    def __init__(self, attr):
        self.username = attr[USERNAME_INDEX]
        self.neme = attr[NAME_INDEX]
        self.surename = attr[SURENAME_INDEX]
        self.categories = self.load_categories()

    def load_categories(self):
        c_manage = CategoryManager()
        return c_manage.user_categories(self.username)    






class CategoryManager():
    def __init__(self):
        self.users_categories = CATEGORY_TEMPLATE

    def load_categories(self):
        if os.path.exists(CATEGORIES_LIBRARY):
            with open(CATEGORIES_LIBRARY, 'r') as file:
                self.users_categories = json.load(file)        

    def new_user_cat(self,username):
        self.load_categories()
        self.users_categories['users'][username] = []
        
        with open(CATEGORIES_LIBRARY, 'w') as file:
            json.dump(self.users_categories, file, indent=2)

    def update_categories(self, username, categories):
        self.load_categories()
        if self.figures_in_categories(username):
            self.users_categories['users'][username] = categories

            with open(CATEGORIES_LIBRARY, 'w') as file:
                json.dump(self.users_categories, file, indent=2)

    def user_categories(self, username):
        self.load_categories()
        if self.figures_in_categories(username):
            return self.users_categories['users'][username]
        return [] 

    def figures_in_categories(self,username):
        self.load_categories()
        return username in self.users_categories['users']         






class ContentSaver:
    def __init__(self,attr):
        self.user = attr['user']
        self.text = self.encoding_handling(attr['text'])
        self.filename = attr['filename']
        self.title = self.encoding_handling(attr['title'])
        self.url = attr['url']

    
    def save_pdf(self):
        if os.path.exists(self.user.username):
            pdf = PDF(self.title)
            pdf.add_page()
            pdf.set_font('DejaVu', '', CONTENT_FONT_SIZE)
            pdf.set_title(self.title)

            # for line in self.set_content().split('\n'):
            #     pdf.write(8, line)
            #     pdf.ln(8)

            pdf.multi_cell(AUTO_TEXT_CELL_WIDTH,TEXT_CELL_HEIGHT,self.text)
            pdf.multi_cell(AUTO_TEXT_CELL_WIDTH,TEXT_CELL_HEIGHT,self.url)

            extension = '.pdf'
            path = self.user.username + '/' + self.filename + extension

            try:
                pdf.output(path)
            except UnicodeEncodeError:
                pdf = PDF()
                pdf.write('ERROR')
                pdf.output(path)    
             

    def save_txt(self):
        if os.path.exists(self.user.username):
            extension = '.txt'
            path = self.user.username + '/' + self.filename + extension
            content = self.set_content()
            
            try:
                with open(path, 'w') as file:
                    file.write(content)
            except UnicodeEncodeError:
                with open(path,'w') as file:
                    file.write('ERROR')
                    
    def set_content(self):
        content = self.title
        content += self.text
        content += '\n'
        content += self.url
        return content
    
    def encoding_handling(self,text):
        return text.encode('latin-1',errors = 'ignore').decode('latin-1')
    
    

class ContentGetter:
    def __init__(self,user):
        self.user = user

    def get_user_txt_files(self):
        directory = self.user.username
        if os.path.exists(directory):
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.txt')]
        return []
    
    def get_file(self, filename):
        directory = self.user.username + '/' + filename
        if os.access(directory, os.R_OK):
            with open(directory, 'r') as file:
                file_content = file.read()
                return file_content
        return EMPTY_STRING    

