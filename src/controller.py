import asyncio
from concurrent.futures import ProcessPoolExecutor


async def scrape_videos_by_search(tiktok_scraper, keyword, db_manager):
    videos_data = await tiktok_scraper.scrape_tiktok_search(keyword)
    print(f"Number of videos scraped for '{keyword}': {len(videos_data)}")
    db_manager.bulk_insert_video_data(videos_data)


async def scrape_videos_by_hashtag(tiktok_scraper, hashtag, db_manager):
    videos_data = await tiktok_scraper.scrape_tiktok_hashtag(hashtag)
    print(f"Number of videos scraped for '{hashtag}': {len(videos_data)}")
    db_manager.bulk_insert_video_data(videos_data)


async def scrape_user(tiktok_scraper, user, db_manager):
    user_data = await tiktok_scraper.scrape_tiktok_user(username=user)
    db_manager.add_user(user_data)


def run_scraping_task(scraping_func, *args):
    asyncio.run(scraping_func(*args))


def run_concurrent_scraping(
    scraping_func, items, tiktok_scraper, db_manager, num_workers=4
):
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(
                run_scraping_task, scraping_func, tiktok_scraper, item, db_manager
            )
            for item in items
        ]
        for future in futures:
            future.result()  # Block until the future is done
