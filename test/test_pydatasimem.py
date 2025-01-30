import unittest
import sys
import os
import json
import pandas as pd
import datetime as dt
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pydatasimem import _Validation ,ReadSIMEM 

test_urls = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-04-13&datasetId=ec6945&columnDestinyName=&values=', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945&columnDestinyName=&values=']

EXCEPTION = False
EC6945_REQUEST_FILE = 'EC6945_request.json'
EC6945_RECORDS_FILE = 'EC6945_records.json'
EC6945_DATASET_INFO_FILE = 'EC6945_dataset_info.json'
API_RESULTS_FILE = 'API_results.json'

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
    @patch('src.pydatasimem.ReadSIMEM._make_request')
    def setUp(cls, mock_request):
        """
        Initialization previous to each test, creates a ReadSIMEM object.
        """
        # Every request replaced by the mock object and the return replaced 
        # by the information in the given file
        cls.mock_request = mock_request
        test_data = cls.read_test_data(EC6945_DATASET_INFO_FILE)
        cls.mock_request.return_value = test_data
        cls.dataset_id = "ec6945"
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
            # When no request is needed just continues with the execution 
            EXCEPTION = False
            return
        # Make sure that the mock is appearing where is needed
        cls.mock_request.assert_called_once()
        
    def test_set_datasetid(self):
        """
        Checks that the dataset ID initialized in setup is correct inside the ReadSIMEM object
        and the dataset ID is correctly changed inside the ReadSIMEM object
        
        """
        # Checks that the value initialized in setup is correct inside the object
        test_id = self.dataset_id
        init_id = self.read_simem._ReadSIMEM__dataset_id
        self.assertEqual(init_id, test_id)

    def test_set_dates(self):
        """
        Checks that the dates initialized in setup are correct inside the ReadSIMEM object
        and the dates are correctly changed inside the ReadSIMEM object
        """

        # Checks that the value initialized in setup is correct inside the object
        test_start_date = dt.datetime(2024, 4, 14, 0, 0)
        test_end_date = dt.datetime(2024, 4, 16, 0, 0)
        init_start_date = self.read_simem._ReadSIMEM__start_date
        init_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(init_start_date, test_start_date)
        self.assertEqual(init_end_date, test_end_date)

        # Checks that the value is correctly changed inside the object
        test_datetime_date = dt.datetime(2021, 1, 1, 0, 0)
        test_string_date = '2021-01-01'

        # Checks the result when a string is given
        self.read_simem.set_dates(test_string_date, test_string_date)
        changed_start_date = self.read_simem._ReadSIMEM__start_date
        changed_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(changed_start_date, test_datetime_date)
        self.assertEqual(changed_end_date, test_datetime_date)
        
        # Checks the result when entered a datetime object is given
        self.read_simem.set_dates(test_datetime_date, test_datetime_date)
        changed_start_date = self.read_simem._ReadSIMEM__start_date
        changed_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(changed_start_date, test_datetime_date)
        self.assertEqual(changed_end_date, test_datetime_date)
        self.apply_exception()


    def test_set_filter(self):
        """
        Checks that the filter is correctly assigned and the filter url attribute
        exists in the ReadSIMEM object.
        """
        test_list_filter = ('test_column', ["value1", "value2"])
        self.read_simem.set_filter(test_list_filter[0], test_list_filter[1])
        changed_filter = self.read_simem._filter_values
        self.assertEqual(changed_filter, test_list_filter)
        filter_url = getattr(self.read_simem, '_filter_url', None)
        self.assertIsNotNone(filter_url)
        self.apply_exception()
        
    def test_set_dataset_data(self):
        """
        Checks that the initialized information is correctly assigned to the attributes in 
        the ReadSIMEM object.
        """
        init_dataset_info = self.read_simem._ReadSIMEM__dataset_info
        self.assertIsInstance(init_dataset_info, dict)

        init_columns = self.read_simem._ReadSIMEM__columns
        self.assertIsInstance(init_columns, pd.DataFrame)
        self.assertFalse(init_columns.empty, "DataFrame is empty")

        init_metadata = self.read_simem._ReadSIMEM__metadata
        self.assertIsInstance(init_metadata, pd.DataFrame)
        self.assertFalse(init_metadata.empty, "DataFrame is empty")

        init_date_filter = self.read_simem._ReadSIMEM__date_filter
        self.assertIsInstance(init_date_filter, str)
        init_name = self.read_simem._ReadSIMEM__name
        self.assertIsInstance(init_name, str)
        init_granularity = self.read_simem._ReadSIMEM__granularity
        self.assertIsInstance(init_granularity, str)
        init_resolution = self.read_simem._ReadSIMEM__resolution
        self.assertIsInstance(init_resolution, int)

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

    # Deprecated 
    def test_get_records(self):
        mock_records = self.read_test_data(EC6945_RECORDS_FILE)
        test_request = self.read_test_data(EC6945_REQUEST_FILE)
        self.mock_request.get.return_value.json.return_value = test_request
        
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        records = self.read_simem._get_records(url, self.mock_request)
        self.assertTrue(len(records), len(mock_records))
        self.apply_exception()


    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.dump')
    def test_save_dataset_json_file(self, mock_json_dump, mock_open):
        """
        Test saving dataset to a JSON file.
        """
        result = {"result": {"metadata": {}, "records": []}}
        self.read_simem._ReadSIMEM__save_dataset(result, 'json')
        mock_open.assert_called_once_with('EC6945_2024-04-14_2024-04-16.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(result, mock_open(), ensure_ascii=False)

    @patch('pandas.DataFrame.to_csv')
    def test_save_dataset_csv_file(self, mock_to_csv):
        """
        Test saving dataset to a CSV file.
        """
        result = pd.DataFrame()
        self.read_simem._ReadSIMEM__save_dataset(result, 'csv')
        mock_to_csv.assert_called_once_with('EC6945_2024-04-14_2024-04-16.csv', encoding='utf-8', index=False)


    def test_get_datasetid(self):
        object_value = self.read_simem._ReadSIMEM__dataset_id
        function_return = self.read_simem.get_datasetid()
        self.assertEqual(object_value, function_return)
        self.apply_exception()


    def test_get_startdate(self):
        object_value = self.read_simem._ReadSIMEM__start_date
        function_return = self.read_simem.get_startdate()
        self.assertEqual(object_value, function_return)
        self.apply_exception()

    def test_get_enddate(self):
        object_value = self.read_simem._ReadSIMEM__end_date
        function_return = self.read_simem.get_enddate()
        self.assertEqual(object_value, function_return)
        self.apply_exception()

    def test_get_filter_url(self):
        test_list_filter = ('test_column', ["value1", "value2"])
        self.read_simem.set_filter(test_list_filter[0], test_list_filter[1])

        object_value = self.read_simem._ReadSIMEM__filter_url
        function_return = self.read_simem.get_filter_url()
        self.assertEqual(object_value, function_return)
        self.apply_exception()

    def test_get_filters(self):
        test_list_filter = ('test_column', ["value1", "value2"])
        self.read_simem.set_filter(test_list_filter[0], test_list_filter[1])
        object_value = self.read_simem._filter_values
        function_return = self.read_simem.get_filters()
        self.assertEqual(function_return, object_value)
        self.apply_exception()


    def test_get_resolution(self):
        object_value = self.read_simem._ReadSIMEM__resolution
        function_return = self.read_simem.get_resolution()
        self.assertEqual(function_return, object_value)
        self.apply_exception()


    def test_get_granularity(self):
        object_value = self.read_simem._ReadSIMEM__granularity
        function_return = self.read_simem.get_granularity()
        self.assertEqual(function_return,object_value)
        self.apply_exception()


    def test_get_metadata(self):
        function_return = self.read_simem.get_metadata()
        self.assertFalse(function_return.empty, "DataFrame is empty")
        self.apply_exception()


    def test_get_columns(self):
        function_return = self.read_simem.get_columns()
        self.assertFalse(function_return.empty, "DataFrame is empty")
        self.apply_exception()


    def test_get_name(self):
        object_value = self.read_simem._ReadSIMEM__name
        function_return = self.read_simem.get_name()
        self.assertEqual(function_return,object_value)
        self.apply_exception()


    def test_get_dataset_info(self):
        function_return = self.read_simem._ReadSIMEM__get_dataset_info()
        self.assertIsInstance(function_return, dict)
        self.apply_exception()

    def test_records_formating(self):
        data_api = self.read_test_data(API_RESULTS_FILE)
        result = self.read_simem._records_formating(data_api, 'json')
        self.assertIsInstance(result, dict)
        self.assertIn('result', result)
        self.assertIn('records', result['result'])
        self.assertEqual(len(result['result']['records']), 1080)

        result = self.read_simem._records_formating(data_api, 'csv')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1080)

        result = self.read_simem._records_formating(data_api, 'default')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 1080)


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


if __name__ == '__main__':
    unittest.main()
