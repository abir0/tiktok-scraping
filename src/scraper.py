import random
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


# List of user agents for UA rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
]


# Utility functions
def parse_int(text: str) -> int:
    """Parse numeric texts and return integers."""
    text = text.strip().upper()
    if "K" in text:
        return int(float(text.replace("K", "")) * 1_000)
    elif "M" in text:
        return int(float(text.replace("M", "")) * 1_000_000)
    else:
        return int(text)


def extract_username(text: str) -> str | None:
    """Extract username from text or url."""
    pattern = r"(?<=/@)[\w._]+"
    match = re.search(pattern, text)
    return match.group(0) if match else None


# Base scraper class to handle browser operations
class Scraper:
    def __init__(self, user_agent=None):
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.browser = None
        self.page = None

    async def initialize_browser(self):
        """Initialize the browser and open a new page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        context = await self.browser.new_context(user_agent=self.user_agent)
        self.page = await context.new_page()
        await self.page.wait_for_timeout(1000)  # Wait for the page to settle

    async def close_browser(self):
        """Close the browser and release resources."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

    async def scroll_down(self, scrolls=10, min_distance=600, max_distance=1000):
        """Scroll down the page a specified number of times."""
        for _ in range(scrolls):
            scroll_distance = random.randint(min_distance, max_distance)
            await self.page.evaluate(
                f'window.scrollBy({{top: {scroll_distance}, behavior: "smooth"}});'
            )
            await self.page.wait_for_timeout(random.randint(3000, 4000))


# TikTokScraper class for specific TikTok scraping operations
class TikTokScraper(Scraper):
    def __init__(self, user_agent=None):
        super().__init__(user_agent)
        self.base_url = "https://www.tiktok.com"

    async def scrape_tiktok_search(self, keyword):
        """Scrape TikTok videos based on a search keyword."""
        await self.initialize_browser()
        await self.page.goto(self.base_url)
        await self.page.wait_for_timeout(10000)  # Allow time for the page to load

        # Locate the search bar and perform a search
        search_bar = self.page.locator("input[name='q']")
        await search_bar.click()
        await search_bar.fill(keyword)
        await search_bar.press("Enter")
        await self.page.wait_for_timeout(10000)  # Wait for search results

        # Use the scroll_down method to load more videos
        await self.scroll_down()

        html_content = await self.page.content()
        await self.close_browser()  # Close the browser

        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        pattern = re.compile(r".*-DivItemContainerForSearch")
        posts = soup.find_all("div", class_=pattern)

        video_data = []
        for post in posts:
            try:
                video_url = post.find("a").get("href")
                caption_pattern = re.compile(r"css-.*-SpanText")
                video_caption = post.find("span", class_=caption_pattern).get_text()
                author_username = post.find(
                    "a", attrs={"data-e2e": "search-card-user-link"}
                ).get("href")
                video_data.append(
                    {
                        "video_url": video_url,
                        "video_caption": video_caption,
                        "author_username": extract_username(author_username),
                    }
                )
            except Exception as e:
                print(f"Error during scraping: {e}")

        return video_data

    async def scrape_tiktok_hashtag(self, hashtag):
        """Scrape TikTok videos associated with a specific hashtag."""
        await self.initialize_browser()
        await self.page.goto(f"{self.base_url}/tag/{hashtag.replace("#","")}")
        await self.page.wait_for_timeout(10000)  # Wait for hashtag page to load
        await self.page.wait_for_load_state("networkidle")

        # Use the scroll_down method to load more videos
        await self.scroll_down()

        html_content = await self.page.content()
        await self.close_browser()

        # Parse HTML content for videos
        soup = BeautifulSoup(html_content, "html.parser")
        pattern = re.compile(r"css-.*-DivItemContainerV2")
        posts = soup.find_all("div", class_=pattern)

        video_data = []
        for post in posts:
            try:
                video_url = post.find("a").get("href")
                caption_pattern = re.compile(r"css-.*-SpanText")
                video_caption = post.find("span", class_=caption_pattern).get_text()
                author_username = post.find(
                    "a", attrs={"data-e2e": "challenge-item-avatar"}
                ).get("href")
                video_data.append(
                    {
                        "video_url": video_url,
                        "video_caption": video_caption,
                        "author_username": extract_username(author_username),
                    }
                )
            except Exception as e:
                print(f"Error during scraping: {e}")

        return video_data

    async def scrape_tiktok_user(self, username):
        """Scrape user data from a TikTok user profile."""
        await self.initialize_browser()
        await self.page.goto(f"{self.base_url}/@{username}")
        await self.page.wait_for_timeout(10000)  # Wait for profile page to load
        await self.page.wait_for_load_state("networkidle")

        html_content = await self.page.content()
        await self.close_browser()

        # Parse user statistics from the profile page
        soup = BeautifulSoup(html_content, "html.parser")
        following_count = soup.find(
            "strong", attrs={"data-e2e": "following-count"}
        ).get_text(strip=True)
        followers_count = soup.find(
            "strong", attrs={"data-e2e": "followers-count"}
        ).get_text(strip=True)
        likes_count = soup.find("strong", attrs={"data-e2e": "likes-count"}).get_text(
            strip=True
        )

        return {
            "username": username,
            "following_count": parse_int(following_count),
            "followers_count": parse_int(followers_count),
            "likes_count": parse_int(likes_count),
        }
