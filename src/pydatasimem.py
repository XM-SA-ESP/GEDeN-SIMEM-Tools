"""
Module built to simplify the integration of python with the SIMEM open data API 

Author: Sebastian Montoya
"""
import sys
import os
import requests
import logging
import pandas as pd
from dataclasses import dataclass
import datetime as dt
import time 
from itertools import repeat


DATASETID = ""
VARIABLE_INVENTORY_ID = "a5a6c4"
CATALOG_ID =  "e007fb"
REFERENCE_DATE = '1990-01-01'
DATE_FORMAT = "%Y-%m-%d"
TODAY = dt.datetime.strftime(dt.datetime.now(), DATE_FORMAT)
BASE_API_URL = "https://www.simem.co/backend-files/api/PublicData?startdate={}&enddate={}"


class _Validation:
    
    @staticmethod 
    def log_approve(variable):
        approve_message = f"Variable values validated: {variable}"
        logging.debug(approve_message)

    @staticmethod
    def filter(var_column : str, var_values: str | list) -> None | tuple[str,list]:
        if not var_column and not var_values:
            logging.info("No filter has been chosen.")
            return None
        if not var_column or not var_values:
            logging.info("Check that the column and values are both defined for the filter. No filter has been chosen")
            return None
        if not isinstance(var_column, str):
            raise TypeError("Column filter must be a string")
        if isinstance(var_values, str):
            var_values = [var_values]
        elif not isinstance(var_values, list):
            raise TypeError("Values filter must be a string or a list")
        var_filter = (var_column, var_values)
        _Validation.log_approve(var_filter)
        return var_filter
    
    @staticmethod
    def date(var_date) -> dt.datetime:
        try:  
            if isinstance(var_date, dt.datetime):
                return var_date
            var_date = dt.datetime.strptime(var_date, DATE_FORMAT)
            return var_date
        except ValueError:
            raise ValueError("Incorrect date format, use YYYY-MM-DD")


    @staticmethod
    def datasetid(var_dataset_id: str):
        if not isinstance(var_dataset_id, str):
            raise TypeError("Incorrect data type for ID, must be a string")
        var_dataset_id = var_dataset_id.strip()
        if len(var_dataset_id) > 6:
            raise ValueError("Invalid dataset ID")
        if not var_dataset_id.isalnum():
            raise ValueError("Dataset ID must be alphanumeric")
        _Validation.log_approve(var_dataset_id)
        return var_dataset_id
    
    @staticmethod
    def catalog_type(cat_type: str):
        if not isinstance(cat_type, str):
            raise TypeError("Incorrect data type for catalog type, must be a string")
        cat_type = cat_type.lower()
        if cat_type not in ('datasets', 'variables'):
            raise ValueError("Wrong parameter registered. Write 'Datasets' or 'Variables'.")
        _Validation.log_approve(cat_type)
        return cat_type

                
        
