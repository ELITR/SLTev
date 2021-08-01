import os

from flicker_modules import calc_revise_count, calc_flicker_score
from flicker_modules import calc_average_flickers_per_sentence, calc_average_flickers_per_tokens
from evaluator import documantlevel_bleu_score_evaluation, wordbased_segmenter_bleu_score_evaluation
from evaluator import references_statistical_info, get_average_references_token_count
from evaluator import get_timestamps_table_without_partials
from evaluator import get_timestamps_table
from multi_docs_utils import candidate_delay_evaluation_with_partials, candidate_delay_evaluation_without_partials
from multi_docs_utils import print_delay_scores


def multi_docs_flicker_evaluation(evaluation_object):
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    #flicker evaluation
    print("tot      Flicker       count_changed_Tokens  ", int(calc_revise_count(candidate_sentences)))
    print("tot      Flicker       count_changed_content ", int(calc_flicker_score(candidate_sentences)))
    print(
        "mean     flicker across sentences            ",
        str("{0:.3f}".format(round(calc_average_flickers_per_sentence(candidate_sentences), 3))),
        )
    print(
        "mean     flicker across whole documents      ",
        str("{0:.3f}".format(round(calc_average_flickers_per_tokens(candidate_sentences), 3))),
        )


def multi_docs_quality_evaluation(evaluation_object):
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    references_docs = evaluation_object.get('references_docs')
    references = []
    for ref in references_docs:
        ref_segments = []
        for doc in ref:
            for segment in doc:
                ref_segments.append(segment)
        references.append(ref_segments)
    current_path = os.getcwd()
    evaluation_object = {
        'candidate_sentences': candidate_sentences,
        'language': 'en',
        'SLTev_home': evaluation_object.get('SLTev_home'),
        'current_path': current_path, 
        'references': references,
        }

    # bleu score evaluation
    documantlevel_bleu_score_evaluation(references, candidate_sentences)
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)



def multi_docs_delay_evaluation(evaluation_object):
    current_path = os.getcwd()
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    references_docs = evaluation_object.get('references_docs')
    merge_docs_segments_ref = []
    for ref in references_docs:
        ref_segments = []
        for doc in ref:
            for segment in doc:
                ref_segments.append(segment)
        merge_docs_segments_ref.append(ref_segments)
    ostt_docs = evaluation_object.get('ostt_docs')

    MovedWords = 1 # count of moving words to each side when we are using Time-based segmentation and word-based segmentation
    references_statistical_info(merge_docs_segments_ref) # print statistical info
    delay_results = {}
    for index, OStt_sentences in enumerate(ostt_docs):
        references = [ref[index] for ref in references_docs ]
        average_refernces_token_count = get_average_references_token_count(references)
        Ts = []
        for reference in references:
            timestamps_table = get_timestamps_table_without_partials(OStt_sentences, reference)
            Ts.append(timestamps_table)
        evaluation_object = {
            'Ts': Ts,
            'candidate_sentences': candidate_sentences,
            'OStt_sentences': OStt_sentences,
            'language': 'en',
            'SLTev_home': evaluation_object.get('SLTev_home'),
            'current_path': current_path, 
            'MovedWords': MovedWords,
            'average_refernces_token_count': average_refernces_token_count,
            'references': references,
            'time_span': 3000
            }
        result = candidate_delay_evaluation_without_partials(evaluation_object)
        for k, v in result.items():
            if delay_results.get(k):
                delay_results[k] += v
            else:
                delay_results[k] = v

        Ts = []
        for reference in references:
            timestamps_table = get_timestamps_table(OStt_sentences, reference)
            Ts.append(timestamps_table)
        evaluation_object['Ts'] = Ts
        result = candidate_delay_evaluation_with_partials(evaluation_object)
        for k, v in result.items():
            if delay_results.get(k):
                delay_results[k] += v
            else:
                delay_results[k] = v
    print_delay_scores(delay_results, len(ostt_docs))


def simple_multi_docs_flicker_evaluation(evaluation_object):
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    #flicker evaluation
    print("tot      Flicker       count_changed_content ", int(calc_flicker_score(candidate_sentences)))



def simple_multi_docs_quality_evaluation(evaluation_object):
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    references_docs = evaluation_object.get('references_docs')
    references = []
    for ref in references_docs:
        ref_segments = []
        for doc in ref:
            for segment in doc:
                ref_segments.append(segment)
        references.append(ref_segments)
    current_path = os.getcwd()
    evaluation_object = {
        'candidate_sentences': candidate_sentences,
        'language': 'en',
        'SLTev_home': evaluation_object.get('SLTev_home'),
        'current_path': current_path, 
        'references': references,
        }

    # bleu score evaluation
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)



def simple_multi_docs_delay_evaluation(evaluation_object):
    current_path = os.getcwd()
    candidate_docs = evaluation_object.get('candidate_docs')
    candidate_sentences = [ segment for doc in candidate_docs for segment in doc]
    references_docs = evaluation_object.get('references_docs')
    ostt_docs = evaluation_object.get('ostt_docs')

    MovedWords = 1 # count of moving words to each side when we are using Time-based segmentation and word-based segmentation
    delay_results = {}
    for index, OStt_sentences in enumerate(ostt_docs):
        references = [ref[index] for ref in references_docs ]
        average_refernces_token_count = get_average_references_token_count(references)

        Ts = []
        for reference in references:
            timestamps_table = get_timestamps_table(OStt_sentences, reference)
            Ts.append(timestamps_table)
        evaluation_object = {
            'Ts': Ts,
            'candidate_sentences': candidate_sentences,
            'OStt_sentences': OStt_sentences,
            'language': 'en',
            'SLTev_home': evaluation_object.get('SLTev_home'),
            'current_path': current_path, 
            'MovedWords': MovedWords,
            'average_refernces_token_count': average_refernces_token_count,
            'references': references,
            'time_span': 3000
            }
        result = candidate_delay_evaluation_with_partials(evaluation_object)
        for k, v in result.items():
            if delay_results.get(k):
                delay_results[k] += v
            else:
                delay_results[k] = v
    print_delay_scores(delay_results, len(ostt_docs))

        
