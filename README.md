# Data Quality Assessment 
## Project Description
Open data often has quality issues. These can negatively impact the results of analyses or data-driven models based on the data.  

In this project, our goal is to identify quality issues in datasets from [NYC Open Data](https://opendata.cityofnewyork.us). In particular, we develop methods to automatically identify suspicious/anomalous values in tables.  These values may be explicit null values (e.g., N/A), disguised null values (e.g., 999-999-9999 in a phone number column), syntactic outliers (e.g., alpha-numeric strings in a column consisting of alphabetic last names), semantic outliers (e.g., a state name in a column of city names), misspellings (e.g., brokklyn vs brooklyn), etc. One important question to explore is: can we define quality measures for datasets to help users make more informed decisions when they are selecting datasets?

## possible method
1. use existing profiling tools to help understand the data, e.g., Datamart Profiler (https://pypi.org/project/datamart-profiler, https://docs.auctus.vida-nyu.org/python/datamart-profiler.html). To visualize the profiler results, can use the data-profile-viewer library. 
2. Different features may be used to identify outliers within a list of column values. Example features are value length, frequency, character composition, special characters, etc.. What combinations of these features are most suitable to discover the different types of quality issues? A second approach is to use similarity (e.g., edit distance, n-grams, phonetic similarity) between values. This approach works best when given a controlled vocabulary of valid terms. Such vocabularies can either be extracted from online data sources (e.g., list of US cities) or from the data at hand itself (e.g., the most frequent names across many city name columns can be used as a seed for a curated list of city names). A third source of information is the co-occurrence with values in other columns (e.g., two city names that are similar in edit distance and that have the same ZIP code are likely to be the same).

## Purpose
develop (semi-)automated techniques that classify column values into one of the following four categories:
1) Valid value
2) Misspelling/Abbreviation of a valid value
3) Invalid value
4) NULL value
For values in class 2 list the valid value. For invalid values, flag them as semantic outliers (e.g., values that are valid in a different column/domain) if appropriate.

NULL values can be represented in many different ways (e.g., NULL, n/a, 999, 999-999-9999) and there are different types of outliers, therefore, manual inspection will be required to obtain this information. You can use existing profiling tools to help you better understand the data, e.g., the Datamart profiler (https://docs.auctus.vida-nyu.org/python/datamart-profiler.html) and data-profile-viewer, both available as Python packages:
https://pypi.org/project/datamart-profiler
https://github.com/soniacq/DataProfileVis

You should also try to answer the following questions:
+ Are there patterns for how NULL values/outliers are represented?
+ What is the precision and recall of the techniques you designed/implemented?
+ When and why does your approach fail?

## References & Resource
+ [Efficient Algorithms for Mining Outliers from Large Data Sets. Ramaswamy et al., SIGMOD 2000.](https://dl.acm.org/doi/abs/10.1145/342009.335437) 
+ [Cleaning disguised missing data: a heuristic approach. Ming Hua, Jian Pei. KDD 2007: 950-958](https://web.archive.org/web/20070824063404id_/http:/www.cs.sfu.ca/~jpei/publications/dmv-kdd07.pdf)
+ pyOD
  + [github](https://github.com/yzhao062/pyod)
  + [doc](https://pyod.readthedocs.io/en/latest/)

## Team
<a href="https://github.com/Iris-Song/PerHapS/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Iris-Song/PerHapS&columns=5&max=10"/>
</a>

## Result Output
column_name; value; frequency; category

![](./img/result_example.png)