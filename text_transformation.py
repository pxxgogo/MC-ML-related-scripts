# coding=utf-8

import argparse
import datetime
import json
import os
import random
import re

import numpy.random as nr

MIN_FREQUENCY = 2
SHOW_PERCENT = 100
SHORT_SENTENCE_PATTERN = re.compile(r"([,，；;])")

log_file = open("log.txt", 'w')

def sentence_split(file_path):
    file_handle = open(file_path, 'r')
    line = file_handle.readline()
    new_lines = []
    line_tag = 0
    while not line == "":
        content = line.strip('\n')
        if line_tag % 1000000 == 0:
            print(line_tag, end='\r')
        if content == "" or content == "\n":
            line_tag += 1
            line = file_handle.readline()
            continue
        short_sentences = SHORT_SENTENCE_PATTERN.split(content)
        No = 0
        new_line = ""
        while No < len(short_sentences):
            short_sentence = short_sentences[No]
            if short_sentence in [',', '，', ';', '；']:
                new_line += short_sentence
                new_lines.append(new_line)
                new_line = ""
            else:
                new_line = short_sentence
            No += 1
        if not new_line == "":
            new_lines.append(new_line)
        line_tag += 1
        line = file_handle.readline()
    new_lines.sort()
    pre_line = ""
    line_No = 0
    del_num = 0
    print()
    while line_No < len(new_lines):
        line = new_lines[line_No]
        if line_No % (len(new_lines) // SHOW_PERCENT) == 0:
            print(line_No / len(new_lines), end='\r')
        if line == pre_line:
            new_lines[line_No] = ""
            del_num += 1
            line_No += 1
        else:
            pre_line = line
            line_No += 1
    print("lines size:", len(new_lines))
    print("del lines size:", del_num)
    new_lines.sort(key=lambda x: len(x), reverse=True)
    line_No = len(new_lines) - 1
    while line_No >= 0 and new_lines[line_No] == "":
        new_lines.pop(line_No)
        line_No -= 1
    random.shuffle(new_lines)
    print("lines size:", len(new_lines))
    print("--------Finish splitting sentence-------")
    return new_lines

def transform_text(content, word_map):
    char_list = content.split(" ")
    for i in range(len(char_list)):
        if char_list[i] == "":
            continue
        if not char_list[i] in word_map:
            if char_list[i].find("{{E}}") > -1:
                char_list[i] = '{{E}}'
            elif char_list[i].find("{{#}}") > -1:
                char_list[i] = '{{#}}'
            else:
                log_file.write("ERROR WORD: %s \n" % char_list[i])
                char_list[i] = '{{R}}'
        char_list[i] = str(word_map[char_list[i]])
    ret = " ".join(char_list) + "\n"
    return ret

def lines_sample(lines, word_map, percent, output_dir):
    train_No_list = []
    valid_No_list = []
    test_No_list = []
    line_num = 0
    ftrain = open(os.path.join(output_dir, 'ptb.train.txt'), 'w')
    fvalid = open(os.path.join(output_dir, 'ptb.valid.txt'), 'w')
    ftest = open(os.path.join(output_dir, 'ptb.test.txt'), 'w')
    line_max_num = len(lines) * percent
    for line in lines:
        if line_num > line_max_num:
            break
        if line_num % (line_max_num // SHOW_PERCENT) == 0:
            print(line_num / line_max_num, end='\r')
        tmp = nr.random()
        if tmp <= 0.75:
            train_No_list.append(line_num)
        elif tmp <= 0.85:
            valid_No_list.append(line_num)
        else:
            test_No_list.append(line_num)
        line_num += 1
    print()
    print("WRITE TRAIN DATA: ")
    line_num = 0
    for line_No in train_No_list:
        if line_num % (len(train_No_list) // SHOW_PERCENT) == 0:
            print(line_num / len(train_No_list), end='\r')
        content = lines[line_No].strip('\n')
        ret = transform_text(content, word_map)
        ftrain.write(ret)
        line_num += 1

    print()
    print("WRITE VALID DATA: ")
    line_num = 0
    for line_No in valid_No_list:
        if line_num % (len(valid_No_list) // SHOW_PERCENT) == 0:
            print(line_num / len(valid_No_list), end='\r')
        content = lines[line_No].strip('\n')
        ret = transform_text(content, word_map)
        fvalid.write(ret)
        line_num += 1

    print()
    print("WRITE TEST DATA: ")
    line_num = 0
    for line_No in test_No_list:
        if line_num % (len(test_No_list) // SHOW_PERCENT) == 0:
            print(line_num / len(test_No_list), end='\r')
        content = lines[line_No].strip('\n')
        ret = transform_text(content, word_map)
        ftest.write(ret)
        line_num += 1

def print_tmp_text(lines, output_dir):
    line_num = 0
    file_handle = open(os.path.join(output_dir, "short_sentence_full_corpus.txt"), 'w')
    for line in lines:
        if line_num > len(lines):
            break
        if line_num % (len(lines) // SHOW_PERCENT) == 0:
            print(line_num / len(lines), end='\r')
        file_handle.write(line + "\n")
        line_num += 1
    file_handle.close()


def main():
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('--word_map_dir', type=str, default='./word_map_new.json')
    parser.add_argument('--output_dir', type=str, default='./filtered_%s/' % str(now))
    parser.add_argument('--percent', type=float, default=1)
    args = parser.parse_args()

    input_file = args.input
    word_map = json.loads(open(args.word_map_dir).read())
    output_dir = args.output_dir
    percent = args.percent

    if output_dir not in os.listdir("."):
        os.mkdir(output_dir)
    lines = sentence_split(input_file)
    print_tmp_text(lines, output_dir)
    lines_sample(lines, word_map, percent, output_dir)
    print()
    print("Completed!")



main()
log_file.close()
