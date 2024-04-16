import requests
import re
import json
from bs4 import BeautifulSoup

def convert_sectors_to_tickers(input_string):
    # Mapping from sector names to ETF ticker symbols
    sector_to_ticker = {
        "Information Technology": "XLK",
        "Technology": "XLK",
        "Financials": "XLF",
        "Health Care": "XLV",
        "Consumer Discretionary": "XLY",
        "Communication Services": "XLC",
        "Telecommunications": "XLC",
        "Industrials": "XLI",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Materials": "XLB",
        "Basic Materials": "XLB",
        "Utilities": "XLU",
        "Real Estate": "XLRE"
    }

    # Split the input string into individual sector entries
    sectors = input_string.split(',')

    # Parse each sector entry and convert to ticker symbol
    result = []
    for sector in sectors:
        name, weight = sector.split(':')
        name = name.strip()
        ticker = sector_to_ticker.get(name)
        if ticker:
            result.append(f"{ticker}:{weight}")

    # Join all converted entries into a single string
    return ','.join(result)

def fetch_and_parse_qqq_data(url):
    # Fetch the data from the URL
    response = requests.get(url)
    response.raise_for_status()

    # Extract the JavaScript code block containing the sector data
    data_match = re.search(r'var options = ({.*?});', response.text, re.DOTALL)

    if not data_match:
        print("Data not found in the response.")
        return

    # Convert the JavaScript object to valid JSON by fixing the formatting
    data_json_str = data_match.group(1)

    # Attempt to load the JSON data into a Python dictionary
    try:
        data_json = json.loads(data_json_str)
        # Navigate through the JSON to find the CSV data part
        csv_data = data_json['data']['csv']

        # Parse the CSV data into a dictionary of sectors and weights
        sector_weights = {}
        for line in csv_data.split('\n'):
            if ';' in line:
                sector, weight = line.split(';')
                sector = sector.strip('" \n')
                weight = weight.strip()
                if sector:  # To avoid blank lines
                    sector_weights[sector] = weight

        # Print the results in the required format
        formatted_output = ','.join(f"{sector}:{weight}" for sector, weight in sector_weights.items())
        print(convert_sectors_to_tickers(formatted_output))

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except KeyError as e:
        print(f"Key error: {e}")

def scrape_spy_sector_weights(url):
    # Send a request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the table by class
    table = soup.select_one('.chart-treemap .ssmp-table > .data-table', class_='data-table')
    
    # Initialize a dictionary to store the sector weights
    sector_weights = {}

    # Iterate over each row in the table body, skipping the header
    for row in table.find_all('tr'):
        # Find all 'td' elements in the row
        cells = row.find_all('td')
        if len(cells) == 2:  # Ensure there are exactly two columns, as expected
            sector = cells[0].get_text(strip=True)
            weight = cells[1].get_text(strip=True).strip('%')  # Remove the '%' character
            sector_weights[sector] = weight

    # Print formatted sector weights
    formatted_weights = ",".join(f"{sector}:{weight}" for sector, weight in sector_weights.items())
    print(convert_sectors_to_tickers(formatted_weights))

def get_sector_weights(ticker):
    print()
    if ticker == 'SPY':
        url = 'https://www.ssga.com/us/en/intermediary/etfs/funds/spdr-sp-500-etf-trust-spy'
        scrape_spy_sector_weights(url)
    elif ticker == 'QQQ':
        url = 'https://app.everviz.com/inject/PDI1PphBI/'
        fetch_and_parse_qqq_data(url)
    else:
        print("Invalid ticker. Please enter 'SPY' or 'QQQ'.")
    print()

if __name__ == "__main__":
    ticker = input("Enter ETF ticker (SPY or QQQ): ").strip().upper()
    get_sector_weights(ticker)
