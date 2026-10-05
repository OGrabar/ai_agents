                                  config             model   n  accuracy  cost_per_task  cost_per_correct  avg_steps  avg_seconds
                          cheap no tools       gpt-4o-mini 151   0.02000        0.00004           0.00205    1.00000      1.70000
                 wiki search+page+tavily       gpt-4o-mini 151   0.70000        0.00032           0.00045    2.89000      6.40000
                        wiki search+page       gpt-4o-mini 151   0.70000        0.00036           0.00052    3.42000      6.50000
                             wiki search       gpt-4o-mini 151   0.34000        0.00050           0.00149    4.43000      9.70000
                         strong no tools claude-sonnet-4.6 151   0.09000        0.00201           0.02170    1.00000      5.60000
                    mid wiki search+page  claude-haiku-4.5 151   0.72000        0.00867           0.01201    4.08000     24.40000
 cascade wiki search+page, threshold 0.0      mini + haiku 151   0.70199        0.00044           0.00063    3.76159      8.04200
 cascade wiki search+page, threshold 0.7      mini + haiku 151   0.72848        0.00181           0.00248    4.31126     10.91418
cascade wiki search+page, threshold 0.85      mini + haiku 151   0.74834        0.00280           0.00374    4.73510     13.20690
cascade wiki search+page, threshold 0.95      mini + haiku 151   0.76821        0.00417           0.00543    5.41722     16.83273