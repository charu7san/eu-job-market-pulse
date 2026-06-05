"""
Test different filter combinations for Austria to understand the 0 jobs issue
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY')

def test_austria_filters():
    """Test different filter combinations for Austria"""
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("❌ Error: ADZUNA_APP_ID or ADZUNA_APP_KEY not set")
        return
    
    country_code = "at"
    search_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    
    test_cases = [
        ("No filters", {}),
        ("IT category only", {"category": "it-jobs"}),
        ("Keywords only", {"what": "software developer engineer data analyst"}),
        ("IT category + keywords (CURRENT)", {"category": "it-jobs", "what": "software developer engineer data analyst"}),
        ("Broad tech keywords", {"what": "developer"}),
        ("IT category + broad", {"category": "it-jobs", "what": "developer"}),
    ]
    
    print("=" * 70)
    print("AUSTRIA FILTER ANALYSIS")
    print("=" * 70)
    
    for description, extra_params in test_cases:
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "content-type": "application/json",
            "results_per_page": 10,
            **extra_params
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            job_count = data.get("count", 0)
            mean_salary = data.get("mean_salary", 0)
            
            print(f"\n{description}:")
            print(f"  Jobs: {job_count:,}")
            print(f"  Avg Salary: €{mean_salary:,.2f}" if mean_salary else "  Avg Salary: N/A")
            
            if job_count > 0:
                results = data.get("results", [])
                if results:
                    print(f"  Sample job: {results[0].get('title', 'N/A')}")
        
        except Exception as e:
            print(f"\n{description}:")
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_austria_filters()
