# twitter-analysis-app

This is a standalone and serverless app, that helps you find people around you that migth be interested in your content. It uses NLP to compare your content with your follower's followers and provides a similarity score between 0 and 1. It builds a sqlite database, so you can connect it to your favorite Data Visualization tool.

Setup instructions:

1. Clone this repo to your computer.
2. Create a virtual environment using your favorite tool (Conda, Virtualenv...)
3. Within the environment, and from the root folder of the project, install the requirements by doing:

   ```
   pip install -r requirements.txt
   ```

4. Within the main folder of the project, create a file named _.env_ and add to it the variables

5. Run the app.py in your terminal with:

   ```
   python ./src/app.py
   ```

6. Follow the instructions. You'll have to input your Twitter API keys and the Username you want to config for the app. That information will be stored locally in a _.env_ file within the main folder of the project.

   \* If you prefer to create the _.env_ file by yourself, the required variables are: CONSUMER_KEY, CONSUMER_SECRET_KEY (those are your Twitter API Keys), USER_SCREEN_NAME (this is the screen name of the main user account), and PYTHONWARNINGS, that you can set to "ignore" for production, or check the available options [here](https://docs.python.org/3/library/warnings.html).

   \*\* If you can't run the file, try granting execution permissions:

   ```
   chmod +x <filename>
   ```
