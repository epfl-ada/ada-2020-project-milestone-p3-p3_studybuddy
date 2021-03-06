# Project Milestione P3: studybuddy

## Title
Inverse Chilling Effect: General Data Protection Regulation application and Wikipedia Use

## Abstract
On the 27th of April 2016, the European Parliament adopted the [General Data Protection Regulation (GDPR)](https://gdpr-info.eu/). The regulation became effective the 25th May 2018. This new european regulation sets principles applicable to any business or institution on the management of personal data inside the European Union and European Economic Area. More precisely it ensures data safeguard and privacy, and provides the user with more control and information on its data. Our project will explore if there has been a reverse chilling effect in some european states following the adoption of the regulation and its start of effectiveness. To answer this, we intend to build a new dataset using the same article keywords used in the original paper but extracted from german Wikipedia. We will focus on pageviews and explore trends before and after the aforementioned dates with two Interrupted Time Series (ITS) analyses.

## Research Questions
1. Is there an inverse chilling effect (e.g. immediate spike) following the announcement of the regulation adoption?
2. Is there an inverse chilling effect (e.g. immediate spike) following the day when the regulation became effective?
3. Has there been a change in trends in the viewing of critical terms related to the regulation after each one of the dates? (27.04.2016 & 25.05.2018)

## Proposed dataset
We will retrieve our own dataset using the [Wikipedia REST API](https://wikimedia.org/api/rest_v1/) to obtain the pageviews data given the same list of keywords from the original paper “Chilling Effects: Online Surveillance and Wikipedia Use”. This tool allows us to conveniently extract data as JSON objects. We will consider data from German Wikipedia domain (`de.wikipedia`) only. We aim to build a `.csv` file in a format similar to what we were provided with in the first milestones to reproduce the figures of the original paper.

## Methods
* **Keyword list**: Start from the same list of keywords (from US Homeland Security) as the original paper. Update this list of keywords to fit to European GDPR by removing irrelevant keywords.
* **Data collection**: Extract Wikipedia pageviews (as stated in *Proposed datasets*) for our list of keywords, across April 2015 - April 2017 for the first date and May 2017 - May 2019 for the second date. Primarily focus on German data (`de.wikipedia`), since we speculate this is the Wikipedia domain whose fraction of European-only viewers is the most significant (with respect to other domains such as French Wikipedia including views from Canada and Africa for example).
* **Data analysis**:
Perform a primary analysis on German data, the same way as done in the article:
  * Compare “raw” means before and after interruption events.
  * Implement linear regression on the ITS dataset to provide an answer to our research questions which will be performed with and without control groups. We will implement two linear regressions for which we will illustrate how pre- and post-trends are affected by the two interruption events (27.04.2016 and 25.05.2018).
* **Further Research**: Depending on the obtained data and preliminary results, evaluate the possibility to further answer our research questions with data from other domains (e.g `es.wikipedia`), used for example as control groups for which GDPR is irrelevant.

## Proposed timeline
1. **30.11 - 04.12**: We will first get the required German Wikipedia articles pageviews and aggregate them in monthly bins. In parallel, we will review the keyword list helping to provide more insightful answers to the inverse chilling effect research questions.
2. **05.12 - 08.12**: We will proceed with data wrangling, cleaning and preprocessing. We will also need to research for causes of possible inconsistencies (i.e. terrorism events/breaking news which created a significant change in traffic, which is independent of the trend).
3. **08.12 - 13.12**: Start the data analysis and visualizations parts. We will plot the inverse chilling effect trends using linear regression.
4. **14.12 - 18.12**: Prepare the report and the short video.

![Timeline](Images/Planning.JPG?raw=true "Title")

## Organization within the team
* In week 1, Matthias will query and aggregate the data to create a `.csv` file with monthly pageviews per article. When he is finished, he will help with data analysis and begin writing the report.
* In week 1, Nicolas and Gonxhe will in parallel review the keywords list to refine the dataset of Terrorism-related articles (which may impact the inverse chilling effect). They will as well prepare the base functions and the plots to reproduce data analysis using linear regression.
* In week 2, Gonxhe will focus on data wrangling and cleaning to make sure that the data will be fitted well on a regression model.
* In week 2, Nicolas will handle the possible research that will be required to explain some unexpected values (e.g. because of events similar to Hamas). He will create the figures with the help of Matthias.
* In week 3, all teammates will be finishing the data analysis and report.
* At any time, all teammates will be ready to handle unexpected results and be flexible enough to reconsider some of the above steps if necessary.

## Questions for TAs (optional)

We had a small reflection considering the short video we had to send at the end of the milestone. Indeed, we were considering writing a paper and not implementing a story telling website. But in that case, what do you expect the video to look like? Shall we speak on a PowerPoint to present the results, or should we use the notebook and interactively present it?


# Project structure

## Notebooks

1. `Scraping.ipynb`: build the framework and create functions to scrape Wikipedia pageviews with python mwviews packagw
1. `Outdated-dumps.ipynb`: exploration of the aggregated  200GB data of the deprecated Wikipedia  pagecounts dataset, 
generate figures for the report comparing the pagecounts vs pageviews from Wikipedia REST API
1. `MilestoneP4.ipynb`: analyse pageviews of GDPR-related articles and popular articles (i.e. control group), directly 
scrapes pageviews based on keyword files `data/GDPR_de.txt`
  

## Scraping & keywords

### Review the template keywords

Output of `python src/update_keywords.py`:

```
usage: update_keywords.py [-h] template domain

positional arguments:
  template    file containing newline-delimited keywords, filename pattern: *_template*
  domain      wikipedia domain/project (en, de, fr, ...)

optional arguments:
  -h, --help  show this help message and exit
```
 
Example command:

```bash
python src/update_keywords.py data/keywords_terrorism_de_template.txt de
```

This creates a file `data/keywords_terrorism_de.txt` that we can use to scrape pageviews. 
See the contents of `keywords_terrorism_de_template.txt` for more details about reviewing keywords.


#### More details

If you want to check keywords (e.g. their translation), create a template file '<name>_template.txt' 
(have template at the end!) and run `src/update_keywords.py`, see docstring of the script for more info.

This will generate a new file `<name>_<language>.txt` that you can comment with `#`. You have to check the keywords
mapping and then use it in the notebook to scrape pageviews. This procedure aims to simplify the scaping, since 
article names much match exactly. 

### Scraping with Wikipedia REST API

See the `Scraping.ipynb` notebook. The problem is that there is no data available before July 2015. 

### Data from outdated pagecount dumps

Note: that following hourly data files do not exist:

```
pagecounts-20150527-150000.gz
pagecounts-20150401-010000.gz
```

The following data could not be loaded (it requires > 25 BG RAM to decompress and load it into memory, compared to 
~1GB for all other files):

```pagecounts-20150509-060000.gz```


