import unittest
import sys
import os
import json
import pandas as pd
import datetime as dt
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pydatasimem import _Validation ,ReadSIMEM, VariableSIMEM

test_urls = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-04-13&datasetId=ec6945', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945']

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
            cls.dataset_id,
            cls.start_date,
            cls.end_date
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
        filter_url = getattr(self.read_simem, '_ReadSIMEM__filter_url', None)
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

    def test_get_records(self):
        mock_records = self.read_test_data(EC6945_RECORDS_FILE)
        test_request = self.read_test_data(EC6945_REQUEST_FILE)
        self.mock_request.get.return_value.json.return_value = test_request
        
        url = 'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-14&enddate=2024-04-16&datasetId=ec6945'
        records = self.read_simem._get_records(url, self.mock_request)
        self.assertTrue(len(records), len(mock_records))
        self.apply_exception()


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


class FakeReadSIMEM:

    def __init__(self, dataset_id, start_date, end_date, *args, **kwargs):
        self.dataset_id = dataset_id
        self.start_date = start_date
        self.end_date = end_date
 
    def main(self, filter=False):
        df = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-10", "2024-01-15", "2024-01-20"]),
            "Valor": [100, 200, 300],
            "CodigoVariable": ["PrecioEscasez"] * 3
        })
        return df
 
    def get_granularity(self):
        return "daily"
 
    def get_startdate(self):
        return "2024-01-10"
 
    def get_enddate(self):
        return "2024-01-20"
 
