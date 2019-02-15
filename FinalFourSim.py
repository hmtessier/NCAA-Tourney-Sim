
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 12:55:30 2018

@author: Henry Tessier
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import random
from collections import Counter
import seaborn as sns


# Base url, and a lambda func to return url for a given year
base_url = 'http://kenpom.com/index.php'
url_year = lambda x: '%s?y=%s' % (base_url, str(x) if x != 2018 else base_url)

# Create a method that parses a given year and spits out a raw dataframe
def import_raw_year(year):
    
    #Imports raw data from a ken pom year into a dataframe
    
    f = requests.get(url_year(year))
    soup = BeautifulSoup(f.text, "lxml")
    table_html = soup.find_all('table', {'id': 'ratings-table'})

    # Weird issue w/ <thead> in the html
    # Prevents us from just using pd.read_html
    # Let's find all the thead contents and just replace/remove them
    # This allows us to easily put the table row data into a dataframe using panda
    thead = table_html[0].find_all('thead')

    table = table_html[0]
    for x in thead:
        table = str(table).replace(str(x), '')

    df = pd.read_html(table)[0]
    df['year'] = year
    return df
    

# Import all the years into a singular dataframe
df = None
pickyear = input("Enter Year (2002 - 2018): ")
print("")
print("Gathering most recent statistics...")
df = pd.concat( (df, import_raw_year(pickyear)), axis=0) 

# Column rename based off of original website
df.columns = ['Rank', 'Team', 'Conference', 'W-L', 'AdjEM', 
             'AdjustO', 'AdjustO Rank', 'AdjustD', 'AdjustD Rank',
             'AdjustT', 'AdjustT Rank', 'Luck', 'Luck Rank', 
             'SOS_Pyth', 'SOS Pyth Rank', 'SOS OppO', 'SOS OppO Rank',
             'SOS OppD', 'SOS OppD Rank', 'NCSOS Pyth', 'NCSOS Pyth Rank', 'Year']
             
# Lambda that returns true if given string is a number and a valid seed number (1-16)
valid_seed = lambda x: True if str(x).replace(' ', '').isdigit() \
                and int(x) > 0 and int(x) <= 16 else False

# Use lambda to parse out seed/team
df['Seed'] = df['Team'].apply(lambda x: x[-2:].replace(' ', '') \
                              if valid_seed(x[-2:]) else np.nan )

df['Team'] = df['Team'].apply(lambda x: x[:-2] if valid_seed(x[-2:]) else x)

# Split W-L column into wins and losses
df['Wins'] = df['W-L'].apply(lambda x: int(re.sub('-.*', '', x)) )
df['Losses'] = df['W-L'].apply(lambda x: int(re.sub('.*-', '', x)) )
df.drop('W-L', inplace=True, axis=1)


df=df[[ 'Year', 'Rank', 'Team', 'Conference', 'Wins', 'Losses', 'Seed','AdjEM', 
             'AdjustO', 'AdjustO Rank', 'AdjustD', 'AdjustD Rank',
             'AdjustT', 'AdjustT Rank', 'Luck', 'Luck Rank', 
             'SOS_Pyth', 'SOS Pyth Rank', 'SOS OppO', 'SOS OppO Rank',
             'SOS OppD', 'SOS OppD Rank', 'NCSOS Pyth', 'NCSOS Pyth Rank']]
             
df = df[['Team','Wins','Losses','AdjEM','SOS_Pyth']]
df.Team = df.Team.str.rstrip()
df.Team = df.Team.str.replace('\s+', '_')
df.Team = df.Team.str.replace('.', '')
df.Team = df.Team.str.replace('&', '')
df.Team = df.Team.str.replace('\'', '')
df['WLPercentage'] = df.Wins / (df.Losses + df.Wins)
df['Name'] = df.Team
df = df.set_index('Name')


# ______________________Data Import Completed_________________________________

def sim_game(Team1, Team2):
    results = []
    #for x in range(reps):    
    ELO1 = ((df.loc[Team1].AdjEM + 40) + ((df.loc[Team1].SOS_Pyth + 15) * df.loc[Team1].WLPercentage))    
    ELO2 = ((df.loc[Team2].AdjEM + 40) + ((df.loc[Team2].SOS_Pyth + 15) * df.loc[Team2].WLPercentage))
    m = ELO1 - ELO2
    A = (1/(1+10**(abs(m)/23)))
    odds = (1-A)
    if m < 0:
        odds = (1-odds)
    result = random.random() <= odds
        
    if result == True:
        return(Team1)
    else:
        return(Team2)


#Final Four Simulator
print("")
four1 = {}
four2 = {}
x = 1
y = 1
while x < 3:    
    four1["Seed{0}".format(x)] = input("Enter Semifinal 1, Team "+str(x)+ ": ")
    if (four1["Seed{0}".format(x)]) not in df.Team:
        print("Team not found")
    else:
        x += 1
while y < 3:    
    four2["Seed{0}".format(y)] = input("Enter Semifinal 2, Team: "+str(y)+": ")
    if (four2["Seed{0}".format(y)]) not in df.Team:
        print("Team not found")
    else:
        y += 1
        
reps = int(input('Enter number of tournaments to simulate: '))

winners = []
for x in range(reps):
    
    Win1 = sim_game(four1['Seed1'],four1['Seed2'])
    Win2 = sim_game(four2['Seed1'],four2['Seed2'])
    Champ = sim_game(Win1,Win2)
    winners += [Champ]
    
totwins = Counter(winners)
for x in totwins:
    totwins[x] = totwins[x]/reps
    
results = pd.DataFrame(list(totwins.items()), columns=['Team', 'Win Share %'])
results['Team'] = results['Team'].str.replace('_', ' ')
results["Win Share %"] = (results["Win Share %"] * 100)
results = results.sort_values(["Win Share %"], ascending = False)
Output = sns.barplot(x = results["Win Share %"], y = results["Team"])
Output.set(xlabel = "Projected Win Shares (%)")
print(results)
    
    
    