@dataclass
class ReadSIMEM:
    """
    Class to request dataset information and data to SIMEM using API

    Parameters: 
    dataset_id : str
        ID of the dataset to request data.
    start_date : str | dt.datetime 
        The starting date for the data slicing.
    end_date : str | dt.datetime 
        The ending date for the data slicing.
    filter_column (Optional): str 
        The column name to apply the filter on.
    filter_values (Optional): str | list 
        The values to filter the column by.
    
    Attributes:
    url_api : str
        The base URL for the SIMEM API.
    session : requests.Session
        The session for making requests to the API.
    __filter_values : tuple[str, list]
        The filter values for the dataset request.
    __filter_url : str
        The filter URL for the dataset request.
    __dataset_info : dict
        The dataset information.
    __metadata : pd.DataFrame
        The metadata of the dataset.
    __columns : pd.DataFrame
        The columns of the dataset.
    __name : str
        The name of the dataset.
    __granularity : str
        The granularity of the dataset.
    __resolution : int
        The resolution of the dataset.
    __date_filter : str
        The date filter column.

    Methods:

    __init__(self, dataset_id: str, start_date: str | dt.datetime, end_date: str | dt.datetime,
             filter_column: str = None, filter_values: str | list = None):
        Initializes the ReadSIMEM instance with the given parameters making a request to the API to extract
        the dataset metadata for further use.

    set_filter(self, column, values) -> None:
        Sets the filter for the dataset request and the complement for the URL.
        If one of the 2 arguments are not given the filter won't set.
    
    set_dates(self, start_date: str | dt.datetime, end_date: str | dt.datetime) -> None:
        Sets the start and end dates for the dataset request.
    
    main(self, data_format: str = 'csv', save_file: bool = False, filter: bool = False) -> pd.DataFrame | dict:
        Retrieves the dataset data for the given dates.
    """

    def __init__(self, dataset_id: str, start_date: str | dt.datetime, end_date: str| dt.datetime,
                 filter_column: str = None, filter_values: str | list = None):
        t0 = time.time()
        print('*' * 100)
        print('Initializing object')
        self.url_api: str = BASE_API_URL
        self._set_datasetid(dataset_id)
        self.set_dates(start_date, end_date)
        self.set_filter(filter_column, filter_values)
        self._set_dataset_data()
        t1 = time.time()
        logging.info(f'Initiallization complete in: {t1 - t0 : .2f} seconds.')
        print(f'The object has been initialized with the dataset: "{self.__name}"')
        print('*' * 100)


    def set_filter(self, column, values) -> None:
        """
        Sets the filter for the dataset request and the complement for the URL.
        If one of the 2 arguments are not given the filter won't set.
        
        Parameters:
        column : str
            The column name to apply the filter on.
        values : str | list
            The values to filter the column by.
        
        Returns:
        None
        """
        var_filter = _Validation.filter(column, values)
        if var_filter is None:
            var_filter = ''
            self.__filter_url: str = "&columnDestinyName=&values="
            return
        self._filter_values: tuple[str, list] =  var_filter
        self.__filter_url: str = f"&columnDestinyName={column}&values={','.join(var_filter[1])}"
        logging.info("Filter defined")

    def _set_datasetid(self, dataset_id) -> None:
        """
        Sets the dataset ID for the request and complement the basic url for the defined dataset.
        
        Parameters:
        dataset_id : str
            The dataset ID to be set.
        
        Returns:
        None
        """
        dataset_id = _Validation.datasetid(dataset_id)
        self.__dataset_id: str = dataset_id.lower()
        self.url_api = self.url_api + f"&datasetId={dataset_id}"
        logging.info("ID defined")

    def set_dates(self, start_date: str | dt.datetime, 
                  end_date: str | dt.datetime) -> None:
        """
        Sets the start and end dates for the dataset request.
        
        Parameters:
        start_date : str | dt.datetime
            The start date for the dataset request.
        end_date : str | dt.datetime
            The end date for the dataset request.
        
        Returns:
        None
        """
        start_date = _Validation.date(start_date)
        end_date = _Validation.date(end_date)
        if start_date > end_date:
            logging.info("Dataset will be empty - Start date is bigger than end date")
        self.__start_date: dt.datetime = start_date
        self.__end_date: dt.datetime = end_date
        if hasattr(self, '__dataset_info'):
            self.__dataset_info["parameters"]["startDate"] =  dt.datetime.strftime(start_date)
            self.__dataset_info["parameters"]["endDate"] =  dt.datetime.strftime(end_date)
        logging.info("Dates defined")
        
    def _set_dataset_data(self) -> None:
        """
        Internal method to set dataset information and metadata.
        Makes a initial request to the API to extract and organize all the information 
        related to the required dataset inside the object.
        
        Returns:
        None
    
        """
        with requests.Session() as session:
            url = self.url_api.format(REFERENCE_DATE, REFERENCE_DATE)
            response = self._make_request(url, session)
            response["parameters"]["startDate"] = dt.datetime.strftime(self.get_startdate(), DATE_FORMAT)
            response["parameters"]["endDate"] = dt.datetime.strftime(self.get_enddate(), DATE_FORMAT)
            self.__dataset_info = response
            metadata = response["result"]["metadata"]
            self.__columns: pd.DataFrame = pd.DataFrame.from_dict(response["result"]["columns"])
            self.__date_filter: str = response["result"]["filterDate"]
            self.__metadata: pd.DataFrame = pd.DataFrame.from_records([metadata])
            self.__name: str = response["result"]["name"]
            self.__granularity: str = metadata["granularity"]
            self.__resolution: int = self.__check_date_resolution(self.__granularity)
            session.close()
        
    def main(self, output_folder : str = "", filter: bool = False) -> pd.DataFrame:
        """
        Creates a dataframe with the information about the required dataset 
        in the given dates.
        
        Parameters:
        data_format : str 
            The format in which to return the data. Default is 'csv'.
        save_file : bool
            If True, the extracted data will be saved to a file. Default is False.
        filter : bool
            If True, applies a filter to the data extraction process. Default is False.
        
        Returns:
        result: 
            The extracted and formatted data.
        """
        print('Inicio consulta sincronica') 
        
        t0 = time.time()
        resolution: int = self.get_resolution()
        urls: list[str] = self.__create_urls(self.get_startdate(), self.get_enddate(), resolution, filter)
        t1 = time.time()
        print(f'Creacion url: {t1 - t0}')

        with requests.Session() as session:
            records = list(map(self._get_records, urls, repeat(session)))
        
        records = [item for sublist in records for item in sublist if len(sublist) != 0]

        t2 = time.time()
        print(f'Extraccion de registros: {t2 - t1}')

        result = pd.DataFrame.from_records(records)
        if os.path.exists(output_folder):
            new_file = self.__save_dataset(output_folder, result)
            result = pd.read_csv(new_file)
        print('End of data extracting process')
        print('*' * 100)
        
        return result


    def _get_records(self, url: str, session: requests.Session) -> list:
        """
        Makes the request and returns a list of records from the dataset.
        
        Parameters:
        url : str
            The URL for the dataset request.
        session : requests.Session
            The session for making the request.
        
        Returns:
        list
            A list of records from the dataset.
        """
        response = self._make_request(url, session)
        result = response.get('result', {}) 
        records = result.get('records', [])
        if len(records) == 0:
           print(f'For the URL: {url}') 
           print('There are 0 records') 
        logging.info("Records saved: %d rows registered.", len(records))
        
        # result = pd.DataFrame.from_records(records)
        
        return records


    def __save_dataset(self, output_folder: str, result : pd.DataFrame = None) -> str:
        """
        This method saves the dataset to a file with a default name that includes the dataset ID and the date range.
        The file is saved in CSV format.
        
        Parameters:
            output_folder : str
            The folder where the output file will be saved.

        Returns:
            str
            The path to the saved file.
        
        """
        
        print('The file will be saved with a default name.')
        datasetid = f'{self.get_datasetid().upper()}'
        fechas = f'{self.get_startdate().date()}_{self.get_enddate().date()}'
        file_name = '_'.join([datasetid, fechas])
        file_name = os.path.join(output_folder, file_name + '.csv')

        result.to_csv(file_name, index=False)
        print(f'{file_name} saved into {output_folder}')
        logging.info("%s from %s to %s dataset saved.", self.get_datasetid(), self.get_startdate(), self.get_enddate())
       
        return file_name 
    
    @staticmethod
    def _make_request(url: str, session: requests.Session) -> dict:
        """
        Makes the GET request to the URL inside a session and delivers a dictionary
        with the response.
        
        Parameters:
        url : str
            The URL for the dataset request.
        session : requests.Session
            The session for making the request.
        
        Returns:
        dict
            A dictionary containing the response in json encoded format.
        """
        response = session.get(url)
        logging.info("Response with status: %s", response.status_code)
        response.raise_for_status()
        data = response.json()

        status : str = data.get('success', False)
        api_params = data.get('parameters', None)
        datasetid = api_params.get('idDataset', None)
        if status is not True and datasetid not in [CATALOG_ID, VARIABLE_INVENTORY_ID]: 
            message : str = data.get('message', None)
            print(f'For the URL: {url}')
            print(f'The next message was returned: {message}')

        return data


    @staticmethod
    def __check_date_resolution(granularity: str) -> int:
        """
        Checks if the date range given in the object is allowed in a request to the API.
        
        Parameters:
        granularity : str
            The granularity of the date range (e.g., 'Diaria', 'Horaria', 'Mensual', 'Semanal', 'Anual').
        
        Returns:
        int
            The maximum allowed date range in days.
        """
        if granularity in ['Diaria','Horaria']:
            resolution = 31
        elif granularity in ['Mensual','Semanal']:
            resolution = 731
        elif granularity == 'Anual':
            resolution = 1827
        else:
            resolution = 0
        
        return resolution

    @staticmethod
    def _generate_start_dates(start_date: dt.datetime, end_date: dt.datetime, resolution: int):
        """
        Generator to deliver a list of date ranges.
        
        Parameters:
        start_date : dt.datetime
            The start date of the range.
        end_date : dt.datetime
            The end date of the range.
        resolution : int
            The maximum allowed date range in days.
        
        Yields:
        str
            The start dates in the specified date range formatted as strings.
        """
        intervals = (end_date - start_date)/resolution

        for i in range(0, intervals.days + 1):
            yield (start_date + dt.timedelta(days=resolution)*i).strftime(DATE_FORMAT)
        yield (end_date.strftime(DATE_FORMAT))

    def __create_urls(self, start_date: str, end_date: str, resolution: int, filter: bool= False) -> list[str]:
        """
        Receive the limit dates and deliver the API URLs for the dataset id 
        and different date ranges based on resolution.
        
        Parameters:
        start_date : str
            The start date of the range in 'YYYY-MM-DD' format.
        end_date : str
            The end date of the range in 'YYYY-MM-DD' format.
        resolution : int
            The maximum allowed date range in days.
        filter : bool, optional
            Whether to apply the filter to the dataset request (default is False).
        
        Returns:
        list[str]
            A list of URLs for the dataset requests.
        """
        start_dates: list[str] = list(date for date in self._generate_start_dates(start_date, end_date, resolution))
        end_dates: list[str] = [(dt.datetime.strptime(date,'%Y-%m-%d') - dt.timedelta(days=1)).strftime('%Y-%m-%d') for date in start_dates]
        end_dates[-1] = start_dates[-1]
        start_dates.pop(-1)
        end_dates.pop(0)
        if filter:
            base_url = self.url_api + self.get_filter_url()
        else:
            base_url = self.url_api
        urls: list[str] = list(map(base_url.format, start_dates, end_dates))
            
        logging.info("Urls created between %s and %s for %s", self.get_startdate(), self.get_enddate(), self.get_datasetid())
        return urls

    def get_datasetid(self) -> str:
        """
        Returns the dataset ID.
        
        Returns:
        str
            The dataset ID.
        """
        return self.__dataset_id

    def get_startdate(self) -> dt.datetime:
        """
        Returns the start date of the dataset object.
        
        Returns:
        dt.datetime
            The start date in datetime object.
        """
        return self.__start_date

    def get_enddate(self) -> dt.datetime:
        """
        Returns the end date of the dataset object.
        
        Returns:
        dt.datetime
            The end date in datetime object.
        """
        return self.__end_date

    def get_filter_url(self) -> str | None:
        """
        Returns the filter URL complement for the dataset request.
        
        Returns:
        str
            The filter URL.
        """
        var_filter_url = getattr(self, "_ReadSIMEM__filter_url", None)
        if var_filter_url is None:
            logging.info("No filter assigned.")
        return var_filter_url

    def get_filters(self) -> tuple | None:
        """
        Returns the filter values for the dataset request.
        
        Returns:
        tuple | str
            The filter values.
        """
        var_filter_values = getattr(self, "_filter_values", None)
        if var_filter_values is None:
            logging.info("No filter assigned.")  
        return var_filter_values  

    def get_resolution(self) -> int:
        """
        Returns the resolution of the dataset object.
        
        Returns:
        int
            The resolution in days.
        """
        return self.__resolution

    def get_granularity(self) -> str:
        """
        Returns the granularity of the dataset object.
        
        Returns:
        str
            The granularity (e.g., 'Diaria', 'Horaria', 'Mensual', 'Semanal', 'Anual').
        """
        return self.__granularity

    def get_metadata(self) -> dict:
        """
        Returns the metadata of the dataset.
        
        Returns:
        dict
            The metadata of the dataset.
        """
        return self.__metadata

    def get_columns(self) -> pd.DataFrame:
        """
        Returns the columns of the dataset.
        
        Returns:
        pd.DataFrame
            A DataFrame containing the columns of the dataset.
        """
        return self.__columns  

    def get_name(self) -> str:
        """
        Returns the name of the dataset.
        
        Returns:
        str
            The name of the dataset.
        """
        return self.__name
    
    def get_filter_column(self) -> str:
        """
        Retrieves the assigned column to filter the dates in SIMEM.

        Returns:
        str
            The current column filter.
        """
        return self.__date_filter

    def __get_dataset_info(self) -> dict:
        """
        Returns the dataset information.
        
        Returns:
        dict
            A dictionary containing the dataset information.
        """
        return self.__dataset_info


