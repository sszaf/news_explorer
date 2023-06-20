import sys
import unicodedata
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QStackedWidget
from PyQt5 import QtGui
import db
import random
from articles import ArticleObtainer, ArticleWrapper, TRANSLATION_SUCCESS
from abc import ABC, ABCMeta,abstractmethod

SIGNUP_PANEL_UI = 'signup_dialog.ui'
LOGGING_PANEL_UI = 'logging_dialog.ui'
MAINWINDOW_UI = 'start.ui'
ARTICLE_VIEW_UI = 'article_view.ui'
LOAD_PANEL_UI = 'load_panel_ui.ui'

PDF = 'pdf'
TXT = 'txt'

MISSING_INPUT_MESSAGE = 'ALL FIELDS SHOULD BE FILLED'

SUCCESSFULL_LOGIN_MESSAGE = 'SUCCESSFULLY LOGGED IN'
USER_DOESNT_EXIST_MESSAGE = 'INCORRECT USERNAME'
INCORRECT_PASSWD_MESSAGE = 'INCORRECT PASSWORD'

SUCCESSFULL_SIGNUP_MESSAGE = 'ACCOUNT HAS BEEN CREATED'
DIFFERENT_PASSWDS_MESSAGE = 'DIFFERENT PASSWORDS HAVE BEEN ENTERED'
BAD_PASSWORD_MESSAGE = "PASSWORD DOESN'T MEET SECURITY TERMS"
NOT_ALLOWED_NAME = 'USERNAME NOT ALLOWED'

LOGO_IMAGE = 'logo.png'
SEARCH_IMAGE = 'search.png'
HOME_IMAGE = 'home.png'
LOAD_IMAGE = 'load.png'

CATEGORY_CHANGE_INDEX = -1

ARTICLE_OBJECT_INDEX = 1

LOGIN_PANEL_WIDTH = 560
LOGIN_PANEL_HEIGHT = 720

SIGNUP_PANEL_WIDTH = 620
SIGNUP_PANEL_HEIGHT = 840
 
MAIN_WINDOW_HEIGHT = 780
MAIN_WINDOW_WIDTH = 1120

EMPTY_STRING = ''

CATEGORIES_MAPPING = {0: 'business',
                      1:'entertainment',
                      2:'general',
                      3:'health',
                      4:'science',
                      5:'sports',
                      6:'technology'}


SAVE_PARAMETERS_TEMPLATE = {'user':None,
                            'title':None,
                            'text':None,
                            'url':None,
                            'filename':None}




class AbcQDialogMetaClass(ABCMeta, type(QDialog)):
    pass

class UserAuthentication(ABC, metaclass = AbcQDialogMetaClass):
    @abstractmethod
    def __init__(self):
        self.inputs = []

    def open_home_page(self,user=None):
        home_page = MainWindow(user)
        widget.addWidget(home_page)
        widget.setFixedSize(MAIN_WINDOW_WIDTH,MAIN_WINDOW_HEIGHT)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def all_fields_provided(self):
        return all(map(lambda x: len(x.text())>0,self.inputs))


