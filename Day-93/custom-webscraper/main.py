#!/usr/bin/env python3
"""
recipe_scraper.py — Scrape recipes into a CSV using a real, visible browser.

This uses Selenium to drive an actual Chrome window: it opens, navigates to
each page, waits for it to load, and you can watch it happen. That's
different from a plain HTTP-request scraper, which fetches page content
invisibly in the background with no window at all.

Once a page is loaded, the actual data extraction still reads the
schema.org "Recipe" structured data that almost every recipe site embeds
as JSON-LD for Google's rich-snippet search results — that's far more
reliable than scraping a site's CSS classes, which break on every redesign.

Requirements:
    pip install selenium beautifulsoup4
    Google Chrome must be installed on your machine.
    (Selenium 4.6+ automatically downloads the matching chromedriver —
     no separate driver install needed.)

Usage:
    # Scrape a single recipe page (a Chrome window will open and navigate to it)
    python recipe_scraper.py --url https://www.allrecipes.com/recipe/12345/example/

    # Scrape every recipe linked from a category/search page
    python recipe_scraper.py --listing https://www.allrecipes.com/recipes/96/salad/ --max 10

    # Scrape a list of URLs from a text file (one URL per line)
    python recipe_scraper.py --urls-file recipe_urls.txt -o recipes.csv

    # Run without a visible window (background mode, like the old approach)
    python recipe_scraper.py --url ... --headless
"""

import argparse
import csv
import json
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

USER_AGENT = "Mozilla/5.0 (compatible; RecipeResearchBot/1.0; +https://example.com/bot)"
PAGE_LOAD_TIMEOUT = 15

CSV_FIELDS = [
    "name", "url", "author", "rating_value", "rating_count",
    "prep_time_min", "cook_time_min", "total_time_min", "servings",
    "category", "cuisine", "calories",
    "ingredients", "instructions", "image_url",
]


# ----------------------------------------------------------------------
# Browser setup
# ----------------------------------------------------------------------

