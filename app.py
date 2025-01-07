from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)  # Initialize the Flask application

# Load books from JSON file
def load_books_from_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

# Filter books by genre (case insensitive)
def get_books_by_genre(genre, books):
    genre = genre.strip().lower()  # Normalize the input genre
    filtered_books = [book for book in books if book.get("genre", "").lower() == genre]
    return filtered_books

# Load books dataset
books = load_books_from_json("books.json")

# Track previously suggested books
suggested_books = {}

# Home route (renders front-end)
@app.route("/")
def home():
    return render_template("index.html")

# Chatbot API endpoint
@app.route("/get_books", methods=["POST"])
def get_books():
    user_input = request.json.get("user_input", "").lower()
    
    # Handle greetings
    greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
    if any(greeting in user_input for greeting in greetings):
        return jsonify({"status": "success", "message": "Hello! How can I assist you today? Please ask about a genre of books!"})

    # Handle genre queries with suggestions
    if any(phrase in user_input for phrase in ["books", "suggest", "recommend"]):
        # Extract the genre from user input
        possible_genre = None
        if "fiction" in user_input:
            possible_genre = "fiction"
        elif "horror" in user_input:
            possible_genre = "horror"
        elif "romance" in user_input:
            possible_genre = "romance"
        elif "fantasy" in user_input:
            possible_genre = "fantasy"
        elif "sci-fi" in user_input or "science fiction" in user_input:
            possible_genre = "science fiction"
        elif "mystery" in user_input:
            possible_genre = "mystery"
        elif "historical" in user_input:
            possible_genre = "historical fiction"
        
        if possible_genre:
            # Track and suggest books
            if possible_genre not in suggested_books:
                suggested_books[possible_genre] = 0

            filtered_books = get_books_by_genre(possible_genre, books)
            print(f"Filtered books: {filtered_books}")  # Debugging line

            start_index = suggested_books[possible_genre]
            
            if start_index < len(filtered_books):
                book = filtered_books[start_index]
                print(f"Selected book: {book}")  # Debugging line
                suggested_books[possible_genre] += 1
                
                # Check if the book has a valid description
                book_name = book.get("title", "Unknown Title")
                description = book.get("description", None)
                print(f"Book description: {description}")  # Debugging line

                # Modify the response based on whether the description is present
                if description:
                    response = {
                        "book_name": book_name,
                        "description": description  # Show description
                    }
                else:
                    response = {
                        "book_name": book_name,
                        "description": "No description available"  # Default message if no description
                    }

                return jsonify({
                    "status": "success",
                    "message": f"Chatbot answer: Here's a {possible_genre} book suggestion: {book_name} by {book['author']}.",
                    "user_query": f"User asked: Suggest me {possible_genre} books",
                    "book_info": response
                })
            else:
                suggested_books[possible_genre] = 0
                return jsonify({
                    "status": "success",
                    "message": f"Chatbot answer: Sorry, I have suggested all {possible_genre} books. Would you like to explore a different genre?",
                    "user_query": f"User asked: Suggest me {possible_genre} books",
                    "book_info": None
                })
        else:
            return jsonify({
                "status": "error",
                "message": "I didn't understand your request. Please ask about a genre of books, like 'fiction books' or 'suggest a fiction book'.",
                "user_query": f"User asked: {user_input}",
                "book_info": None
            })
    
    else:
        return jsonify({
            "status": "error",
            "message": "I didn't understand your request. Please ask about a genre of books!",
            "user_query": f"User asked: {user_input}",
            "book_info": None
        })

if __name__ == "__main__":
    app.run(debug=True)