class MainWindow(QMainWindow):
    def __init__(self,current_user):
        super(QMainWindow,self).__init__()
        loadUi(MAINWINDOW_UI,self)
       
        self.user = current_user
        self.checkboxes = self.check_boxes()
        self.ao = ArticleObtainer()
        self.list_content = []


        self.initial_look()        

        self.set_logo()
        self.set_search_icon()
        self.set_load_icon()

        self.buttons_listening()
        self.listWidget.currentRowChanged.connect(self.open_article)
        
    
    
    def checked_boxes(self):
        liked_categories = []
        check_box_index = 0
        for category in self.checkboxes:
            if category.isChecked(): liked_categories.append(check_box_index)
            check_box_index+=1
        return liked_categories    



    def check_boxes(self):
        checkboxes = [self.chBx_business,self.chBx_entertainment,self.chBx_general,
                      self.chBx_health,self.chBx_science,self.chBx_sports,self.chBx_technology]
        return checkboxes
    
    def save_categories(self):
        cm = db.CategoryManager()
        liked_categories = self.checked_boxes()
        cm.update_categories(self.user.username,liked_categories)

    def open_article(self):
        article_index = self.listWidget.currentRow()
        if article_index != CATEGORY_CHANGE_INDEX:
            article = self.list_content[article_index][ARTICLE_OBJECT_INDEX]
            article_view = ArticleView(self.user, article)
            article_view.exec_()


    def logging_state(self):
        return self.user   

    def buttons_listening(self):
       self.business.clicked.connect(lambda:self.category_selected('business')) 
       self.entertainment.clicked.connect(lambda:self.category_selected('entertainment'))
       self.health.clicked.connect(lambda:self.category_selected('health')) 
       self.sports.clicked.connect(lambda:self.category_selected('sports'))
       self.technology.clicked.connect(lambda:self.category_selected('technology')) 
       self.science.clicked.connect(lambda:self.category_selected('science'))
       self.general.clicked.connect(lambda:self.category_selected('general')) 
       self.login_button.clicked.connect(self.log_in_out)
       self.search_button.clicked.connect(self.user_phrase_search)
       self.proposed_content.clicked.connect(self.propose_content)
       self.load_button.clicked.connect(self.open_load_panel)

    def initial_look(self):
        if self.logging_state():
            self.login_button.setText('LOG OUT')
            self.setup_categories()
            self.statusbar.showMessage('LOGGED AS: {}'.format(self.user.username))
        else:
            self.hide_logged_user_content()
            self.statusbar.showMessage('NOT LOGGED IN')
            self.login_button.setText('LOG IN')

    def log_in_out(self):
        if self.logging_state():
            self.login_button.setText('LOG IN')
            self.statusbar.showMessage('NOT LOGGED IN')
            self.hide_logged_user_content()
            self.save_categories()
            self.user = None

        else:
            login_panel = LoggingPanel()
            widget.addWidget(login_panel)
            widget.setFixedSize(LOGIN_PANEL_WIDTH,LOGIN_PANEL_HEIGHT)
            widget.setCurrentIndex(widget.currentIndex()+1)


    def get_content(self):
        self.list_content = self.ao.get_articles_with_titles()


    def propose_content(self):
        query = EMPTY_STRING
        checked_boxes = self.checked_boxes()
        if len(checked_boxes) == 1:
            query = CATEGORIES_MAPPING[checked_boxes[0]]
        elif len(checked_boxes) > 1:
            query = self.proposed_content_query(checked_boxes)
        self.key_word_search(query)


    def proposed_content_query(self,checked_boxes):
        categories = random.sample(checked_boxes,k=2)
        return CATEGORIES_MAPPING[categories[0]] +" "+ CATEGORIES_MAPPING[categories[1]]

    def key_word_search(self, phrase):
        if phrase != EMPTY_STRING:
            self.ao.search_by_keyword(phrase)
            self.set_articles_list()


    def setup_categories(self):
        user_categories = self.user.categories
        for category in user_categories:
            self.checkboxes[category].setChecked(True)


    def user_phrase_search(self):
        phrase = self.search_field.text()
        if len(phrase) > 0:
            self.key_word_search(phrase)


    def category_selected(self,category):
        self.ao.search_by_category(category)
        self.set_articles_list()


    def set_articles_list(self):    
        self.listWidget.clear()
        self.get_content()
        for title,article in self.list_content:
            self.listWidget.addItem(title)


    def set_logo(self):
        qpixmap = QtGui.QPixmap(LOGO_IMAGE)
        self.logo.setPixmap(qpixmap)

    def set_search_icon(self):
        image = QtGui.QImage(SEARCH_IMAGE)
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
        self.search_button.setIcon(icon)

    def set_load_icon(self):
        image = QtGui.QImage(LOAD_IMAGE)
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
        self.load_button.setIcon(icon)    


    def open_load_panel(self):
        load_panel = LoadPanel(self.user)
        load_panel.exec_()    

    def hide_logged_user_content(self):
        self.chBx_business.setVisible(False)
        self.chBx_entertainment.setVisible(False) 
        self.chBx_health.setVisible(False) 
        self.chBx_sports.setVisible(False) 
        self.chBx_technology.setVisible(False)         
        self.chBx_science.setVisible(False) 
        self.chBx_general.setVisible(False)
        self.proposed_content.setVisible(False)
        self.load_button.setVisible(False) 




