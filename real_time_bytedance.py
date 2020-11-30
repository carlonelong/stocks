import json
import time 
from datetime import datetime
import random 
import requests
from subprocess import call

real_time_url = "https://stock.snssdk.com/v1/quotes/stockdetail?code={code}&deal=1&deal_size=50&os=mac&os_version=10.15.7&h5_from=browser&app_id=0&device_id=0&timestamp={timestamp}"

real_time_price = {} 
timestamps = []
pre_close = 0.0

file_name_tpl = "real_time_data-{}"

def get_real_time_raw_data(stock_code):
	timestamp = int(time.time())	
	url = real_time_url.format(code=stock_code, timestamp=timestamp)
	# add header if neccesary.	
	resp = requests.get(url)
	data = json.loads(resp.text)
	return data

def update_data(data): #返回是否有更新
	global pre_close
	origin_len = len(timestamps)
	stock_data = data["data"]
	deal_data = stock_data["deal"]
	for d in deal_data:
		timestamp = int(d["time_stamp"])
		if timestamp not in real_time_price:
			real_time_price[timestamp] = float(d["trade_price"])
			timestamps.append(timestamp)
	# minute_data = stock_data["minute"]
	# for m in minute_data:
	# 	point = m.split(" ")	
	# 	minute_close_price = point[1]
	pre_close = float(stock_data["detail"]["pre_close"])
	return origin_len != len(timestamps)

def is_up():
	global pre_close
	# 15秒涨1%以上。
	if len(timestamps) <= 5:
		return False
	
	percent1 = (real_time_price[timestamps[-1]] - real_time_price[timestamps[-5]])/pre_close
	percent2 = (real_time_price[timestamps[-1]] - real_time_price[timestamps[-3]])/pre_close
	if percent1 >= 0.003 and percent2 > 0:
		return True	
		
def is_down():
	global pre_close
	# 15秒跌1%以上。
	if len(timestamps) <= 5:
		return False
	percent1 = (real_time_price[timestamps[-1]] - real_time_price[timestamps[-5]])/pre_close
	percent2 = (real_time_price[timestamps[-1]] - real_time_price[timestamps[-3]])/pre_close
	if percent1 <= -0.003 and percent2 < 0:
		return True	

def mock_data():
	global pre_close
	pre_close = 100.5
	timestamp = int(time.time())
	if not real_time_price:
		timestamps.append(timestamp)
		real_time_price[timestamp] = pre_close
	else:
		price = int(random.uniform(99.20, 102.35)*100)/100.0
		real_time_price[timestamp] = price
		timestamps.append(timestamp)
	return True

def notify(title, msg):
	cmd = 'display notification \"' + msg + '\" with title \"' + title + '\" sound name \"' + 'Glass.aiff' + '\"'
	call(["osascript", "-e", cmd])



def main():
	global real_time_price
	stock_code = "sz002049"
	stock_name = "紫光国微"
	while(1):
		# now = time.strftime("%H:%M:%S", time.localtime())
		# if now[:2] < "09" or now[:2] >= "15" or "13" > now[:2] >= "12" or "13:00" > now[:5] > "11:30":
		# 	print("{} 闭市".format(now))
		# 	time.sleep(60)
		# 	continue
		# weekday = datetime.now().isoweekday()
		# if weekday in (6, 7):
		# 	print("weekday: {weekday} 闭市".format(weekday=weekday))
		# 	time.sleep(8*3600)
		# 	continue
		if not real_time_price:
			print("load {}".format(load()))
			real_time_price = load() or {}
		# if update_data(get_real_time_raw_data(stock_code)):
		if mock_data():
			# print("update at {}: {}".format(timestamps[-1], real_time_price[timestamps[-1]]))
			if is_up():
				print("peak!!!!")
				notify("拉升了", "{time} {name}拉升超过0.3%".format(time=now, name=stock_name))
			if is_down():
				print("valley!!!!")
				notify("跌了快买", "{time} {name}爸爸，跌了0.3%".format(time=now, name=stock_name))
			save(real_time_price)
			print("save {}".format(real_time_price))
		time.sleep(2)

def save(content):
	filename = file_name_tpl.format(datetime.now().strftime("%Y-%m-%d")) 
	with open(filename, "w") as f:
		f.write(json.dumps(content))		

def load():
	filename = file_name_tpl.format(datetime.now().strftime("%Y-%m-%d")) 
	try:
		with open(filename, "r") as f:
			return json.loads(f.read())	
	except FileNotFoundError:
		return None 
	
	
if "__main__" == __name__:
	main()
