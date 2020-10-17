from flask import Flask, render_template, request, jsonify
from waitress import serve

from view import index
import json
import os
import argparse

parser =  argparse.ArgumentParser(description='POS')
parser.add_argument('-p', '--port', type=int, required=True, help='Port')
parser.add_argument('-f', '--path', type=str, required=True, help='File path')
args = parser.parse_args()

app = Flask(__name__)
app.DEBUG = True
app.jinja_env.auto_reload = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.add_url_rule('/', 'index', index)

data = None

def load():
    global data
    with open(args.path, 'r', encoding='utf-8') as f:
        data = json.load(f)

@app.route('/save',methods=['GET','POST'])
def save():
    global data
    with open(args.path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        return json.dumps({'CODE': 200})

@app.route('/post',methods=['GET','POST'])
def get_data():
    load()
    return json.dumps(data)

def get_speaker(tokens):
    if not tokens:
        return []
    result = []
    temp = []
    for token in tokens:
        if temp:
            print(token[0] - temp[-1][0])
        if temp and token[0] - temp[-1][0] != 1:
            
            result.append([''.join([i[1] for i in temp]), '+'.join([i[2] for i in temp])])
            temp = []
        temp.append(token)
    result.append([''.join([i[1] for i in temp]), '+'.join([i[2] for i in temp])])
    return result

@app.route('/result',methods=['GET','POST'])
def get_result():
    global data
    try:
        temp = eval(list(request.form.to_dict().keys())[0])
        temp['tokens'].sort()
        res = {}
        id = temp['id']
        res['is_process'] = True
        res['sentence'] = temp['sentence']
        res['raw_sentence'] = temp['raw_sentence']
        if temp['type']:
            res['type'] = temp['type']
        res['judge'] = temp['validity']
        res['subjects'] = []
        for subjects in temp['subjects']:
            subjects[1] = '+'.join(subjects[1].split())
            res['subjects'].append(subjects)
        print(res['subjects'])
        res['speaker'] = get_speaker(temp['tokens'])#''.join([i[1] for i in temp['tokens']])
        res['simplified_tuples'] = temp['simplified_tuples']
        res['tuples'] = temp['tuples']
        print(res['speaker'])
    
        # pos = temp['tuples']
        # tokens = [i[1:] for i in temp['tokens']]
        # res['fastHan'] = [validity, tokens, pos]
        data[id] = res
        return json.dumps({'CODE': 200})
    except Exception as e:
        print(e)
        return json.dumps({'CODE': 404})
    

if __name__ == '__main__':
    serve(app, port=args.port)
    # app.run(debug=True)

# python run.py -p 6001 -f static/data/data_500.json
# python run.py -p 6002 -f static/data/data_1000.json
# python run.py -p 6003 -f static/data/data_1500.json