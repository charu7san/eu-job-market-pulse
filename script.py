import os
import json
import time
import requests
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

# Expanded from 7 → 14 EU/EEA countries with confirmed Adzuna coverage
COUNTRIES = {
    'at': 'Austria',
    'be': 'Belgium',
    'de': 'Germany',
    'dk': 'Denmark',
    'es': 'Spain',
    'fi': 'Finland',
    'fr': 'France',
    'ie': 'Ireland',
    'it': 'Italy',
    'nl': 'Netherlands',
    'no': 'Norway',
    'pl': 'Poland',
    'pt': 'Portugal',
    'se': 'Sweden',
}

# Adzuna category tag for IT/tech roles (applied to all country fetches)
BASE_CATEGORY = "it-jobs"
BASE_SEARCH = "software developer engineer data analyst"  # broad tech keyword net
SKILLS = [
    'Python', 'SQL', 'Power BI', 'Tableau', 'Spark',
    'dbt', 'Airflow', 'Looker', 'Snowflake', 'Excel',
    'Azure', 'AWS', 'React', 'TypeScript', 'Node.js',
    'Java', 'Docker', 'Kubernetes', 'Linux', 'Git', 'JavaScript'
]

# Eurostat country codes (ISO-2 uppercase)
EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "une_rt_m?format=JSON&geo={geo}&unit=PC_ACT&age=TOTAL&sex=T&lastTimePeriod=1"
)


def fetch_eurostat_unemployment(country_code: str) -> Optional[float]:
    """Fetch latest monthly unemployment rate for a country from Eurostat.
    Returns a float (e.g. 3.1) or None if unavailable."""
    geo = country_code.upper()
    try:
        resp = requests.get(EUROSTAT_URL.format(geo=geo), timeout=10)
        if resp.status_code != 200:
            return None
        payload = resp.json()
        # Values dict: keys are stringified indices, pick the last non-null
        values = payload.get("value", {})
        if not values:
            return None
        # Get the last value in the ordered dict
        last_val = list(values.values())[-1]
        return round(float(last_val), 1) if last_val is not None else None
    except Exception as e:
        print(f"  Eurostat fetch failed for {country_code}: {e}")
        return None


