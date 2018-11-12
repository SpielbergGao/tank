# Author: Spielberg Gao
# import explode as Explode
import pygame, sys, time
from pygame.locals import *
from random import randint


class TankMain(object):
    """坦克大战的主窗口"""
    width = 600
    height = 500
    my_tank_missile_list = []
    my_tank = None
    enemy_list = pygame.sprite.Group()  # 敌方坦克的组
    explode_list = []
    enemy_missile_list = pygame.sprite.Group()

    # 开始游戏的方法
    def start_game(self):
        pygame.init()  # pygame模块初始化,加载系统的资源
        # 创建一个屏幕,屏幕(窗口)的大小(宽,高),窗口的特性(0,RESIZEBLE,FULLSCREEM),颜色的位数(32)
        screem = pygame.display.set_mode((TankMain.width, TankMain.height), RESIZABLE, 32)
        # 给窗口设置标题
        pygame.display.set_caption("坦克大战")

        TankMain.my_tank = My_Tank(screem)  # 创建一个我方坦克，坦克显示在屏幕的中下部位置
        if len(TankMain.enemy_list) == 0:
            for i in range(1, 6):  # 游戏开始的时候初始化5个敌方坦克
                TankMain.enemy_list.add(Enemy_Tank(screem))  # 通过坦克类生成并初始化5个坦克添加到 地方坦克列表中
        while True:
            if len(TankMain.enemy_list) < 5:
                TankMain.enemy_list.add(Enemy_Tank(screem))  # 把敌方坦克放到组里面

            # color RGB(0,100,200)
            screem.fill((0, 0, 0))  # 设置屏幕的背景色为黑色
            # 显示左上角的文字
            for i, text in enumerate(self.write_text(), 0):
                screem.blit(text, (0, 5 + (15 * i)))
            self.get_event(TankMain.my_tank, screem)  # 获取事件,根据获取的事情处理
            if TankMain.my_tank:
                TankMain.my_tank.hit_enemy_missile()  # 我方坦克和敌方坦克炮弹进行碰撞检测
            if TankMain.my_tank and TankMain.my_tank.live:
                TankMain.my_tank.display()  # 在屏幕上显示我方坦克
                TankMain.my_tank.move()  # 在屏幕上移动我方坦克
            else:
                TankMain.my_tank = None

            # 显示和随机移动 多有的地方坦克
            for enemy in TankMain.enemy_list:
                enemy.display()
                enemy.random_move()
                enemy.random_fire()

            # 显示所有的我方炮弹
            for m in TankMain.my_tank_missile_list:
                if m.live:
                    m.display()
                    m.hit_tank()  # 炮弹打中地方坦克
                    m.move()
                else:
                    TankMain.my_tank_missile_list.remove(m)

            # 显示所有的敌方炮弹
            for m in TankMain.enemy_missile_list:
                if m.live:
                    m.display()
                    m.move()
                else:
                    TankMain.enemy_missile_list.remove(m)

            for explode in TankMain.explode_list:
                explode.display()

            # 显示重置
            time.sleep(0.05)  # 每次绘制的延迟
            pygame.display.update()

    def get_event(self, my_tank, screem):  # 获取所有的事件(敲击键盘,鼠标点击等)
        for event in pygame.event.get():
            if event.type == QUIT:
                # 程序退出
                self.stop_game()
            if event.type == KEYDOWN and (not my_tank) and event.key == K_n:
                TankMain.my_tank = My_Tank(screem)
            if event.type == KEYDOWN and my_tank:
                if event.key == K_LEFT or event.key == K_a:
                    my_tank.direction = "L"
                    my_tank.stop = False
                if event.key == K_RIGHT or event.key == K_d:
                    my_tank.direction = "R"
                    my_tank.stop = False
                if event.key == K_UP or event.key == K_w:
                    my_tank.direction = "U"
                    my_tank.stop = False
                if event.key == K_DOWN or event.key == K_s:
                    my_tank.direction = "D"
                    my_tank.stop = False
                if event.key == K_ESCAPE:  # 敲击 ESC 键 退出
                    self.stop_game()
                if event.key == K_SPACE:
                    m = my_tank.fire()
                    m.good = True  # 我方坦克发射的炮弹
                    TankMain.my_tank_missile_list.append(m)
            if event.type == KEYUP and my_tank:
                if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_UP or event.key == K_DOWN:
                    my_tank.stop = True

    # 关闭游戏
    def stop_game(self):
        sys.exit()

    # 在屏幕的左上角显示文字类容
    def write_text(self):
        # 定义一个字体
        font = pygame.font.SysFont("simsunnsimsun", 12)
        # 根据字体创建一个文件的图像
        text_sf1 = font.render("敌方坦克数量为:%d" % len(TankMain.enemy_list), True, (255, 0, 0))
        # 根据字体创建一个文件的图像
        text_sf2 = font.render("我方坦克炮弹的数量:%d" % len(TankMain.my_tank_missile_list), True, (255, 0, 0))
        return text_sf1, text_sf2


