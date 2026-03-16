import unittest
from unittest.mock import patch

import pandas as pd

from unige_data_vis_data_collector.scripts.oil_prices.oil_bulletin_prep import transform_oil_prices


class TestOilBulletinPrep(unittest.TestCase):
    def setUp(self):
        # Create a mock dataframe that reflects the structure we saw in the Excel file
        # We only need enough columns to test the extraction of euro95 and diesel
        data = {
            'Consumer prices of petroleum products inclusive of duties and taxes': ['Date', None, '2026-03-09', '2026-03-02'],
            'CTR': [None, None, 'EU_', 'EU_'],
            'EU_price_with_tax_euro95': ['1000 l', None, 1774.084779, 1664.651018],
            'EU_price_with_tax_diesel': ['1000 l', None, 1861.403622, 1629.222729],
            'CTR.1': [None, None, 'EUR_', 'EUR_'],
            'EUR_price_with_tax_euro95': ['1000 l', None, 1835.502109, 1719.955342],
            'EUR_price_with_tax_diesel': ['1000 l', None, 1893.715138, 1661.815029],
            'CTR.2': [None, None, 'AT_', 'AT_'],
            'AT_price_with_tax_euro95': ['1000 l', None, 1708, 1515],
            'AT_price_with_tax_diesel': ['1000 l', None, 1898, 1564],
            'CTR.3': [None, None, 'BE_', 'BE_'],
            'BE_price_with_tax_euro95': ['1000 l', None, 1628.94, 1540.93],
            'BE_price_with_tax_diesel': ['1000 l', None, 1846.77, 1681.41]
        }
        # Columns must be exactly as in the mock Excel dump
        columns = [
            'Consumer prices of petroleum products inclusive of duties and taxes',
            'CTR', 'EU_price_with_tax_euro95', 'EU_price_with_tax_diesel',
            'CTR.1', 'EUR_price_with_tax_euro95', 'EUR_price_with_tax_diesel',
            'CTR.2', 'AT_price_with_tax_euro95', 'AT_price_with_tax_diesel',
            'CTR.3', 'BE_price_with_tax_euro95', 'BE_price_with_tax_diesel'
        ]
        self.mock_df = pd.DataFrame(data, columns=columns)

    @patch('pandas.read_excel')
    def test_transform_oil_prices(self, mock_read_excel):
        mock_read_excel.return_value = self.mock_df

        # Test the transformation
        # We need to provide a dummy path
        output_df = transform_oil_prices('dummy_input.xlsx')

        # Check columns
        expected_columns = ['date', 'country', 'gas_type', 'price_per_liter_euro_with_tax']
        self.assertEqual(list(output_df.columns), expected_columns)

        # Check some values
        # For AT, 2026-03-09, euro95: 1708 / 1000 = 1.708
        at_euro95 = output_df[(output_df['country'] == 'AT') &
                              (output_df['date'] == '2026-03-09') &
                              (output_df['gas_type'] == 'euro95')]
        self.assertFalse(at_euro95.empty)
        self.assertAlmostEqual(at_euro95.iloc[0]['price_per_liter_euro_with_tax'], 1.708)

        # For BE, 2026-03-02, diesel: 1681.41 / 1000 = 1.68141
        be_diesel = output_df[(output_df['country'] == 'BE') &
                              (output_df['date'] == '2026-03-02') &
                              (output_df['gas_type'] == 'diesel')]
        self.assertFalse(be_diesel.empty)
        self.assertAlmostEqual(be_diesel.iloc[0]['price_per_liter_euro_with_tax'], 1.68141)

        # Regions: EU, EUR, AT, BE = 4 regions
        # 2 dates, 2 gas types = 4 per region. 4*4 = 16 rows.
        self.assertEqual(len(output_df), 16)
