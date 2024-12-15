import discord
from discord.ext import commands, tasks
import praw
import requests
import os
import json
from io import BytesIO
import atexit  # To ensure the file is saved when the bot exits

# Load configuration from JSON file
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
REDDIT_CLIENT_ID = config['reddit_client_id']
REDDIT_CLIENT_SECRET = config['reddit_client_secret']
REDDIT_USER_AGENT = config['reddit_user_agent']

# Initialize PRAW
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

# Initialize Discord Bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

# File to store sent image URLs
SENT_IMAGES_FILE = 'sent_images.txt'
DOWNLOAD_FOLDER = 'downloaded_images'
your_channel_id = 1317847595565191248

# Ensure the download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Helper function to load sent image URLs from the file
def load_sent_images():
    try:
        with open(SENT_IMAGES_FILE, 'r') as file:
            sent_images = set(file.read().splitlines())  # Read and return as a set of URLs
            print(f"Loaded {len(sent_images)} sent image URLs.")  # Log number of loaded URLs
            return sent_images
    except FileNotFoundError:
        print("No previous sent images file found. Starting fresh.")
        return set()  # Return an empty set if the file doesn't exist

# Helper function to save sent image URLs to the file
def save_sent_images(sent_images):
    try:
        with open(SENT_IMAGES_FILE, 'w') as file:
            file.write("\n".join(sent_images))
        print(f"Saved {len(sent_images)} sent image URLs.")  # Log saving process
    except Exception as e:
        print(f"Error saving sent images: {e}")

# Function to fetch and send images from a subreddit
async def fetch_and_send_images(subreddit_name: str):
    """Fetch and send images from a subreddit."""
    print(f"Fetching top posts from r/{subreddit_name}")  # Debugging

    try:
        # Load already sent image URLs from the file
        sent_images = load_sent_images()
        print(f"Loaded {len(sent_images)} previously sent image URLs.")  # Log how many URLs were loaded

        # Fetch subreddit and posts
        subreddit = reddit.subreddit(subreddit_name)

        posts = []

        # Fetch the top posts in the last 24 hours and filter for images
        for submission in subreddit.top(time_filter="day", limit=100):  # Increased limit to 100 to fetch more posts
            if submission.url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.webp')) and not submission.is_self:
                posts.append(submission)

        # Now send up to 50 unique images, skipping already sent ones
        sent_count = 0
        for post in posts:
            if post.url not in sent_images and sent_count < 50:  # Allow up to 50 images
                # Download the image
                image_data = requests.get(post.url).content

                # Save the image to the disk in the DOWNLOAD_FOLDER
                image_name = os.path.basename(post.url)  # Use the image filename from URL
                image_path = os.path.join(DOWNLOAD_FOLDER, image_name)

                with open(image_path, 'wb') as f:
                    f.write(image_data)

                # Create an embed with the image and other details
                embed = discord.Embed(
                    title=post.title,
                    description=f"**Author:** u/{post.author.name}",
                    url=post.url,
                    color=discord.Color.pink()
                )

                # Send the embed and image to Discord
                with open(image_path, 'rb') as f:
                    await client.get_channel(your_channel_id).send(
                        embed=embed,
                        file=discord.File(f, image_name)
                    )  # Replace with your channel ID

                # Mark this image as sent
                print(f"Marking image as sent: {post.url}")  # Debugging
                sent_images.add(post.url)
                sent_count += 1

                # Save the sent URLs frequently
                save_sent_images(sent_images)

                # Delete the local image after sending it
                os.remove(image_path)

        if sent_count < 50:
            await client.get_channel(your_channel_id).send(f"Found less than 50 unique image posts in r/{subreddit_name}.")

    except Exception as e:
        print(f"An error occurred: {e}")
        await client.get_channel(your_channel_id).send("An error occurred while fetching the posts.")

# Registering exit function to ensure saving happens when the bot is stopped
atexit.register(lambda: save_sent_images(load_sent_images()))

# Background task to run every 25 hours
@tasks.loop(hours=25)
async def auto_fetch_images():
    """Automatically fetch and send images every 25 hours."""
    await fetch_and_send_images('pics')  # Replace with your subreddit name

# Start the task when the bot is ready
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    auto_fetch_images.start()  # Start the auto-fetching task

client.run(TOKEN)