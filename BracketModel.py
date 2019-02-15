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

print("")
region = {}
x = 1
while x < 17:    
    region["Seed{0}".format(x)] = input("Enter "+str(x)+" Seed Team: ")
    if (region["Seed{0}".format(x)]) not in df.Team:
        print(x, "seed team not found")
    else:
        x += 1
        

def sim_game(Team1, Team2):
    #results = []
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
        
"""    
#For running multiple simulations of 1 game rather than multiple simulations of 1 region

        results += [result]
    if results.count(True) > results.count(False):
        return(Team1)
    elif results.count(False) > results.count(True):
        return(Team2)
    else:
        if ELO1 > ELO2:
            return(Team1)
        else:
            return(Team2)
"""

reps = int(input('Enter number of tournaments to simulate: '))


###################################
###NCAA Tourney Region Simulator###
###################################

Winners = []
Round1W = []
Round2W = []
Round3W = []

for x in range(reps):
#Round 1
    Win1 = sim_game(region['Seed1'],region['Seed16'])
    Win2 = sim_game(region['Seed8'],region['Seed9'])
    Win3 = sim_game(region['Seed5'],region['Seed12'])
    Win4 = sim_game(region['Seed4'],region['Seed13'])
    Win5 = sim_game(region['Seed6'],region['Seed11'])
    Win6 = sim_game(region['Seed3'],region['Seed14'])
    Win7 = sim_game(region['Seed7'],region['Seed10'])
    Win8 = sim_game(region['Seed2'],region['Seed15'])
    Round1W += [Win1,Win2,Win3,Win4,Win5,Win6,Win7,Win8]

#Round 2
    Win2_1 = sim_game(Win1,Win2)
    Win2_2 = sim_game(Win3,Win4)
    Win2_3 = sim_game(Win5,Win6)
    Win2_4 = sim_game(Win7,Win8)
    Round2W += [Win2_1,Win2_2,Win2_3,Win2_4]

#Round 3
    Win3_1 = sim_game(Win2_1,Win2_2)
    Win3_2 = sim_game(Win2_3,Win2_4)
    Round3W += [Win3_1,Win3_2]

#Round 4
    WinFF = sim_game(Win3_1,Win3_2)
    Winners += [WinFF]

#Graph for final round winner

totwins = Counter(Winners)
for x in totwins:
    totwins[x] = totwins[x]/reps

results = pd.DataFrame(list(totwins.items()), columns=['Team', 'Win Share %'])
results['Team'] = results['Team'].str.replace('_', ' ')
results["Win Share %"] = (results["Win Share %"] * 100)
results = results.sort_values(["Win Share %"], ascending = False)
Output = sns.barplot(x = results["Win Share %"], y = results["Team"])
Output.set(xlabel = "Projected Win Shares (%)")
#print(results)

######### Data for all previous rounds ##########

round1wins = Counter(Round1W)
round2wins = Counter(Round2W)
round3wins = Counter(Round3W)

for x in round3wins:
    round3wins[x] = round3wins[x]/reps
for x in round2wins:
    round2wins[x] = round2wins[x]/reps
for x in round1wins:
    round1wins[x] = round1wins[x]/reps

results3 = pd.DataFrame(list(round3wins.items()), columns=['Team', 'Win Share %'])
results3['Team'] = results3['Team'].str.replace('_', ' ')
results3["Win Share %"] = (results3["Win Share %"] * 100)
results3 = results3.sort_values(["Win Share %"], ascending = False)

results2 = pd.DataFrame(list(round2wins.items()), columns=['Team', 'Win Share %'])
results2['Team'] = results2['Team'].str.replace('_', ' ')
results2["Win Share %"] = (results2["Win Share %"] * 100)
results2 = results2.sort_values(["Win Share %"], ascending = False)

results1 = pd.DataFrame(list(round1wins.items()), columns=['Team', 'Win Share %'])
results1['Team'] = results1['Team'].str.replace('_', ' ')
results1["Win Share %"] = (results1["Win Share %"] * 100)
results1 = results1.sort_values(["Win Share %"], ascending = False)

print("")
print("Make Final Four Probability:")
print(results)
print("")
print("Make Elite Eight Probability:")
print(results3)
print("")
print("Make Sweet 16 Probability:")
print(results2)
print("")
print("Make Second Round Probability:")
print(results1)
