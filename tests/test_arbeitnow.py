"""
Test script for Arbeitnow API
Tests job fetching, pagination, and data structure
"""
import requests
import time

def test_arbeitnow_basic_fetch():
    """Test basic job fetch from first page"""
    print("\n=== Testing Arbeitnow Basic Fetch ===")
    
    url = "https://www.arbeitnow.com/api/job-board-api"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Jobs on Page 1: {len(data.get('data', []))}")
        
        # Check data structure
        jobs = data.get('data', [])
        if jobs:
            sample_job = jobs[0]
            print(f"✓ Sample Job Title: {sample_job.get('title', 'N/A')}")
            print(f"✓ Sample Job Company: {sample_job.get('company_name', 'N/A')}")
            print(f"✓ Sample Job Location: {sample_job.get('location', 'N/A')}")
            print(f"✓ Sample Job Remote: {sample_job.get('remote', False)}")
            print(f"✓ Sample Job Tags: {sample_job.get('tags', [])}")
        
        # Check pagination links
        links = data.get('links', {})
        print(f"\n✓ Pagination Links:")
        print(f"    - First: {links.get('first', 'None')}")
        print(f"    - Next: {links.get('next', 'None')}")
        print(f"    - Prev: {links.get('prev', 'None')}")
        print(f"    - Last: {links.get('last', 'None')}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_arbeitnow_pagination():
    """Test pagination to fetch multiple pages"""
    print("\n=== Testing Arbeitnow Pagination ===")
    
    url = "https://www.arbeitnow.com/api/job-board-api"
    total_jobs = 0
    page_count = 0
    max_pages = 5  # Limit test to 5 pages
    
    try:
        while url and page_count < max_pages:
            page_count += 1
            print(f"\n  Fetching page {page_count}...")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('data', [])
            if not jobs:
                print(f"  ⚠ No jobs found on page {page_count}, stopping")
                break
            
            total_jobs += len(jobs)
            print(f"    Jobs on page {page_count}: {len(jobs)}")
            print(f"    Running total: {total_jobs}")
            
            # Get next page URL
            url = data.get('links', {}).get('next')
            
            if not url:
                print(f"  ✓ No more pages (reached end)")
                break
            
            time.sleep(0.3)  # Be nice to the API
        
        print(f"\n✓ Total Jobs Fetched: {total_jobs} across {page_count} pages")
        print(f"✓ Average per page: {total_jobs / page_count:.1f}")
        
        return total_jobs > 0
    except Exception as e:
        print(f"❌ Error on page {page_count}: {e}")
        return False


def test_arbeitnow_remote_jobs():
    """Test counting remote vs non-remote jobs"""
    print("\n=== Testing Arbeitnow Remote Jobs ===")
    
    url = "https://www.arbeitnow.com/api/job-board-api"
    remote_count = 0
    non_remote_count = 0
    total_jobs = 0
    max_pages = 3
    page_count = 0
    
    try:
        while url and page_count < max_pages:
            page_count += 1
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('data', [])
            if not jobs:
                break
            
            for job in jobs:
                if job.get('remote'):
                    remote_count += 1
                else:
                    non_remote_count += 1
                total_jobs += 1
            
            url = data.get('links', {}).get('next')
            time.sleep(0.3)
        
        remote_pct = (remote_count / total_jobs * 100) if total_jobs > 0 else 0
        
        print(f"✓ Total Jobs Analyzed: {total_jobs}")
        print(f"✓ Remote Jobs: {remote_count} ({remote_pct:.1f}%)")
        print(f"✓ Non-Remote Jobs: {non_remote_count} ({100 - remote_pct:.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_arbeitnow_skills_detection():
    """Test detecting skills from job listings"""
    print("\n=== Testing Arbeitnow Skills Detection ===")
    
    SKILLS = ['Python', 'SQL', 'React', 'JavaScript', 'AWS', 'Docker']
    url = "https://www.arbeitnow.com/api/job-board-api"
    skills_count = {skill: 0 for skill in SKILLS}
    total_jobs = 0
    max_pages = 3
    page_count = 0
    
    try:
        while url and page_count < max_pages:
            page_count += 1
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('data', [])
            if not jobs:
                break
            
            for job in jobs:
                total_jobs += 1
                tags = [tag.lower() for tag in job.get('tags', [])]
                title = job.get('title', '').lower()
                desc = job.get('description', '').lower()
                
                for skill in SKILLS:
                    if (skill.lower() in tags or 
                        skill.lower() in title or 
                        skill.lower() in desc):
                        skills_count[skill] += 1
            
            url = data.get('links', {}).get('next')
            time.sleep(0.3)
        
        print(f"✓ Total Jobs Analyzed: {total_jobs}")
        print(f"\n  Skills Breakdown:")
        sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)
        for skill, count in sorted_skills:
            pct = (count / total_jobs * 100) if total_jobs > 0 else 0
            print(f"    - {skill}: {count} jobs ({pct:.1f}%)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_arbeitnow_full_pagination():
    """Test fetching ALL pages to understand the issue"""
    print("\n=== Testing Arbeitnow FULL Pagination (This may take a while) ===")
    
    url = "https://www.arbeitnow.com/api/job-board-api"
    total_jobs = 0
    page_count = 0
    
    print("⚠ Warning: This will fetch ALL pages. Press Ctrl+C to stop.\n")
    
    try:
        while url:
            page_count += 1
            print(f"  Page {page_count}...", end=" ", flush=True)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get('data', [])
            if not jobs:
                print(f"❌ Empty page, stopping")
                break
            
            total_jobs += len(jobs)
            print(f"{len(jobs)} jobs (total: {total_jobs})")
            
            # Get next page URL
            next_url = data.get('links', {}).get('next')
            
            if not next_url:
                print(f"\n✓ Reached the last page!")
                break
            
            url = next_url
            time.sleep(0.5)  # Be respectful to the API
        
        print(f"\n✓ FINAL RESULTS:")
        print(f"  Total Pages: {page_count}")
        print(f"  Total Jobs: {total_jobs}")
        print(f"  Average per page: {total_jobs / page_count:.1f}")
        
        return total_jobs > 0
    except KeyboardInterrupt:
        print(f"\n\n⚠ Stopped by user at page {page_count}")
        print(f"  Jobs so far: {total_jobs}")
        return False
    except Exception as e:
        print(f"\n❌ Error on page {page_count}: {e}")
        print(f"  Last URL attempted: {url}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ARBEITNOW API TEST SUITE")
    print("=" * 60)
    
    results = {
        "Basic Fetch": test_arbeitnow_basic_fetch(),
        "Pagination (5 pages)": test_arbeitnow_pagination(),
        "Remote Jobs": test_arbeitnow_remote_jobs(),
        "Skills Detection": test_arbeitnow_skills_detection(),
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
    
    # Ask if user wants to run full pagination test
    print("\n" + "=" * 60)
    print("Optional: Run FULL pagination test? (y/n)")
    print("This will fetch ALL pages and may take several minutes.")
    print("=" * 60)
    
    # For automated testing, skip this prompt
    # Uncomment the line below to run automatically:
    # test_arbeitnow_full_pagination()
