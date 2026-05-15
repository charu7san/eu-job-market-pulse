import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

COUNTRIES = ['at', 'be', 'de', 'es', 'fr', 'it', 'nl']
BASE_SEARCH = "Technology"
SKILLS = [
    'Python', 'SQL', 'Power BI', 'Tableau', 'Spark', 
    'dbt', 'Airflow', 'Looker', 'Snowflake', 'Excel', 
    'Azure', 'AWS', 'React', 'TypeScript', 'Node.js',
    'Java', 'Docker', 'Kubernetes', 'Linux', 'Git', 'JavaScript'
]

def fetch_data():
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set.")
        return

    data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "global_metrics": {"total_listings": 0, "avg_eu_salary": 0},
        "countries": [],
        "sources": [
            {"name": "Adzuna", "url": "https://www.adzuna.com/", "description": "Aggregated job market data and salary trends across Europe."},
            {"name": "Arbeitnow", "url": "https://www.arbeitnow.com/", "description": "Tech-focused job board with a focus on European and remote roles."}
        ]
    }

    total_listings = 0
    total_salary_sum = 0
    countries_with_salary = 0

    # 1. Fetch Adzuna Data (Aggregates)
    for country in COUNTRIES:
        print(f"Fetching Adzuna data for {country}...")
        try:
            country_data = {
                "code": country,
                "job_count": 0,
                "avg_salary": 0,
                "remote_percentage": 0,
                "top_cities": [],
                "skills_breakdown": []
            }

            search_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "what": BASE_SEARCH,
                "content-type": "application/json"
            }
            
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            res_json = response.json()
            
            country_data["job_count"] = res_json.get("count", 0)
            country_data["avg_salary"] = res_json.get("mean_salary", 0)
            
            if country_data["avg_salary"] == 0:
                results = res_json.get("results", [])
                salaries = [ (r.get("salary_min", 0) + r.get("salary_max", 0))/2 for r in results if r.get("salary_min") or r.get("salary_max") ]
                if salaries: country_data["avg_salary"] = sum(salaries) / len(salaries)
            
            total_listings += country_data["job_count"]
            if country_data["avg_salary"] > 0:
                total_salary_sum += country_data["avg_salary"]
                countries_with_salary += 1

            # Geodata
            geo_url = f"https://api.adzuna.com/v1/api/jobs/{country}/geodata"
            geo_response = requests.get(geo_url, params=params)
            if geo_response.status_code == 200:
                locations = geo_response.json().get("locations", [])
                sorted_locations = sorted(locations, key=lambda x: x.get("count", 0), reverse=True)
                country_data["top_cities"] = [
                    {"name": loc.get("location", {}).get("display_name", "Unknown"), "count": loc.get("count", 0)}
                    for loc in sorted_locations[:6]
                ]
            
            # Remote
            remote_params = params.copy()
            remote_params["what_phrase"] = "remote"
            remote_response = requests.get(search_url, params=remote_params)
            if remote_response.status_code == 200:
                remote_count = remote_response.json().get("count", 0)
                if country_data["job_count"] > 0:
                    country_data["remote_percentage"] = round((remote_count / country_data["job_count"]) * 100, 2)

            # Skills
            for skill in SKILLS:
                skill_params = params.copy()
                skill_params["what_and"] = skill
                skill_response = requests.get(search_url, params=skill_params)
                if skill_response.status_code == 200:
                    skill_count = skill_response.json().get("count", 0)
                    country_data["skills_breakdown"].append({"skill": skill, "count": skill_count})
                time.sleep(0.5)

            data["countries"].append(country_data)
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching Adzuna data for {country}: {e}")

    # 2. Fetch Arbeitnow Data (Individual Jobs - Paginated)
    print("Fetching Arbeitnow data (paginated)...")
    arbeit_url = "https://www.arbeitnow.com/api/job-board-api"
    arbeit_listings = 0
    arbeit_remote_count = 0
    arbeit_skills = {skill: 0 for skill in SKILLS}
    
    current_page = 1
    while arbeit_url:
        try:
            print(f"  Fetching Arbeitnow page {current_page}...")
            response = requests.get(arbeit_url)
            if response.status_code != 200: break
            
            res_json = response.json()
            jobs = res_json.get("data", [])
            if not jobs: break
            
            arbeit_listings += len(jobs)
            for job in jobs:
                if job.get("remote"): arbeit_remote_count += 1
                tags = [tag.lower() for tag in job.get("tags", [])]
                for skill in SKILLS:
                    if skill.lower() in tags or skill.lower() in job.get("title", "").lower():
                        arbeit_skills[skill] += 1
            
            # Pagination
            arbeit_url = res_json.get("links", {}).get("next")
            current_page += 1
            time.sleep(0.5) # Be kind to the API
            
            # Safety limit for demonstration (remove or increase for production)
            if current_page > 10: break 
            
        except Exception as e:
            print(f"Error fetching Arbeitnow page {current_page}: {e}")
            break

    # 3. Merge Metrics
    data["global_metrics"]["total_listings"] = total_listings + arbeit_listings
    if countries_with_salary > 0:
        data["global_metrics"]["avg_eu_salary"] = round(total_salary_sum / countries_with_salary, 2)
    
    # Merge Arbeitnow skills into global totals (already implicitly handled by App.jsx aggregating countries)
    # But since Arbeitnow is global, we can add a 'virtual' country for Arbeitnow or just add to total listings
    # I'll add a 'virtual' country for Arbeitnow to keep it clean
    arbeit_country = {
        "code": "arbeitnow",
        "job_count": arbeit_listings,
        "avg_salary": 0,
        "remote_percentage": round((arbeit_remote_count / arbeit_listings * 100), 2) if arbeit_listings > 0 else 0,
        "top_cities": [],
        "skills_breakdown": [{"skill": s, "count": c} for s, c in arbeit_skills.items()]
    }
    data["countries"].append(arbeit_country)

    os.makedirs('public/data', exist_ok=True)
    with open('public/data/market_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Successfully saved combined data to public/data/market_data.json")

if __name__ == "__main__":
    fetch_data()
