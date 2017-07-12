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


def file_count(lines):
    word_map_count = {}
    line_num = 0
    for line in lines:
        if line_num % (len(lines) // SHOW_PERCENT) == 0:
            print(line_num / len(lines), end='\r')
        content = line.strip('\n')
        char_list = content.split(" ")
        for word in char_list:
            if word == "":
                continue
            try:
                word_map_count[word] += 1
            except:
                word_map_count[word] = 1
        line_num += 1
    print("--------Finish file mapping-------")
    return word_map_count


def file_filter(lines, word_map_count, threshold, output_dir):
    line_num = 0
    for line in lines:
        if line_num % (len(lines) // SHOW_PERCENT) == 0:
            print(line_num / len(lines), end='\r')
        content = line.strip('\n')
        char_list = content.split(" ")
        i = 0
        for word in char_list:
            if word == "":
                i += 1
                continue
            try:
                if word_map_count[word] < threshold:
                    char_list[i] = "{{R}}"
                    word_map_count.__delitem__(word)
            except:
                char_list[i] = "{{R}}"
            i += 1
        # if line_num % 10000 == 0:
        #   print(".", end=" ")
        lines[line_num] = " ".join(char_list)
        line_num += 1
    word_map_int = {}
    No = 1
    for word, num in word_map_count.items():
        word_map_int[word] = No
        No += 1

    word_map_int["{{vocab_size}}"] = len(word_map_count)
    if not output_dir in os.listdir("./"):
        os.mkdir(output_dir)
    with open(os.path.join(output_dir, 'new_words_map.json'), 'w') as f_word_map:
        f_word_map.write(json.dumps(word_map_int))
    print("--------Finish file filtering-------")
    return word_map_int


def lines_sample(lines, word_map_int, percent):
    sample_lines = list(filter(lambda x: nr.random() * 100.0 <= percent, lines))
    train = []
    valid = []
    test = []
    lines = []
    line_num = 0
    for line in sample_lines:
        if line_num % (len(sample_lines) // SHOW_PERCENT) == 0:
            print(line_num / len(sample_lines), end='\r')
        tmp = nr.random()
        if tmp <= 0.75:
            train.append(line)
        elif tmp <= 0.85:
            valid.append(line)
        else:
            test.append(line)
        line_num += 1
    sample_lines = []
    print()
    line_num = 0
    for line in train:
        if line_num % (len(train) // SHOW_PERCENT) == 0:
            print(line_num / len(train), end='\r')
        content = line.strip('\n')
        char_list = content.split(" ")
        for i in range(len(char_list)):
            if (char_list[i] == ""):
                continue
            char_list[i] = str(word_map_int[char_list[i]])
        train[line_num] = " ".join(char_list) + "\n"
        line_num += 1

    line_num = 0
    print()
    for line in test:
        if line_num % (len(test) // SHOW_PERCENT) == 0:
            print(line_num / len(test), end='\r')
        content = line.strip('\n')
        char_list = content.split(" ")
        for i in range(len(char_list)):
            if (char_list[i] == ""):
                continue
            char_list[i] = str(word_map_int[char_list[i]])
        test[line_num] = " ".join(char_list) + "\n"
        line_num += 1

    line_num = 0
    print()
    for line in valid:
        if line_num % (len(valid) // SHOW_PERCENT) == 0:
            print(line_num / len(valid), end='\r')
        content = line.strip('\n')
        char_list = content.split(" ")
        for i in range(len(char_list)):
            if (char_list[i] == ""):
                continue
            char_list[i] = str(word_map_int[char_list[i]])
        valid[line_num] = " ".join(char_list) + "\n"
        line_num += 1
    return train, valid, test


def main():
    now = datetime.datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('--output_dir', type=str, default='./filtered_%s/' % str(now))
    parser.add_argument('--threshold', type=int, default=100)
    parser.add_argument('--percent', type=int, default=10)
    args = parser.parse_args()

    input_file = args.input
    threshold = args.threshold
    output_dir = args.output_dir
    percent = args.percent

    lines = sentence_split(input_file)
    word_map_count = file_count(lines)
    word_map_int = file_filter(lines, word_map_count, threshold, output_dir)
    train, valid, test = lines_sample(lines, word_map_int, percent)

    with open(os.path.join(args.output_dir, 'ptb.train.txt'), 'w') as ftrain:
        ftrain.writelines(train)
    with open(os.path.join(args.output_dir, 'ptb.valid.txt'), 'w') as fvalid:
        fvalid.writelines(valid)
    with open(os.path.join(args.output_dir, 'ptb.test.txt'), 'w') as ftest:
        ftest.writelines(test)
    print("Completed!")


main()
