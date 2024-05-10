import unittest
import sys
import os
import random
import json
import pandas as pd
sys.path.append(os.getcwd())
from src.pydatasimem import PyDataSimem

test_urls = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-04-13&datasetId=EC6945', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=EC6945']


class test_clase(unittest.TestCase):

    def test_main(self):
        dataset_id : str = 'EC6945'
        inital_date = '2024-03-14'
        final_date = '2024-04-16'
        obj = PyDataSimem()
        df = obj.main(dataset_id, inital_date, final_date)
        df.sort_values('FechaHora', inplace=True)
        df.reset_index(inplace=True, drop=True)
        mock_df = self.read_test_dataframe(f"{dataset_id}.csv")
        pd.testing.assert_frame_equal(df, mock_df)

    def test_read_granularity(self):
        obj = PyDataSimem()
        obj.dataset_id = 'EC6945'
        granularity = obj.read_granularity()
        self.assertEqual(granularity, "Horaria")

        obj.dataset_id = 'e007fb'
        granularity = obj.read_granularity()
        self.assertEqual(granularity, 'Diaria')

    def test_make_request(self):
        dataset_id : str = 'EC6945'
        obj = PyDataSimem()
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        response = obj.make_request(url)
        response_status = response['success']
        response_dataset_id = response['parameters']['idDataset']
        response_records_amount = len(response["result"]["records"])
        self.assertTrue(response_status)
        self.assertEqual(response_dataset_id, dataset_id)
        self.assertGreater(response_records_amount, 0)

    def test_check_date_resolution(self):
        mock_granularity = 'Horaria'
        obj = PyDataSimem()
        resolution = obj.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 31)

        mock_granularity = 'Mensual'
        resolution = obj.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 731)

        mock_granularity = 'Anual'
        resolution = obj.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 1827)


    def test_create_urls(self):
        dataset_id : str = 'EC6945'
        inital_date = '2024-03-14'
        final_date = '2024-04-16'
        resolution = 31
        obj = PyDataSimem()
        obj.dataset_id = dataset_id
        urls = obj.create_urls(inital_date, final_date, resolution)
        self.assertListEqual(urls, test_urls)
    
    def test_generate_start_dates(self):
        initial_date = '2024-03-14'
        final_date = '2024-04-16'
        resolution = 31
        obj = PyDataSimem()
        dates = list(date for date in obj.generate_start_dates(initial_date, final_date, resolution))
        mock_dates = ['2024-03-14', '2024-04-14', '2024-04-16']
        self.assertListEqual(dates, mock_dates)

    def test_get_records(self):
        dataset_id : str = 'EC6945'
        obj = PyDataSimem()
        obj.dataset_id = dataset_id
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        records = obj.get_records(url)
        mock_records = self.read_test_data(f'{dataset_id}_records.json')
        self.assertTrue(len(records), len(mock_records))
    
    def test_get_dataset_info(self):
        dataset_id : str = 'EC6945'
        obj = PyDataSimem()
        obj.dataset_id = dataset_id
        obj.start_date = '2024-03-14'
        obj.end_date = '2024-04-16'
        response = obj.get_dataset_info()
        response_status = response['success']
        response_dataset_id = response['parameters']['idDataset']
        response_records_amount = len(response["result"]["records"])
        self.assertTrue(response_status)
        self.assertEqual(response_dataset_id, dataset_id)
        self.assertEqual(response_records_amount, 0)

    def test_save_dataset(self):
        dataset_id = 'EC6945'
        obj = PyDataSimem()
        dataset_info = self.read_test_data(f'{dataset_id}_dataset_info.json')
        records = [self.read_test_data(f'{dataset_id}_records.json')]
        dataset = obj.save_dataset(dataset_info, records)
        dataset_metadata = dataset['result']['metadata']
        dataset_records = dataset['result']['records']
        
        mock_dataset = self.read_test_data(f'{dataset_id}_request.json')
        mock_dataset_metadata = mock_dataset['result']['metadata']
        mock_dataset_records = mock_dataset['result']['records']

        self.assertEqual(dataset_metadata, mock_dataset_metadata)
        self.assertCountEqual(dataset_records, mock_dataset_records)

    def read_test_data(self, filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        with open(path) as file:
            filedata = json.load(file)
        return filedata
    
    def read_test_dataframe(self, filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        dataframe = pd.read_csv(path)
        return dataframe
