from AstraEcho import AstraEcho
from AstraConfig import AstraConfig

# 全局加载配置文件





if __name__ == '__main__':
    AstraConfig.load("config/config.json")

    try:
        echo = AstraEcho()
        print("\n🚀 Both services are running. Press Ctrl+C to stop.")

    except KeyboardInterrupt:
       pass