class CatalogSIMEM(ReadSIMEM):
    """
    Class to interact with the SIMEM catalogs.
    
    Args:
    catalog_type : str
        The type of catalog to extract from the webpage ('Datasets', 'Variables')

    Methods:
    get_data(self) -> pd.DataFrame:
        Retrieves the catalog data stored in the object.

    """
    
    def __init__(self, catalog_type: str):
        
        self.set_dates(REFERENCE_DATE, TODAY)
        self.url_api = BASE_API_URL
        
        catalog_type = _Validation.catalog_type(catalog_type)
        if catalog_type == 'datasets':
            self._set_datasetid(CATALOG_ID)
        elif catalog_type == 'variables':
            self._set_datasetid(VARIABLE_INVENTORY_ID)

        self._set_dataset_data()
        self.url_api = self.url_api.format(self.get_startdate(), self.get_enddate())
        with requests.Session() as session:
            datasets = super()._get_records(self.url_api, session)
            self.__data = pd.DataFrame.from_records(datasets)
        logging.info("Catalog retrieved correctly.")

    def get_data(self) -> pd.DataFrame:
        """
        Retrieves the data stored in the object.

        Returns:
            pd.DataFrame: The data stored in the object.
        """
        return self.__data


if __name__ == '__main__':

    logging.getLogger()
    dataset_id = 'c41fe8'  
    fecha_inicio = '2024-09-06'
    fecha_fin = '2024-12-06'

    simem = ReadSIMEM(dataset_id, fecha_inicio, fecha_fin, 'CodigoVariable', 'GReal')
    df = simem.main(output_folder='D:\Repositories\RP-GEDeN-SIMEM-Tools', filter=True)

    print('printing')
