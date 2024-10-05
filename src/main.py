import asyncio
import os
from dotenv import load_dotenv

from analyzer import UserDataAnalysis
from loader import DatabaseManager
from scraper import TikTokScraper, USER_AGENTS


# Load environment variables from the .env file
load_dotenv(".env", override=True)


async def main():
    # Initialize the database manager and TikTok scraper
    db_manager = DatabaseManager(db_url=os.getenv("DB_URL"))
    tiktok_scraper = TikTokScraper(user_agent=USER_AGENTS[0])

    # List of keywords to scrape from TikTok
    keywords = [
        "beautiful destinations",
        "places to visit",
        "places to travel",
        "places that don't feel real",
        "travel hacks",
    ]

    # Scrape videos for each keyword and save to database
    for keyword in keywords:
        videos_data = await tiktok_scraper.scrape_tiktok_search(keyword)
        print(f"Number of videos scraped for '{keyword}': {len(videos_data)}")
        db_manager.bulk_insert_video_data(videos_data)

    # List of hashtags to scrape from TikTok
    hashtags = [
        "#traveltok",
        "#wanderlust",
        "#backpackingadventures",
        "#luxurytravel",
        "#hiddengems",
        "#solotravel",
        "#roadtripvibes",
        "#travelhacks",
        "#foodietravel",
        "#sustainabletravel",
    ]

    # Scrape videos for each hashtag and save to database
    for hashtag in hashtags:
        videos_data = await tiktok_scraper.scrape_tiktok_hashtag(hashtag)
        print(f"Number of videos scraped for '{hashtag}': {len(videos_data)}")
        db_manager.bulk_insert_video_data(videos_data)

    users = db_manager.get_all_users()
    print(users)
    for user in users:
        user_data = await tiktok_scraper.scrape_tiktok_user(username=user)
        db_manager.add_user(user_data)

    # Export data to JSON file
    db_manager.export_to_json("tiktok_data.json")

    # Analyze the data
    analyzer = UserDataAnalysis(db_manager.engine)
    analyzer.display_top_influencers()


if __name__ == "__main__":
    asyncio.run(main())
