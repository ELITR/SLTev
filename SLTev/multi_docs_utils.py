import uuid
import os
import shutil
from delay_modules import time_based_evaluation
from delay_modules import word_based_evaluation
from utilities import mwerSegmenter_error_message
from utilities import eprint

def get_ostt_docs(ostt_lines, split_token):
    ostt_docs = []
    docs_sentence = []
    for line in  ostt_lines:
        if ''.join(line[0]).startswith(split_token[1:]):
            ostt_docs.append(docs_sentence)
            docs_sentence = []
        else:
            docs_sentence.append(line)

    if docs_sentence:
        ostt_docs.append(docs_sentence)
        docs_sentence = []
    return ostt_docs


def get_candidate_docs(candidate_lines, split_token):
    candidate_docs = []
    docs_sentence = []
    for line in  candidate_lines:
        if ''.join(line[0][3:]).startswith(split_token):
            candidate_docs.append(docs_sentence)
            docs_sentence = []
        else:
            docs_sentence.append(line)
    if docs_sentence:
        candidate_docs.append(docs_sentence)
        docs_sentence = []
    return candidate_docs


def get_ref_docs(references, split_token):
    references_docs = []
    for ref_lines in references:
        ref_docs = []
        docs_sentence = []
        for line in  ref_lines:
            if ''.join(line).startswith(split_token):
                ref_docs.append(docs_sentence)
                docs_sentence = []
            else:
                docs_sentence.append(line)

        if docs_sentence:
            ref_docs.append(docs_sentence)
            docs_sentence = []
        references_docs.append(ref_docs)
    return references_docs


def candidate_delay_evaluation_without_partials(evaluation_object):
    delay, missing_tokens = time_based_evaluation(
        evaluation_object.get('Ts'),
        evaluation_object.get('candidate_sentences'),
        evaluation_object.get('OStt_sentences')
        )
    result ={}
    result['tot_T'] = round(delay, 3)
    result['avg_T'] = round((delay / evaluation_object.get('average_refernces_token_count')), 3)
    result['miss_token_T'] = missing_tokens
    try:
        temp_folder = os.path.join('.', str(uuid.uuid4()))
        delay, missing_tokens, mWERQuality = word_based_evaluation(evaluation_object, temp_folder)
        result['tot_W'] = round(delay, 3)
        result['avg_W'] = round((delay / evaluation_object.get('average_refernces_token_count')), 3)
        result['miss_token_W'] = missing_tokens
        result['mwer_quality_W'] = mWERQuality        
    except:
        os.chdir(evaluation_object.get('current_path'))
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()
    return result
      

def candidate_delay_evaluation_with_partials(evaluation_object):
    delay, missing_tokens = time_based_evaluation(
        evaluation_object.get('Ts'),
        evaluation_object.get('candidate_sentences'),
        evaluation_object.get('OStt_sentences')
        )
    result = {}
    result['tot_PT'] = round(delay, 3)
    result['avg_PT'] = round((delay / evaluation_object.get('average_refernces_token_count')), 3)
    result['miss_token_PT'] = missing_tokens

    try:
        temp_folder = os.path.join('.', str(uuid.uuid4()))
        delay, missing_tokens, _ = word_based_evaluation(evaluation_object, temp_folder)
        result['tot_PW'] = round(delay, 3)
        result['avg_PW'] = round((delay / evaluation_object.get('average_refernces_token_count')), 3)
        result['miss_token_PW'] = missing_tokens
    except:
        os.chdir(evaluation_object.get('current_path'))
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()
    return result

def print_delay_scores(delay_results, docs_count):
    """
    example of delay results:
    {'tot_T': 2053846.889, 'avg_T': 48812.976, 'miss_token_T': 96, 'tot_W': 4107506.532, 'avg_W': 87962.82, 'miss_token_W': 63,
    'mwer_quality_W': 2170.883, 'tot_PT': 2053847.68, 'avg_PT': 48812.97900000001, 'miss_token_PT': 96, 'tot_PW': 4107510.398,
    'avg_PW': 87962.881, 'miss_token_PW': 63}
    """
    if delay_results.get('tot_T'):
        print(
            "tot      Delay         T                     ",
            str("{0:.3f}".format(delay_results['tot_T']/docs_count))
        )
        print(
            "avg      Delay         T                     ",
            str("{0:.3f}".format(delay_results['avg_T']/docs_count))
            )
        print("tot      MissedTokens  T                     ", int(delay_results['miss_token_T']/docs_count))
    if delay_results.get('tot_W'):
        print(
            "tot      Delay         W                     ",
            str("{0:.3f}".format(delay_results['tot_W']/docs_count))
            )
        print(
            "avg      Delay         W                     ",
            str("{0:.3f}".format(delay_results['avg_W']/docs_count))
        )
        print("tot      MissedTokens  W                     ", int(delay_results['miss_token_W']/docs_count))
        print("tot      mWERQuality   W                     ",  str("{0:.3f}".format(delay_results['mwer_quality_W']/docs_count)))

    if delay_results.get('tot_PT'):
        print(
                "tot      Delay         PT                    ",
                str("{0:.3f}".format(delay_results['tot_PT']/docs_count)),
            )
        print(
                "avg      Delay         PT                    ",
                str("{0:.3f}".format(delay_results['avg_PT']/docs_count)),
            )
        print("tot      MissedWords   PT                    ", int(delay_results['miss_token_PT']/docs_count))
    if delay_results.get('tot_PW'):
        print(
            "tot      Delay         PW                    ",
            str("{0:.3f}".format(delay_results['tot_PW']/docs_count)),
            )
        print(
                "avg      Delay         PW                    ",
                str("{0:.3f}".format(delay_results['avg_PW']/docs_count)),
            )
        print("tot      MissedTokens  PW                    ", int(delay_results['miss_token_PW']/docs_count))
   
    
def docs_count_checking(evaluation_object):
    candidate_docs = evaluation_object.get('candidate_docs')
    references_docs = evaluation_object.get('references_docs')
    ostt_docs = evaluation_object.get('ostt_docs')

    if len(candidate_docs) != len(references_docs[0]) or len(candidate_docs) != len(ostt_docs):
        eprint("The number of documents in candidate, OStt and reference is not equal")
        # TODO, check withh all references not hust with reference 0
        return 0
    return 1
    
def docs_ostt_ref_parity_checking(evaluation_object):
    references_docs = evaluation_object.get('references_docs')
    ostt_docs = evaluation_object.get('ostt_docs')

    for reference_docs in references_docs:
        for i in range(len(ostt_docs)):
            if len(reference_docs[i]) != len(ostt_docs[i]):
                eprint(f"The number of complete segments in reference and ostt in the docs {i} are not equal")
                return 0
    return 1