def fetch_data():
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set.")
        return

    data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "global_metrics": {
            "total_listings": 0,
            "avg_eu_salary": 0,
            "avg_salary_transparency_pct": 0,
        },
        "countries": [],
        "sources": [
            {
                "name": "Adzuna",
                "url": "https://www.adzuna.com/",
                "description": "Aggregated job market data and salary trends across Europe."
            },
            {
                "name": "Arbeitnow",
                "url": "https://www.arbeitnow.com/",
                "description": "Tech-focused job board with a focus on European and remote roles."
            },
            {
                "name": "Eurostat",
                "url": "https://ec.europa.eu/eurostat",
                "description": "Official EU statistical office — unemployment rates by country."
            }
        ]
    }

    total_listings = 0
    total_salary_sum = 0
    countries_with_salary = 0
    total_transparency_sum = 0
    countries_with_transparency = 0

    # ─── 1. Adzuna per-country fetch ───────────────────────────────────────────
    for country_code, country_name in COUNTRIES.items():
        print(f"\nFetching Adzuna data for {country_name} ({country_code})...")
        try:
            country_data = {
                "code": country_code,
                "job_count": 0,
                "avg_salary": 0,
                "remote_percentage": 0,
                "salary_transparency_pct": 0,
                "unemployment_rate": None,
                "top_cities": [],
                "skills_breakdown": []
            }

            search_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "category": BASE_CATEGORY,   # restrict to IT/tech roles only
                "content-type": "application/json",
                "results_per_page": 50,
            }

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            res_json = response.json()

            country_data["job_count"] = res_json.get("count", 0)
            country_data["avg_salary"] = res_json.get("mean_salary", 0) or 0

            # Salary transparency: % of result listings that include a salary figure
            results = res_json.get("results", [])
            if results:
                listings_with_salary = sum(
                    1 for r in results
                    if r.get("salary_min") or r.get("salary_max")
                )
                transparency_pct = round((listings_with_salary / len(results)) * 100, 1)
                country_data["salary_transparency_pct"] = transparency_pct
                total_transparency_sum += transparency_pct
                countries_with_transparency += 1

                # Fallback avg salary from individual results if mean_salary missing
                if country_data["avg_salary"] == 0:
                    salaries = [
                        (r.get("salary_min", 0) + r.get("salary_max", 0)) / 2
                        for r in results
                        if r.get("salary_min") or r.get("salary_max")
                    ]
                    if salaries:
                        country_data["avg_salary"] = round(sum(salaries) / len(salaries), 2)

            total_listings += country_data["job_count"]
            if country_data["avg_salary"] > 0:
                total_salary_sum += country_data["avg_salary"]
                countries_with_salary += 1

            # Geodata — top 6 cities/regions
            geo_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/geodata"
            geo_response = requests.get(geo_url, params=params, timeout=10)
            if geo_response.status_code == 200:
                locations = geo_response.json().get("locations", [])
                sorted_locations = sorted(locations, key=lambda x: x.get("count", 0), reverse=True)
                country_data["top_cities"] = [
                    {
                        "name": loc.get("location", {}).get("display_name", "Unknown"),
                        "count": loc.get("count", 0)
                    }
                    for loc in sorted_locations[:6]
                ]

            # Remote percentage
            remote_params = {**params, "what": "remote"}
            remote_response = requests.get(search_url, params=remote_params, timeout=10)
            if remote_response.status_code == 200:
                remote_count = remote_response.json().get("count", 0)
                if country_data["job_count"] > 0:
                    country_data["remote_percentage"] = round(
                        (remote_count / country_data["job_count"]) * 100, 2
                    )

            # Skills breakdown
            for skill in SKILLS:
                skill_params = {**params, "what": skill}
                skill_response = requests.get(search_url, params=skill_params, timeout=10)
                if skill_response.status_code == 200:
                    skill_count = skill_response.json().get("count", 0)
                    country_data["skills_breakdown"].append({"skill": skill, "count": skill_count})
                time.sleep(0.5)

            # Eurostat unemployment rate (no API key needed)
            print(f"  Fetching Eurostat unemployment for {country_code.upper()}...")
            country_data["unemployment_rate"] = fetch_eurostat_unemployment(country_code)
            time.sleep(0.3)

            data["countries"].append(country_data)
            print(f"  ✓ {country_name}: {country_data['job_count']} jobs, "
                  f"{country_data['salary_transparency_pct']}% salary transparency, "
                  f"unemployment: {country_data['unemployment_rate']}%")
            time.sleep(1)

        except Exception as e:
            print(f"  ✗ Error fetching Adzuna data for {country_code}: {e}")

    # ─── 2. Arbeitnow — full paginated fetch ──────────────────────────────────
    print("\nFetching Arbeitnow data (all pages)...")
    arbeit_url = "https://www.arbeitnow.com/api/job-board-api"
    arbeit_listings = 0
    arbeit_remote_count = 0
    arbeit_skills = {skill: 0 for skill in SKILLS}

    current_page = 1
    while arbeit_url:
        try:
            print(f"  Fetching Arbeitnow page {current_page}...")
            response = requests.get(arbeit_url, timeout=10)
            if response.status_code != 200:
                break

            res_json = response.json()
            jobs = res_json.get("data", [])
            if not jobs:
                break

            arbeit_listings += len(jobs)
            for job in jobs:
                if job.get("remote"):
                    arbeit_remote_count += 1
                tags = [tag.lower() for tag in job.get("tags", [])]
                desc = job.get("description", "").lower()
                title = job.get("title", "").lower()
                for skill in SKILLS:
                    if (skill.lower() in tags
                            or skill.lower() in title
                            or skill.lower() in desc):
                        arbeit_skills[skill] += 1

            # Pagination — no artificial limit
            arbeit_url = res_json.get("links", {}).get("next")
            current_page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error on Arbeitnow page {current_page}: {e}")
            break

    print(f"  ✓ Arbeitnow: {arbeit_listings} jobs across {current_page - 1} pages")

    # ─── 3. Merge global metrics ──────────────────────────────────────────────
    data["global_metrics"]["total_listings"] = total_listings + arbeit_listings
    if countries_with_salary > 0:
        data["global_metrics"]["avg_eu_salary"] = round(total_salary_sum / countries_with_salary, 2)
    if countries_with_transparency > 0:
        data["global_metrics"]["avg_salary_transparency_pct"] = round(
            total_transparency_sum / countries_with_transparency, 1
        )

    # Arbeitnow as a virtual country entry
    arbeit_country = {
        "code": "arbeitnow",
        "job_count": arbeit_listings,
        "avg_salary": 0,
        "remote_percentage": round((arbeit_remote_count / arbeit_listings * 100), 2) if arbeit_listings > 0 else 0,
        "salary_transparency_pct": 0,
        "unemployment_rate": None,
        "top_cities": [],
        "skills_breakdown": [{"skill": s, "count": c} for s, c in arbeit_skills.items()]
    }
    data["countries"].append(arbeit_country)

    # ─── 4. Write output ──────────────────────────────────────────────────────
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/market_data.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("\n✓ Successfully saved to public/data/market_data.json")
    print(f"  Countries: {len(COUNTRIES)} | Total listings: {data['global_metrics']['total_listings']}")
    print(f"  Avg salary transparency: {data['global_metrics']['avg_salary_transparency_pct']}%")


if __name__ == "__main__":
    fetch_data()