# 坦克大战游戏中所有对象的超级父类
class BaseItem(pygame.sprite.Sprite):
    def __init__(self, screem):
        pygame.sprite.Sprite.__init__(self)
        # 所有对象功能的属性
        self.screem = screem  # 坦克在移动或者显示过程中需要用到当前游戏的屏幕

    # 表示把坦克对应的图片显示在游戏窗口上
    def display(self):
        if self.live:
            self.image = self.images[self.direction]  # 拿到图片(坦克每次根据方向的变化拿到不同方向的坦克)
            self.screem.blit(self.image, self.rect)  # 开始画图


class Tank(BaseItem):
    # 定义类属性,所有坦克对象 高和宽都是一样的,只有类属性才是所有对象共享的  类属性是不变的
    width = 50
    height = 50

    def __init__(self, screem, left, top):
        super().__init__(screem)
        self.direction = "D"  # 代表坦克的方向,默认方向往下(上下左右)
        self.speed = 5  # 坦克移动的速度
        self.stop = False
        self.images = {"L": pygame.image.load("images/tankL.gif"), "R": pygame.image.load("images/tankR.gif"),
                       "U": pygame.image.load("images/tankU.gif"),
                       "D": pygame.image.load("images/tankD.gif")}  # 坦克的所有图片,key:方向 value: 图片(surface)
        self.image = self.images[self.direction]  # 坦克的图片由方向决定
        self.rect = self.image.get_rect()  # 获得图片的边界
        self.rect.left = left  # 拿到x坐标
        self.rect.top = top  # 拿到y坐标
        self.live = True  # 决定坦克的生命状态(生/死)

    def move(self):
        if not self.stop:  # 如果坦克不是停止状态
            if self.direction == "L":  # 如果坦克的方向向左，那么只需要改坦克的left就ok了。left在减小
                if self.rect.left > 0:  # 判断坦克是否在屏幕左边的边界上
                    self.rect.left -= self.speed
                else:
                    self.rect.left = 0
            elif self.direction == "R":  # 如果坦克方向向右，坦克的right增加就ok了。
                if self.rect.right < TankMain.width:  # 坦克已经在屏幕的最右边的话就不能往右移动了
                    self.rect.right += self.speed
                else:
                    self.rect.right = TankMain.width
            elif self.direction == "D":  # 如果坦克方向向下，坦克的bottom增加就ok了。
                if self.rect.bottom < TankMain.height:
                    self.rect.top += self.speed
                else:
                    self.rect.bottom = TankMain.height
            elif self.direction == "U":  # 如果坦克方向向上，坦克的top减小就ok了。
                if self.rect.top > 0:
                    self.rect.top -= self.speed
                else:
                    self.rect.top = 0

    def fire(self):
        m = Missile(self.screem, self)
        return m


class My_Tank(Tank):
    def __init__(self, screem):
        super().__init__(screem, 275, 400)  # 创建一个我方坦克
        self.stop = True  # 是True 代表停止状态
        self.live = True

    def hit_enemy_missile(self):
        hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_missile_list, False)
        for m in hit_list:  # 我方坦克中弹了
            m.live = False
            TankMain.enemy_missile_list.remove(m)
            self.live = False
            explode = Explode(self.screem, self.rect)
            TankMain.explode_list.append(explode)

