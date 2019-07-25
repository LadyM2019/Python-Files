import tweepy
import csv
import json

import sys
import urllib.request
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, \
    QTextEdit, QPushButton, QLineEdit, QFrame, QMessageBox
from PyQt5.QtGui import QPixmap


with open('twitter_credentials.json') as cred_data:
    info = json.load(cred_data)
    consumer_key = info['CONSUMER_KEY']
    consumer_secret = info['CONSUMER_SECRET']
    access_key = info['ACCESS_KEY']
    access_secret = info['ACCESS_SECRET']


def resize_image_with_qt(src, dest):
    image_map = QtGui.QPixmap(src)
    image_map_resized = image_map.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
    image_map_resized.save(dest)
    return dest


def download_web_image(url, number):
    full_name = str(number) + ".jpg"
    resize_pic = str(number) + "_.jpg"
    if '.png' in url:
        full_name = str(number) + ".png"
        resize_pic = str(number) + "_.png"
    urllib.request.urlretrieve(url, full_name)
    resize_image_with_qt(full_name, resize_pic)
    return resize_pic


def get_100_tweets(twitter_handle):

    # create authentication for accessing Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    # initialize Tweepy API
    api = tweepy.API(auth)
    try:
        user = api.get_user(twitter_handle)
    except Exception:
        return None

    # open the spreadsheet we will write to
    with open(f'{twitter_handle}.csv', 'w') as file:

        w = csv.writer(file)

        # write header row to spreadsheet
        w.writerow(['timestamp', 'tweet_text', 'username', 'followers_count', 'profile_image'])

        # for each tweet matching our twitter handle, write row info to the spreadsheet
        for tweet in tweepy.Cursor(api.search, q=twitter_handle+' -filter:retweets', \
                                   lang="en", tweet_mode='extended').items(100):
            w.writerow([tweet.created_at, tweet.full_text.replace('\n', ' ').encode('utf-8'),
                        tweet.user.screen_name.encode('utf-8'),
                        tweet.user.followers_count, tweet.user.profile_image_url])
    return user


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "Twitter Scraping Application"
        self.top = 0
        self.left = 0
        self.width = 1800
        self.height = 790
        self.label = QLabel(self)
        self.line_edit = QLineEdit(self)
        self.push_button_search = QPushButton('Search', self)
        self.label_picture = QLabel(self)
        self.label_name = QLabel(self)
        self.textEdit = QTextEdit(self)
        self.button_show = QPushButton('Preview Image', self)
        self.push_button_quit = QPushButton('Quit', self)
        self.push_button_del = QPushButton('Delete all', self)

        self.init_window()

    def init_window(self):
        self.label.setGeometry(410, 30, 110, 31)
        self.label.setText('Twitter handle')
        self.line_edit.setGeometry(530, 30, 481, 31)
        self.push_button_search.setGeometry(1030, 30, 141, 31)
        self.push_button_search.clicked.connect(self.load_from_file)
        self.push_button_del.clicked.connect(self.del_all_data)
        self.push_button_quit.clicked.connect(self.quit_window)
        self.button_show.clicked.connect(self.show_picture)

        self.label_picture.setAutoFillBackground(True)
        self.label_picture.setGeometry(10, 80, 500, 500)
        self.label_picture.setFrameStyle(QFrame.WinPanel | QFrame.Sunken)
        self.label_picture.setLineWidth(2)
        self.label_name.setGeometry(10, 30, 261, 31)
        self.label_name.setFrameStyle(QFrame.WinPanel | QFrame.Sunken)
        self.label_name.setLineWidth(2)
        # list of twitted lines
        self.textEdit.setGeometry(530, 80, 1260, 700)
        self.button_show.setGeometry(280, 30, 121, 31)
        self.push_button_del.setGeometry(10, 739, 111, 41)
        self.push_button_quit.setGeometry(400, 739, 111, 41)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def load_from_file(self):
        self.textEdit.clear()
        print(self.line_edit.text())
        twitter_handle = self.line_edit.text()
        file_name = twitter_handle + '.csv'
        user = get_100_tweets(twitter_handle)
        if not user:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Finding User")
            msg.setText("No user found with entered twitter handle.")
            msg.setGeometry(500, 400, 30, 100)
            msg.exec()
            return
        url = user.profile_image_url
        original_url = url.replace("_normal", "")
        name_image = download_web_image(original_url, 101)
        self.label_picture.setPixmap(QPixmap(name_image))
        self.label_name.setText(user.name)
        with open(file_name, 'r') as file:
            reader = csv.reader(file, delimiter=',')
            for i, line in enumerate(reader):
                if i != 0:
                    self.textEdit.append("\t".join(line))

    def del_all_data(self):
        self.line_edit.setText("")
        self.label.setText("")
        self.label_name.setText("")
        self.textEdit.clear()
        self.label_picture.seText("")

    def quit_window(self):
        exit(0)

    def del_picture_user(self):
        self.label_name.setText("")
        self.label_picture.setText("")

    def show_picture(self):
        cursor = self.textEdit.textCursor()
        doc = self.textEdit.document()
        block_list = doc.findBlockByLineNumber(cursor.blockNumber()).text().split("\t")
        if len(block_list) == 5:
            url = block_list[4]
            original_url = url.replace("_normal", "")
            name_image = download_web_image(original_url, cursor.blockNumber())
            self.label_picture.setPixmap(QPixmap(name_image))
            user_name = str(block_list[2]).replace("b'", "")
            self.label_name.setText(user_name.replace("'", ""))
        else:
            self.del_picture_user()


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
