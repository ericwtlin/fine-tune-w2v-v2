import numpy as np
import pdb
import sys,getopt
from scipy.stats import spearmanr
from utils import logging_set
import logging
import argparse
import gensim
import os

from sim_test1 import read_vectors, calc_sim
from sim_test2 import read_synset, synset_test
from analogy_test import analogy_test

import debugger

def evaluation(emb_file_path, similarity_test_paths, synset_paths, analogy_paths, best_scores=dict()):
    """

    Args:
        emb_file_path:
        similarity_test_paths:  Single file or multiple files in the format: file_path1|file_path2
        synset_paths: the same as similarity_test_paths
        analogy_paths: the same as similarity_test_paths
        best_scores: dict, which stores the best score of every testing file

    Returns:
        best_scores
        save_flag: if at least one test result among these test files is beetter than ever, save the embedding
    """
    logging.info("Evaluating...")

    save_flag = False

    if similarity_test_paths is not None:
        # test 1
        word_size, embed_dim, dict_word, embeddings = read_vectors(emb_file_path)
        for similarity_test_path in similarity_test_paths.split("|"):
            logging.info('TEST1. To evaluate embedding %s and similarity_test_file %s: ' % (emb_file_path, os.path.basename(similarity_test_path)))
            cnt, total, score = calc_sim(word_size, embed_dim, dict_word, embeddings, similarity_test_path)
            logging.info('test score: %0.6f' % score.correlation)
            if score.correlation > best_scores.get(similarity_test_path, 0):
                save_flag = True
                best_scores[similarity_test_path] = score


    emb = gensim.models.KeyedVectors.load_word2vec_format(emb_file_path, binary=False, unicode_errors='ignore')
    if synset_paths is not None:
        # test 2
        for synset_path in synset_paths.split("|"):
            logging.info('TEST2. To evaluate embedding %s and synset_test_file %s:' % (emb_file_path, os.path.basename(synset_path)))
            synset = read_synset(synset_path)
            score = synset_test(synset, emb)
            logging.info('emb score: %0.6f' % score)
            if score > best_scores.get(synset_path, 0):
                save_flag = True
                best_scores[synset_path] = score

    if analogy_paths is not None:
        # test analogy
        for analogy_path in analogy_paths.split("|"):
            logging.info('TEST ANALOGY. To evaluate embedding %s and analogy_test_file %s:' % (emb_file_path, os.path.basename(analogy_path)))
            sem_acc, syn_acc = analogy_test(emb, analogy_path)
            logging.info('Semantic accuracy: %.6f; Syntactic accuracy: %.6f' % (sem_acc, syn_acc))

            best_sem_acc, best_syn_acc = best_scores.get(analogy_path, [0, 0])
            if sem_acc > best_sem_acc:
                save_flag = True
                best_sem_acc = sem_acc

            if syn_acc > best_syn_acc:
                save_flag = True
                best_syn_acc = syn_acc

            best_scores[analogy_path] = [best_sem_acc, best_syn_acc]

    return best_scores, save_flag


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Philly arguments parser")

    parser.add_argument('emb_file_name', type=str)
    parser.add_argument('--similarity_test_paths', type=str, default='data/240.txt|data/297.txt')
    parser.add_argument('--synset_paths', type=str, default='data/nsem3-adjusted.txt')
    parser.add_argument('--analogy_test_paths', type=str, default='data/analogy.txt')
    parser.add_argument('--log_path', type=str, default='evaluation.log')
    args, _ = parser.parse_known_args()
    logging_set(args.log_path)

    if args.similarity_test_paths == 'None':
        args.similarity_test_paths = None
    if args.synset_paths == 'None':
        args.synset_paths = None
    if args.analogy_test_paths == 'None':
        args.analogy_test_paths = None
    best_scores, save_flag = evaluation(args.emb_file_name, args.similarity_test_paths, args.synset_paths, args.analogy_test_paths)