class Enemy_Tank(Tank):
    def __init__(self, screem):
        super().__init__(screem, randint(1, 5) * 100, 200)
        self.speed = 4
        self.step = 8  # 坦克按照某个方向连续移动的步数
        self.get_random_direction()

    # 获得一个随机的方向
    def get_random_direction(self):
        r = randint(0, 4)  # 得到一个坦克的移动方向和停止的随机数
        if r == 4:
            self.stop = True
        elif r == 1:
            self.direction = "L"
            self.stop = False
        elif r == 2:
            self.direction = "R"
            self.stop = False
        elif r == 0:
            self.direction = "D"
            self.stop = False
        elif r == 3:
            self.direction = "U"
            self.stop = False

    # 敌方坦克,按照一个确定随机方向,连续移动6步,然后才能再次改变方向
    def random_move(self):
        if self.live:
            if self.stop == 0:
                self.get_random_direction()
                self.step = 6
            else:
                self.move()
                self.step -= 1

    def random_fire(self):
        r = randint(0, 50)
        if r == 10 or r == 20 or r == 30 or r == 40:
            m = self.fire()
            TankMain.enemy_missile_list.add(m)
        else:
            return


class Missile(BaseItem):
    width = 12
    height = 12

    def __init__(self, screem, tank):
        super().__init__(screem)
        self.tank = tank
        self.direction = tank.direction  # 子弹的方向由所发射的坦克方向决定
        self.speed = 12  # 子弹移动的速度
        self.images = {"L": pygame.image.load("images/missileL.gif"), "R": pygame.image.load("images/missileR.gif"),
                       "U": pygame.image.load("images/missileU.gif"), "D": pygame.image.load("images/missileD.gif")}
        self.image = self.images[self.direction]  # 坦克的图片由方向决定
        self.rect = self.image.get_rect()  # 获得图片的边界
        self.rect.left = tank.rect.left + (tank.width - self.width) / 2  # 拿到子弹的中心点
        self.rect.top = tank.rect.top + (tank.height - self.height) / 2  # 拿到y坐标
        self.live = True  # 子弹是否被消灭了
        self.good = False

    def move(self):
        if self.live:  # 如果炮弹还存在
            if self.direction == "L":  # 如果炮弹的方向向左，那么只需要改坦克的left就ok了。left在减小
                if self.rect.left > 0:  # 判断坦克是否在屏幕左边的边界上
                    self.rect.left -= self.speed
                else:
                    self.live = False
            elif self.direction == "R":  # 如果炮弹方向向右，坦克的right增加就ok了。
                if self.rect.right < TankMain.width:  # 炮弹已经在屏幕的最右边的话就不能往右移动了
                    self.rect.right += self.speed
                else:
                    self.live = False
            elif self.direction == "D":  # 如果坦克方向向下，坦克的bottom增加就ok了。
                if self.rect.bottom < TankMain.height:
                    self.rect.top += self.speed
                else:
                    self.live = False
            elif self.direction == "U":  # 如果坦克方向向上，坦克的top减小就ok了。
                if self.rect.top > 0:
                    self.rect.top -= self.speed
                else:
                    self.live = False

    # 子弹击中坦克,第一种我方炮弹击中地方坦克,地方炮弹击中我方坦克
    def hit_tank(self):
        if self.good:  # 如果炮弹是我方炮弹
            hit_list = pygame.sprite.spritecollide(self, TankMain.enemy_list, False)
            for e in hit_list:
                e.live = False
                TankMain.enemy_list.remove(e)  # 如果敌方坦克被击中,就从列表中删除地方坦克
                self.live = False
                explode = Explode(self.screem, e.rect)  # 产生一个爆炸对象
                TankMain.explode_list.append(explode)


# 爆炸类
class Explode(BaseItem):
    def __init__(self, screem, rect):
        super().__init__(screem)
        self.live = True
        self.images = [pygame.image.load("images/0.gif"),
                       pygame.image.load("images/1.gif"),
                       pygame.image.load("images/2.gif"),
                       pygame.image.load("images/3.gif"),
                       pygame.image.load("images/4.gif"),
                       pygame.image.load("images/5.gif"),
                       pygame.image.load("images/6.gif"),
                       pygame.image.load("images/7.gif"),
                       pygame.image.load("images/8.gif"),
                       pygame.image.load("images/9.gif"),
                       pygame.image.load("images/10.gif")]
        self.step = 0
        self.rect = rect  # 爆炸的位置和发生爆炸前,子弹碰倒坦克位置一样,在构建爆炸的时候把坦克的rect传递进来

    # display 方法在整个游戏运行过程中,循环调用,每隔.05秒调用一次
    def display(self):
        if self.live:
            if self.step == len(self.images):  # 最后一张爆炸已经显示了
                self.live = False
            else:
                self.image = self.images[self.step]
                self.screem.blit(self.image, self.rect)
                self.step += 1
        else:
            pass  # 删除该对象


game = TankMain()
game.start_game()
