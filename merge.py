import json
import os


def merge(src, dst):
	src_data = None
	dst_data = None

	with open(src, 'r', encoding='utf-8') as f:
		src_data = json.load(f)
	with open(dst, 'r', encoding='utf-8') as f:
		dst_data = json.load(f)
	dst_data.update(src_data)
	with open(dst, 'w', encoding='utf-8') as f:
		json.dump(dst_data, f)

	print(len(dst_data.keys()))

if __name__ == '__main__':
	indice = [500, 1000, 1500]
	for index in indice:
		merge('static/data/new_new_data_{}.json'.format(index), 'static/data/new_data_{}.json'.format(index))
		merge('static/data/new_data_{}.json'.format(index), 'static/data/data_{}.json'.format(index))
	merge('static/data/data_500.json', 'static/data/data_1000.json')
	merge('static/data/data_1000.json', 'static/data/data_1500.json')