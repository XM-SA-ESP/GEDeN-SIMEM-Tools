import unittest
import sys
import os
import json
import pandas as pd
import datetime as dt
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pydatasimem import _Validation ,ReadSIMEM 

test_urls = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-04-13&datasetId=EC6945', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=EC6945']


class TestValidation(unittest.TestCase):

    def test_log_approve(self):
        try:
            _Validation.log_approve("test_variable")
        except Exception as e:
            self.fail(f"log_approve raised an exception: {e}")

    def test_filter_no_column_no_values(self):
        column = None
        values = None
        result = _Validation.filter(column, values)
        self.assertIsNone(result)

    def test_filter_no_column(self):
        column = None
        values = "values"
        result = _Validation.filter(column, values)
        self.assertIsNone(result)

    def test_filter_no_values(self):
        column = "Column"
        values = None
        result = _Validation.filter(column, values)
        self.assertIsNone(result)

    def test_filter_invalid_column_type(self):
        column = 123
        values = "values"
        with self.assertRaises(TypeError):
            _Validation.filter(column, values)

    def test_filter_invalid_values_type(self):
        column = "Column"
        values = 123
        with self.assertRaises(TypeError):
            _Validation.filter(column, values)


    def test_filter_valid_string_value(self):
        column = "column"
        values = "values"
        result = _Validation.filter(column, values)
        self.assertEqual(result, ("column", ["values"]))

    def test_filter_valid_list_value(self):
        column = "column"
        values = ["value1", "value2"]
        result = _Validation.filter(column, values)
        self.assertEqual(result, ("column", ["value1", "value2"]))

    def test_date_with_datetime(self):
      
        date = dt.datetime(2023, 1, 1)
        result = _Validation.date(date)
        self.assertEqual(result, date)

    def test_date_with_valid_string(self):
        date_str = "2023-01-01"
        result = _Validation.date(date_str)
        self.assertEqual(result, dt.datetime(2023, 1, 1))

    def test_date_with_invalid_string(self):
        with self.assertRaises(ValueError):
            _Validation.date("invalid-date")

    def test_date_with_invalid_type(self):
        with self.assertRaises(TypeError):
            _Validation.date(123)

    def test_datasetid_with_valid_id(self):
        result = _Validation.datasetid("abc123")
        self.assertEqual(result, "abc123")

    def test_datasetid_with_invalid_type(self):
        with self.assertRaises(TypeError):
            _Validation.datasetid(123)

    def test_datasetid_with_invalid_length(self):
        with self.assertRaises(ValueError):
            _Validation.datasetid("abcdefg")

    def test_datasetid_with_non_alphanumeric(self):
        with self.assertRaises(ValueError):
            _Validation.datasetid("abc123!")

    def test_catalog_type_with_valid_type(self):
        result = _Validation.catalog_type("datasets")
        self.assertEqual(result, "datasets")
        result = _Validation.catalog_type("variables")
        self.assertEqual(result, "variables")

    def test_catalog_type_with_invalid_type(self):
        with self.assertRaises(ValueError):
            _Validation.catalog_type("invalid")

    def test_catalog_type_with_non_string(self):
        with self.assertRaises(TypeError):
            _Validation.catalog_type(123)



