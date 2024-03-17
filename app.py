from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def generate():
    response_details = []
    response_reviews = []

    if request.method == "POST":
        conn = sqlite3.connect('shelf-2.0.db')
        cur = conn.cursor()

        type = request.form['type']
        genre = request.form['genre']
        length = request.form['length']
        print(type, genre, length)

        if type == 'Anything' and genre == "Anything" and length == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id ORDER BY RANDOM() LIMIT 1;'
            ).fetchone()
        elif type == 'Anything' and genre == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE length_ = ? ORDER BY RANDOM() LIMIT 1;',(length,)
            ).fetchone()
        elif type == 'Anything' and length == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE genre = ? ORDER BY RANDOM() LIMIT 1;',(genre,)
            ).fetchone()
        elif genre == 'Anything' and length == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE type = ? ORDER BY RANDOM() LIMIT 1;',(type,)
            ).fetchone()
        elif type == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE genre = ? AND length_ = ? ORDER BY RANDOM() LIMIT 1;',(genre, length)
            ).fetchone()
        elif genre == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE type = ? AND length_ = ? ORDER BY RANDOM() LIMIT 1;',(type, length)
            ).fetchone()
        elif length == "Anything":
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE type = ? AND genre = ? ORDER BY RANDOM() LIMIT 1;',(type, genre)
            ).fetchone()
        else:
            generate_query = cur.execute(
                'SELECT books.title, types.type, genres.genre, lengths.length_ FROM books JOIN types JOIN genres JOIN lengths ON books.type_id = types.id AND books.genre_id = genres.id AND books.length_id = lengths.id WHERE type = ? AND genre = ? AND length_ = ? ORDER BY RANDOM() LIMIT 1;',(type, genre, length)
                ).fetchone()
        if generate_query is None:
            print('No Entry Found')
        else:
            print(generate_query)
            response_title = generate_query[0]
            generated_type = generate_query[1]
            generated_genre = generate_query[2]
            generated_length = generate_query[3]
            generated_bookid = cur.execute('SELECT id FROM books WHERE title = ?',(response_title,)).fetchone()[0]
            generated_gbookid = cur.execute('SELECT gbook_id FROM books WHERE title = ?',(response_title,)).fetchone()[0]
            print("id:", generated_bookid, "Gbook id:", generated_gbookid, "title:", response_title)

            generated_details = cur.execute(
                'SELECT writers.writer FROM books JOIN authors JOIN writers ON authors.book_id = books.id AND authors.writer_id = writers.id WHERE book_id = ?', (generated_bookid,)
            ).fetchall()
            print(generated_details)
            generated_authors = []
            for tuple in generated_details:
                for author in tuple:
                    generated_authors.append(author)
            response_authors = ' & '.join(generated_authors)

            response_details = generated_type + " | " + generated_genre + " | " + generated_length
            
            print(response_title, "by", response_authors + ":", response_details)

            '''SELECT review FROM reviews WHERE book_id = ? ORDER BY RANDOM() LIMIT 3''', (generated_bookid,)
            generated_reviews = cur.execute(
                '''SELECT review FROM reviews WHERE book_id = ? ORDER BY RANDOM() LIMIT 3''', (generated_bookid,)
            ).fetchall()
            for review in generated_reviews:
                response_reviews.append(review)
            print(response_reviews)

            bookcover_url = "https://books.google.com/books/publisher/content/images/frontcover/" + generated_gbookid + "?fife=w400-h600&source=gbs_api"

            return render_template("recommendation.jinja2", title = response_title, author = response_authors, details = response_details, reviews = response_reviews, bookcover = bookcover_url)
    return render_template('homepage.html')



