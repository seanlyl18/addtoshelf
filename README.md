# Welcome to Add To Shelf!
This is a simple web development project I made for bookworms to randomly generate books that others love!

## How To Use
This website has been designed to be as intuitive to navigate as possible, but here is a step-by-step guide to get your book recommendation!

### Homepage
THe homepage has a form with 3 dropdown menus where you can specify what type (fiction or non-fiction), genre and length of book you're looking for. Or, you can just click the "Anything!" option and be surprised! Upon submission, the page will automatically take them to the Recommendation page where your recommendation will be!

### Recommendation Page
Here is your book recommendation! This book was randomly chosen (with your criteria in mind) from a database of books that other users love and recommend, and below the book details you'll find 3 bite-sized reviews of who the contributors feel will enjoy the book! Feel free to walk away with your newfound book title, but you can also choose to recommend books to other users too, by clicking into the Suggest Page. 

### Suggest Page
Thank you for the love for books! Here, you'll fill in the book title and author (don't worry if you don't remember exactly what they are, we'll check with Google Books to make sure it's right). Below that, tell us what type, genre and how long the book is. And finally, tell us in 280 characters or less what kind of person would fall in love this read! 

## How It Works
### Generating Recommendations
After the submission of the form, a POST request will be sent containing the conditions entered in by the user. These conditions are translated into an SQLite query, where the details of the book (title, author, 3 reviews for the book and Google Books ID) will be retrieved. Using the Google Book Id, a URL to the specific book's cover image can be generated. All these details are organised and stored where they can be sent into the Recommendations Page (a .jinja2 file). With Jinja, a unique page can be generated without having to manually code each of them. The generated book cover and its details are further formatted, styled and rendered. All webpages are also responsive and mobile-friendly!

If there's no record in the database that meets the specified critieria, the page simply reloads. 

### Database Structure
This database is created with SQLite (a relational database) and visualised with its DB Browser. 

The "books" table is the heart of the entire database, containing the foreign keys to the "types", "genres, "lengths" (which contain a predetermined list of options that correspond with the values in the HTML form) as well as storing the unique Google Book IDs. There are hence one-to-many relationships between "books" and the 3 mentioned tables. The "reviews" table is also similar, and has a foreign key to the "books" table, as well as a short review. 

Storing the authors names are more complicated, as books can be co-authored by multiple writers. So, a many-to-many relationship exists between the "writers" and "books" tables, with "authors" being the intermediate table where its primary key is the combination of the 2 foreign keys. 

### Suggesting Books
The form on the homepage was designed to be filled in very quickly with simple but effective client-side validation using dropdown menus (<select> elements). However, the Suggest page's form required users to type in text by themselves, and hence server-side validation was needed to prevent duplication of entries into the databse. Google Books and its search functionw was used to iron this out. By using the keywords (title and author's/authors' name) and adding them into a query URL (Google Books API), the search results data were returned in JSON. 

After parsing through it and the necessary information (GBook ID, exact title and author, and book page count). the data is used to check whether the book existed in the database or not. If it doesn't exist, all the data will be added to and commited. If it does exist, the details that were not validated (i.e. the type and genre) would be updated and a review will be added, enabling a book recommendation to be self-corrected if one user accidentally inputs an inaccurate detail. 

## How To Download and Run This Web App
1. Download all the files and maintain the folder structure
2. In order to access the database, download the SQLite DB Browser from this URL: https://sqlitebrowser.org/dl/
3. pip install all the dependencies and packages from requirements.txt
4. Run flask (flask run command) and copy the host IP address provided to the browser (locallly hosted)

### Troubleshooting
If the error is "database is locked", write the changes in the DB browser before running Flask. 

If there are any errors, bugs or difficulties running the app, feel free to raise an issue on this repo or email me (seanlyl18@gmail.com)
