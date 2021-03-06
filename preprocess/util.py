#!usr/bin/env python
# -*- coding: utf-8 -*-

import re
import jieba
import json

# the directory where the data lies
DATA_DIR  = "../../data/CAIL2018-small-data/"

# training file name
TRAIN_FNAME = "data_train.json"

# sample date file name
SAMPLE_FNAME = "data_sample.json"

# testing file name
TEST_FNAME = "data_test.json"

# location of `law.txt` file
LAW_FILE_LOC = "../law.txt"

# location of `accu.txt` file
ACCU_FILE_LOC = "../accu.txt"

# the location of stopwords
STOPWORDS_LOC = "../stopwords.txt"

# TF-IDF model dumped file location
TFIDF_LOC = "./predictor/model/tfidf.model"

# accusation model dumped file location
ACCU_LOC = "./predictor/model/accusation.model"

# article model dumped file location
ART_LOC = "./predictor/model/article.model"

# imprisonment model dumped file location
IMPRISON_LOC = "./predictor/model/imprisonment.model"

# dump the mid-data to local `.pkl` file or not
DUMP = False

# print something log info or not
DEBUG = True

# digitize the death penalty and life imprisonments
DEATH_IMPRISONMENT = -2
LIFE_IMPRISONMENT = -1

jieba.load_userdict("../dictionary/userdict.txt")


def load_stopwords(stopwords_fname):
    """ load stopwords into set from local file """
    stopwords = set()
    with open(stopwords_fname, "r") as f:
        for line in f.readlines():
            stopwords.add(line.strip())

    return stopwords


stopwords = None

def cut_line(line):
    """ cut the single line using `jieba` """

    global stopwords

    # remove the date and time
    line = re.sub(r"\d*年\d*月\d*日", "", line)
    line = re.sub(r"\d*[时|时许]", "", line)
    line = re.sub(r"\d*分", "", line)

    word_list = jieba.cut(line)

    if stopwords is None:
        print("stopwords loaded.")
        stopwords = load_stopwords(STOPWORDS_LOC)

    # remove the stopwords
    words = [word for word in word_list and word not in stopwords]

    text = " ".join(words)

    # correct some results
    # merge「王」and「某某」into「王某某」
    text = re.sub(" 某某", "某某", text)

    # merge「2000」and「元」into「2000元」
    text = re.sub(" 元", "元", text)
    text = re.sub(" 余元", "元", text)

    text = re.sub("价 格", "价格", text)

    return text


def load_law_and_accu_index():
    """ load laws and accusation name and make index """
    law = {}
    lawname = {}
    with open(LAW_FILE_LOC, "r", encoding="utf-8") as f:
        line = f.readline()
        while line:
            lawname[len(law)] = line.strip()
            law[line.strip()] = len(law)
            line = f.readline()


    accu = {}
    accuname = {}
    with open(ACCU_FILE_LOC, "r", encoding="utf-8") as f:
        line = f.readline()
        while line:
            accuname[len(accu)] = line.strip()
            accu[line.strip()] = len(accu)
            line = f.readline()

    if DEBUG:
        print("law and accusation files loaded.")
    return law, accu, lawname, accuname


law, accu, lawname, accuname = load_law_and_accu_index()


def get_class_num(kind):
    global law
    global accu

    if kind == "law":
        return len(law)
    elif kind == "accu":
        return len(accu)
    else:
        raise KeyError


def get_name(index, kind):
    global lawname
    global accuname

    if kind == "law":
        return lawname[index]
    elif kind == "accu":
        return accuname[index]
    else:
        raise KeyError


def get_time(imprison_dict):
    if imprison_dict['death_penalty']:
        return DEATH_IMPRISONMENT

    if imprison_dict['life_imprisonment']:
        return LIFE_IMPRISONMENT

    return int(imprison_dict["imprisonment"])


def get_label(d, kind):
    """ get the index of the law or accusation
    NOTICE: only return the fist label of multi-label data
    """
    global law
    global accu

    if kind == "law":
        return law[str(d["meta"]["relevant_articles"][0])]
    elif kind == "accu":
        return accu[d["meta"]["accusation"][0]]
    elif kind == "time":
        return get_time(d["meta"]["term_of_imprisonment"])
    else:
        raise KeyError

