import atexit
import subprocess
import sys
import time

from AstraEcho import AstraEcho
from AstraConfig import AstraConfig

# 全局加载
AstraConfig.load("config/config.json")

# 任意位置读取




if __name__ == '__main__':
    mcp_proc = subprocess.Popen(
        [sys.executable, "weather_test.py"],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    print("✅ MCP Server started on http://localhost:8000")


    def cleanup():
        print("\nShutting down services...")
        mcp_proc.terminate()
        mcp_proc.wait()
        print("✅ All services stopped.")


    atexit.register(cleanup)

    try:
        print("\n🚀 Both services are running. Press Ctrl+C to stop.")
        # while True:
        #     time.sleep(1)
        echo = AstraEcho()
    except KeyboardInterrupt:
        cleanup()