class TestVariableSIMEM(unittest.TestCase):
 
    def setUp(self):
        self.dummy_json = {
            "PrecioEscasez": {
                "name": "Precio de escasez",
                "dataset_id": "ae3f2",
                "var_column": "CodigoVariable",
                "value_column": "Valor",
                "version_column": "",
                "date_column": "Fecha",
                "maestra_column": "SISTEMA",
                "codMaestra_column": None,
                "esRegistro": 1,
                "esVersionado": 0
            }
        }
        patcher = patch.object(VariableSIMEM, '_read_json', return_value=self.dummy_json)
        self.addCleanup(patcher.stop)
        patcher.start()
 
        patcher2 = patch('src.pydatasimem.ReadSIMEM', FakeReadSIMEM)
        self.addCleanup(patcher2.stop)
        patcher2.start()
 
        self.var_simem = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31", esCalidad=False)
 
    def test_get_data(self):
        data = self.var_simem.get_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.index.name, "Fecha")
        self.assertEqual(len(data), 3)
 
    def test_describe_data(self):
        stats = self.var_simem.describe_data()
        expected = {
            "Precio de escasez": {
                "mean": 200.0,
                "median": 200.0,
                "std_dev": 100.0,
                "min": 100.0,
                "max": 300.0,
                "null_count": 0,
                "zero_count": 0,
                "start_date": "2024-01-10", 
                "end_date": "2024-01-20",   
                "granularity": "daily"
            }
        }
        self.assertEqual(stats, expected)
 
    @patch("src.pydatasimem.webbrowser.open")
    def test_time_series_data(self, mock_web_open):
        with patch("src.pydatasimem.go.Figure.write_html") as mock_write_html:
            self.var_simem.time_series_data()
            mock_write_html.assert_called_with("time_series_plot.html")
            mock_web_open.assert_called_with("time_series_plot.html")
 
    def test_get_structure_data(self):
        var_simem_calidad = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31", esCalidad=True)
        data = var_simem_calidad.get_data()
        expected_columns = ['fecha', 'codigoMaestra', 'codigoVariable', 'maestra', 'valor']
        self.assertListEqual(list(data.columns), expected_columns)

    def test_order_date(self):
        data = pd.DataFrame({
            'FechaInicio': ['2024-01-05', '2024-01-10', '2024-02-05', '2024-02-10'],
            'FechaPublicacion': ['2024-01-15', '2024-01-20', '2024-02-15', '2024-02-20']
        })
        data['FechaInicio'] = pd.to_datetime(data['FechaInicio'])
        data['FechaPublicacion'] = pd.to_datetime(data['FechaPublicacion'])
        
        ordered = VariableSIMEM._VariableSIMEM__order_date(data.copy(), 'FechaPublicacion')
        
        self.assertIn('month', ordered.columns)
        self.assertIn('order', ordered.columns)
        
        for month, group in ordered.groupby('month'):
            self.assertTrue((group['order'] == 0).any())
            self.assertTrue((group['order'] <= 0).all())

    def test_filter_by_order(self):
        df = pd.DataFrame({
            'month': [1, 1, 1, 2, 2, 2],
            'order': [0, -1, -2, 0, -1, -2],
            'value': [10, 20, 30, 40, 50, 60]
        })
 
        filtered = VariableSIMEM._VariableSIMEM__filter_by_order(df.copy(), 0)
        expected = df[df['order'] == 0].reset_index(drop=True).drop(columns=['month'])
        pd.testing.assert_frame_equal(filtered, expected)
 
        filtered2 = VariableSIMEM._VariableSIMEM__filter_by_order(df.copy(), 1)
        expected2 = df[df['order'] == 0].reset_index(drop=True).drop(columns=['month'])
        pd.testing.assert_frame_equal(filtered2, expected2)
 
        filtered3 = VariableSIMEM._VariableSIMEM__filter_by_order(df.copy(), -3)
        expected3 = df[df['order'] == -2].reset_index(drop=True).drop(columns=['month'])
        pd.testing.assert_frame_equal(filtered3, expected3)

    def test_calculate_stats(self):
        df = pd.DataFrame({
            'Valor': [100, 200, 300, None, 0]
        })
        dummy_json = {
            "PrecioEscasez": {
                "name": "Precio de escasez",
                "dataset_id": "dummy",
                "var_column": "CodigoVariable",
                "value_column": "Valor",
                "version_column": "",
                "date_column": "Fecha",
                "maestra_column": "SISTEMA",
                "codMaestra_column": None,
                "esRegistro": 1,
                "esVersionado": 0
            }
        }
        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json
        vs._VariableSIMEM__start_date = "2024-01-01"
        vs._VariableSIMEM__end_date = "2024-12-31"
        vs._VariableSIMEM__granularity = "daily"
 
        stats = VariableSIMEM._VariableSIMEM__calculate_stats(vs, df, 'Valor')
 
        expected_mean = 150.0         
        expected_median = 150.0        
        expected_std = float(pd.Series([100,200,300,0]).std()) 
        expected_min = 0.0
        expected_max = 300.0
        expected_null_count = 1
        expected_zero_count = 1
 
        self.assertEqual(stats['mean'], expected_mean)
        self.assertEqual(stats['median'], expected_median)
        self.assertAlmostEqual(stats['std_dev'], expected_std, places=2)
        self.assertEqual(stats['min'], expected_min)
        self.assertEqual(stats['max'], expected_max)
        self.assertEqual(stats['null_count'], expected_null_count)
        self.assertEqual(stats['zero_count'], expected_zero_count)
        self.assertEqual(stats['start_date'], "2024-01-01")
        self.assertEqual(stats['end_date'], "2024-12-31")
        self.assertEqual(stats['granularity'], "daily")

    def test_set_structure(self):
        dummy_json = {
            "PrecioEscasez": {
            "name": "Precio de escasez",
            "dataset_id": "dummy",
            "var_column": "CodigoVariable",
            "value_column": "Valor",
            "version_column": "",
            "date_column": "Fecha",
            "maestra_column": "SISTEMA",
            "codMaestra_column": None,
            "esRegistro": 1,
            "esVersionado": 0
            }
        }

        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json
 
        df = pd.DataFrame({
            "Fecha": ["2024-01-01", "2024-01-02"],
            "Valor": [100, 200],
            "CodigoVariable": ["PrecioEscasez", "PrecioEscasez"]
        })
 
        structured = VariableSIMEM._VariableSIMEM__set_structure(vs, df.copy())
 
        expected = pd.DataFrame({
            "fecha": ["2024-01-01", "2024-01-02"],
            "codigoMaestra": ["SISTEMA", "SISTEMA"],
            "codigoVariable": ["PrecioEscasez", "PrecioEscasez"],
            "maestra": ["SISTEMA", "SISTEMA"],
            "valor": [100, 200]
        })
        pd.testing.assert_frame_equal(structured.reset_index(drop=True), expected)

    def test_filter_date(self):
        dataset = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-05", "2024-01-10", "2024-01-15"]),
            "version": ["v1", "v1", "v1"],
            "Valor": [100, 200, 300]
        })
 
        dates_df = pd.DataFrame({
            "Version": ["v1"],
            "FechaInicio": [pd.to_datetime("2024-01-01")],
            "FechaFin": [pd.to_datetime("2024-01-12")],
            "FechaPublicacion": [pd.to_datetime("2024-01-01")],
            "EsMaximaVersion": [True],
            "order": [0]
        })
 
        result = VariableSIMEM._filter_date(dataset.copy(), dates_df, "Fecha", "version")
 
        if "index" in result.columns:
            result = result.drop(columns=["index", "Version"])
 
        expected = dataset[dataset["Fecha"].isin([pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-10")])].copy()
        expected.set_index(["Fecha", "version"], inplace=True)
 
        pd.testing.assert_frame_equal(result, expected)

    def test_calculate_version(self):
        dummy_json = {
            "PrecioEscasez": {
            "name": "Precio de escasez",
            "dataset_id": "dummy",
            "var_column": "CodigoVariable",
            "value_column": "Valor",
            "version_column": "Version",
            "date_column": "Fecha",
            "maestra_column": "SISTEMA",
            "codMaestra_column": None,
            "esRegistro": 1,
            "esVersionado": 1
            }
        }
 
        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json
        vs._VariableSIMEM__start_date = pd.to_datetime("2024-01-01")
        vs._VariableSIMEM__end_date = pd.to_datetime("2024-12-31")
 
        df = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-05", "2024-01-10", "2024-01-15"]),
            "Valor": [100, 200, 300],
            "CodigoVariable": ["PrecioEscasez"] * 3,
            "Version": ["v1", "v1", "v1"]
        })
 
        dummy_versions_df = pd.DataFrame({
            "Version": ["v1"],
            "FechaInicio": [pd.to_datetime("2024-01-01")],
            "FechaFin": [pd.to_datetime("2024-01-12")],
            "FechaPublicacion": [pd.to_datetime("2024-01-01")],
            "EsMaximaVersion": [True],
            "order": [0]
        })
 
        with patch.object(VariableSIMEM, "_VariableSIMEM__versions", return_value=dummy_versions_df):
            result = vs._calculate_version(df.copy(), 0)
 
        if "index" in result.columns:
            result = result.drop(columns=["index"])
 
        expected = df[df["Fecha"].isin([pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-10")])].copy()
        expected.set_index(["Fecha", "Version"], inplace=True)

        pd.testing.assert_frame_equal(result, expected)
 
    def test_read_validation(self):
        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
    
        mock_df = pd.DataFrame({"Fecha": ["2024-01-01"], "Valor": [100]})
    
        with patch.object(vs, "_read", return_value=mock_df) as mock_read:
            vs._VariableSIMEM__read_validation("2024-01-01", "2024-12-31")
 
            mock_read.assert_called_once()
 
            vs._VariableSIMEM__read_validation("2024-01-01", "2024-12-31")
            mock_read.assert_called_once() 
        
    def test_index_df(self):
        dummy_json_versioned = {
            "PrecioEscasez": {
            "name": "Precio de escasez",
            "dataset_id": "dummy",
            "var_column": "CodigoVariable",
            "value_column": "Valor",
            "version_column": "Version",
            "date_column": "Fecha",
            "esVersionado": 1
            }
        }
        dummy_json_non_versioned = {
            "PrecioEscasez": {
            "name": "Precio de escasez",
            "dataset_id": "dummy",
            "var_column": "CodigoVariable",
            "value_column": "Valor",
            "version_column": "",
            "date_column": "Fecha",
            "esVersionado": 0
            }
        }
 
        df = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Valor": [100, 200],
            "Version": ["v1", "v1"]
        })

        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json_versioned
        indexed_df = vs._index_df(df.copy())
        self.assertEqual(list(indexed_df.index.names), ["Fecha", "Version"])
 
        vs._VariableSIMEM__json_file = dummy_json_non_versioned
        indexed_df = vs._index_df(df.copy())
        self.assertEqual(list(indexed_df.index.names), ["Fecha"])
    
    def test_get_index_data(self):
        dummy_json = {
            "PrecioEscasez": {
            "name": "Precio de escasez",
            "dataset_id": "dummy",
            "var_column": "CodigoVariable",
            "value_column": "Valor",
            "version_column": "Version",
            "date_column": "Fecha",
            "esVersionado": 1
            }
        }
 
        df = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Valor": [100, 200],
            "Version": ["v1", "v1"]
        })
 
        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json
 
        with patch.object(vs, "_VariableSIMEM__read_validation") as mock_read_validation, \
            patch.object(vs, "_index_df", return_value=df.set_index(["Fecha", "Version"])) as mock_index_df, \
            patch.object(vs, "_calculate_version", return_value=df.set_index(["Fecha", "Version"])) as mock_calc_version:
 
            mock_read_validation.assert_called_once()
 
            mock_index_df.assert_called_once()
 
            mock_calc_version.assert_called_once()
            
    def test_show_info(self):
        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
 
        with patch.object(vs, "describe_data") as mock_describe, \
            patch.object(vs, "time_series_data") as mock_time_series:
 
            vs.show_info()
 
            mock_describe.assert_called_once()
            mock_time_series.assert_called_once()

if __name__ == '__main__':
    unittest.main()