def build_driver(headless=False):
    """Launch Chrome. By default this opens a real, visible window so you
    can watch the scraper navigate — pass headless=True to run it silently
    in the background instead."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--window-size=1280,900")
    # Reduces Chrome's "automation" banner/quirks without hiding anything
    # about what the browser is doing.
    options.add_argument("--disable-blink-features=AutomationControlled")

    try:
        # Selenium 4.6+ auto-downloads the matching chromedriver — no
        # separate driver install needed, as long as Chrome itself is installed.
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        sys.exit(
            "Couldn't start Chrome. Make sure Google Chrome is installed "
            f"on this machine.\n\nOriginal error: {e}"
        )

    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def fetch_html(driver, url, settle_seconds=1.5):
    """Navigate to a URL in the real browser window and return the
    rendered page source once it's loaded."""
    driver.get(url)

    try:
        WebDriverWait(driver, PAGE_LOAD_TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        pass  # proceed with whatever loaded — many sites never hit "complete" cleanly

    # A small scroll + pause: gives lazy-loaded content a chance to appear,
    # and lets you actually see the page before it moves to the next one.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
    time.sleep(settle_seconds)

    return driver.page_source


# ----------------------------------------------------------------------
# Politeness: robots.txt
# ----------------------------------------------------------------------

def is_allowed_by_robots(url, user_agent=USER_AGENT):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True  # if robots.txt can't be read, don't block on that alone


# ----------------------------------------------------------------------
# ISO 8601 duration parsing (schema.org uses "PT30M", "PT1H15M", etc.)
# ----------------------------------------------------------------------

def iso8601_duration_to_minutes(duration):
    if not duration or not isinstance(duration, str):
        return None
    match = re.match(r"P(?:T(?:(\d+)H)?(?:(\d+)M)?)?", duration)
    if not match:
        return None
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    total = hours * 60 + minutes
    return total if total > 0 else None


# ----------------------------------------------------------------------
# Flattening messy schema.org shapes into plain strings/lists
# ----------------------------------------------------------------------

def flatten_instructions(value):
    """recipeInstructions can be a string, a list of strings, a list of
    HowToStep dicts, or a list of HowToSection dicts containing steps."""
    steps = []

    def walk(node):
        if node is None:
            return
        if isinstance(node, str):
            for line in re.split(r"\n+", node):
                line = line.strip()
                if line:
                    steps.append(line)
        elif isinstance(node, dict):
            node_type = node.get("@type", "")
            if node_type == "HowToSection":
                for item in node.get("itemListElement", []):
                    walk(item)
            else:
                text = node.get("text") or node.get("name")
                if text:
                    steps.append(text.strip())
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return steps


def flatten_ingredients(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value.strip()]
    return []


def get_calories(nutrition):
    if not isinstance(nutrition, dict):
        return None
    calories = nutrition.get("calories")
    if not calories:
        return None
    match = re.search(r"[\d.]+", str(calories))
    return match.group(0) if match else str(calories).strip()


def first_of(value):
    if isinstance(value, list) and value:
        value = value[0]
    if isinstance(value, dict):
        return value.get("name", "")
    if isinstance(value, str):
        return value
    return ""


# ----------------------------------------------------------------------
# Finding and parsing the Recipe JSON-LD block
# ----------------------------------------------------------------------

def find_recipe_jsonld(soup):
    def as_recipe(node):
        if isinstance(node, dict):
            node_type = node.get("@type")
            types = node_type if isinstance(node_type, list) else [node_type]
            if "Recipe" in types:
                return node
        return None

    for tag in soup.find_all("script", type="application/ld+json"):
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
        except json.JSONDecodeError:
            continue

        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            recipe = as_recipe(candidate)
            if recipe:
                return recipe
            if isinstance(candidate, dict) and "@graph" in candidate:
                for node in candidate["@graph"]:
                    recipe = as_recipe(node)
                    if recipe:
                        return recipe
    return None


def extract_recipe(html, url):
    soup = BeautifulSoup(html, "html.parser")
    recipe = find_recipe_jsonld(soup)
    if recipe is None:
        return None

    rating = recipe.get("aggregateRating") or {}
    nutrition = recipe.get("nutrition") or {}
    image = recipe.get("image")
    if isinstance(image, list) and image:
        image = image[0]
    if isinstance(image, dict):
        image = image.get("url", "")

    return {
        "name": (recipe.get("name") or "").strip(),
        "url": url,
        "author": first_of(recipe.get("author")),
        "rating_value": rating.get("ratingValue", ""),
        "rating_count": rating.get("ratingCount", rating.get("reviewCount", "")),
        "prep_time_min": iso8601_duration_to_minutes(recipe.get("prepTime")) or "",
        "cook_time_min": iso8601_duration_to_minutes(recipe.get("cookTime")) or "",
        "total_time_min": iso8601_duration_to_minutes(recipe.get("totalTime")) or "",
        "servings": recipe.get("recipeYield", ""),
        "category": first_of(recipe.get("recipeCategory")),
        "cuisine": first_of(recipe.get("recipeCuisine")),
        "calories": get_calories(nutrition) or "",
        "ingredients": " | ".join(flatten_ingredients(recipe.get("recipeIngredient"))),
        "instructions": " | ".join(flatten_instructions(recipe.get("recipeInstructions"))),
        "image_url": image or "",
    }


# ----------------------------------------------------------------------
# Discovering recipe links from a listing/category/search page
# ----------------------------------------------------------------------

def discover_recipe_links(html, base_url, link_pattern=r"/recipe/\d+/"):
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(link_pattern)

    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if pattern.search(href):
            full_url = urljoin(base_url, href)
            # Strip query string/fragment so print/tracking variants of the
            # same recipe collapse to one canonical URL.
            parsed = urlparse(full_url)
            canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.add(canonical)
    return sorted(links)


# ----------------------------------------------------------------------
# Smart URL resolution: figure out if a page IS a recipe, or LINKS to some
# ----------------------------------------------------------------------

def resolve_recipe_urls(driver, start_url, max_recipes, link_pattern):
    """Given any URL — a single recipe, a category page, or even a
    homepage — figure out what to scrape:
      - If the page itself is a recipe, scrape just that one.
      - Otherwise, look for recipe links on the page and scrape up to
        max_recipes of them automatically.
    Returns (urls_to_scrape, cache) where cache holds any recipe data we
    already parsed while checking, so we don't fetch that page twice.
    """
    print(f"Opening {start_url} ...")
    html = fetch_html(driver, start_url)

    recipe = extract_recipe(html, start_url)
    if recipe is not None:
        print(f"This page is itself a recipe: {recipe['name']!r}")
        return [start_url], {start_url: recipe}

    print("This isn't a single recipe page — looking for recipe links on it...")
    links = discover_recipe_links(html, start_url, link_pattern)

    if not links and link_pattern != r"/recipe/":
        # The site's URL shape might not match the default pattern (e.g. no
        # numeric ID in the path) — retry with a looser fallback before giving up.
        links = discover_recipe_links(html, start_url, r"/recipe/")

    if not links:
        print(
            "No recipe links found on this page. Try pointing --url at a "
            "category or search page instead of a homepage, or pass "
            "--link-pattern if this site uses a different URL structure."
        )
        return [], {}

    chosen = links[:max_recipes]
    print(f"Found {len(links)} recipe link(s) on this page — scraping {len(chosen)} of them.")
    return chosen, {}


# ----------------------------------------------------------------------
# Main scraping loop
# ----------------------------------------------------------------------

def scrape_urls(driver, urls, output_path, delay, cached_recipes=None):
    cached_recipes = cached_recipes or {}
    rows = []

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] {url}")

        if url in cached_recipes:
            recipe = cached_recipes[url]
            rows.append(recipe)
            print(f"  found: {recipe['name']!r}  (already loaded)")
            continue

        if not is_allowed_by_robots(url):
            print("  skipped: disallowed by robots.txt")
            continue

        try:
            html = fetch_html(driver, url)
        except WebDriverException as e:
            print(f"  skipped: browser navigation failed ({e})")
            continue

        recipe = extract_recipe(html, url)
        if recipe is None:
            print("  skipped: no schema.org Recipe data found on this page")
            continue

        rows.append(recipe)
        print(f"  found: {recipe['name']!r}")

        if i < len(urls):
            time.sleep(delay)

    if not rows:
        print("\nNo recipes were scraped — nothing to write.")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} recipe(s) to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape recipes into a CSV using a real (visible, by default) browser.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--url",
        help="Any page: a single recipe, a category page, or a homepage. "
             "If it's not itself a recipe, recipe links found on it are scraped automatically."
    )
    parser.add_argument("--listing", help="Same as --url, but always treated as a page to find links on")
    parser.add_argument("--urls-file", help="A text file of already-known recipe URLs, one per line")
    parser.add_argument(
        "--link-pattern", default=r"/recipe/\d+/",
        help=r"Regex to identify recipe links (default: /recipe/\d+/, AllRecipes' URL shape)"
    )
    parser.add_argument("--max", type=int, default=10, help="Max recipes to auto-scrape from a page (default: 10)")
    parser.add_argument("-o", "--output", default="recipes.csv", help="Output CSV path (default: recipes.csv)")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds to wait between page visits (default: 2.0)")
    parser.add_argument("--headless", action="store_true", help="Run without a visible browser window")
    parser.add_argument("--keep-open", action="store_true", help="Leave the browser window open when finished")
    args = parser.parse_args()

    if not args.url and not args.listing and not args.urls_file:
        parser.error("provide --url, --listing, and/or --urls-file")

    urls = []
    cached_recipes = {}

    if args.urls_file:
        with open(args.urls_file, encoding="utf-8") as f:
            urls.extend(line.strip() for line in f if line.strip())

    driver = build_driver(headless=args.headless)
    try:
        for start_url in filter(None, [args.url, args.listing]):
            if not is_allowed_by_robots(start_url):
                print(f"Skipping {start_url}: disallowed by robots.txt")
                continue

            found_urls, found_cache = resolve_recipe_urls(
                driver, start_url, args.max, args.link_pattern
            )
            urls.extend(found_urls)
            cached_recipes.update(found_cache)

        if not urls:
            print("No recipe URLs to scrape.")
            return

        scrape_urls(driver, urls, args.output, args.delay, cached_recipes)

    finally:
        if args.keep_open:
            input("\nPress Enter to close the browser window...")
        driver.quit()


if __name__ == "__main__":
    main()