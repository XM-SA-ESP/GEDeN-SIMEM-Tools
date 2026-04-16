import unittest
import sys
import os
import json
import pandas as pd
import datetime as dt
from unittest.mock import patch, MagicMock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.pydatasimem import _Validation ,ReadSIMEM, CatalogSIMEM, VariableSIMEM, MaestraSIMEM
import tempfile

TEST_RESPONSE = {
    "parameters": {"startDate": "", "endDate": ""},
    "result": {
        "records": [{'x': 1}],
        "metadata": {"granularity": "Diaria"},
        "columns": [{"name": "col"}],
        "filterDate": "Fecha",
        "name": "TestDataset"
    }
}

TEST_URLS = ['https://www.simem.co/backend-files/api/PublicData?startdate=2024-03-14&enddate=2024-03-31&datasetId=ec6945', 
             'https://www.simem.co/backend-files/api/PublicData?startdate=2024-04-01&enddate=2024-04-16&datasetId=ec6945']

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

    def test_datasetid_non_alphanumeric(self):
        with self.assertRaises(ValueError):
            _Validation.datasetid("abc123!")

    def test_cod_variable_invalid_type(self):
        list_variables = {"var1": {}, "var2": {}}
        with self.assertRaises(TypeError):
            _Validation.cod_variable(123, list_variables, "variable")

    def test_cod_variable_not_in_list(self):
        list_variables = {"var1": {}, "var2": {}}
        with self.assertRaises(ValueError):
            _Validation.cod_variable("var3", list_variables, "variable")

    def test_dataset_empty_dataframe(self):
        empty_df = pd.DataFrame()
        with self.assertRaises(TypeError):
            _Validation.dataset(empty_df, "2024-01-01", "2024-01-31")
    
    def test_validate_filter_ok_with_list_values(self):
        f = ["Campo", "=", ["A", "B"]]
        out = _Validation.validate_filter(f)
        self.assertEqual(out, f)

    def test_validate_filter_wrong_length(self):
        with self.assertRaises(TypeError):
            _Validation.validate_filter(["SoloDos", "="])

    def test_validate_filter_wrong_types(self):
        with self.assertRaises(TypeError):
            _Validation.validate_filter([123, "=", ["A"]])
        with self.assertRaises(TypeError):
            _Validation.validate_filter(["Campo", 123, ["A"]])
        with self.assertRaises(TypeError):
            _Validation.validate_filter(["Campo", "=", 123])
        with self.assertRaises(TypeError):
            _Validation.validate_filter(["Campo", "=", ["A", 1]])  # elemento no string

    def test_validate_operation_value_between_ok(self):
        op, val = _Validation.validate_operation_value("between", ["1", "2"])
        self.assertEqual(op, "between")
        self.assertEqual(val, "1,2")

    def test_validate_operation_value_in_requires_list(self):
        with self.assertRaises(ValueError):
            _Validation.validate_operation_value("in", "A")

    def test_validate_operation_value_gt_requires_string(self):
        with self.assertRaises(ValueError):
            _Validation.validate_operation_value(">", ["10"])

    def test_validate_operation_value_between_needs_two_values(self):
        with self.assertRaises(ValueError):
            _Validation.validate_operation_value("between", ["1"])

    def test_validate_operation_value_invalid_op(self):
        with self.assertRaises(TypeError):
            _Validation.validate_operation_value("foo", "bar")

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

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value=TEST_RESPONSE)
    @patch('src.pydatasimem.ReadSIMEM._get_records', return_value=[{"col": "val"}])
    @patch('src.pydatasimem.ReadSIMEM._ReadSIMEM__create_urls', return_value=["fake_url"])
    @patch('os.path.exists', return_value=True)
    @patch('src.pydatasimem.ReadSIMEM._ReadSIMEM__save_dataset', return_value="fake.csv")
    @patch('pandas.read_csv', return_value=pd.DataFrame([{"col": "val"}]))
    def test_main_with_save(self, mock_read_csv, mock_save, mock_exists, mock_urls, mock_records, mock_request):
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-10")
        result = obj.main(output_folder=".")
        self.assertIsInstance(result, pd.DataFrame)
        mock_save.assert_called_once()

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value=TEST_RESPONSE)
    def test_save_dataset_creates_file(self, mock_request):
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-10")
        with tempfile.TemporaryDirectory() as tmpdir:
            df = pd.DataFrame({"a": [1, 2]})
            file_path = obj._ReadSIMEM__save_dataset(tmpdir, df)
            self.assertTrue(os.path.exists(file_path))
            self.assertTrue(file_path.endswith(".csv"))

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value=TEST_RESPONSE)
    def test_save_dataset_without_result(self, mock_request):
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-10")
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = obj._ReadSIMEM__save_dataset(tmpdir, None)
            self.assertTrue(file_path.endswith(".csv"))

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

        test_start_date = dt.datetime(2024, 4, 14, 0, 0)
        test_end_date = dt.datetime(2024, 4, 16, 0, 0)
        init_start_date = self.read_simem._ReadSIMEM__start_date
        init_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(init_start_date, test_start_date)
        self.assertEqual(init_end_date, test_end_date)

        test_datetime_date = dt.datetime(2021, 1, 1, 0, 0)
        test_string_date = '2021-01-01'

        self.read_simem.set_dates(test_string_date, test_string_date)
        changed_start_date = self.read_simem._ReadSIMEM__start_date
        changed_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(changed_start_date, test_datetime_date)
        self.assertEqual(changed_end_date, test_datetime_date)
        
        self.read_simem.set_dates(test_datetime_date, test_datetime_date)
        changed_start_date = self.read_simem._ReadSIMEM__start_date
        changed_end_date = self.read_simem._ReadSIMEM__end_date
        self.assertEqual(changed_start_date, test_datetime_date)
        self.assertEqual(changed_end_date, test_datetime_date)
        self.apply_exception()

    def test_set_dataset_data(self):
        """
        Checks that the initialized information is correctly assigned to the attributes in 
        the ReadSIMEM object.
        """

        init_columns = self.read_simem._ReadSIMEM__columns
        self.assertIsInstance(init_columns, pd.DataFrame)
        self.assertFalse(init_columns.empty, "DataFrame is empty")

        init_metadata = self.read_simem._ReadSIMEM__metadata
        self.assertIsInstance(init_metadata, pd.DataFrame)
        self.assertFalse(init_metadata.empty, "DataFrame is empty")

        init_name = self.read_simem._ReadSIMEM__name
        self.assertIsInstance(init_name, str)
        init_granularity = self.read_simem._ReadSIMEM__granularity
        self.assertIsInstance(init_granularity, str)
        init_resolution = self.read_simem._ReadSIMEM__resolution
        self.assertIsInstance(init_resolution, int)

    def test_check_date_resolution(self):
        
        test_granularity = "Horaria"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 1)

        test_granularity = "Mensual"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 24)

        test_granularity = "Anual"
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)
        self.assertEqual(resolution, 60)

        test_granularity = ""
        resolution = self.read_simem._ReadSIMEM__check_date_resolution(test_granularity)        
        self.assertEqual(resolution, 0)
        self.apply_exception()
    
    def test_generate_start_dates(self):
        initial_date = dt.datetime(2024, 3, 14, 0, 0)
        final_date = dt.datetime(2024, 4, 16, 0, 0)
        resolution = 1
        obj = self.read_simem
        dates = list(obj._generate_dates(initial_date, final_date, resolution))
        mock_dates = [['2024-03-14', '2024-04-01'], ['2024-03-31', '2024-04-16']]
        self.assertListEqual(dates, mock_dates)
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

    def test_generate_dates_basic(self):
        start = dt.datetime(2024, 1, 15)
        end = dt.datetime(2024, 3, 10)
        start_dates, end_dates = ReadSIMEM._generate_dates(start, end, resolution=1)
        self.assertTrue(len(start_dates) > 0)
        self.assertTrue(len(end_dates) > 0)
        self.assertEqual(start_dates[0], "2024-01-15")

    @patch('src.pydatasimem.ReadSIMEM._make_request')  # Evita red en __init__ -> _set_dataset_data
    def test__create_urls_builds_expected_urls(self, mock_req):
        # Respuesta mínima para que __init__ no truene
        mock_req.return_value = {
            "parameters": {"startDate": "", "endDate": ""},
            "result": {
                "metadata": {"granularity": "Diaria"},
                "columns": [{"name": "col"}],
                "filterDate": "Fecha",
                "name": "Dataset"
            }
        }
        # Importante: también parcheamos requests.Session para que __init__ no abra sesión real
        with patch('requests.Session'):
            obj = ReadSIMEM("ec6945", "2024-03-14", "2024-04-16")
            # Forzamos generate_dates (no usa red) para controlar las fechas
            with patch('src.pydatasimem.ReadSIMEM._generate_dates',
                       return_value=(["2024-03-14", "2024-04-01"],
                                     ["2024-03-31", "2024-04-16"])):
                urls = obj._ReadSIMEM__create_urls(obj.get_startdate(), obj.get_enddate(), obj.get_resolution())
                expected = [
                    "https://www.simem.co/backend-files/api/datos-publicos?startDate=2024-03-14&endDate=2024-03-31&datasetId=ec6945",
                    "https://www.simem.co/backend-files/api/datos-publicos?startDate=2024-04-01&endDate=2024-04-16&datasetId=ec6945",
                ]
                self.assertListEqual(urls, expected)

    @patch('src.pydatasimem.ReadSIMEM._make_request')
    @patch('requests.Session')  # Evita sesión real en __init__
    def test__get_filter_and_setfilter_getfilters(self, mock_sess, mock_req):
        mock_req.return_value = {
            "parameters": {"startDate": "", "endDate": ""},
            "result": {
                "metadata": {"granularity": "Diaria"},
                "columns": [{"name": "col"}],
                "filterDate": "Fecha",
                "name": "Dataset"
            }
        }
        obj = ReadSIMEM("aecac4", "2024-01-01", "2024-01-31")

        # __get_filter (estático-privado): sólo transforma a estructura de API (sin postear nada)
        raw = ["Valor", "between", ["80", "100"]]
        flt = ReadSIMEM._ReadSIMEM__get_filter(raw)
        self.assertEqual(flt[0]["Fd"], "Valor")
        self.assertEqual(flt[0]["Op"], "btw")
        self.assertEqual(flt[0]["Vl"], "80,100")

        # set_filter / get_filters (estado interno)
        with self.assertRaises(TypeError):
            obj.set_filter(None)
        obj.set_filter(raw)
        gf = obj.get_filters()
        self.assertIsInstance(gf, list)
        self.assertEqual(gf[0]["Fd"], "Valor")

    @patch('src.pydatasimem.ReadSIMEM._make_request')
    @patch('requests.Session')
    def test__get_filter_bool_flag(self, mock_sess, mock_req):
        mock_req.return_value = {
            "parameters": {"startDate": "", "endDate": ""},
            "result": {"metadata": {"granularity": "Diaria"},
                       "columns": [{"name": "c"}],
                       "filterDate": "Fecha", "name": "Dataset"}
        }
        obj = ReadSIMEM("aecac4", "2024-01-01", "2024-01-31")
        obj._ReadSIMEM__filter = True
        self.assertTrue(obj._ReadSIMEM__get_filter_bool())

    @patch('src.pydatasimem.ReadSIMEM._make_request')
    @patch('requests.Session')
    def test__set_datasetid_affects_urls(self, mock_sess, mock_req):
        mock_req.return_value = {
            "parameters": {"startDate": "", "endDate": ""},
            "result": {"metadata": {"granularity": "Diaria"},
                       "columns": [{"name": "col"}],
                       "filterDate": "Fecha",
                       "name": "Dataset"}
        }
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-31")
        # El __init__ ya agregó datasetId a url_data_api y url_info_api
        self.assertIn("&datasetId=abc123", obj.url_data_api)

        # Si pido catalog=True, anexa a url_api
        obj._set_datasetid("zz99zz", catalog=True)
        self.assertIn("&datasetId=zz99zz", obj.url_api)

    def test__make_request_get_and_post_only_with_mock_session(self):
        # Creamos una sesión falsa y respuestas falsas; no hay red real
        mock_session = MagicMock()

        # GET -> data con 'success' y 'parameters'
        resp_get = MagicMock()
        resp_get.status_code = 200
        resp_get.json.return_value = {
            "success": True,
            "parameters": {"idDataset": "xxxxxx"},
            "result": {"records": [{"a": 1}]}
        }

        # POST -> data genérica
        resp_post = MagicMock()
        resp_post.status_code = 200
        resp_post.json.return_value = {"records": [{"b": 2}]}

        mock_session.get.return_value = resp_get
        mock_session.post.return_value = resp_post

        # GET
        out_get = ReadSIMEM._make_request("http://dummy", mock_session, type='get', filter=False)
        self.assertIn("result", out_get)

        # POST sin filtro
        out_post = ReadSIMEM._make_request("http://dummy", mock_session, type='post', filter=False)
        self.assertIn("records", out_post)

        # POST con filtro
        out_post_f = ReadSIMEM._make_request(
            "http://dummy", mock_session, type='post', filter=True, filters=[{"Fd": "X"}]
        )
        self.assertIn("records", out_post_f)

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value={
        "parameters": {"startDate": "", "endDate": ""},
        "result": {
            "metadata": {"granularity": "Diaria"},
            "columns": [{"name": "col"}],
            "filterDate": "Fecha",
            "name": "TestDataset"
        }
    })
    @patch('requests.Session')  # evita abrir sesiones reales
    def test__set_dataset_data_populates_attributes(self, mock_sess, mock_req):
        # Instanciará y llamará _set_dataset_data en __init__, pero con mocks
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-31")
        # Afirmamos el estado (sin red)
        self.assertIsInstance(obj.get_columns(), pd.DataFrame)
        self.assertIsInstance(obj.get_metadata(), pd.DataFrame)
        self.assertIsInstance(obj.get_name(), str)
        self.assertIn(obj.get_granularity(), ["Diaria", "Horaria", "Mensual", "Semanal", "Anual"])

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value=TEST_RESPONSE)
    @patch('requests.Session')
    def test__get_records_get_and_zero(self, mock_sess, mock_mr):
        # Instancia sin red: __init__ también queda amortiguado por Session mock + _make_request mock
        obj = ReadSIMEM("abc123", "2024-01-01", "2024-01-31")

        # GET -> lista con 1 registro (no hay red real)
        out = obj._get_records("http://dummy", session=MagicMock(), type='get')
        self.assertEqual(out, [{"x": 1}])

        # GET -> cero registros
        with patch('src.pydatasimem.ReadSIMEM._make_request', return_value={"result": {"records": []}}):
            out0 = obj._get_records("http://dummy", session=MagicMock(), type='get')
            self.assertEqual(out0, [])

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

