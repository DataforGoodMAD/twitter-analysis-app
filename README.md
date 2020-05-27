# twitter-analysis-app

Setup instructions:

1. Clone this repo to your computer.
2. Create a virtual environment using your favorite tool (Conda, Virtualenv...)
3. Within the environment, and from the root folder of the project, install the requirements by doing:
    ```
    pip install -r requirements.txt
    ```

4. Within the main folder of the project, create a file named *.env* and add to it the variables CONSUMER_KEY and CONSUMER_SECRET_KEY (those are your Twitter API Keys), and USER_SCREEN_NAME (this is the screen name of the main user account). 

5. Run the db_models.py to create the database:
    ```
    python ./src/db_models.py
    ```
6. Run the app.py file to fill the database with the main user timeline, tokens and followers.
    ```
    python ./src/app.py
    ```

    ** If you can't run any of the files, try granting execution permissions:
    ```
    chmod +x <filename>
    ``` 
