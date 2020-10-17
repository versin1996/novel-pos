import json

# with open('static/data/data_1000.json', 'r', encoding='utf-8') as f:
# 	data = json.load(f)
# 	for k, v in list(data.items()):
# 		if v['is_process']:
# 			print(k, v)
n = 215
cnt = 0
# data_1500.json
with open('static/data/data_1500.json', 'r', encoding='utf-8') as f:
	data = json.load(f)
	for k, v in list(data.items()):
		# if 'judge' not in v.keys():
		if not v['is_process']:
			print(k, v.keys(), v['is_process'])
		# if k == str(n):
		# 	for i, j in v.items():
		# 		print(i, j)
	# for k, v in list(data.items())[n:n+1]:
	# 	print(k)
	# 	for i, j in v.items():
	# 		print(i, j)
	# print(len(data.keys()))

# 	print(cnt)

	
# 130 false []

# 45 True
# 60 模型未找到
# 793