class TestCatalogSIMEM(unittest.TestCase):

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value={
        "parameters": {},
        "result": {
            "metadata": {"granularity": "Diaria"},
            "columns": [{"name": "col"}],
            "filterDate": "Fecha",
            "name": "CatalogTest"
        }
    })
    @patch('src.pydatasimem.ReadSIMEM._get_records', return_value=[{"id": 1, "name": "test"}])
    def test_init_and_get_data_datasets(self, mock_records, mock_request):
        obj = CatalogSIMEM("datasets")
        data = obj.get_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn("name", data.columns)

    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value={
        "parameters": {},
        "result": {
            "metadata": {"granularity": "Diaria"},
            "columns": [{"name": "col"}],
            "filterDate": "Fecha",
            "name": "CatalogTest"
        }
    })
    @patch('src.pydatasimem.ReadSIMEM._get_records', return_value=[{"id": 2, "name": "variable"}])
    def test_init_and_get_data_variables(self, mock_records, mock_request):
        obj = CatalogSIMEM("variables")
        data = obj.get_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn("name", data.columns)
    
    @patch('src.pydatasimem.ReadSIMEM._set_datasetid')
    @patch('src.pydatasimem.ReadSIMEM._get_records', return_value=[{"id": 1}])
    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value={
        "parameters": {}, "result": {"metadata": {"granularity": "Diaria"},
                                     "columns": [{"name": "col"}],
                                     "filterDate": "Fecha", "name": "Catalog"}})
    def test_init_datasets_calls_set_datasetid_with_catalog_id(self, mock_req, mock_records, mock_setid):
        obj = CatalogSIMEM("datasets")
        mock_setid.assert_called()   # llamado con catalog=True y catalog_id
        self.assertFalse(obj.get_data().empty)

    @patch('src.pydatasimem.ReadSIMEM._set_datasetid')
    @patch('src.pydatasimem.ReadSIMEM._get_records', return_value=[{"id": 2}])
    @patch('src.pydatasimem.ReadSIMEM._make_request', return_value={
        "parameters": {}, "result": {"metadata": {"granularity": "Diaria"},
                                     "columns": [{"name": "col"}],
                                     "filterDate": "Fecha", "name": "Catalog"}})
    def test_init_variables_calls_set_datasetid_with_variable_inventory_id(self, mock_req, mock_records, mock_setid):
        obj = CatalogSIMEM("variables")
        mock_setid.assert_called()
        self.assertFalse(obj.get_data().empty)

