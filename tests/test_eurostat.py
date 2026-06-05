"""
Test script for Eurostat API
Tests unemployment rate fetching for EU countries
"""
import requests

EUROSTAT_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "une_rt_m?format=JSON&geo={geo}&unit=PC_ACT&age=TOTAL&sex=T&lastTimePeriod=1"
)

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


def fetch_unemployment_rate(country_code):
    """Fetch unemployment rate for a single country"""
    geo = country_code.upper()
    try:
        resp = requests.get(EUROSTAT_URL.format(geo=geo), timeout=10)
        if resp.status_code != 200:
            return None, f"HTTP {resp.status_code}"
        
        payload = resp.json()
        values = payload.get("value", {})
        
        if not values:
            return None, "No values in response"
        
        # Get the last value
        last_val = list(values.values())[-1]
        if last_val is None:
            return None, "Last value is null"
        
        return round(float(last_val), 1), "✓"
    except Exception as e:
        return None, str(e)[:50]


def test_eurostat_single_country():
    """Test fetching unemployment for a single country"""
    print("\n=== Testing Eurostat Single Country (Germany) ===")
    
    country_code = "de"
    url = EUROSTAT_URL.format(geo=country_code.upper())
    
    try:
        print(f"Request URL: {url}\n")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status Code: {response.status_code}")
        
        # Parse the response structure
        values = data.get("value", {})
        dimension = data.get("dimension", {})
        
        print(f"✓ Data points found: {len(values)}")
        
        if values:
            last_val = list(values.values())[-1]
            print(f"✓ Latest unemployment rate: {last_val}%")
            
            # Try to get the time period
            time_dim = dimension.get("time", {})
            time_category = time_dim.get("category", {})
            time_index = time_category.get("index", {})
            if time_index:
                last_period = list(time_index.keys())[-1]
                print(f"✓ Time period: {last_period}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_eurostat_all_countries():
    """Test fetching unemployment for all EU countries"""
    print("\n=== Testing Eurostat All Countries ===")
    
    results = []
    successful = 0
    
    for code, name in COUNTRIES.items():
        rate, status = fetch_unemployment_rate(code)
        
        if rate is not None:
            results.append((name, rate, "✓"))
            print(f"  {name:15} ({code.upper()}): {rate:5.1f}% ✓")
            successful += 1
        else:
            results.append((name, None, status))
            print(f"  {name:15} ({code.upper()}): ❌ {status}")
    
    print(f"\n✓ Successful: {successful}/{len(COUNTRIES)} countries")
    
    # Show statistics
    if successful > 0:
        rates = [r[1] for r in results if r[1] is not None]
        avg_rate = sum(rates) / len(rates)
        min_rate = min(rates)
        max_rate = max(rates)
        
        print(f"\nUnemployment Statistics:")
        print(f"  Average: {avg_rate:.1f}%")
        print(f"  Range: {min_rate:.1f}% - {max_rate:.1f}%")
        
        # Find countries with min and max
        min_country = next(r[0] for r in results if r[1] == min_rate)
        max_country = next(r[0] for r in results if r[1] == max_rate)
        print(f"  Lowest: {min_country} ({min_rate:.1f}%)")
        print(f"  Highest: {max_country} ({max_rate:.1f}%)")
    
    return successful == len(COUNTRIES)


def test_eurostat_response_structure():
    """Test and document the response structure"""
    print("\n=== Testing Eurostat Response Structure ===")
    
    country_code = "de"
    url = EUROSTAT_URL.format(geo=country_code.upper())
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("Response Keys:")
        for key in data.keys():
            print(f"  - {key}")
        
        print("\nDimension Keys:")
        dimension = data.get("dimension", {})
        for key in dimension.keys():
            print(f"  - {key}")
        
        print("\nValue Structure:")
        values = data.get("value", {})
        print(f"  Type: {type(values)}")
        print(f"  Count: {len(values)}")
        if values:
            first_key = list(values.keys())[0]
            last_key = list(values.keys())[-1]
            print(f"  First key: {first_key} -> {values[first_key]}")
            print(f"  Last key: {last_key} -> {values[last_key]}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_eurostat_error_handling():
    """Test how the API handles invalid requests"""
    print("\n=== Testing Eurostat Error Handling ===")
    
    test_cases = [
        ("XX", "Invalid country code"),
        ("us", "Non-EU country (US)"),
        ("gb", "UK (post-Brexit)"),
    ]
    
    for code, description in test_cases:
        url = EUROSTAT_URL.format(geo=code.upper())
        try:
            response = requests.get(url, timeout=10)
            print(f"\n  {description} ({code.upper()}):")
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                values = data.get("value", {})
                if values:
                    last_val = list(values.values())[-1]
                    print(f"    Result: {last_val}% (Unexpected success!)")
                else:
                    print(f"    Result: Empty data")
            else:
                print(f"    Result: Error (as expected)")
        except Exception as e:
            print(f"    Exception: {str(e)[:50]}")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("EUROSTAT API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Single Country": test_eurostat_single_country(),
        "All Countries": test_eurostat_all_countries(),
        "Response Structure": test_eurostat_response_structure(),
        "Error Handling": test_eurostat_error_handling(),
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
