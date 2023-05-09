from multiprocessing import Process
import os

def run_script():
    os.system("python3 test.py")

if __name__ == '__main__':
    processes = []
    for i in range(10):
        p = Process(target=run_script)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