class TestVariableSIMEM(unittest.TestCase):
 
    def setUp(self):
        self.dummy_json = {
            "variable": {
                "PrecioEscasez": {
                    "name": "Precio de escasez",
                    "dataset_id": "ae3f2",
                    "var_column": "CodigoVariable",
                    "value_column": "Valor",
                    "version_column": None,
                    "date_column": "Fecha",
                    "dimensions": [],
                    "maestra_column": "SISTEMA",
                    "codMaestra_column": None,
                    "esTX2PrimeraVersion": 0
                }
            }
        }
        patcher = patch.object(VariableSIMEM, '_read_json', return_value=self.dummy_json)
        self.addCleanup(patcher.stop)
        patcher.start()
        patcher2 = patch('src.pydatasimem.ReadSIMEM', FakeReadSIMEM)
        self.addCleanup(patcher2.stop)
        patcher2.start()
        self.var_simem = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31", quality_check=False)

        self.df_versions = pd.DataFrame({
            'Version': ['TX1', 'TX2', 'TXR'],
            'FechaInicio': ['2024-01-01', '2024-01-01', '2024-01-01'],
            'FechaFin': ['2024-01-31', '2024-01-31', '2024-01-31'],
            'FechaPublicacion': ['2024-01-10', '2024-01-11', '2024-01-12'],
            'EsMaximaVersion': [1, 0, 0],
            'order': [0, 1, 2]
        })

    @patch('requests.get')
    def test_read_json_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"variable": {"var1": {"name": "TestVar"}}}
        mock_get.return_value = mock_response

        result = VariableSIMEM._read_json()
        self.assertIn("variable", result)

    @patch.object(VariableSIMEM, "_read_json", return_value={"variable": {"test_var": {"name": "Test Variable"}}})
    def test_read_json_returns_expected_dict(self, mock_read_json):
        result = VariableSIMEM._read_json()
        self.assertIn("test_var", result["variable"])
        self.assertEqual(result["variable"]["test_var"]["name"], "Test Variable")

    @patch.object(VariableSIMEM, "_read_json", return_value={
        "variable": {
            "var1": {"name": "TestVar", "dimensions": ["dim1"], "version_column": "vcol", "date_column": "dcol"}
        }
    })
    def test_get_collection_structure(self, mock_json):
        df = VariableSIMEM.get_collection()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("CodigoVariable", df.columns)
        self.assertIn("Nombre", df.columns)
        self.assertIn("Dimensiones", df.columns)
        self.assertTrue(any("vcol" in dims or "dcol" in dims for dims in df["Dimensiones"]))
 
    def test_get_data(self):
        data = self.var_simem.get_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.index.name, "Fecha")
        self.assertEqual(len(data), 3)
 
    def test_get_structure_data(self):
        var_simem_calidad = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31", quality_check=True)
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
        
        ordered = VariableSIMEM._order_date(data.copy(), 'FechaPublicacion')
        
        self.assertIn('month', ordered.columns)
        self.assertIn('order', ordered.columns)
        
        for month, group in ordered.groupby('month'):
            self.assertTrue((group['order'] == 0).any())
            self.assertTrue((group['order'] <= 0).all())

    def test_calculate_stats(self):
        df = pd.DataFrame({
            'Valor': [100, 200, 300, None, 0]
        })
        dummy_json = {
            "variable": {
                "PrecioEscasez": {
                    "name": "Precio de escasez",
                    "dataset_id": "ae3f2",
                    "var_column": "CodigoVariable",
                    "value_column": "Valor",
                    "version_column": None,
                    "date_column": "Fecha",
                    "dimensions": [],
                    "maestra_column": "SISTEMA",
                    "codMaestra_column": None,
                    "esTX2PrimeraVersion": 0
                    }
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

    def test_filter_date(self):
        dataset = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-05", "2024-01-10", "2024-01-15"]),
            "Valor": [100, 200, 300],
            "CodigoVariable": ["PrecioEscasez"] * 3,
            "Version": ["v1", "v1", "v2"]
        })

        dataset.set_index(["Fecha", "Version"], inplace=True)
 
        dates_df = pd.DataFrame({
            "Version": ["v1"],
            "FechaInicio": [pd.to_datetime("2024-01-01")],
            "FechaFin": [pd.to_datetime("2024-01-12")],
            "FechaPublicacion": [pd.to_datetime("2024-01-01")],
            "esMaximaVersion": [True],
            "order": [0]
        })
 
        result = VariableSIMEM._filter_date(dataset.copy(), dates_df, "Fecha", "Version")
 
        dataset.reset_index(inplace=True)
        expected = dataset[dataset["Fecha"].isin([pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-10")])].copy()
        expected.set_index(["Fecha", "Version"], inplace=True)
 
        pd.testing.assert_frame_equal(result, expected)
        
    def test_index_df(self):
        dummy_json = {
            "variable": {
                "PrecioEscasez": {
                    "name": "Precio de escasez",
                    "dataset_id": "ae3f2",
                    "var_column": "CodigoVariable",
                    "value_column": "Valor",
                    "version_column": None,
                    "date_column": "Fecha",
                    "dimensions": [],
                    "maestra_column": "SISTEMA",
                    "codMaestra_column": None,
                    "esTX2PrimeraVersion": 0
                    }
                }
        }
 
        df = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "Valor": [100, 200],
            "Version": ["v1", "v1"]
        })

        vs = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-12-31")
        vs._VariableSIMEM__json_file = dummy_json
        indexed_df = vs._index_df(df.copy())
        self.assertEqual(list(indexed_df.index.names), ["Fecha"])

    def test_filter_group_by_order_esTX2_true(self):
        result = VariableSIMEM._filter_group_by_order(self.df_versions, 'Version', 'order', 0, esTX2=1)
        self.assertTrue((result['Version'] == 'TX2').all())

    def test_filter_group_by_order_order_value_present(self):
        result = VariableSIMEM._filter_group_by_order(self.df_versions, 'Version', 'order', 1, esTX2=0)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['order'], 1)

    def test_filter_group_by_order_order_value_greater_than_max(self):
        result = VariableSIMEM._filter_group_by_order(self.df_versions, 'Version', 'order', 99, esTX2=0)
        self.assertEqual(result.iloc[0]['order'], self.df_versions['order'].max())

    def test_filter_group_by_order_order_value_less_than_min_adds_TX1_or_TX2(self):
        df_no_tx = self.df_versions[self.df_versions['Version'] == 'TXR'].copy()
        result = VariableSIMEM._filter_group_by_order(df_no_tx, 'Version', 'order', -5, esTX2=0)
        self.assertIn('TX1', result['Version'].values)

    def test_get_last_registry_returns_last_row(self):
        last_row = VariableSIMEM._get_last_registry(self.df_versions)
        self.assertEqual(last_row['Version'], 'TXR')
        self.assertEqual(last_row['order'], 2)

    def test_set_order_version_adds_new_row_TX2(self):
        registry = VariableSIMEM._get_last_registry(self.df_versions)
        updated_df = VariableSIMEM._set_order_version(self.df_versions.copy(), registry, self.df_versions['order'], version='TX2')
        self.assertTrue(len(updated_df) > len(self.df_versions))
        self.assertIn('TX2', updated_df['Version'].values)

    def test_set_order_version_adds_new_row_TX1(self):
        registry = VariableSIMEM._get_last_registry(self.df_versions)
        updated_df = VariableSIMEM._set_order_version(self.df_versions.copy(), registry, self.df_versions['order'], version='TX1')
        self.assertTrue(len(updated_df) > len(self.df_versions))
        self.assertIn('TX1', updated_df['Version'].values)

    def test_filter_by_version_existing_version(self):
        df = self.df_versions.copy()
        df['month'] = [1, 1, 1]
        result = VariableSIMEM._filter_by_version(df, version_value='TX2', start_date='2024-01-01', end_date='2024-01-31')
        self.assertTrue((result['Version'] == 'TX2').all())

    def test_filter_by_version_adds_missing_version(self):
        df_no_tx = self.df_versions[self.df_versions['Version'] == 'TXR'].copy()
        df_no_tx['month'] = [1]
        result = VariableSIMEM._filter_by_version(df_no_tx, version_value='TX1', start_date='2024-01-01', end_date='2024-01-31')


    def test_filter_group_by_version_existing_version(self):
        df = self.df_versions.copy()
        result = VariableSIMEM._filter_group_by_version(df, 'Version', 'order', 'TX2')
        self.assertTrue((result['Version'] == 'TX2').all())

    def test_filter_group_by_version_adds_version_if_missing(self):
        df_no_tx = self.df_versions[self.df_versions['Version'] == 'TXR'].copy()
        result = VariableSIMEM._filter_group_by_version(df_no_tx, 'Version', 'order', 'TX1')
        self.assertIn('TX1', result['Version'].values)

    @patch.object(VariableSIMEM, '_process_month', return_value=pd.DataFrame({
        'Version': ['TX1'],
        'FechaInicio': ['2024-02-01'],
        'FechaFin': ['2024-02-28'],
        'FechaPublicacion': ['2024-02-10'],
        'EsMaximaVersion': [1],
        'order': [0],
        'month': [2]
    }))
    def test_generate_missing_months_adds_data(self, mock_process):
        df = pd.DataFrame({
            'Version': ['TX1'],
            'FechaInicio': ['2024-01-01'],
            'FechaFin': ['2024-01-31'],
            'FechaPublicacion': ['2024-01-10'],
            'EsMaximaVersion': [1],
            'order': [0],
            'month': [1]
        })
        result = VariableSIMEM._generate_missing_months(df, start_date='2024-01-01', end_date='2024-02-28')
        self.assertTrue(any(result['FechaInicio'] == '2024-02-01'))
        mock_process.assert_called_once()

    @patch('src.pydatasimem.ReadSIMEM.main', return_value=pd.DataFrame({
        'FechaInicio': ['2024-02-01'],
        'FechaPublicacion': ['2024-02-10'],
        'order': [0]
    }))
    def test_process_month_returns_dataframe(self, mock_main):
        result = VariableSIMEM._process_month('2024-02-01')
        self.assertIsInstance(result, pd.DataFrame)
        self.assertIn('FechaPublicacion', result.columns)
        mock_main.assert_called_once()
    
    @patch('src.pydatasimem.ReadSIMEM.__init__', return_value=None)  # Evita side-effects/red al instanciar
    @patch('src.pydatasimem.ReadSIMEM.main', return_value=pd.DataFrame({
        'Version': ['TX1', 'TX2'],
        'FechaInicio': ['2024-01-01', '2024-01-01'],
        'FechaFin': ['2024-01-31', '2024-01-31'],
        'FechaPublicacion': ['2024-01-10', '2024-01-11'],
        'EsMaximaVersion': [1, 0],
        'order': [0, 1],
        'month': [1, 1]
    }))
    @patch.object(VariableSIMEM, '_order_date', side_effect=lambda dataset, date_column: dataset.assign(month=[1, 1]))
    @patch.object(VariableSIMEM, '_filter_by_version', return_value=pd.DataFrame({'Version': ['TX2']}))
    def test_versions_with_string_version(self, mock_filter_by_version, mock_order_date, mock_main, mock_init):
        if not hasattr(VariableSIMEM, '_cache'):
            VariableSIMEM._cache = {}
        else:
            VariableSIMEM._cache.clear()

        result = VariableSIMEM._versions(
            pd.to_datetime('2024-01-01'),
            pd.to_datetime('2024-01-31'),
            'dummy_id',
            version='TX2',
            esTX2=False
        )

        self.assertTrue((result['Version'] == 'TX2').all())

        mock_init.assert_called_once()
        mock_main.assert_called_once()
        mock_order_date.assert_called_once()
        mock_filter_by_version.assert_called_once()

    @patch('src.pydatasimem.ReadSIMEM.main', return_value=pd.DataFrame({
        'Version': ['TX1', 'TX2'],
        'FechaInicio': ['2024-01-01', '2024-01-01'],
        'FechaFin': ['2024-01-31', '2024-01-31'],
        'FechaPublicacion': ['2024-01-10', '2024-01-11'],
        'EsMaximaVersion': [1, 0],
        'order': [0, 1],
        'month': [1, 1]
    }))
    @patch.object(VariableSIMEM, '_order_date', side_effect=lambda dataset, date_column: dataset.assign(month=[1, 1]))
    @patch.object(VariableSIMEM, '_filter_by_order', return_value=pd.DataFrame({'Version': ['TX1']}))
    def test_versions_with_int_version(self, mock_filter, mock_order, mock_main):
        result = VariableSIMEM._versions(pd.to_datetime('2024-01-01'),
                                        pd.to_datetime('2024-01-31'),
                                        'dummy_id', version=1, esTX2=False)
        self.assertTrue((result['Version'] == 'TX1').all())
        mock_filter.assert_called_once()

    def test_validate_version_df_empty_adds_dummy(self):
        empty_df = pd.DataFrame()
        result = VariableSIMEM._validate_version_df(empty_df, first_date=pd.to_datetime('2024-01-01'))
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Version'], '0')

    def test_validate_version_df_non_empty_returns_same(self):
        df = pd.DataFrame({'Version': ['TX1']})
        result = VariableSIMEM._validate_version_df(df, first_date=pd.to_datetime('2024-01-01'))
        self.assertTrue(result.equals(df))

    @patch.object(VariableSIMEM, '_versions', return_value=pd.DataFrame({
        'Version': ['TX1'],
        'FechaInicio': ['2024-01-01'],
        'FechaFin': ['2024-01-31'],
        'FechaPublicacion': ['2024-01-10'],
        'EsMaximaVersion': [1],
        'order': [0]
    }))
    @patch.object(VariableSIMEM, '_filter_date', return_value=pd.DataFrame({'Fecha': ['2024-01-10'], 'Version': ['TX1']}))
    def test_calculate_version_filters_correctly(self, mock_filter_date, mock_versions):
        df = pd.DataFrame({'Fecha': ['2024-01-10'], 'Valor': [100], 'Version': ['TX1']})
        result = self.var_simem._calculate_version(df, version='TX1')
        self.assertIn('Fecha', result.columns)
        mock_filter_date.assert_called_once()

    @patch.object(VariableSIMEM, '_read_dataset_data')
    @patch.object(VariableSIMEM, '_index_df', return_value=pd.DataFrame({
        'Fecha': ['2024-01-10', '2024-01-11'],
        'Valor': [100, 200],
        'Version': ['TX1', 'TX1']
    }))
    def test_describe_data_returns_statistics(self, mock_index, mock_read):
        self.var_simem._VariableSIMEM__granularity = "daily"
        stats = self.var_simem.describe_data()
        self.assertIsInstance(stats, dict)
        self.assertIn('Precio de escasez', stats)
        self.assertIn('mean', stats['Precio de escasez'])
        self.assertEqual(stats['Precio de escasez']['mean'], 150.0)
    
    def test_create_filter_merges_correctly(self):
        f1 = ["CodigoVariable", "=", "PrecioEscasez"]
        f2 = ["Valor", ">", "0"]
        out = VariableSIMEM.create_filter(f1, f2)
        self.assertEqual(len(out), 2)
        self.assertIn(f1, out)
        self.assertIn(f2, out)

        # Si f2 es lista de listas, se agrega f1 al final
        out2 = VariableSIMEM.create_filter(f1, [f2])
        self.assertEqual(out2, [f2, f1])

    @patch('src.pydatasimem.ReadSIMEM')
    def test__read_dataset_data_builds_filter_and_sets_data(self, FakeRead):
        # Fake ReadSIMEM.main() regresa dataset simple
        FakeRead.return_value.main.return_value = pd.DataFrame({
            "Fecha": pd.to_datetime(["2024-01-10"]),
            "Valor": [100],
            "CodigoVariable": ["PrecioEscasez"],
            "Version": ["TX1"]
        })
        v = VariableSIMEM("PrecioEscasez", "2024-01-01", "2024-01-31")
        out = v._read_dataset_data("2024-01-01", "2024-01-31")
        self.assertIsInstance(out, pd.DataFrame)
        self.assertEqual(out.shape[0], 1)
    
