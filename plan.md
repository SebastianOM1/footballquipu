# PERUVIAN FOOTBALL PROJECT (NAME TBD)
## Concept
A website that displays data about the first division of the Peruvian football league. It allows users to search by year, by competition, by team, by player, etc.

In addition, a public API will be made available.

## Acquiring the data
The data will be acquired through scraping of the DeChalaca.com website. They have "fichas" or stat spreadsheets for each game of each year going back to 2012. From 2011 to 2009 these were published only in image format and collecting data from them may be a bit more tricky to get information out of.

## Data fields
For players the data includes: Yellow cards, red cards, goals, manner of goal, minutes played, starting/sub status, and a score given by the DeChalaca team of writers (from 1 to 20), this also comes with the MVP status, which is given to the player with the highest score of the game.

For teams, the above data is included for each of their players. In addition, their formation is included and through it the position of each player is elucidated. The team's captain is also determined by inspection of the data.

## Plan
### 1) Scraping the data
Using: Python

Asynchronously scraping all of the data in the DeChalaca website may seem like the most efficient option, but out of fear of overwhelming their services the "less potent" requests library will be used.

The first step of this plan will be to create a program that scrapes all of the necessary data and stores it in .txt files.

### 2) Parsing the data
Using: Python

### 3) Building a database
Using:

### 4) Website building
Using: React

### 5) API
Using: