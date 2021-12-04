# COVID Dashboard

A simple personalised COVID Dashboard

## Installation

Clone the git repository and navigate to directory

```bash
git clone https://github.com/EthanHofton/CovidDashboard.git
cd CovidDashboard
```

or alternatively, download directly from the github page [here](https://github.com/EthanHofton/CovidDashboard)

Once the repository has been downloaded, install the package dependencies using the `requirements.txt` file

Download package dependencies to local machine:
```bash
pip install -r requirements.txt
```

Download package dependencies to a virtual environment for Mac/Linux:
```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Download package dependencies to a virtual environment for Windows:
```bash
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

After installing, navigate to the project directory. Next, if you choose to install the package dependencies to a virtual environment, activate the virtual environment (to check if the environment is already active, (venv) will appear before the console line)

For Mac/Linux
```bash
. venv/bin/activate
```

For Windows
```bash
venv\Scripts\activate
```

After the virtual environment has been activated (if using one), run the flask app

For Mac/Linux
```bash
export FLASK_APP=flaskr
flask run
```

For Windows
```bash
set FLASK_APP=flaskr
flask run
```

## Usage

navigate to the dashboard webpage [http://localhost:5000/index](http://localhost:5000/index)

## Features

The middle panel of the dashboard contains local covid infection rates for the specified location in the json config file. There are also infection rates, current hospital cases and current deaths for the specified national location in the config file

The right hand panel contains a stack of news articles, the news articles can be filtered by editing the `'search_term'` parameter in the config file. News articles may also be closed by clicking the x in the top right corner of the article you wish to close. The articles will not reappear.

The left hand panel contains a list of all scheduled updates. Updates may be cancelled by clicking the cross in the top right corner of the update you wish to cancel.

Updates may be scheduled in the bottom of the middle panel by entering a title for the update, the time the update should trigger, and weather or not the update should be repetin, if it should update the covid infection rates data or if it should update the news articles and then clicking the submit button

## Personalisation

The config file may be found in the `flaskr/` directive and is named `config.json`. To customise the dashboard edit the values of each of the parameters you would like to change.

To change the number of news article results, edit the `'pageSize'` parameter in the `'news_api'` section to the desired amount. For example, to change the number of news articles to 5:

```json
"pageSize" : 5
```

To change the search terms for the news article, change the `'search_terms'` parameter in the `'dashboard'` section:

```json
"search_terms" : "Covid COVID-19"
```

## Dashboard Personalisation

The values that may be changed in the dashboard section of the config file are:

The title of the dashboard, using `title`

```json
"title" : "Covid19 Dashboard",
```

The local location the dashboard displays data for, using `local_location`

```json
"local_location" : "Exeter",
```

The type of location the local location is, using `local_location_type`

```json
"local_location_type" : "ltla",
```

The national location the dashboard gathers data for, using `national_location`

```json
"national_location" : "England",
```

The type of location the national location is, using `national_location_type`

```json
"national_location_type" : "nation",
```

the favicon file the dashboard uses, using `favicon`

```json
"favicon" : "favicon.ico",
```

The search terms that are used to filter the news articles, using `search_terms`

```json
"search_terms" : "Covid COVID-19 coronavirus"
```

Editing the values in the config file will update the dashboard respectively

## News

The dashboard uses the [News API](https://newsapi.org/) to gather news stories and display them on the dashboard. The way the webpage displays the news articles can be personalised by editing the config file. The parameters that can be edited are:

`language`, this parameter will return news articles in the specified language

```json
"language" : "en",
```

`pageSize`, this parameter edit the number of news articles to be returned (max=100)

```json
"pageSize" : 2,
```

`from`, this parameter will return news articles from [from] may days ago

```json
"from" : 5,
```

`sortBy`, this parameter will change the order the news articles are returned in. possible values for `sortBy` are (`relevancy` , `popularity` and `publishedAt`. [see newsAPI documentation for more](https://newsapi.org/docs/))

```json
"sortBy" : "publishedAt"
```

## Logging

A detailed log of the programs history will be saved to a log in the `flaskr/logs` directory called `'data.log'`. the logging level can be changed in the config file:

```json
"level" : 10
```

The levels are as follows:

| Level| Value |
|----------|-------|
| NOTSET   | 0     |
| DEBUG    | 10    |
| INFO     | 20    |
| WARNING  | 30    |
| ERROR    | 40    |
| CRITICAL | 50    |

The location of the log file may also be changed in the config file:

```json
"logfile" : "flaskr/logs/data.log",
```

The format the logger will output may also be changed in the config file:

```json
"format" : "%(levelname)s:%(name)s: [%(asctime)s] - %(message)s",
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

# Information For Developers

The code uses an event driven architecture using flask. To get covid data, the program uses the `uk_covid19` module and to get news articles the program uses the news API ([see more](https://newsapi.org/)). To schedule updates, the program uses `sched`. logging is handled by the `logging` module.

The webpage is set to refresh every 60 seconds. The idea behind this is that if data has been updated, when the page is auto refreshing the data in the data structures that got updated will be re-displayed.

## update scheduling and displaying data

when an update is triggered, to update the covid data there is a global data structure called `COVID_DATA` that the function writes to and once the page refreshes, the data in this data structure will be displayed. The news article updates work on a similar idea/ There is a global list called `ARTICLES` that the update function writes to and once the page refreshes, the articles in the list is redisplayed.
