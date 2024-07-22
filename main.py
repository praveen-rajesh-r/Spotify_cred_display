import spotipy
from spotipy.oauth2 import SpotifyOAuth
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import requests
from io import BytesIO

# Replace these with your Spotify API credentials
SPOTIPY_CLIENT_ID = 'SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'SPOTIPY_REDIRECT_URI'

scope = "user-read-currently-playing"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

class SpotifyWidget:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry('300x300+10+10')  # Adjusted to a square for album art
        self.root.attributes('-topmost', True)

        self.canvas = tk.Canvas(root, width=300, height=300, highlightthickness=0)
        self.canvas.pack()

        self.text = tk.Text(root, font=('Helvetica', 12), wrap='word', bg='white', fg='black', borderwidth=0, highlightthickness=0)
        self.text.place(relx=0.5, rely=0.9, anchor=tk.CENTER, width=280, height=60)  # Set width and height to fit text
        self.text.configure(state='disabled')

        self.update_track()

        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.do_move)

    def update_track(self):
        try:
            current_track = sp.currently_playing()
            if current_track is not None and current_track['is_playing']:
                track = current_track['item']
                artist_name = track['artists'][0]['name']
                track_name = track['name']
                album_cover_url = track['album']['images'][0]['url']

                display_text = f"{artist_name} - {track_name}"
                self.text.configure(state='normal')
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, display_text)
                self.text.configure(state='disabled')
                self.update_background(album_cover_url)
            else:
                self.text.configure(state='normal')
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, "No song currently playing")
                self.text.configure(state='disabled')
                self.canvas.delete("bg_img")

        except Exception as e:
            self.text.configure(state='normal')
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, f"Error: {str(e)}")
            self.text.configure(state='disabled')
            self.canvas.delete("bg_img")

        self.root.after(1000, self.update_track)  # Update every 10 seconds

    def update_background(self, image_url):
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))

        img = img.resize((300, 300), Image.ANTIALIAS)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.4)  # Make the image 40% transparent

        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image, tags="bg_img")

    def start_move(self, event):
        self.startX = event.x
        self.startY = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.startX
        y = self.root.winfo_y() + event.y - self.startY
        self.root.geometry(f'+{x}+{y}')

def run_app():
    root = tk.Tk()
    app = SpotifyWidget(root)
    root.mainloop()

if __name__ == '__main__':
    run_app()
