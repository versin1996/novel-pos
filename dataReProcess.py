import re
import os
import json
from tqdm import tqdm
from fastHan import FastHan


before_subj_symbols = ['，', '。', '？', '！', '：', '；', '……', '…', '——', '—', '~', '～', '-', '－']
before_subj_symbols += [',', '.', '?', '!', ':', ';']

def extract_speeches_and_contexts(output):
    line_idx, line = output
    open_quote, close_quote = '“', '”'
    open_indexes = [match.start() for match in re.finditer(open_quote, line)]
    close_indexes = [match.end() for match in re.finditer(close_quote, line)]
    if len(open_indexes) != len(close_indexes):
        output = output + [[], [line], [[0, len(line)]], None]
        return output

    # remove nested quotes
    if len(open_indexes) > 0:
        sorted_pairs = sorted(list(zip(open_indexes, close_indexes)), key=lambda x: x[0])
        pairs = [sorted_pairs[0]]
        for i in range(1, len(sorted_pairs)):
            last_open, last_close = pairs[-1]
            curr_open, curr_close = sorted_pairs[i]
            if curr_open < last_close:
                pairs[-1] = (last_open, curr_close)
                lline = list(line)
                assert lline[curr_open] == '“' and lline[last_close - 1] == '”'
                lline[curr_open], lline[last_close - 1] = '‘', '’'
                line = ''.join(lline)
            else:
                pairs.append(sorted_pairs[i])
    else:
        pairs = []

    open_close_indexes = [(open_idx, close_idx) for open_idx, close_idx in pairs
        if open_idx < close_idx and (line[close_idx - 2] in before_subj_symbols or close_idx == len(line))]
    speeches = [line[open_idx: close_idx] for open_idx, close_idx in open_close_indexes]

    context_boundaries = [[None, None] for _ in range(len(open_close_indexes) + 1)]
    context_boundaries[0][0] = 0
    for i, (open_idx, close_idx) in enumerate(open_close_indexes):
        context_boundaries[i][1] = open_idx
        context_boundaries[i + 1][0] = close_idx
    context_boundaries[-1][1] = len(line)
    context_boundaries = [cb for cb in context_boundaries if cb[1] - cb[0] > 0]
    contexts = [line[cb[0]: cb[1]] for cb in context_boundaries]

    if len(speeches) == 1:
        open_idx, close_idx = open_close_indexes[0]
        if open_idx == 0: speech_position = 'leftmost'
        elif close_idx == len(line): speech_position = 'rightmost'
        else: speech_position = 'middle'
    elif len(speeches) == 2 and len(contexts) == 1:
        speech_position = 'bothends'
    else:
        speech_position = None
    output = output + [speeches, contexts, context_boundaries, speech_position]
    return output

def extract_speech(line):
    speeches = extract_speeches_and_contexts([0, line])[2]
    return '“' + ''.join([speech[1: -1] for speech in speeches]) + '”'

def extract_context(line):
    contexts = extract_speeches_and_contexts([0, line])[3]
    return ''.join(contexts)
  
def extract_subjects(line, model, is_strip=False):
    if is_strip:
        context = extract_context(line)
    else:
        context = line
    subjects = []
    tuples = model(context, target="Parsing")[0].answer_list
    for i, (word, _, role, pos) in enumerate(tuples):
        if role == 'nsubj' and pos in ['NR', 'NN', 'PN', 'VV']:
            subject, subj_pos = word, pos
            for j in reversed(range(i)):
                prev_word, _, _, prev_pos = tuples[j]
                if prev_pos in ['JJ', 'NN', 'CD', 'M', 'DT', 'NR']:
                    subject = prev_word + subject
                    subj_pos = '+'.join([prev_pos, subj_pos])
                else:
                    break
            for j in range(i + 1, len(tuples)):
                next_word, _, _, next_pos = tuples[j]
                if next_pos in ['DEC', 'DEV']:
                    subject = subject + next_word
                    subj_pos = '+'.join([subj_pos, next_pos])
                break
            subjects.append([subject, subj_pos])
    return subjects

def extract_subjects(line, model, is_strip=False):
    if is_strip:
        line = extract_context(line)
    else:
        context_boundaries = extract_speeches_and_contexts([0, line])[4]
    subjects = []
    simplified_tuples = []
    position = 0
    tuples = model(line, target="Parsing")[0].answer_list
    if not is_strip:
        total_word_len = sum(len(word) for word, _, _, _ in tuples)
        assert total_word_len == len(line), '%d != %d' % (total_word_len, len(line))

    for i, (word, _, role, pos) in enumerate(tuples):
        if not is_strip and not any(cb[0] <= position < cb[1] for cb in context_boundaries):
            position += len(word)
            continue
        simplified_tuples.append([word, role, pos])
        if pos in ['NR', 'NN', 'PN'] and role == 'nsubj' or \
            pos == 'NR' and (i == 0 or tuples[i - 1][-1] == 'PU'):
            subject, subj_pos = word, pos
            for j in reversed(range(i)):
                prev_word, _, _, prev_pos = tuples[j]
                modifiers = ['JJ', 'NR', 'NN', 'CD', 'M']
                if pos != 'NR': modifiers += ['DT']
                if prev_pos in modifiers:
                    subject = prev_word + subject
                    subj_pos = '+'.join([prev_pos, subj_pos])
                else:
                    break
            for j in range(i + 1, len(tuples)):
                next_word, _, _, next_pos = tuples[j]
                if next_pos in ['DEC', 'DEV']:
                    subject = subject + next_word
                    subj_pos = '+'.join([subj_pos, next_pos])
                break
            subjects.append([subject, subj_pos])
        position += len(word)
    return subjects, tuples, simplified_tuples

def write_data(data, index):
	with open('static/data/data_{}.json'.format(index), 'w') as f:
		data = json.dumps(data, ensure_ascii=False)
		f.write(data)

def reprocess(path, file):
    model_fastHan = FastHan(model_type='large')
    result = {}
    with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        cnt = 0
        for k, v in data.items():
            try:
                if v['is_process'] == False:
                    print(k, v['sentence'])
                    cnt += 1
                    subjects, tuples, simplified_tuples = extract_subjects(v['sentence'], model_fastHan)
                    v['subjects'] = subjects
                    v['tuples'] = tuples
                    v['simplified_tuples'] = simplified_tuples
                    v['is_process'] = False
                    result[k] = v
            except:
                pass
        print(cnt)
    with open(os.path.join(path, 'new_{}'.format(file)), 'w', encoding='utf-8') as f:
        json.dump(result, f)


if __name__ == '__main__':
    reprocess('static/data/', 'new_data_1000.json')
	# model_fastHan = FastHan()
	# result = {}
	# with open('0subject_rand5000.txt', 'r', encoding='utf-8') as f:
	#     cnt = 0
	#     temp = enumerate(f.readlines())
	#     for index, line in tqdm(temp):
	#     	line = line.strip()
	#     	subjects, tuples, simplified_tuples = extract_subjects(line.split('::')[1], model_fastHan)
	#     	result[index] = {
	#     		'id': str(index),
	#     		'is_process': False,
	#     		'tokens': [],
	#     		'type': None,
	#     		'validity': None,
	#     		'subjects': subjects,
	#     		'tuples': tuples,
	#     		'simplified_tuples': simplified_tuples,
	#     		'raw_sentence': line,
	#     		'sentence': line.split('::')[1]
	#     	}
	#     	cnt = index + 1
	#     	if cnt % 500 == 0:
	#     		write_data(result, cnt)
	#     		result = {}
	#     if cnt % 500 != 0:
	#     	write_data(result, cnt)