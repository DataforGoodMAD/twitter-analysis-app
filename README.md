# twitter-analysis-app

This is a standalone and serverless app, that helps you find people around you that migth be interested in your content. It uses NLP to compare your content with your follower's followers and provides a similarity score between 0 and 1. It builds a sqlite database, so you can connect it to your favorite Data Visualization tool.

__Python__: This repository has been tested only for Python 3.7.x.

Setup instructions:

1. Clone this repo to your computer.
2. Create a virtual environment using your favorite tool (Poetry, Conda, Virtualenv...). The easies way to do this is by doing:

   ```
   python -m venv env
   source env/bin/activate
   ```

3. Within the environment, and from the root folder of the project, install the requirements by doing:

   ```
   pip install -r requirements.txt
   ```

4. Download the data for NLTK with:
   ```
   python -m nltk.downloader wordnet stopwords
   ```

5. Run the app.py in your terminal with:

   ```
   python ./app.py
   ```

   The first time you run the app, you'll have to input your Twitter API keys and the Username you want to config for the app. That information will be stored locally in a _.env_ file within the main folder of the project.

   \* If you prefer to create the _.env_ file by yourself, the required variables are: CONSUMER_KEY, CONSUMER_SECRET_KEY (those are your Twitter API Keys), and USER_SCREEN_NAME (this is the screen name of the main user account).

   \*\* If you can't run the file, try granting execution permissions:

   ```
   chmod +x <filename>
   ```

6. To build a standalone executable file, you can use PyInstaller (the required version is already included in the `requirements.txt`). You can do it with:

   ```
   pyinstaller --onefile -c -n twitter_influence --additional-hooks-dir pyinstaller-hooks./app.py
   ```
