import requests
import os
import time
import json
import pandas as pd
import logging
from dataclasses import dataclass
from datetime import datetime as dt
from datetime import timedelta 
from itertools import repeat, chain

logger = logging.getLogger("application")
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "", "%")
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.addHandler(logging.FileHandler(r'log/mylog.log'))
logger.setLevel(logging.DEBUG)
logger.info('\n inicia extraccion PyDataSIMEM %s', str(dt.strftime(dt.now(), format='%Y-%m-%d %H:%m:%S')))

DATASETID = 'EC6945'

@dataclass
class PyDataSimem:
    """
    Class to request datasets to SIMEM using API
    """

    dataset_id: str
    start_date: str = '1990-01-01'
    end_date: str = '1990-01-01'
    url_api: str = "https://www.simem.co/backend-files/api/PublicData?startdate={}&enddate={}&datasetId={}"
    ref_date = '1990-01-01'
    session = requests.Session()
    

    def main(self) -> pd.DataFrame:
        """
        Creates a .csv or .json file with the information about the required dataset 
        in the given dates
        """
        logger.info(f"For the dataset {self.dataset_id} and the dates {self.start_date} to {self.end_date}")
        granularity: str = self.read_granularity()
        resolution: int = self.check_date_resolution(granularity)
        urls: list[str] = self.create_urls(self.start_date, self.end_date, resolution)
        records = (map(self.get_records, urls))
        dataset_info: dict = self.get_dataset_info()
        dataset: dict = self.save_dataset(dataset_info, records)
        self.session.close()
        # if path is None:
        #     path = os.getcwd() + "\\" + self.dataset_id
        
        # if filetype == "json":
        #     self.dict_to_json(dataset, path)

        # elif filetype == "csv":
        #     dataset = pd.DataFrame(dataset["result"]["records"])
        #     dataset.to_csv(path + ".csv", index=index)

        return pd.DataFrame.from_dict(dataset["result"]["records"])

    def read_granularity(self) -> str:
        """
        Obtains the metadata info of the dataset and checks granularity
        """
        metadata: dict = self.get_metadata()
        granularity: str = metadata["granularity"]
        logger.info(f"Granularity -> {granularity}")
        return granularity

    def get_metadata(self) -> dict:
        """
        Make the API request with dates that gives only the dataset
        information and converts into a dictionary
        """
        url = self.url_api.format(self.ref_date, self.ref_date, self.dataset_id.lower())
        response: dict =  self.make_request(url)  # Typing
        metadata: dict = response["result"]["metadata"]
        logger.info("Metadata saved.")
        return metadata
    
    def get_records(self, url: str) -> list:
        """
        Make the request and delivers a dictionary with only the records of
        the dataset
        """
        response = self.make_request(url)
        records = response["result"]["records"]
        logger.info(f"There are {len(records)} records")
        return records

    def get_dataset_info(self) -> dict:
        """
        Make the request to get the dataset information with 0 records
        """
        url = self.url_api.format(self.ref_date, self.ref_date, self.dataset_id.lower())
        dataset_info: dict =  self.make_request(url)
        dataset_info["parameters"]["startDate"] = self.start_date
        dataset_info["parameters"]["endDate"] = self.end_date

        return dataset_info

    def save_dataset(self, dataset_info: dict, records: list[list]):
        """
        Creates a deserialized json in a dictionary that includes the dataset info and 
        the records of the selected dates
        """
        dataset_info["result"]["records"].extend(
            [item for sublist in records for item in sublist])

        return dataset_info
    
    def make_request(self, url: str) -> dict:
        """
        Make the get request to the URL inside a session and delivers a dictionary
        with the response
        """
        response = self.session.get(url)
        logger.info("Request done with status code {response.status_code}")
        return response.json()

    def check_date_resolution(self, granularity: str) -> int:
        """
        Checks if the date range given in the object is allowed in a request to the API
        """
        if granularity in ['Diaria','Horaria']:
            resolution = 31
        elif granularity in ['Mensual','Semanal']:
            resolution = 731
        elif granularity == 'Anual':
            resolution = 1827
        
        return resolution
    
    def dict_to_json(self, response: dict, name: str= None) -> None:
        """
        Saves the given dictionary in a .json file
        """
        if name is None:
            name = self.dataset_id

        with open(name, 'w') as file:
            json.dump(response, file)
        file.close()
        logger.info("Dictionary saved in JSON file")
        return None
    
    def generate_start_dates(self, start_date: str, end_date: str, resolution: int):
        """
        Generator to deliver a list of date ranges 
        """
        start_date = dt.strptime(start_date, "%Y-%m-%d")  # Typing
        end_date = dt.strptime(end_date, "%Y-%m-%d")

        intervals = (end_date - start_date)/resolution

        for i in range(0, intervals.days + 1, 2):
            yield (start_date + timedelta(days=resolution)*i).strftime("%Y-%m-%d")
            
            if start_date + timedelta(days=resolution)*(i+1) < end_date:
                yield (start_date + timedelta(days=resolution)*(i+1)).strftime("%Y-%m-%d")
        yield (end_date.strftime("%Y-%m-%d"))



    def create_urls(self, start_date: str, end_date: str, resolution: int) -> list[str]:
        """
        Recieve the limit dates and delivers the API URLs for the dataset id 
        and different dates ranges based on resolution
        """
        start_dates: list[str] = list(date for date in self.generate_start_dates(start_date, end_date, resolution))
        end_dates: list[str] = [(dt.strptime(date,'%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d') for date in start_dates]
        end_dates[-1] = start_dates[-1]
        start_dates.pop(-1)
        end_dates.pop(0)
        urls: list[str] = list(map(self.url_api.format, start_dates, end_dates, repeat(self.dataset_id)))

        return urls



if __name__ == '__main__':

    start = time.perf_counter()

    object = PyDataSimem(DATASETID, "2024-04-14", "2024-04-16")
    dataset_df = object.main()
    path = r'D:/Repos/PyDataSimem/test/test_data/' + f'{object.dataset_id}.csv'
    dataset_df.to_csv(path, index=False)

    end = time.perf_counter()
    print(f"Time taken: {end - start:.3f} seconds")
