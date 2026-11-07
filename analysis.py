"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"

OUTPUT_DIR = Path("output")


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url, timeout=10)  ##send the request and store it as a response
    except requests.exceptions.Timeout:
        print("Error: the request timed out. The server took too long to respond.")  ##server was too slow
        return []
    except requests.exceptions.ConnectionError:
        print("Error: could not connect. Check your internet connection.")  ##no internet or the server is unreachable
        return []
    except requests.exceptions.RequestException as err:
        print(f"Error: the request failed ({err}).")  ##any other requet problem
        return []

    if response.status_code != 200:
        print(f"Error: the API returned status code {response.status_code}.") ##try catching another error maybe a 404
        return []

    try:
        return response.json() ##converts the json text into python list of dict
    except ValueError:
        print("Error: the API response was not valid JSON.")  ##raises an error if server send sth that isn't valid json
        return []


def explore(record: dict, indent: int = 0) -> None:  ##recursion --function that calls itself...none returns nothing
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    for key, value in record.items():
        print(f"{'  ' * indent}{key}: {type(value).__name__}")
        if isinstance(value, dict):
            explore(value, indent + 1)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for c in customers:
        domain = c["email"].split("@")[1]      # e.g. "april.biz"
        rows.append({
            "id": c["id"],
            "name": c["name"],
            "username": c["username"],
            "email": c["email"],
            "email_domain": domain.split(".")[-1],   # e.g. "biz"
            "phone": c["phone"],
            "city": c["address"]["city"],
            "zipcode": c["address"]["zipcode"],
            "latitude": float(c["address"]["geo"]["lat"]),
            "longitude": float(c["address"]["geo"]["lng"]),
            "company": c["company"]["name"],
            "website": c["website"],
        })
    return rows


def unique_cities(customers: list[dict]) -> set[str]: ##Shld return a set of strings
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}
    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1
    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain (e.g. 'biz', 'tv')."""
    domains = [c["email"].split("@")[1].split(".")[-1] for c in customers]
    return {d: domains.count(d) for d in set(domains)}


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Turn the list of flat dicts into a DataFrame."""
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: Path) -> None:
    """Save a labelled chart of the distribution to path."""
    raise NotImplementedError

def sort_counts(counts: dict[str, int]) -> dict[str, int]: ####Helper to sort and print  Gives them as a list
    """Return a copy of the counts sorted from most to least common."""
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))  ##Convert them back toa dict

def export_csvs(df: pd.DataFrame, counts: dict[str, int]) -> None:
    """Write customers.csv and city_counts.csv to the output folder (no index)."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    df.to_csv(OUTPUT_DIR / "customers.csv", index=False)

    city_df = pd.DataFrame(list(counts.items()), columns=["city", "customers"])
    city_df.to_csv(OUTPUT_DIR / "city_counts.csv", index=False)


if __name__ == "__main__":
    customers = get_customers()
    print(f"Fetched {len(customers)} customers")
    if customers:
        explore(customers[0])
        rows = extract_attributes(customers)
        print()
        print(rows[0])
        # print("latitude type:", type(rows[0]["latitude"]).__name__)##Check whether the conversion took place
        cities = unique_cities(customers)
        print(f"Unique cities: {len(cities)}")
        print(f"Customers: {len(customers)}")
        print(sorted(cities)) ##Turns the cities into alphabetical list

        hand_cities = city_counts(customers)
        hand_domains = email_domain_counts(customers)

        print("\nCustomers per city:")
        for city, n in sort_counts(city_counts(customers)).items():
            print(f"  {city}: {n}")

        print("\nCustomers per email domain:")
        for domain, n in sort_counts(email_domain_counts(customers)).items():
            print(f"  {domain}: {n}")

         # Step 6: pandas
        df = to_dataframe(rows)
        print("\nDataFrame shape:", df.shape)
        print("\nDataFrame dtypes:")
        print(df.dtypes)

        pandas_cities = df["city"].value_counts().to_dict()
        pandas_domains = df["email_domain"].value_counts().to_dict()
        print("\nPandas agrees on cities: ", pandas_cities == hand_cities)
        print("Pandas agrees on domains:", pandas_domains == hand_domains)

        export_csvs(df, sort_counts(hand_cities))
        print("\nSaved output/customers.csv and output/city_counts.csv")

        
