# This file contains logs from running python codes

asr_result = """Evaluating the file  sample-data/sample.en.en.asr  in terms of  WER score against  sample-data/sample.en.OSt
LPC    0.265
LPW    0.274
WM     0.323
"""

mt_result = """Evaluating the file  sample-data/sample.en.cs.mt  in terms of translation quality against  sample-data/sample.cs.OSt
--       TokenCount    reference1             37
avg      TokenCount    reference*             37
--       SentenceCount reference1             4
avg      SentenceCount reference*             4
tot      sacreBLEU     docAsWhole             32.786
avg      sacreBLEU     mwerSegmenter          25.850
"""

slt_result = """Evaluating the file  sample-data/sample.en.cs.slt  in terms of translation quality against  sample-data/sample.cs.OSt
--       TokenCount    reference1             37
avg      TokenCount    reference*             37
--       SentenceCount reference1             4
avg      SentenceCount reference*             4
OStt     Duration      --                     137.000
tot      Delay         T                      213.369
avg      Delay         T                      5.767
tot      MissedTokens  T                      19
tot      Delay         W                      285.161
avg      Delay         W                      7.707
tot      MissedTokens  W                      14
tot      mWERQuality   W                      40.5405
tot      Delay         PT                     216.079
avg      Delay         PT                     5.840
tot      MissedWords   PT                     19
tot      Delay         PW                     336.845
avg      Delay         PW                     9.104
tot      MissedTokens  PW                     14
tot      sacreBLEU     docAsWhole             32.786
avg      sacreBLEU     mwerSegmenter          25.850
detailed sacreBLEU     span-000000-003000     31.213
avg      sacreBLEU     span*                  31.213
tot      Flicker       count_changed_Tokens   9
tot      Flicker       count_changed_content  23
mean     flicker across sentences             0.705
mean     flicker across whole documents       0.742
"""

asrt_result = """Evaluating the file  sample-data/sample.en.en.asrt  in terms of translation quality against  sample-data/sample.en.OSt
--       TokenCount    reference1             38
avg      TokenCount    reference*             38
--       SentenceCount reference1             4
avg      SentenceCount reference*             4
OStt     Duration      --                     137.000
tot      Delay         T                      0.000
avg      Delay         T                      0.000
tot      MissedTokens  T                      38
tot      Delay         W                      0.000
avg      Delay         W                      0.000
tot      MissedTokens  W                      10
tot      mWERQuality   W                      31.5789
tot      Delay         PT                     0.000
avg      Delay         PT                     0.000
tot      MissedWords   PT                     38
tot      Delay         PW                     0.000
avg      Delay         PW                     0.000
tot      MissedTokens  PW                     10
tot      sacreBLEU     docAsWhole             35.398
avg      sacreBLEU     mwerSegmenter          37.461
detailed sacreBLEU     span-000000-003000     34.176
avg      sacreBLEU     span*                  34.176
tot      Flicker       count_changed_Tokens   0
tot      Flicker       count_changed_content  0
mean     flicker across sentences             0.000
mean     flicker across whole documents       0.000
"""

