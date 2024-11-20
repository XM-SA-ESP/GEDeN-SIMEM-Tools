import unittest
import sys
import os
import json
import pandas as pd
import datetime as dt
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pydatasimem import _Validation ,ReadSIMEM 

test_urls = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-04-13&datasetId=ec6945', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945']

EXCEPTION = False
EC6945_REQUEST_FILE = 'EC6945_request.json'
EC6945_RECORDS_FILE = 'EC6945_records.json'
EC6945_DATASET_INFO_FILE = 'EC6945_dataset_info.json'

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
    def setUp(cls, mock_session):
        """
        Initialization previous to each test, creates a ReadSIMEM object to work.
        """
        # Every session opened in the tests is replaced by the mock object
        cls.mock_session = mock_session
        test_data = cls.read_test_data(EC6945_DATASET_INFO_FILE)
        cls.mock_session.return_value.get.return_value.json.return_value = test_data
        cls.dataset_id = "ec6945"
        cls.exception = False
        cls.start_date = "2024-04-14"
        cls.end_date = "2024-04-16"
        cls.read_simem = ReadSIMEM(
            var_dataset_id=cls.dataset_id,
            var_start_date=cls.start_date,
            var_end_date=cls.end_date
        )

    @classmethod
    def tearDown(cls):
        global EXCEPTION 
        if EXCEPTION:
            EXCEPTION = False
            return
        # Make sure that the mock is appearing where is needed
        cls.mock_session.return_value.get.return_value.json.assert_called_once()
        
    def test_set_datasetid(self):
        """
        Sets an allowed datasetid.
        """
        test_id = 'ab1234'
        self.read_simem.set_datasetid(test_id)
        self.assertEqual(self.read_simem._ReadSIMEM__dataset_id, test_id)
        self.apply_exception()

    def test_set_dates(self):
        """
        Sets two inputs of allowed dates.
        """
        datetime_date = dt.datetime(2021, 1, 1, 0, 0)
        string_date = '2021-01-01'
        # Checks the result when entered a string date
        self.read_simem.set_dates(string_date, string_date)
        self.assertEqual(self.read_simem._ReadSIMEM__start_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__end_date, datetime_date)
        
        # Checks the result when entered a datetime date
        self.read_simem.set_dates(datetime_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__start_date, datetime_date)
        self.assertEqual(self.read_simem._ReadSIMEM__end_date, datetime_date)
        self.apply_exception()


    def test_set_filter(self):
        """
        Sets an allowed column and list of values
        """
        list_filter = ('test_column', ["value1", "value2"])
        self.read_simem.set_filter(list_filter[0], list_filter[1])
        self.assertEqual(self.read_simem._ReadSIMEM__filter_values, list_filter)
        self.apply_exception()
        

    def test_set_dataset_data(self):
        """
        Sets the mocked information into the attributes of the object.
        """
        self.read_simem._set_dataset_data()
        self.assertIsInstance(self.read_simem._ReadSIMEM__dataset_info, dict)
        self.assertIsInstance(self.read_simem._ReadSIMEM__columns, pd.DataFrame)
        self.assertFalse(self.read_simem._ReadSIMEM__columns.empty, "DataFrame is empty")
        self.assertIsInstance(self.read_simem._ReadSIMEM__metadata, pd.DataFrame)
        self.assertFalse(self.read_simem._ReadSIMEM__metadata.empty, "DataFrame is empty")

        self.assertIsInstance(self.read_simem._ReadSIMEM__date_filter, str)
        self.assertIsInstance(self.read_simem._ReadSIMEM__name, str)
        self.assertIsInstance(self.read_simem._ReadSIMEM__granularity, str)
        self.assertIsInstance(self.read_simem._ReadSIMEM__resolution, int)

    def test_check_date_resolution(self):

        test_granularity = "Horaria"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 31)

        test_granularity = "Mensual"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 731)

        test_granularity = "Anual"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 1827)

        test_granularity = ""
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)        
        self.assertEqual(resolution, 0)
        self.apply_exception()
        
        

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


    def test_make_request(self):
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        response = self.read_simem._make_request(url, self.mock_session.return_value)
        response_status = response['success']
        response_dataset_id = response['parameters']['idDataset']
        self.assertTrue(response_status)
        self.assertEqual(response_dataset_id, self.dataset_id)


    def test_create_urls(self):
        initial_date = dt.datetime(2024, 3, 14, 0, 0)
        final_date = dt.datetime(2024, 4, 16, 0, 0)
        resolution = 31
        urls = self.read_simem._ReadSIMEM__create_urls(initial_date, final_date, resolution)
        self.assertListEqual(urls, test_urls)
        self.apply_exception()
    
    def test_generate_start_dates(self):
        initial_date = dt.datetime(2024, 3, 14, 0, 0)
        final_date = dt.datetime(2024, 4, 16, 0, 0)
        resolution = 31
        obj = self.read_simem
        dates = list(date for date in obj._generate_start_dates(initial_date, final_date, resolution))
        mock_dates = ['2024-03-14', '2024-04-14', '2024-04-16']
        self.assertListEqual(dates, mock_dates)
        self.apply_exception()

    def test_get_records(self):
        mock_records = self.read_test_data(EC6945_RECORDS_FILE)
        test_request = self.read_test_data(EC6945_REQUEST_FILE)
        self.mock_session.get.return_value.json.return_value = test_request
        
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        records = self.read_simem._get_records(url, self.mock_session)
        self.assertTrue(len(records), len(mock_records))
        self.apply_exception()

    def test_save_dataset(self):
        
        dataset_info = self.read_test_data(EC6945_DATASET_INFO_FILE)
        records = [self.read_test_data(EC6945_RECORDS_FILE)]
        dataset = self.read_simem._ReadSIMEM__save_dataset(dataset_info, records)
        dataset_metadata = dataset['result']['metadata']
        dataset_records = dataset['result']['records']
        
        mock_dataset = self.read_test_data(EC6945_REQUEST_FILE)
        mock_dataset_metadata = mock_dataset['result']['metadata']
        mock_dataset_records = mock_dataset['result']['records']

        self.assertEqual(dataset_metadata, mock_dataset_metadata)
        self.assertCountEqual(dataset_records, mock_dataset_records)
        self.apply_exception()

    @staticmethod
    def read_test_data(filename):
        path = os.getcwd()+os.sep + r'test/test_data/' + filename
        with open(path) as file:
            filedata = json.load(file)
        return filedata
    
    @staticmethod
    def apply_exception():
        global EXCEPTION
        EXCEPTION = True

    # def read_test_dataframe(self, filename):
    #     path = os.getcwd() + os.sep + r'test/test_data/' + filename
    #     dataframe = pd.read_csv(path)
    #     return dataframe

if __name__ == '__main__':
    unittest.main()
