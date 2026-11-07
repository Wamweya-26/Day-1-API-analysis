# Pesa Pulse: where are our customers?

Pesa Pulse has a new partner who shares a customer directory through an API, and marketing wants
to know the basics before planning regional campaigns: how many customers there
are, where they are, and what the data looks like.

Data source: https://jsonplaceholder.typicode.com/users

## How to run

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install the packages: `pip install -r requirements.txt`
4. Run the analysis: `python analysis.py`

It prints the results in the terminal and saves the CSVs and charts in `output/`.
The script creates the `output/` folder itself if it is missing.

## What's in the repo

- `analysis.py` has all the code
- `output/customers.csv` has one row per customer (10 rows, 12 columns)
- `output/city_counts.csv` has the number of customers per city
- `output/customer_distribution.png` is the chart by city
- `output/email_domain_distribution.png` is the chart by email domain
- `requirements.txt` lists requests, pandas and matplotlib

## How I did it

**Getting the data.** `get_customers()` uses `requests` with a 10 second timeout
so it can't hang. It checks the status code, and it catches timeouts, connection
errors and bad JSON. If anything fails it prints a short message and returns an
empty list, so the script stops cleanly instead of crashing. I tested this with a
wrong URL (404) and with my Wi-Fi off.

**Exploring the structure.** `explore()` is a recursive function that prints
every key in a record with its type, indented by depth. Two attributes are
nested: `address` (which holds `street`, `suite`, `city`, `zipcode` and another
dict called `geo`) and `company` (which holds `name`, `catchPhrase` and `bs`).
The deepest values are the coordinates, reached with
`customer["address"]["geo"]["lat"]` and `customer["address"]["geo"]["lng"]`.
They come as strings, so I convert them to floats.

**Extracting attributes.** `extract_attributes()` returns one flat dict per
customer with 12 fields: id, name, username, email, email_domain, phone, city,
zipcode, latitude, longitude, company and website. The email domain is the last
part after the final dot (for example `biz`). I kept zipcode as text because it
is an identifier and some contain dashes.

**Unique cities.** I used a set comprehension. There are (10) unique cities for
(10) customers, so every customer is in a different city. For marketing, that
means city is too detailed to group customers by.

**Counting.** `city_counts()` uses a loop with `dict.get()`. `email_domain_counts()`
uses a dict comprehension. Neither uses `Counter` or pandas. A small helper,
`sort_counts()`, sorts both from most to least common.

**Pandas.** I loaded the flat rows into a DataFrame (shape <(10, 12)>). The
latitude and longitude columns are `float64`. I checked my hand-written counts
against `value_counts()` and they matched for both cities and email domains.

**Export.** Both CSVs are written with `index=False` so pandas' row numbers do
not show up as an extra column.

**Charts.** `plot_distribution()` saves a labelled bar chart. I made one by city
and one by email domain.

## What I found

- There are (10) customers and (10) different cities, so no city has more than
  one customer. A campaign aimed at one city would reach a single person.
- The most common email domain is `.<biz>`, with (3) customers. The other
  domains have (1) each, so email domain is the only attribute I looked at that
  gives any kind of grouping.
- The city chart is not very useful because every bar is the same height. The
  email domain chart is more useful because the bars differ, so you can see which
  group is biggest. If marketing wants regional campaigns, they will probably
  need a broader grouping than city, such as using the latitude and longitude to
  group customers by region.

## Assumptions

- The API is the single source of truth for the customer directory.
- Latitude and longitude arrive as text and I convert them to floats.
- "Email domain" means the top-level domain only (`biz`, `tv`, and so on).
- "Company" means the company's name.
- Column names such as `email_domain` and `customers` are my own choice.