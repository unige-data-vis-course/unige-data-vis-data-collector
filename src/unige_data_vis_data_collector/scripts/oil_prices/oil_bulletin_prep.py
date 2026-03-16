"""
An Excel file is downloaded from https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en
=> Price developments 2005 onwards (xlsx) with weekly gas price since 2005
We want to transform these data into a more manageable form
"""

import argparse
import os

import pandas as pd


def transform_oil_prices(input_file: str) -> pd.DataFrame:
    """
    Transforms gasline prices from excel file to a data vis ready DataFrame.
    """
    # Parse only the first sheet
    # lines 2 and 3 must be skipped (index 1 and 2 in 0-based)
    # However, the headers are in line 1.
    # Let's read it all and then drop the rows.
    df = pd.read_excel(input_file, sheet_name=0)

    # The first column contains the date
    date_col = df.columns[0]

    # Drop lines 2 and 3 (index 0 and 1 of the data rows, since header is already read)
    # df.iloc[0] is 'Date', '1000 l' etc.
    # df.iloc[1] is NaN, NaN etc.
    df = df.drop([0, 1]).reset_index(drop=True)

    # Rename the date column
    df = df.rename(columns={date_col: 'date'})

    # Melt the dataframe to get a long format
    # We are interested in columns ending with _euro95 and _diesel
    # Column names are like 'AT_price_with_tax_euro95'

    # Identify price columns
    price_cols = [c for c in df.columns if c.endswith('_euro95') or c.endswith('_diesel')]

    # Filter rows where date is NOT null
    df = df[df['date'].notnull()]

    # Keep only date and price columns
    df = df[['date'] + price_cols]

    # Melt
    melted = df.melt(id_vars=['date'], value_vars=price_cols, var_name='raw_type', value_name='price_1000l')

    # Extract country and gas_type
    # Example: 'AT_price_with_tax_euro95' -> country='AT', gas_type='euro95'
    melted['country'] = melted['raw_type'].str.extract(r'^([A-Z]{2,3})_')

    # Fix for 'EU' and 'EUR' which might be 2 or 3 letters
    # The regex ^([A-Z]{2,3})_ should handle AT, BE, EU, EUR

    melted['gas_type'] = melted['raw_type'].apply(lambda x: 'euro95' if 'euro95' in x else 'diesel')

    # Drop rows where price is null or not a number
    melted = melted[pd.to_numeric(melted['price_1000l'], errors='coerce').notnull()]

    # Divide by 1000
    melted['price_per_liter_euro_with_tax'] = melted['price_1000l'].astype(float) / 1000.0

    # Select final columns
    result = melted[['date', 'country', 'gas_type', 'price_per_liter_euro_with_tax']]

    # Convert date to string YYYY-MM-DD for consistency
    result['date'] = pd.to_datetime(result['date']).dt.strftime('%Y-%m-%d')

    return result


def main():
    parser = argparse.ArgumentParser(description='Transform Weekly Oil Bulletin Prices History from Excel to CSV')
    parser.add_argument('input', help='Input Excel file path')
    parser.add_argument('--output', '-o', help='Output CSV file path', default='out/oil_prices.csv')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found.")
        return

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    df = transform_oil_prices(args.input)
    df.to_csv(args.output, index=False)
    print(f"Transformation complete. Saved to {args.output}")


if __name__ == "__main__":
    main()
