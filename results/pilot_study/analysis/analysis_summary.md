# Pilot Study Analysis Summary

## Overall

| n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- |
| 180 | 0.750 | 0.111 | 0.139 | 0.000 | 0.000 |

## By Model Family and Prompt Condition

| family | condition | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude | control | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Claude | iiv_penalty | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| GPT | control | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| GPT | iiv_penalty | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| Gemini | control | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemini | iiv_penalty | 30 | 0.500 | 0.133 | 0.367 | 0.000 | 0.000 |

## By Model Family and Snippet Type

| family | snippet type | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude | optimal | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| Claude | sub-optimal | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| GPT | optimal | 30 | 0.500 | 0.267 | 0.233 | 0.000 | 0.000 |
| GPT | sub-optimal | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Gemini | optimal | 30 | 0.500 | 0.133 | 0.367 | 0.000 | 0.000 |
| Gemini | sub-optimal | 30 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## By Prompt Condition and Snippet Type

| condition | snippet type | n | edit % | abstention % | over-edit % | false abstention % | unknown % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| control | optimal | 45 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| control | sub-optimal | 45 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| iiv_penalty | optimal | 45 | 0.000 | 0.444 | 0.556 | 0.000 | 0.000 |
| iiv_penalty | sub-optimal | 45 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Narrative Summary

Across all 180 records, models edited 75.0% of cases, abstained 11.1%, and over-edited 13.9%.

Under `control`, the edit rate was 100.0% overall and 100.0% on sub-optimal snippets, showing that the baseline prompt strongly pushed models toward editing.

Under `iiv_penalty`, optimal-snippet abstention was 44.4% overall, but over-edit remained 55.6%, so calibrated restraint was only partial.

Optimal-snippet abstention by family under the penalty condition ranked as: Claude: 26.7%, GPT: 26.7%, Gemini: 13.3%.

By family on optimal snippets under the penalty condition, abstention was highest for Claude (26.7%), lowest for Gemini (13.3%), with GPT (26.7%) in between, suggesting that family choice materially affects calibration behavior.

Overall, the pilot gives only weak support to the hypothesis that a penalty prompt alone is enough to make models consistently abstain on optimal code while still editing improvable code.
