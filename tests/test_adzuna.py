"""
Test script for Adzuna API
Tests basic job search, geodata, and pagination functionality
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

def test_adzuna_basic_search():
    """Test basic job search for a single country"""
    print("\n=== Testing Adzuna Basic Search ===")
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("❌ Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set in .env")
        return False
    
    country_code = "de"  # Germany as test case
    search_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "software developer engineer data analyst",
        "category": "it-jobs",
        "content-type": "application/json",
        "results_per_page": 50,
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Total Jobs Found: {data.get('count', 0)}")
        print(f"✓ Results Returned: {len(data.get('results', []))}")
        print(f"✓ Mean Salary: €{data.get('mean_salary', 0):,.2f}")
        
        # Check salary transparency
        results = data.get("results", [])
        if results:
            with_salary = sum(1 for r in results if r.get("salary_min") or r.get("salary_max"))
            transparency = (with_salary / len(results)) * 100
            print(f"✓ Salary Transparency: {transparency:.1f}% ({with_salary}/{len(results)} listings)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_adzuna_geodata():
    """Test geodata endpoint for location information"""
    print("\n=== Testing Adzuna Geodata ===")
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("❌ Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set")
        return False
    
    country_code = "de"
    geo_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/geodata"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "software developer",
        "category": "it-jobs",
    }
    
    try:
        response = requests.get(geo_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        locations = data.get("locations", [])
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Locations Found: {len(locations)}")
        
        # Show top 5 cities
        sorted_locs = sorted(locations, key=lambda x: x.get("count", 0), reverse=True)[:5]
        print("\n  Top 5 Cities:")
        for loc in sorted_locs:
            city = loc.get("location", {}).get("display_name", "Unknown")
            count = loc.get("count", 0)
            print(f"    - {city}: {count} jobs")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_adzuna_remote_filter():
    """Test filtering for remote jobs"""
    print("\n=== Testing Adzuna Remote Filter ===")
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("❌ Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set")
        return False
    
    country_code = "de"
    search_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    
    # First get total jobs
    params_total = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": "software developer",
        "category": "it-jobs",
    }
    
    # Then get remote jobs
    params_remote = {**params_total, "what_phrase": "remote"}
    
    try:
        resp_total = requests.get(search_url, params=params_total, timeout=10)
        resp_remote = requests.get(search_url, params=params_remote, timeout=10)
        
        total_jobs = resp_total.json().get("count", 0)
        remote_jobs = resp_remote.json().get("count", 0)
        
        remote_pct = (remote_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        print(f"✓ Total Jobs: {total_jobs}")
        print(f"✓ Remote Jobs: {remote_jobs}")
        print(f"✓ Remote Percentage: {remote_pct:.2f}%")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_adzuna_multiple_countries():
    """Test API across multiple countries"""
    print("\n=== Testing Adzuna Multiple Countries ===")
    
    countries = {
        'de': 'Germany',
        'fr': 'France',
        'nl': 'Netherlands',
    }
    
    results = []
    for code, name in countries.items():
        search_url = f"https://api.adzuna.com/v1/api/jobs/{code}/search/1"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "what": "software developer",
            "category": "it-jobs",
            "results_per_page": 10,
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            job_count = data.get("count", 0)
            results.append((name, job_count, "✓"))
            print(f"  {name}: {job_count} jobs ✓")
        except Exception as e:
            results.append((name, 0, f"❌ {str(e)[:50]}"))
            print(f"  {name}: ❌ {str(e)[:50]}")
    
    success_count = sum(1 for r in results if r[2] == "✓")
    print(f"\n✓ Successful: {success_count}/{len(countries)} countries")
    
    return success_count == len(countries)


if __name__ == "__main__":
    print("=" * 60)
    print("ADZUNA API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Basic Search": test_adzuna_basic_search(),
        "Geodata": test_adzuna_geodata(),
        "Remote Filter": test_adzuna_remote_filter(),
        "Multiple Countries": test_adzuna_multiple_countries(),
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