class TestMaestraSIMEM(unittest.TestCase):

    def setUp(self):
        self.dummy_json_maestra = {
            "maestra": {
                "SISTEMA": {
                    "name": "Sistema Eléctrico",
                    "dataset_id": "m12345",
                    "var_column": "CodigoMaestra",
                    "date_column": "Fecha",
                    "version_column": None,
                    "value_column": "Valor",
                    "dimensions": []
                }
            }
        }

    @patch.object(VariableSIMEM, '_read_json', return_value={"maestra": {
        "SISTEMA": {
            "name": "Sistema Eléctrico",
            "dataset_id": "m12345",
            "var_column": "CodigoMaestra",
            "date_column": "Fecha",
            "version_column": None,
            "value_column": "Valor",
            "dimensions": []
        }
    }})
    @patch('src.pydatasimem._Validation.cod_variable', return_value="SISTEMA")
    def test_init_sets_attributes_correctly(self, mock_cod_variable, mock_read_json):
        obj = MaestraSIMEM(maestra="SISTEMA", start_date="2024-01-01", end_date="2024-01-31")
        self.assertEqual(obj._var, "SISTEMA")
        self.assertEqual(obj._dataset_id, "m12345")
        self.assertEqual(obj._variable_column, "CodigoMaestra")
        self.assertEqual(obj._date_column, "Fecha")
        self.assertEqual(obj._value_column, "Valor")
        self.assertEqual(obj._start_date.strftime("%Y-%m-%d"), "2024-01-01")
        self.assertEqual(obj._end_date.strftime("%Y-%m-%d"), "2024-01-31")

    @patch.object(VariableSIMEM, '_read_json', return_value={
        "maestra": {
            "SISTEMA": {"name": "Sistema Eléctrico", "dimensions": ["Region"]},
            "AREA": {"name": "Área Operativa", "dimensions": ["Zona"]}
        }
    })
    def test_get_collection_returns_dataframe(self, mock_read_json):
        df = MaestraSIMEM.get_collection()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("Maestra", df.columns)
        self.assertIn("Descripción", df.columns)
        self.assertIn("Cruces", df.columns)
        self.assertTrue(len(df) >= 2)

if __name__ == '__main__':
    unittest.main()
