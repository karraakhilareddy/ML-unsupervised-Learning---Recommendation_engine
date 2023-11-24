from flask import render_template,Flask,request
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user = "root1", pw = "Reddy2000", db = "ml")) 


# Read the Table (data) from MySQL database
sql = 'select * from game'

df = pd.read_sql_query(sql, con = engine)

duplicate = df['game'].duplicated()
sum(duplicate)


df.isna().sum() #find null_values

z= df['userId'].value_counts() #find count

# Let's create a ratings dataframe with average rating and number of ratings:
df.groupby('game')['rating'].mean().sort_values(ascending=False).head()

#grouping by game and counting
x=df.groupby('game')['rating'].count().sort_values(ascending=False)

#creating a dataframe and grouping game 
ratings = pd.DataFrame(df.groupby('game')['rating'].mean())


#Now set the number of ratings column:
ratings['num of ratings'] = pd.DataFrame(df.groupby('game')['rating'].count())

rate = ratings.reset_index()


movies_list = rate['game'].to_list()

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
    # anime_similar_show.drop(["index"], axis=1, inplace=True)
    return(anime_similar_show)

app = Flask(__name__)

@app.route('/')
def home():
    #colours = ['Red', 'Blue', 'Black', 'Orange']
    return render_template("index.html", movies_list = movies_list)

@app.route('/guest', methods = ["post"])

def Guest():
    if request.method == 'POST' :
        mn = request.form["mn"]
        tp = request.form["tp"]
        
        top_n = get_recommendations(mn, topN = int(tp))

        # Transfering the file into a database by using the method "to_sql"
        top_n.to_sql('top_10', con = engine, if_exists = 'replace', chunksize = 1000, index = False)
        
        html_table = top_n.to_html(classes = 'table table-striped')

        return render_template( "data.html", Y = "Results have been saved in your database", Z =  f"<style>\
                    .table {{\
                        width: 50%;\
                        margin: 0 auto;\
                        border-collapse: collapse;\
                    }}\
                    .table thead {{\
                        background-color: #39648f;\
                    }}\
                    .table th, .table td {{\
                        border: 1px solid #ddd;\
                        padding: 8px;\
                        text-align: center;\
                    }}\
                        .table td {{\
                        background-color: #5e617d;\
                    }}\
                            .table tbody th {{\
                            background-color: #ab2c3f;\
                        }}\
                </style>\
                {html_table}") 

if __name__ == '__main__':

    app.run(debug = True)

