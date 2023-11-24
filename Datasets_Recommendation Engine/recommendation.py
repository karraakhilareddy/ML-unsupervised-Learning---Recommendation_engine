import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import seaborn as sns

data = pd.read_csv('D:/assignments/Data_Science/Datasets_Recommendation Engine/game.csv')

engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user = "root1", pw = "Reddy2000", db = "ml")) 

# Upload the Table into Database
data.to_sql('game', con = engine, if_exists = 'replace', chunksize = 1000, index = False)


# Read the Table (data) from MySQL database
sql = 'select * from game'

df = pd.read_sql_query(sql, con = engine)

duplicate = df['game'].duplicated()
sum(duplicate)


df.isna().sum() #find null_values

df['userId'].value_counts() #find count

# Let's create a ratings dataframe with average rating and number of ratings:
df.groupby('game')['rating'].mean().sort_values(ascending=False).head()

#grouping by game and counting
x=df.groupby('game')['rating'].count().sort_values(ascending=False)

#creating a dataframe and grouping game 
ratings = pd.DataFrame(df.groupby('game')['rating'].mean())


#Now set the number of ratings column:
ratings['num of ratings'] = pd.DataFrame(df.groupby('game')['rating'].count())

rate = ratings.reset_index()

    

cosine_sim_matrix = cosine_similarity(rate[['rating']], rate[['rating']])

anime_index = pd.Series(rate.index, index = rate['game']).drop_duplicates()

anime_id = anime_index["Tony Hawk's Pro Skater 2"]
anime_id

def get_recommendations(Name, topN):    
    #topN = 5
    #Name = "Tony Hawk's Pro Skater 2"
    
    # Getting the movie index using its title 
    anime_id = anime_index[Name]
    
    # Getting the pair wise similarity score for all the anime's with that anime
    cosine_scores = list(enumerate(cosine_sim_matrix[anime_id]))
    
    # Sorting the cosine_similarity scores based on scores 
    cosine_scores = sorted(cosine_scores, key = lambda x:x[1], reverse = True)
    
    # Get the scores of top N most similar movies 
    cosine_scores_N = cosine_scores[0: topN + 1]
    
    # Getting the movie index 
    anime_idx  =  [i[0] for i in cosine_scores_N]
    anime_scores = [i[1] for i in cosine_scores_N]
    
    # Similar movies and scores
    anime_similar_show = pd.DataFrame(columns = ["name", "Score"])
    anime_similar_show["name"] = rate.loc[anime_idx, "game"]
    anime_similar_show["Score"] = anime_scores
    anime_similar_show.reset_index(inplace = True)
    
    return(anime_similar_show)

rec = get_recommendations("Tony Hawk's Pro Skater 2", topN = 10)
rec


















































