@app.route('/suggest/', methods=['GET', 'POST'])
def suggest(): 
    from urllib.request import urlopen
    import json
    import string

    if request.method == "POST":
        conn = sqlite3.connect('shelf-2.0.db')
        cur = conn.cursor()

        input_title = request.form['title']
        input_author = request.form['author']
        input_type = request.form['type']
        input_genre = request.form['genre']
        input_length = request.form['length']
        review = request.form['review']
        print(input_title, input_author, input_type, input_genre, input_length, review)

        split_title = input_title.split()
        query_title = '+'.join(split_title)
        split_author = input_author.split()
        for word in split_author:
            word = word.strip()
        query_author = '+'.join(split_author)
        print(query_title, query_author)
        
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        # note: this might create "huge security concerns", but it was mentioned in the context of scraping

        apikey  = 'AIzaSyDw7YjvHQkgxesJJT3UNvGVQC-SI9Scswc'

        gbook_query = 'https://www.googleapis.com/books/v1/volumes?q=' + query_title + '&inauthor:' + query_author
        with urlopen(gbook_query) as response:
            body = response.read().decode()
        results = json.loads(body)
        try:
            return_gbookid = results['items'][0]['id']
            return_title = results['items'][0]['volumeInfo']['title']
            return_author = results['items'][0]['volumeInfo']['authors']
            return_type = input_type
            return_genre = input_genre
            length = results['items'][0]['volumeInfo']['pageCount']
            if int(length) < 250:
                return_length = "Short"
            elif int(length) >= 500:
                return_length = "Long"
            else:
                return_length = "Medium"
            print(return_gbookid, return_title, return_author, return_type, return_genre, return_length)
        except:
            print('>>> Failed to retrieve:', input_title, input_author)
            return_title = input_title
            return_author = list()
            return_author.append(input_author)
            return_type = input_type
            return_genre = input_genre
            return_length = input_length
            print(return_title, return_author, return_type, return_genre, return_length)
        
        # check if the book already exists in the "books table"
        check_book = cur.execute('SELECT title FROM books WHERE title = ?', (return_title,)).fetchone()
        # if the book does not exist, collect the IDs for its type, genre and length, before adding them into the "books" table
        if check_book is None:
            print("Book DOES NOT exist in database")

            cur.execute('INSERT OR IGNORE INTO types (type) VALUES (?)', (return_type,))
            type_id = cur.execute('SELECT id FROM types WHERE type = ?', (return_type,)).fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO genres (genre) VALUES (?)', (return_genre,))
            genre_id = cur.execute('SELECT id FROM genres WHERE genre = ?', (return_genre,)).fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO lengths (length_) VALUES (?)', (return_length,))
            length_id = cur.execute('SELECT id FROM lengths WHERE length_ = ?', (return_length,)).fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO books (gbook_id, title, genre_id ,type_id, length_id) VALUES (?, ?, ?, ?, ?)', (return_gbookid, return_title, genre_id, type_id, length_id))
            book_id = cur.execute('SELECT id FROM books WHERE title = ?', (return_title,)).fetchone()[0]
            print("Book ID:", book_id)

            #with the book id, add the review details into the reviews table
            cur.execute('INSERT OR IGNORE INTO reviews (book_id, review) VALUES (?, ?)', (book_id, review))

            #Iterate through the list of authors and add them to the "writers" table, retrieving their IDs and adding this many-to-one relationship into the intermediate "authors" table
            for author in return_author:
                cur.execute('INSERT OR IGNORE INTO writers (writer) VALUES (?)', (author,))
                writer_id = cur.execute('SELECT id FROM writers WHERE writer = ?', (author,)).fetchone()[0]
                cur.execute('INSERT OR IGNORE INTO authors (book_id, writer_id) VALUES (?, ?)', (book_id, writer_id))

            conn.commit()

        #if the book already exists, then I'll just update the type, genre and length into the "books" table in case it's different, and add in the review
        else:
            print("Book EXISTS in database")

            type_id = cur.execute('SELECT id FROM types WHERE type = ?', (return_type,)).fetchone()[0]

            genre_id = cur.execute('SELECT id FROM genres WHERE genre = ?', (return_genre,)).fetchone()[0]

            length_id = cur.execute('SELECT id FROM lengths WHERE length_ = ?', (return_length,)).fetchone()[0]

            cur.execute('UPDATE OR IGNORE books SET gbook_id = ?, genre_id = ? ,type_id = ?, length_id = ? WHERE title = ?', (return_gbookid, genre_id, type_id, length_id, return_title))
            book_id = cur.execute('SELECT id FROM books WHERE title = ?', (return_title,)).fetchone()[0]
            print("Book ID:", book_id)

            cur.execute('INSERT OR IGNORE INTO reviews (book_id, review) VALUES (?, ?)', (book_id, review))

            conn.commit()

        return redirect(url_for('generate'))
    
    return render_template('review.html')