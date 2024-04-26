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

    # def test_main(self):
    #     dataset_id : str = 'EC6945'
    #     object = PyDataSimem(dataset_id, "2024-04-14", "2024-04-16")
    #     dataset_dataframe = object.main()
    #     mock_dataframe = self.read_test_dataframe(f'{dataset_id}.csv')
    #     pd.testing.assert_frame_equal(dataset_dataframe, mock_dataframe)

    def test_read_granularity(self):
        dataset_id : str = 'EC6945'
        start_date : str = '1990-01-01'
        end_date : str = '1990-01-01'
        object = PyDataSimem(dataset_id, start_date, end_date)
        granularity = object.read_granularity()
        self.assertEqual(granularity, "Horaria")
        

    # def test_get_metadata(self):
    #     dataset_id : str = 'EC6945'
    #     initial_date : str = '1990-01-01'
    #     final_date : str = '1990-01-01'
    #     object = PyDataSimem(dataset_id, initial_date, final_date)
    #     test_metadata = self.read_test_data(f'{dataset_id}_metadata.json')
    #     metadata = object.get_metadata()
    #     self.assertDictEqual(metadata, test_metadata)

    def test_make_request(self):
        dataset_id : str = 'EC6945'
        object = PyDataSimem(dataset_id)
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        response = object.make_request(url)
        response_status = response['success']
        response_dataset_id = response['parameters']['idDataset']
        response_records_amount = len(response["result"]["records"])
        self.assertTrue(response_status)
        self.assertEqual(response_dataset_id, dataset_id)
        self.assertGreater(response_records_amount, 0)

    def test_check_date_resolution(self):
        dataset_id : str = 'EC6945'
        mock_granularity = 'Horaria'
        object = PyDataSimem(dataset_id)
        resolution = object.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 31)

        mock_granularity = 'Mensual'
        resolution = object.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 731)

        mock_granularity = 'Anual'
        resolution = object.check_date_resolution(mock_granularity)
        self.assertEqual(resolution, 1827)


    def test_create_urls(self):
        dataset_id : str = 'EC6945'
        inital_date = '2024-03-14'
        final_date = '2024-04-16'
        resolution = 31
        object = PyDataSimem(dataset_id)
        urls = object.create_urls(inital_date, final_date, resolution)
        self.assertListEqual(urls, test_urls)
    
    def test_generate_start_dates(self):
        dataset_id : str = 'EC6945'
        initial_date = '2024-03-14'
        final_date = '2024-04-16'
        resolution = 31
        object = PyDataSimem(dataset_id, initial_date, final_date)
        dates = list(date for date in object.generate_start_dates(initial_date, final_date, resolution))
        mock_dates = ['2024-03-14', '2024-04-14', '2024-04-16']
        self.assertListEqual(dates, mock_dates)

    def test_get_records(self):
        dataset_id : str = 'EC6945'
        object = PyDataSimem(dataset_id)
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        records = object.get_records(url)
        mock_records = self.read_test_data(f'{dataset_id}_records.json')
        self.assertCountEqual(records, mock_records)
    
    def test_get_dataset_info(self):
        dataset_id : str = 'EC6945'
        object = PyDataSimem(dataset_id)
        response = object.get_dataset_info()
        response_status = response['success']
        response_dataset_id = response['parameters']['idDataset']
        response_records_amount = len(response["result"]["records"])
        self.assertTrue(response_status)
        self.assertEqual(response_dataset_id, dataset_id)
        self.assertEqual(response_records_amount, 0)

    def test_save_dataset(self):
        dataset_id = 'EC6945'
        object = PyDataSimem(dataset_id, '2024-04-14', '2024-04-16')
        dataset_info = self.read_test_data(f'{dataset_id}_dataset_info.json')
        records = [self.read_test_data(f'{dataset_id}_records.json')]
        dataset = object.save_dataset(dataset_info, records)
        dataset_metadata = dataset['result']['metadata']
        dataset_records = dataset['result']['records']
        
        mock_dataset = self.read_test_data(f'{dataset_id}_request.json')
        mock_dataset_metadata = mock_dataset['result']['metadata']
        mock_dataset_records = mock_dataset['result']['records']

        self.assertEqual(dataset_metadata, mock_dataset_metadata)
        self.assertCountEqual(dataset_records, mock_dataset_records)

    def test_dict_to_json(self):
        dataset_id : str = 'EC6945'
        object = PyDataSimem(dataset_id)
        dictionary = object.get_metadata()
        path = os.getcwd()+os.sep + r'test/test_data/test_write_file.json'
        object.dict_to_json(dictionary, path)
        test_json = self.read_test_data('test_write_file.json')
        self.assertDictEqual(dictionary, test_json)

    def read_test_data(self, filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        with open(path) as file:
            filedata = json.load(file)
        return filedata
    
    def read_test_dataframe(self, filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        dataframe = pd.read_csv(path)
        return dataframe
