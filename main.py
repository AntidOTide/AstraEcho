from AstraEcho import AstraEcho
from AstraConfig import AstraConfig

# 全局加载
AstraConfig.load("config/config.json")

# 任意位置读取


# 手动重载
AstraConfig.reload()




if __name__ == '__main__':
    echo = AstraEcho()


