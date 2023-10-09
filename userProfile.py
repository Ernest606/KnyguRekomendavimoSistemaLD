import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from urllib.request import urlopen
import io
import sys
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.optimizers import Adam

userID = int(sys.argv[1])
usersDB = pd.read_csv('DataBase/Users.csv', sep=',')
username = str(usersDB.loc[usersDB['UserID'] ==
               int(sys.argv[1])]['Username'].item())
booksDB = pd.read_csv('DataBase/books_cleaned.csv', sep=',')
ratingsDB = pd.read_csv('DataBase/ratings.csv', sep=',')
model = tf.keras.models.load_model('DataBase/model.h5', compile=False)


def update_model(model, new_data, batch_size=64, epochs=1):
    optimizer = Adam(learning_rate=0.001, epsilon=1e-6,
                     amsgrad=True)  # epsilon = decay rate
    # Using mean squared error as loss function
    model.compile(optimizer=optimizer, loss='mean_squared_error')

    # Split new data into features and target
    user_data, book_data, ratings = new_data['user_id'], new_data['book_id'], new_data['rating']

    # Train the model on the new data
    model.fit(
        [book_data, user_data], ratings,
        batch_size=batch_size,
        epochs=epochs,
        verbose=1
    )


def recommend(user_id):
    ratings = pd.read_csv('DataBase/ratings.csv', sep=',')
    if user_id > 53424:
        ratings = ratings[ratings['user_id'] != 53425]
        ratings.loc[ratings['user_id'] == userID, ['user_id']] = 53425
        user_id = 53425
        ratings = ratings[ratingsDB['user_id'] < 53427]
        update_model(model, ratings)

    book_id = list(ratings.book_id.unique())  # grabbing all the unique books

    # geting all book IDs and storing them in the form of an array
    book_arr = np.array(book_id)
    user_arr = np.array([user_id for i in range(len(book_id))])
    prediction = model.predict([book_arr, user_arr])

    prediction = prediction.reshape(-1)  # reshape to single dimension
    prediction_ids = np.argsort(-prediction)[0:5]

    recommended_books = pd.DataFrame(booksDB.iloc[prediction_ids], columns=[
                                     'book_id', 'isbn', 'authors', 'title', 'average_rating'])
    return recommended_books


class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0,
                                background="#ffffff", width=1000, height=800)
        self.view_port = tk.Frame(
            self.canvas, background="#ffffff", width=1000, height=800)
        self.vsb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview, width=25)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window(
            (4, 4), window=self.view_port, anchor="nw", tags="self.view_port")

        self.view_port.bind("<Configure>", self.onFrameConfigure)

    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class BookRatingApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Book Rating App")
        self.images = []

        self.rated_books = {}

        for index in range(0, len(ratingsDB.loc[ratingsDB['user_id'] == userID] == userID)):
            book_id = ratingsDB.loc[ratingsDB['user_id']
                                    == userID]['book_id'].iloc[index]
            book_title = str(
                booksDB.loc[booksDB['id2'] == book_id]['title'].item())
            book_rating = ratingsDB.loc[ratingsDB['user_id']
                                        == userID]['rating'].iloc[index]
            book_image_url = booksDB.loc[booksDB['id2']
                                         == book_id]['small_image_url'].item()
            self.rated_books[book_title] = {
                "rating": book_rating,
                "image_url": book_image_url
            }

        self.books = {}

        self.book_frames = []

        # Greeting label
        # Replace this with any logic you might have to get the user's name

        self.greeting_label = tk.Label(
            self.master, text=f"Hi, {username}!", font=("Arial", 14))
        self.greeting_label.pack(pady=10)  # Adjust the padding for aesthetics

        self.rate_new_book_button = tk.Button(
            self.master, text="Rate New Book", command=self.show_rate_new_book_dialog)
        self.rate_new_book_button.pack(pady=(0, 10), side=tk.BOTTOM)

        self.recommended_frame = tk.Frame(self.master)
        self.recommended_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.recommend_button = tk.Button(
            self.master, text="Show Recommended Books", command=self.show_recommended_books)
        self.recommend_button.pack(pady=(0, 10), side=tk.RIGHT)

        self.create_widgets()

    def show_recommended_books(self):
        recommended_books_prediction = recommend(userID)

        self.recommended_books = {}

        for x in range(0, len(recommended_books_prediction)):
            book_title = recommended_books_prediction['title'].iloc[x]
            book_rating = recommended_books_prediction['average_rating'].iloc[x]
            book_url = booksDB.loc[booksDB['title'] ==
                                   book_title]['small_image_url'].item()
            self.recommended_books[book_title] = {
                "rating": book_rating,
                "image_url": book_url
            }

        # Display the first 5 books from the list.
        for book_title, book_data in list(self.recommended_books.items())[:5]:
            # Create label for book title
            title_label = tk.Label(self.recommended_frame, text=book_title)
            title_label.pack(pady=(10, 0))

            # Fetch and display book image
            img_data = urlopen(book_data["image_url"]).read()
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((75, 100))  # Resize image to fit
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.recommended_frame, image=photo)
            img_label.image = photo
            img_label.pack(pady=(5, 10))

    def create_widgets(self):
        for frame in self.book_frames:
            frame.destroy()

        self.book_frames = []
        self.images.clear()

        if hasattr(self, "scrollable_frame"):
            self.scrollable_frame.destroy()

        self.scrollable_frame = ScrollableFrame(self.master)
        self.scrollable_frame.pack(expand=True, fill="both")

        for book, info in self.rated_books.items():
            frame = tk.Frame(self.scrollable_frame.view_port)
            frame.pack(pady=5, padx=5, fill=tk.X)

            image_url = info["image_url"]
            image = self.load_image_from_url(image_url)
            if image:
                image = image.resize((70, 90))
                photo = ImageTk.PhotoImage(image)
                self.images.append(photo)
                label_image = tk.Label(frame, image=photo)
                label_image.image = photo
                label_image.pack(side=tk.LEFT)

            book_info = f"{book}\nRating: {info['rating']}"
            label_book_info = tk.Label(frame, text=book_info, anchor=tk.W)
            label_book_info.pack(side=tk.LEFT, padx=(10, 0))

            delete_button = tk.Button(
                frame, text="Delete Book", command=lambda b=book: self.delete_book(b))
            delete_button.pack(side=tk.RIGHT)

            self.book_frames.append(frame)

    def load_image_from_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                return image
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: Unable to retrieve image from URL: {e}")
            return None

    def show_rate_new_book_dialog(self):
        dialog = RateNewBookDialog(
            self.master, self.books, self.create_widgets, self.rated_books)

    def delete_book(self, book):
        if book in self.rated_books:
            self.images.clear()
            del self.rated_books[book]
            self.create_widgets()

            ratingsDB_without_user = ratingsDB[ratingsDB['user_id'] != userID]
            if len(self.rated_books) != 0:
                booksIDs = []
                userIDs = []
                ratingsDB_without_user = ratingsDB[ratingsDB['user_id'] != userID]

                df = pd.DataFrame.from_dict(self.rated_books, orient='index')
                df = df.reset_index().rename(columns={'index': 'book_name'})

                for x in range(0, len(self.rated_books)):
                    userIDs.append(userID)
                    bookName = df['book_name'][x]
                    booksIDs.append(
                        booksDB.loc[booksDB['title'] == bookName]['id2'].item())

                df = df.drop(columns=['book_name'])
                df = df.drop(columns=['image_url'])
                df['book_id'] = booksIDs
                df['user_id'] = userIDs
                df = df[['book_id', 'user_id', 'rating']]
                df['rating'] = df['rating'].astype(int)

                updated_ratingsDB = pd.concat(
                    [ratingsDB_without_user, df], ignore_index=True)
                updated_ratingsDB.to_csv(
                    'DataBase/ratings.csv', sep=',', index=False)
            else:
                ratingsDB_without_user.to_csv(
                    'DataBase/ratings.csv', sep=',', index=False)


