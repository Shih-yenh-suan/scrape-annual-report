import subprocess
import threading
import time

# 监控间隔时间（秒）
MONITOR_INTERVAL = 60

# 要运行的Python脚本
SCRIPT_PATH = "D:\ZZZMydocument\Codes\scrape-annual-reports\美股\scrapeEDGAR.py"


def monitor_output(proc, last_output_time):
    """监控子进程的输出。"""
    while True:
        output = proc.stdout.readline()
        if output:
            print(output.decode('gbk', 'ignore'), end='')
            last_output_time[0] = time.time()
        else:
            time.sleep(1)


def run_script():
    """运行并监控脚本，如果超时则重启。"""
    while True:
        # 启动子进程
        proc = subprocess.Popen(
            ['python', SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # 记录最后输出时间
        last_output_time = [time.time()]

        # 启动监控线程
        monitor_thread = threading.Thread(
            target=monitor_output, args=(proc, last_output_time))
        monitor_thread.start()

        # 检查输出
        while True:
            time.sleep(MONITOR_INTERVAL)
            if time.time() - last_output_time[0] > MONITOR_INTERVAL:
                print("未检测到输出，正在重启脚本...")
                proc.kill()
                break


if __name__ == "__main__":
    run_script()