class LoggingPanel(QDialog,UserAuthentication):
    def __init__(self):
        super(LoggingPanel, self).__init__()
        loadUi(LOGGING_PANEL_UI,self)

        self.set_home_page_icon()
        
        self.define_inputs()

        self.passwd_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.listen_buttons()


    def set_home_page_icon(self):
        image = QtGui.QImage(HOME_IMAGE)
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(image))
        self.home_page.setIcon(icon)


    def listen_buttons(self):
        self.login_button.clicked.connect(self.log_in_attempt)

        self.signup_button.clicked.connect(self.open_registration_panel)     

        self.home_page.clicked.connect(lambda: self.open_home_page())  


    def open_registration_panel(self):
        signup_panel = SignUpPanel()
        widget.addWidget(signup_panel)
        widget.setFixedSize(SIGNUP_PANEL_WIDTH,SIGNUP_PANEL_HEIGHT) 
        widget.setCurrentIndex(widget.currentIndex()+1)


    def define_inputs(self):
        self.inputs = [self.username_input,self.passwd_input]

    def log_in_attempt(self):
        if not self.all_fields_provided():
            self.failure_info.setText(MISSING_INPUT_MESSAGE)
        else:
            db_handler = db.DBManager()    
            username = self.username_input.text()
            passwd = self.passwd_input.text()

            ret_code, user = db_handler.log_in(username,passwd)
            
            if ret_code == db.LOGIN_SUCCESS:
                db_handler.end_connection()
                self.open_home_page(user)
            elif ret_code == db.USER_DOESNT_EXIST:
                self.failure_info.setText(USER_DOESNT_EXIST_MESSAGE)
            else: self.failure_info.setText(INCORRECT_PASSWD_MESSAGE)
            db_handler.end_connection()         
        
    




class SignUpPanel(QDialog,UserAuthentication):
    def __init__(self):
        super(SignUpPanel, self).__init__()
        loadUi(SIGNUP_PANEL_UI,self)

        self.define_inputs()
        self.set_passwd_echomode()

        self.signup_button.clicked.connect(self.signup_attempt)
        self.login_button.clicked.connect(self.open_login_panel)

    def open_login_panel(self):
        login_panel = LoggingPanel()
        widget.addWidget(login_panel)
        widget.setFixedSize(LOGIN_PANEL_WIDTH,LOGIN_PANEL_HEIGHT)
        widget.setCurrentIndex(widget.currentIndex()+1)



    def set_passwd_echomode(self):
        self.passwd_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.rpasswd_input.setEchoMode(QtWidgets.QLineEdit.Password)  

    def define_inputs(self):
         self.inputs = [self.name_input,self.surename_input,self.passwd_input,
                        self.rpasswd_input,self.username_input]


    def signup_attempt(self):
        if not self.all_fields_provided():
            self.failure_info.setText(MISSING_INPUT_MESSAGE)
        else:
            db_handler = db.DBManager()
            ret_code = db_handler.sign_up(self.pack_signup_data())

            if ret_code == db.SIGNUP_SUCCESSS:
                db_handler.end_connection()
                self.open_home_page()
            elif ret_code == db.PASSWORD_COMPLIANCE_FAILURE:
                self.failure_info.setText(DIFFERENT_PASSWDS_MESSAGE)
            elif ret_code == db.PASSWORD_CORRECTNESS_FAILURE:
                self.failure_info.setText(BAD_PASSWORD_MESSAGE)
            elif ret_code == db.USERNAME_NOT_ALLOWED:
                self.failure_info.setText(NOT_ALLOWED_NAME)
            db_handler.end_connection()            



            
    def pack_signup_data(self):
        signup_data = db.SIGNUP_TEMPLATE
        signup_data['username'] = self.username_input.text()
        signup_data['password'] = self.passwd_input.text()
        signup_data['password_rep'] = self.rpasswd_input.text()
        signup_data['name'] = self.name_input.text()
        signup_data['surename'] = self.surename_input.text()
        return signup_data
    





