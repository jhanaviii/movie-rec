from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def calculate_similarity(conn, movie_id1, movie_id2):
    """Calculate similarity between two movies based on user ratings"""
    cur = conn.cursor()
    
    cur.execute('''SELECT r1.rating, r2.rating
                   FROM ratings r1
                   JOIN ratings r2 ON r1.user_id = r2.user_id
                   WHERE r1.movie_id = ? AND r2.movie_id = ?''', (movie_id1, movie_id2))
    rows = cur.fetchall()
    
    ratings1 = [row[0] for row in rows]
    ratings2 = [row[1] for row in rows]
    
    if not ratings1 or not ratings2:
        return 0, 0
    
    # Calculate Pearson correlation coefficient
    mean_rating1 = sum(ratings1) / len(ratings1)
    mean_rating2 = sum(ratings2) / len(ratings2)
    
    numerator = sum((x - mean_rating1) * (y - mean_rating2) for x, y in zip(ratings1, ratings2))
    denominator1 = sum((x - mean_rating1) ** 2 for x in ratings1)
    denominator2 = sum((y - mean_rating2) ** 2 for y in ratings2)
    
    if denominator1 == 0 or denominator2 == 0:
        return 0, 0
    
    correlation = numerator / ((denominator1 ** 0.5) * (denominator2 ** 0.5))
    
    return correlation, len(ratings1)

def recommend_movies(conn, movie_id, num_recommendations=5):
    """Recommend similar movies based on the provided movie_id"""
    cur = conn.cursor()
    
    # Fetch the movie title associated with the provided movie ID
    cur.execute('''SELECT title FROM movies WHERE movie_id = ?''', (movie_id,))
    movie_title = cur.fetchone()[0]
    
    # Fetch all movies except the provided movie ID
    cur.execute('''SELECT DISTINCT movie_id FROM ratings WHERE movie_id != ?''', (movie_id,))
    all_movies = cur.fetchall()
    
    similarity_scores = []
    # Calculate similarity scores between the provided movie and all other movies
    for other_movie in all_movies:
        similarity = calculate_similarity(conn, movie_id, other_movie[0])
        similarity_scores.append((other_movie[0], similarity[0] * similarity[1]))
    
    # Sort movies based on similarity scores
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    recommendations = similarity_scores[:num_recommendations]
    
    recommended_movies = []
    # Fetch movie titles for recommended movie IDs
    for rec in recommendations:
        cur.execute('''SELECT title FROM movies WHERE movie_id = ?''', (rec[0],))
        movie_title = cur.fetchone()[0]
        recommended_movies.append((movie_title, rec[1]))
    
    return recommended_movies

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        movie_id = int(request.form['movie_id'])
        conn = create_connection("movies.db")
        recommendations = recommend_movies(conn, movie_id)
        conn.close()
        return render_template('index.html', recommendations=recommendations)
    return render_template('index.html', recommendations=None)

if __name__ == '__main__':
    app.run(debug=True)

