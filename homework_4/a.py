def acquire(a,new):
    mutex = 1
    while mutex != 0:
        acquire()

def count():
    count += 1

def release():
    mutex = 0

if __name__ == "__main__":
    mutex = 0
    count = 0
    a = 0
    b = 0   # 반복 횟수
    
    while b >= 0:
        acquire(a3)
        count()
        release()
        b -= 1
    exit()