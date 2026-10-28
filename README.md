# 1-hour-ahead mobile traffic forecasting (Telecom Italia, Milan)

Forecasting the internet activity of a city zone one hour ahead from its recent history, using open mobile-network data from Milan. The project compares simple baselines with tree-based models (single decision tree, random forest, gradient boosting), adds quantile-regression prediction intervals, and checks which features the model relies on.

## Summary of results

Test set: 8-14 Nov 2013 (a week the models never saw), 204 zones, 10-minute resolution. Error = per-zone mean absolute error divided by the zone's mean level (in %), median across zones. Lower is better.

| Method | Median error, % |
|---|---|
| Same time yesterday (baseline) | 21.7 |
| Same as one hour ago (baseline) | 19.1 |
| Single decision tree | 15.3 |
| Random forest | 14.6 |
| Gradient boosting | **14.5** |

- Gradient boosting has a lower error than "same time yesterday" in 99% of the 204 zones.
- Most of the gain comes from using a trained model at all (a single tree already gets 15.3%); random forest and gradient boosting are practically tied.
- The "same time yesterday" baseline is worst on Monday (26.9%) and Saturday (25.4%), i.e. when the previous day is a weekend or weekday of a different kind; gradient boosting stays between 13.7% and 15.5% on every day of the test week. This is an observation from one week, not a tested conclusion.
- 5-95% prediction intervals (quantile regression) cover 89.0% of the actual values (target: about 90%); the median interval width is 63.6% of a zone's mean level.
- Permutation importance: the model relies mostly on the value one hour earlier and on time of day; day of week matters least (with one week of training data a weekly pattern cannot be learned).

The numbers above come from my run of the notebook. Models are seeded, but a fresh run can differ in the last decimal; the notebook prints the exact values.

## Data

Telecom Italia Big Data Challenge dataset (Milan), distributed via Harvard Dataverse:
https://doi.org/10.7910/DVN/EGZHFV

- License: Open Database License (ODbL) 1.0.
- Required attribution: data from [BigDataChallenge contest](http://www.telecomitalia.com/tit/en/bigdatachallenge.html), ODI node Trento: http://theodi.fbk.eu/
- Dataset description: https://www.nature.com/articles/sdata201555
- Milan is divided into a 100 x 100 grid (10,000 zones); activity is recorded every 10 minutes. The values are normalised by the provider and have no unit, so errors in this project are relative.
- This repository does **not** contain the dataset or any table derived from it (`data/` is git-ignored). Download the data yourself (see below).

Citation (BibTeX):

```bibtex
@data{DVN/EGZHFV_2015,
author = {Telecom Italia},
publisher = {Harvard Dataverse},
title = {{Telecommunications - SMS, Call, Internet - MI}},
year = {2015},
version = {V1},
doi = {10.7910/DVN/EGZHFV},
url = {https://doi.org/10.7910/DVN/EGZHFV}
}
```

## Method

- **Task.** For each zone and 10-minute step, predict the activity one hour ahead.
- **Sample.** 204 zones (200 random with seed 42, plus 4 zones inspected during exploration), 14 days: 1-14 Nov 2013.
- **Split.** By time: train on 1-7 Nov, test on 8-14 Nov (no random shuffling, to avoid leaking the future).
- **Normalisation.** Each zone is divided by its mean level over the training period, so a single model learns the shape of the day for all zones.
- **Features.** Activity 1 h, 1 h 10 min and 1 h 20 min earlier; same time the day before; time of day; day of week.
- **Models.** Decision tree, random forest, histogram gradient boosting (scikit-learn); hyper-parameters not tuned.
- **Intervals.** Two gradient-boosting models with quantile loss (5% and 95%).
- **Importance.** Permutation importance on the gradient-boosting model.

## How to run

Tested with Python 3.14, pandas 3.1, scikit-learn 1.9 (any recent versions should work).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Download the daily files sms-call-internet-mi-2013-11-01.txt ... -14.txt
#    ("Plain Text" format) from the DOI link above into data/
# 2. Build the table with the selected zones (data/traffic_204_zones.csv)
python scripts/build_dataset.py

# 3. Open and run notebook/forecast.ipynb from top to bottom
jupyter notebook notebook/forecast.ipynb
```

## Project structure

```
.
├── README.md
├── requirements.txt
├── scripts/build_dataset.py     # raw daily files -> data/traffic_204_zones.csv
├── notebook/forecast.ipynb      # analysis, models, intervals, importance
└── data/                        # not tracked (download yourself)
```

## Limitations

- One week for training and one week for testing; results may differ on other weeks. 1 Nov 2013 was a public holiday in Italy.
- 204 of 10,000 zones; only a 1-hour horizon; no hyper-parameter tuning.
- Normalised values without units: errors are relative to a zone's mean level and cannot be converted to real traffic volumes.
- Interval coverage is an average over all zones and times; it may be higher or lower for a particular zone or hour.
- The day-of-week table covers a single week.

## Possible next steps

- Train on several weeks and add a "same time last week" feature.
- Evaluate on several test weeks (rolling-origin validation) and tune hyper-parameters.
- Check interval calibration per zone and per time of day.
- Investigate the sharp spikes (events or measurement artefacts).
- Try other horizons and neural sequence models.
