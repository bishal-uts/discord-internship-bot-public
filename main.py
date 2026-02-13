import os
import json
import requests
import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import random
from dotenv import load_dotenv

load_dotenv()

# Bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

JOB_CACHE_FILE = "seen_jobs.json"
KEYWORDS = ["intern", "internship", "graduate", "grad program", "trainee", "entry level"]
REQUEST_TIMEOUT = 15  # 15 second timeout per request
MAX_SCRAPE_TIME = 45  # 45 seconds max per site

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

def load_seen_jobs():
    if os.path.exists(JOB_CACHE_FILE):
        with open(JOB_CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_jobs(seen_jobs):
    with open(JOB_CACHE_FILE, "w") as f:
        json.dump(list(seen_jobs), f)

def scrape_with_timeout(scraper_func, timeout=MAX_SCRAPE_TIME):
    """Execute scraper function with timeout protection"""
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(scraper_func)
    try:
        result = future.result(timeout=timeout)
        return result if result else []
    except (FuturesTimeoutError, Exception) as e:
        print(f"Scraper timeout or error: {type(e).__name__}")
        return []
    finally:
        executor.shutdown(wait=False)

def scrape_linkedin():
    """Scrape LinkedIn - kept for backwards compatibility"""
    try:
        jobs = []
        url = "https://www.linkedin.com/jobs/search/?keywords=intern&location=Australia&f_TPR=r86400"
        response = requests.get(url, headers=get_random_headers(), timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("div", class_="base-card", limit=3)
        
        for job in job_listings:
            try:
                title_elem = job.find("h3", class_="base-search-card__title")
                company_elem = job.find("h4", class_="base-search-card__subtitle")
                location_elem = job.find("span", class_="job-search-card__location")
                link_elem = job.find("a", class_="base-card__full-link")
                
                if title_elem and company_elem and link_elem:
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": location_elem.text.strip() if location_elem else "Australia",
                        "url": link_elem["href"],
                        "source": "LinkedIn"
                    })
            except:
                continue
        return jobs
    except:
        return []

def scrape_indeed():
    """Scrape Indeed Australia for internships"""
    try:
        jobs = []
        url = "https://au.indeed.com/jobs?q=internship&l=Australia&fromage=1"
        response = requests.get(url, headers=get_random_headers(), timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("div", class_="job_seen_beacon", limit=5)
        
        for job in job_listings:
            try:
                title_elem = job.find("h2", class_="jobTitle")
                company_elem = job.find("span", class_="companyName")
                location_elem = job.find("div", class_="companyLocation")
                
                if title_elem and company_elem:
                    job_link = title_elem.find("a")
                    if job_link and "href" in job_link.attrs:
                        jobs.append({
                            "title": title_elem.text.strip(),
                            "company": company_elem.text.strip(),
                            "location": location_elem.text.strip() if location_elem else "Australia",
                            "url": f"https://au.indeed.com{job_link['href']}",
                            "source": "Indeed"
                        })
            except:
                continue
        return jobs
    except:
        return []

def scrape_seek():
    """Scrape Seek Australia for internships"""
    try:
        jobs = []
        url = "https://www.seek.com.au/internship-jobs"
        response = requests.get(url, headers=get_random_headers(), timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("article", limit=5)
        
        for job in job_listings:
            try:
                title_elem = job.find("a", {"data-automation": "jobTitle"})
                company_elem = job.find("a", {"data-automation": "jobCompany"})
                location_elem = job.find("a", {"data-automation": "jobLocation"})
                
                if title_elem and company_elem:
                    job_url = title_elem.get("href", "")
                    if job_url.startswith("/"):
                        job_url = f"https://www.seek.com.au{job_url}"
                    
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": location_elem.text.strip() if location_elem else "Australia",
                        "url": job_url,
                        "source": "Seek"
                    })
            except:
                continue
        return jobs
    except:
        return []

def scrape_gradconnection():
    """Scrape GradConnection for internships"""
    try:
        jobs = []
        url = "https://au.gradconnection.com/internships/"
        response = requests.get(url, headers=get_random_headers(), timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("div", class_="result", limit=5)
        
        for job in job_listings:
            try:
                title_elem = job.find("h4")
                company_elem = job.find("p", class_="org")
                link_elem = job.find("a")
                
                if title_elem and company_elem and link_elem:
                    job_url = link_elem.get("href", "")
                    if job_url.startswith("/"):
                        job_url = f"https://au.gradconnection.com{job_url}"
                    
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": "Australia",
                        "url": job_url,
                        "source": "GradConnection"
                    })
            except:
                continue
        return jobs
    except:
        return []

def scrape_jora():
    """Scrape Jora Australia for internships"""
    try:
        jobs = []
        url = "https://au.jora.com/j?sp=homepage&q=internship&l=Australia"
        response = requests.get(url, headers=get_random_headers(), timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("div", class_="job-item", limit=5)
        
        for job in job_listings:
            try:
                title_elem = job.find("a", class_="job-title")
                company_elem = job.find("span", class_="job-company")
                location_elem = job.find("span", class_="job-location")
                
                if title_elem and company_elem:
                    job_url = title_elem.get("href", "")
                    if job_url.startswith("/"):
                        job_url = f"https://au.jora.com{job_url}"
                    
                    jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": location_elem.text.strip() if location_elem else "Australia",
                        "url": job_url,
                        "source": "Jora"
                    })
            except:
                continue
        return jobs
    except:
        return []

def fetch_new_internships():
    """Fetch from all sources with timeout protection"""
    seen_jobs = load_seen_jobs()
    new_jobs = []
    
    scrapers = [
        ("Indeed", scrape_indeed),
        ("Seek", scrape_seek),
        ("GradConnection", scrape_gradconnection),
        ("Jora", scrape_jora),
        ("LinkedIn", scrape_linkedin)
    ]
    
    for source_name, scraper in scrapers:
        print(f"Scraping {source_name}...")
        try:
            jobs = scrape_with_timeout(scraper)
            print(f"Found {len(jobs)} jobs from {source_name}")
            
            for job in jobs:
                job_id = f"{job['title']}_{job['company']}"
                if job_id not in seen_jobs:
                    new_jobs.append(job)
                    seen_jobs.add(job_id)
        except Exception as e:
            print(f"Error scraping {source_name}: {str(e)}")
            continue
    
    save_seen_jobs(seen_jobs)
    return new_jobs[:10]  # Return max 10 jobs

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Internship Bot is ready!")
    internship_watcher.start()

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="internjobs")
async def internjobs(ctx):
    """Manually fetch and post the latest internship opportunities"""
    await ctx.send("Searching for new internship opportunities...")
    jobs = fetch_new_internships()
    
    if not jobs:
        await ctx.send("No new jobs found at the moment. Try again later!")
        return
    
    for job in jobs[:5]:  # Limit to 5 posts
        embed = discord.Embed(
            title=f"🚀 New Internship: {job['title']}",
            url=job["url"],
            description=f"**Company:** {job['company']}\n**Location:** {job['location']}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Source: {job['source']}")
        await ctx.send(embed=embed)

@tasks.loop(hours=2)  # Check every 2 hours
async def internship_watcher():
    if CHANNEL_ID == 0:
        return
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return
    
    new_jobs = fetch_new_internships()
    for job in new_jobs:
        embed = discord.Embed(
            title=f"🎓 New Internship: {job['title']}",
            url=job["url"],
            description=f"**Company:** {job['company']}\n**Location:** {job['location']}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Source: {job['source']} | Auto-posted")
        await channel.send(embed=embed)
        time.sleep(2)  # Avoid rate limits

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set")
    else:
        bot.run(TOKEN)
