CREATE TABLE account_timeline (
        tweet_id INTEGER NOT NULL, 
        user_id INTEGER, 
        created_at DATETIME, 
        full_text VARCHAR(300), 
        hashtags VARCHAR(300), 
        truncated INTEGER, 
        display_text_range VARCHAR(100), 
        retweet_count INTEGER, 
        favorite_count INTEGER, 
        PRIMARY KEY (tweet_id)
);
CREATE TABLE tokens_count (
        id INTEGER NOT NULL, 
        token VARCHAR(300), 
        cumulated_count INTEGER, 
        is_hashtag BOOLEAN, 
        last_updated DATETIME, 
        PRIMARY KEY (id), 
        CHECK (is_hashtag IN (0, 1))
);
CREATE TABLE users (
        id INTEGER NOT NULL, 
        screen_name VARCHAR(200), 
        location VARCHAR(200), 
        protected BOOLEAN, 
        followers_count INTEGER, 
        friends_count INTEGER, 
        created_at DATETIME, 
        favourites_count INTEGER, 
        statuses_count INTEGER, 
        default_profile_image BOOLEAN, 
        is_follower BOOLEAN, 
        is_friend BOOLEAN, 
        last_status DATETIME, 
        reviewed BOOLEAN, 
        similarity_score FLOAT, 
        PRIMARY KEY (id), 
        CHECK (protected IN (0, 1)), 
        CHECK (default_profile_image IN (0, 1)), 
        CHECK (is_follower IN (0, 1)), 
        CHECK (is_friend IN (0, 1)), 
        CHECK (reviewed IN (0, 1))
);
CREATE TABLE tweets (
        tweet_id INTEGER NOT NULL, 
        user_id INTEGER, 
        created_at DATETIME, 
        full_text VARCHAR(300), 
        hashtags VARCHAR(300), 
        truncated INTEGER, 
        display_text_range VARCHAR(100), 
        retweet_count INTEGER, 
        favorite_count INTEGER, 
        similarity_score FLOAT, 
        PRIMARY KEY (tweet_id), 
        FOREIGN KEY(user_id) REFERENCES users (id)
);