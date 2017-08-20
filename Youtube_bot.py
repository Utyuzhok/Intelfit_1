from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
from string import ascii_letters
from random import choice, randint
from selenium.common.exceptions import ElementNotInteractableException
import re
import settings


class YoutubeBot():
    driver = None
    mails = None
    email_char_quantity = settings.EMAIL_CHAR_QUANTITY
    db_port = settings.DB_PORT
    comment_url = settings.COMMENT_URL
    video_url = settings.VIDEO_URL
    def __init__(self):
        self.driver = webdriver.Chrome()
        client = MongoClient('mongodb://localhost:27017/')
        self.mails = client.db.mails.find()

    def login(self, email, password):
        self.driver.get(
            'https://accounts.google.com/ServiceLogin/identifier?uilel=3&passive=true&service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26next%3D%252F%26app%3Ddesktop%26feature%3Dsign_in_button%26hl%3Dru&hl=ru&flowName=GlifWebSignIn&flowEntry=AddSession')
        self.driver.find_element_by_id('identifierId').send_keys(email)
        self.driver.find_element_by_id('identifierNext').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        self.driver.find_element_by_name('password').send_keys(password)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'passwordNext')))
        self.driver.find_element_by_id('passwordNext').click()
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "masthead-search-term")))

        return self.driver

    def like_video(self, video_url):
        self.driver.get(video_url)
        self.driver.execute_script("window.scrollBy(0, 200);")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "like-button-renderer-like-button-unclicked")))
        ActionChains(self.driver).move_to_element(self.driver.find_element_by_class_name('like-button-renderer-like-button-unclicked')).perform()
        WebDriverWait(self.driver, 1)
        self.driver.find_element_by_class_name('like-button-renderer-like-button-unclicked').click()

    def like_comment(self, comment_url):
        m = re.search('(?<=&lc=)\S+', comment_url)
        cid = m.group()
        Xpath_to_like_button = "//div[@data-cid = '{}']/div[@class = 'comment-renderer-content']/div[@class = 'comment-renderer-footer']/div[@class = 'comment-action-buttons-toolbar']/span[@role = 'radiogroup']/button[@aria-label = 'Нравится']".format(cid)
        self.driver.get(comment_url)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "comment-simplebox-text")))
        like_button = self.driver.find_element_by_xpath(Xpath_to_like_button)
        like_button.click()


    def rand_gen(self):
        return ''.join(choice(ascii_letters) for i in range(self.email_char_quantity))

    signup_password = settings.SIGNUP_PASSWORD
    signup_phone_num = settings.SIGNUP_PHONE_NUM

    def put_by_id(self, element_id, string):
        return self.driver.find_element_by_id(element_id).send_keys(string)

    def signup(self):
        email = self.rand_gen()
        self.driver.get(
            'https://accounts.google.com/SignUp?dsh=9208795404684141199&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26feature%3Dsign_in_button%26next%3D%252F%26hl%3Dru&service=youtube&hl=ru#FirstName=&LastName=')
        self.put_by_id('FirstName', 'Def')
        self.put_by_id('LastName', 'Name')
        self.put_by_id('GmailAddress', email)
        self.put_by_id('Passwd', self.signup_password)
        self.put_by_id('PasswdAgain', self.signup_password)
        self.put_by_id('BirthDay', randint(1, 30))
        self.driver.find_element_by_id('month-label').click()
        self.driver.find_element_by_id(':{}'.format(randint(1, 8))).click()
        self.put_by_id('BirthYear', '{}'.format(randint(1975, 2003)))
        self.driver.find_element_by_id('Gender').click()
        self.driver.find_element_by_id(':f').click()
        self.put_by_id('RecoveryPhoneNumber', self.signup_phone_num)
        self.driver.find_element_by_id('submitbutton').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "tos-scroll-button")))
        chek = True
        while chek:
            try:
                self.driver.find_element_by_id('tos-scroll-button').click()
            except ElementNotInteractableException:
                chek = False
                ActionChains(self.driver).move_to_element(self.driver.find_element_by_id('iagreebutton')).click(
                    self.driver.find_element_by_id('iagreebutton')).perform()
        self.mails.insert_one({'email': email, 'password': self.signup_password})

        return self.driver