class ArticleView(QDialog):
    def __init__(self, current_user, article):
        super(ArticleView, self).__init__()
        loadUi(ARTICLE_VIEW_UI,self)
        self.setWindowTitle('Article View')
        self.setWindowIcon(QtGui.QIcon(LOGO_IMAGE))

        self.user = current_user
        self.article_wrapper = ArticleWrapper(article)
        self.article = self.article_wrapper.generate_article()

        self.deactivate_logged_user_content()
        self.text_field_setup()
        self.buttons_listening()

    def deactivate_logged_user_content(self):
        if self.user is None:
            self.pdf_export.setVisible(False)
            self.txt_export.setVisible(False)
            self.filename_input.setVisible(False)

    def text_field_setup(self):
        if self.article is not None:
            self.article_text.setText(self.article.text.strip())
        self.article_text.setReadOnly(True)

    def buttons_listening(self):
        self.translate_button.clicked.connect(self.translation)
        self.txt_export.clicked.connect(lambda: self.save(TXT))
        self.pdf_export.clicked.connect(lambda: self.save(PDF))



    def save(self,extension):
        if len(self.filename_input.text()) > 0:
            save_properties = self.set_save_parameters()
            cs = db.ContentSaver(save_properties)
            if extension == TXT:
                cs.save_txt()
            elif extension == PDF:
                cs.save_pdf()    
         

    def set_save_parameters(self):
        parameters = SAVE_PARAMETERS_TEMPLATE
        parameters['user'] = self.user
        parameters['title'] = self.article.title
        parameters['text'] = self.article_text.toPlainText()
        parameters['url'] = self.article.url
        parameters['filename'] = self.filename_input.text()
        return parameters

    def translation(self):
        language = self.comboBox.currentText()
        ret_code,translation = self.article_wrapper.translate(language)
        if ret_code == TRANSLATION_SUCCESS: self.article_text.setText(translation)




class LoadPanel(QDialog):
    def __init__(self,current_user):
        super(QDialog,self).__init__()
        loadUi(LOAD_PANEL_UI,self)
        self.setWindowTitle('File Explorer')
        self.setWindowIcon(QtGui.QIcon(LOGO_IMAGE))

        self.user = current_user
        self.cg = db.ContentGetter(self.user)

        self.text_field.setReadOnly(True)

        self.files = self.user_files()
        self.set_files_list()

        self.files_list.currentRowChanged.connect(self.load_file)

        

    def load_file(self):
        filename = self.files_list.currentItem().text()
        content = self.cg.get_file(filename)
        self.text_field.setText(content)
        
    def user_files(self):
        return self.cg.get_user_txt_files()
    
    def set_files_list(self):
        for file in self.files:
            self.files_list.addItem(file)
        


        







if __name__ == '__main__':
    app = QApplication(sys.argv)
    logging = LoggingPanel()

    widget = QStackedWidget()
    widget.setWindowTitle('News Explorer')
    widget.setWindowIcon(QtGui.QIcon(LOGO_IMAGE))
    widget.addWidget(logging)

    widget.setFixedHeight(LOGIN_PANEL_HEIGHT)
    widget.setFixedWidth(LOGIN_PANEL_WIDTH)
    widget.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