class RateNewBookDialog(BookRatingApp):
    def __init__(self, master, book, update_callback, rated_books):
        self.master = master
        self.update_callback = update_callback
        self.rated_books = rated_books

        self.dialog = tk.Toplevel(master, width=200)
        self.dialog.title("Rate New Book")

        self.book_label = tk.Label(self.dialog, text="Select a book:")
        self.book_label.pack(pady=(10, 0))

        self.entry = tk.Entry(self.dialog)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<KeyRelease>", self.update_listbox)

        self.book_listbox = tk.Listbox(
            self.dialog, selectmode=tk.SINGLE, width=75)
        self.book_listbox.pack(pady=(0, 10), padx=10,
                               fill=tk.BOTH, expand=True)

        for x in range(0, len(booksDB)):
            self.book_listbox.insert(
                tk.END, booksDB["title"][x])

        self.rating_label = tk.Label(
            self.dialog, text="Enter the rating (0 - 5):")
        self.rating_label.pack()

        self.rating_entry = tk.Entry(self.dialog, width=10)
        self.rating_entry.pack(pady=(0, 10))

        self.submit_button = tk.Button(
            self.dialog, text="Submit", command=self.submit)
        self.submit_button.pack()

    def update_listbox(self, event=None):
        search_query = self.entry.get().lower()
        self.book_listbox.delete(0, tk.END)

        for x in range(0, len(booksDB["title"])):
            if search_query in booksDB["title"][x].lower():
                self.book_listbox.insert(tk.END, booksDB["title"][x])

    def submit(self):
        selected_book = self.book_listbox.get(self.book_listbox.curselection())
        image_url = booksDB.loc[booksDB['title'] ==
                                selected_book]['small_image_url'].item()
        rating = self.rating_entry.get()

        try:
            rating = float(rating)
            if 0.0 <= rating <= 5.0:
                self.rated_books[selected_book] = {
                    "rating": rating,
                    "image_url": image_url
                }
                self.update_callback()
                self.dialog.destroy()

                bookID = booksDB.loc[booksDB['title']
                                     == selected_book]['id2'].item()

                tempDf = pd.DataFrame({
                    'book_id': [bookID],
                    'user_id': [userID],
                    'rating': [int(rating)]
                })

                tempDf.to_csv('DataBase/ratings.csv', mode='a',
                              header=False, index=False)

            else:
                messagebox.showerror(
                    "Error", "Rating should be between 0.0 and 5.0")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid rating value.")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookRatingApp(root)
    root.mainloop()
