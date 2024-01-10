import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from login import Ui_Form
import pymysql
import pandas as pd


def menu(uid, uname):
    print(f'欢迎，{uname}。命令列表：')
    print('list：查看您已收藏的专辑')
    print('search：专辑名查找专辑')
    print('quit：退出系统')
    print('help：查看当前可操作指令')
    while True:
        command = input('当前页面：菜单。请选择操作：')
        if command == 'list':
            printlist(uid)

        if command == 'search':
            kw = input('搜索关键词：')
            search(uid, kw)
        if command == 'quit':
            quit()
        if command == 'help':
            print('list：查看您已收藏的专辑')
            print('search：专辑名查找专辑')
            print('quit：退出系统')
            print('help：查看当前可操作指令')


def search(uid, kw):
    sql = f"select alid, atitle, aname from album, artist where \
    artist.arid=album.alid and album.atitle like '%{kw}%'"
    cursor.execute(sql)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=["专辑ID", "专辑标题", "艺术家"])
    print(df)
    print('show + ID：显示专辑曲目列表')
    print('collect + ID：收藏专辑')
    print('return：返回至菜单')
    print('help：查看当前可操作指令')
    while True:
        command = input('当前页面：搜索结果。请选择操作：').split()
        if command[0] == 'show':
            show(command[1])
        if command[0] == 'collect':
            if collect(uid, command[1]):
                return
        if command[0] == 'return':
            return
        if command[0] == 'help':
            print('show + ID：显示专辑曲目列表')
            print('collect + ID：收藏专辑')
            print('return：返回至菜单')
            print('help：查看当前可操作指令')


def show(alid):
    sql = f"select tno, stitle, duration from song where alid={alid} order by tno"
    cursor.execute(sql)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=["序号", "歌曲标题", "秒"])
    df['歌曲时长'] = pd.to_datetime(df['秒'], unit='s').dt.strftime('%M:%S')
    df = df.drop('秒', axis=1)
    print(df.to_string(index=False))
    print('-----------------------------')
    sql = f"select sum(duration) from song where alid={alid}"
    cursor.execute(sql)
    result = cursor.fetchone()
    total = result[0]
    total_M = total // 60
    total_S = total % 60
    print(f'专辑总时长           {total_M}:{total_S}')

def collect(uid, alid):
    sql = f"insert into collection values ('{uid}','{alid}')"
    try:
        cursor.execute(sql)
    except:
        print('收藏失败！')
        return 0
    print('收藏成功！当前收藏列表：')
    printlist(uid)
    return 1


def printlist(uid):
    sql = f"select album.alid, atitle, aname from album, collection, \
    artist where artist.arid=album.arid and collection.alid=album.alid \
    and collection.uid={uid}"
    cursor.execute(sql)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=["ID", "专辑标题", "艺术家"])
    print(df.to_string(index=False))
    print('show + ID：显示专辑曲目列表')
    print('remove + ID：取消收藏专辑')
    print('return：返回至菜单')
    print('help：查看当前可操作指令')
    while True:
        command = input('当前页面：收藏架。请选择操作：').split()
        if command[0] == 'show':
            show(command[1])
        if command[0] == 'remove':
            remove(uid, command[1])
            return
        if command[0] == 'return':
            return
        if command[0] == 'help':
            print('show + ID：显示专辑曲目列表')
            print('remove + ID：取消收藏专辑')
            print('return：返回至菜单')
            print('help：查看当前可操作指令')


def remove(uid, alid):
    sql = f"delete from collection where uid={uid} and alid={alid}"
    try:
        cursor.execute(sql)
    except:
        print('取消收藏失败！')
        return
    print('取消收藏成功！当前收藏列表：')
    printlist(uid)

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.add_signal()

    def add_signal(self):
        self.ui.login_btn.clicked.connect(self.to_login)

    def to_login(self):
        uid = self.ui.user_name.text()
        pwd = self.ui.password.text()
        sql = f"select pwd,uname from users where uid={uid};"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None or result[0] != pwd:
            QMessageBox.warning(self, '错误', '用户名或者密码错误！')
        else:
            loginwindow.close()
            uname = result[1]
            QMessageBox.about(self, '登录成功！', f'欢迎，{uname}！')
            menu(uid, uname)


if __name__ == "__main__":
    conn = pymysql.connect(host='localhost', user='root', password='mysql', db='music')
    cursor = conn.cursor()
    app = QApplication(sys.argv)
    loginwindow = LoginWindow()
    loginwindow.show()
    app.exec()
