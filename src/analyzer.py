import pandas as pd


class UserDataAnalysis:
    def __init__(self, db_engine):
        self.engine = db_engine

    def fetch_data(self):
        query = "SELECT * FROM users;"
        return pd.read_sql(query, self.engine)

    def analyze_top_influencers(self, df):
        top_influencers = df[
            (df["followers_count"] >= 100000) & (df["likes_count"] >= 1000000)
        ]
        return top_influencers

    def display_top_influencers(self):
        user_data = self.fetch_data()
        top_influencers = self.analyze_top_influencers(user_data)
        if not top_influencers.empty:
            print("Top Influencers:")
            print(top_influencers[["username", "followers_count", "likes_count"]])
        else:
            print("No influencers found meeting the criteria.")