class test_clase(unittest.TestCase):

    @classmethod
    @patch('src.pydatasimem.requests.Session')
    def setUpClass(cls, mock_session):
        cls.mock_session = mock_session.return_value
        cls.mock_session.get.return_value.json.return_value = cls.read_test_data('EC6945_dataset_info.json')

        cls.dataset_id = "ec6945"
        cls.start_date = "2024-04-14"
        cls.end_date = "2024-04-16"
        cls.read_simem = ReadSIMEM(
            var_dataset_id=cls.dataset_id,
            var_start_date=cls.start_date,
            var_end_date=cls.end_date
        )
        cls.mock_session.get.return_value.json.assert_not_called()

    def test_set_datasetid(self):
        test_id = 'ab1234'
        self.read_simem.set_datasetid(test_id)
        self.assertEqual(self.read_simem._ReadSIMEM__dataset_id, test_id)

    def test_set_dates(self):
        datetime_date = dt.datetime(2021, 1, 1, 0, 0)
        string_date = '2021-01-01'
        self.read_simem.set_dates(string_date, string_date)
        self.assertEqual(self.read_simem._ReadSIMEM__start_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__end_date, datetime_date)

        self.read_simem.set_dates(datetime_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__start_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__end_date, datetime_date)

    def test_set_filter(self):
        list_filter = ('test_column', ["value1", "value2"])
        self.read_simem.set_filter(list_filter[0], list_filter[1])
        self.assertEqual()
        
    # def test_set_dataset_data(self):
    #     self.read_simem._set_dataset_data()
    #     print(self.read_simem)

    # def test_main(self):
    #     # TODO: Revisar y redefinir
    #     dataset_id : str = 'EC6945'
    #     inital_date = '2024-03-14'
    #     final_date = '2024-04-16'
    #     obj = ReadSIMEM(dataset_id, inital_date, final_date)
    #     df = obj.main()
    #     df.sort_values(df.columns.to_list(), inplace=True)
    #     df.reset_index(inplace=True, drop=True)
    #     mock_df = self.read_test_dataframe(f"{dataset_id}.csv")
    #     pd.testing.assert_frame_equal(df, mock_df, check_like=True)

    # def test_read_granularity(self):
    #     # TODO: Eliminar
    #     dataset_id = 'EC6945'
    #     inital_date = '2024-03-14'
    #     final_date = '2024-04-16'
    #     obj = ReadSIMEM(dataset_id, inital_date, final_date)
    #     granularity = obj.__read_granularity()
    #     self.assertEqual(granularity, "Horaria")

    #     obj.__dataset_id = 'e007fb'
    #     granularity = obj.__read_granularity()
    #     self.assertEqual(granularity, 'Diaria')

    # def test_make_request(self):
    #     # TODO: Revisar y redefinir
    #     dataset_id : str = 'EC6945'
    #     obj = ReadSIMEM()
    #     url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
    #     response = obj._make_request(url)
    #     response_status = response['success']
    #     response_dataset_id = response['parameters']['idDataset']
    #     response_records_amount = len(response["result"]["records"])
    #     self.assertTrue(response_status)
    #     self.assertEqual(response_dataset_id, dataset_id)
    #     self.assertGreater(response_records_amount, 0)

    # def test_check_date_resolution(self):
    #     # TODO: Anadir el caso sin condición 
    #     mock_granularity = 'Horaria'
    #     obj = ReadSIMEM()
    #     resolution = obj.__check_date_resolution(mock_granularity)
    #     self.assertEqual(resolution, 31)

    #     mock_granularity = 'Mensual'
    #     resolution = obj.__check_date_resolution(mock_granularity)
    #     self.assertEqual(resolution, 731)

    #     mock_granularity = 'Anual'
    #     resolution = obj.__check_date_resolution(mock_granularity)
    #     self.assertEqual(resolution, 1827)


    # def test_create_urls(self):
    #     # TODO: Revisar y redefinir
    #     dataset_id : str = 'EC6945'
    #     inital_date = '2024-03-14'
    #     final_date = '2024-04-16'
    #     resolution = 31
    #     obj = ReadSIMEM()
    #     obj.__dataset_id = dataset_id
    #     urls = obj.__create_urls(inital_date, final_date, resolution)
    #     self.assertListEqual(urls, test_urls)
    
    # def test_generate_start_dates(self):
    #     # TODO: Revisar y redefinir
    #     initial_date = '2024-03-14'
    #     final_date = '2024-04-16'
    #     resolution = 31
    #     obj = ReadSIMEM()
    #     dates = list(date for date in obj._generate_start_dates(initial_date, final_date, resolution))
    #     mock_dates = ['2024-03-14', '2024-04-14', '2024-04-16']
    #     self.assertListEqual(dates, mock_dates)

    # def test_get_records(self):
    #     # TODO: Revisar y redefinir
    #     dataset_id : str = 'EC6945'
    #     obj = ReadSIMEM()
    #     obj.__dataset_id = dataset_id
    #     url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
    #     records = obj._get_records(url)
    #     mock_records = self.read_test_data(f'{dataset_id}_records.json')
    #     self.assertTrue(len(records), len(mock_records))
    
    # def test_get_dataset_info(self):
    #     # TODO: Eliminar
    #     dataset_id : str = 'EC6945'
    #     obj = ReadSIMEM()
    #     obj.__dataset_id = dataset_id
    #     obj.start_date = '2024-03-14'
    #     obj.end_date = '2024-04-16'
    #     response = obj.__get_dataset_info()
    #     response_status = response['success']
    #     response_dataset_id = response['parameters']['idDataset']
    #     response_records_amount = len(response["result"]["records"])
    #     self.assertTrue(response_status)
    #     self.assertEqual(response_dataset_id, dataset_id)
    #     self.assertEqual(response_records_amount, 0)

    # def test_save_dataset(self):
    #     # TODO: Revisar y redefinir
    #     dataset_id = 'EC6945'
    #     obj = ReadSIMEM()
    #     dataset_info = self.read_test_data(f'{dataset_id}_dataset_info.json')
    #     records = [self.read_test_data(f'{dataset_id}_records.json')]
    #     dataset = obj.__save_dataset(dataset_info, records)
    #     dataset_metadata = dataset['result']['metadata']
    #     dataset_records = dataset['result']['records']
        
    #     mock_dataset = self.read_test_data(f'{dataset_id}_request.json')
    #     mock_dataset_metadata = mock_dataset['result']['metadata']
    #     mock_dataset_records = mock_dataset['result']['records']

    #     self.assertEqual(dataset_metadata, mock_dataset_metadata)
    #     self.assertCountEqual(dataset_records, mock_dataset_records)

    @staticmethod
    def read_test_data(filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        with open(path) as file:
            filedata = json.load(file)
        return filedata
    
    # def read_test_dataframe(self, filename):
    #     path = os.getcwd() + os.sep + r'test/test_data/' + filename
    #     dataframe = pd.read_csv(path)
    #     return dataframe

if __name__ == '__main__':
    unittest.main()
