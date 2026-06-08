# Pilot Study Analysis Summary

## Overall

| n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- |
| 160 | 0.750 | 0.100 | 0.150 | 0.000 | 0.000 |

## By Model Family and Prompt Condition

| family | condition | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude | control | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Claude | iiv_penalty | 30 | 0.500 | 0.167 | 0.333 | 0.000 | 0.000 |
| GPT | control | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| GPT | iiv_penalty | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| Gemini | control | 20 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemini | iiv_penalty | 20 | 0.500 | 0.150 | 0.350 | 0.000 | 0.000 |

## By Model Family and Snippet Type

| family | snippet type | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude | optimal | 30 | 0.500 | 0.167 | 0.333 | 0.000 | 0.000 |
| Claude | sub-optimal | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| GPT | optimal | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| GPT | sub-optimal | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemini | optimal | 20 | 0.500 | 0.150 | 0.350 | 0.000 | 0.000 |
| Gemini | sub-optimal | 20 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## By Prompt Condition and Snippet Type

| condition | snippet type | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| control | optimal | 40 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| control | sub-optimal | 40 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| iiv_penalty | optimal | 40 | 0.000 | 0.400 | 0.600 | 0.000 | 0.000 |
| iiv_penalty | sub-optimal | 40 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Narrative Summary

Across all 160 records, models edited 75.0% of cases, abstained 10.0%, and over-edited 15.0%.

Under `control`, the edit rate was 100.0% overall and 100.0% on sub-optimal snippets, showing that the baseline prompt strongly pushed models toward editing.

Under `iiv_penalty`, optimal-snippet abstention was 40.0% overall, but over-edit remained 60.0%, so calibrated restraint was only partial.

Optimal-snippet abstention by family under the penalty condition ranked as: GPT: 26.7%, Claude: 16.7%, Gemini: 15.0%.

By family on optimal snippets under the penalty condition, abstention was highest for GPT (26.7%), lowest for Gemini (15.0%), with Claude (16.7%) in between, suggesting that family choice materially affects calibration behavior.

Overall, the pilot gives only weak support to the hypothesis that a penalty prompt alone is enough to make models consistently abstain on optimal code while still editing improvable code.
