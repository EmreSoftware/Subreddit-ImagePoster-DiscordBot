# Subreddit Image Poster Discord Bot
This bot fetches the top images from a specified subreddit and posts them to a designated Discord channel at regular intervals.
Bot expects it to be daily top posts

## Bot Behavior
The bot is designed to fetch the daily top posts from Reddit.

## How it works?
The bot uses PRAW for Reddit interaction and discord.py for Discord integration. Here’s a breakdown of its functionality:

Scheduled Fetching:
- The bot runs every 25 hours, ensuring daily updates while avoiding exact repetition times.

Image Handling:
- Downloads images from Reddit to your local machine.
- Uploads these images to the designated Discord channel.
- Deletes all downloaded media immediately after uploading (or attempting to upload).
- This ensures you avoid broken links due to deleted posts while also saving storage space.

Post Information:
- Each upload includes the original post URL and the author’s username.
- If the file size exceeds Discord’s upload limit, the image is sent as an embedded link instead.

Duplicate Prevention:
- Image links are stored in a file, and the bot checks against this list before sending.
- This ensures no duplicate images are posted.

## Contributing
Feel free to improve the code!

I’m not great at Python and didn’t invest much time polishing this project. If it worked, I left it as is—so contributions are more than welcome!
