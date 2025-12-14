import atexit
import subprocess
import sys
from AstraEcho import AstraEcho
from AstraConfig import AstraConfig
from AstraNex import AstraLogger

# 全局加载配置文件





if __name__ == '__main__':
    AstraConfig.load("config/config.json")
    # mcp_proc = subprocess.Popen(
    #     [sys.executable, "AstraLink/mcp_server.py"],
    #     stdout=sys.stdout,
    #     stderr=sys.stderr
    # )
    # AstraLogger.info(f'✅ MCP Server started on http://localhost:{AstraConfig.get("AstraLink").get("mcp_server").get("mcp_port")}')
    #
    #
    # def cleanup():
    #     print("\nShutting down services...")
    #     mcp_proc.terminate()
    #     mcp_proc.wait()
    #     print("✅ All services stopped.")
    #
    # atexit.register(cleanup)

    try:
        echo = AstraEcho()
        print("\n🚀 Both services are running. Press Ctrl+C to stop.")

    except KeyboardInterrupt:
       pass



