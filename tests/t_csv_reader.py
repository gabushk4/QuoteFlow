from src.error_types import DuplicateCodeError, InvalidFieldsError
from src.utils.csv_reader import read_catalogue, read_demand
from pathlib import Path
from typing import Callable
import csv
import unittest
import tempfile

def write_temp_csv(data: list[list[str]], callback: Callable[[Path], None]) -> None:
    """Write a CSV file in a temporary file and returns the path to the file."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "tmp_catalogue.csv"
        tmp_file.write_text("\n".join([",".join(line) for line in data]))
        if callback is None:
            raise ValueError("Callback function is required.")
        return callback(tmp_file)

class CsvReaderTest(unittest.TestCase):
    #test data
    __catalogue_valid_data = [
        ["code", "name", "price"],
        ["P001", "Pomme", "1.23"],
        ["P002", "Poire", "2.34"]
    ]
    __demand_valid_data = [
        ["code", "quantity"],
        ["P001", "100"],
        ["P002", "200"]
    ]    
    __test_code = "P001"
    __test_valid_catalogue_product = {"code": "P001", "name": "Pomme", "price": "1.23"}
    __test_valid_demand_product = {"code": "P001", "quantity": "100"}    
    
    __catalogue_empty_data = [
        ["code", "name", "price"]
    ]    
    __demand_empty_data = [
        ["code", "quantity"]
    ]    
    
    __catalogue_duplicate_data= [
        ["code", "name", "price"],
        ["P001", "Pomme", "1.23"],
        ["P001", "Pomme", "1.23"]
    ]
    __demand_duplicate_data= [
        ["code", "quantity"],
        ["P001", "100"],
        ["P001", "100"]
    ]    
    
    __invalid_fields_data = [
        ["apple", "banana", "bread"],
        ["P001", "Pomme", "1.23"]        
    ]
    
    #test methods     
    def test_valid(self):
        """Tests a valid catalogue and demand file."""
        def catalogue_callback(tmp_csv_path: Path) -> None:
            catalogue = read_catalogue(tmp_csv_path)
            self.assertEqual(catalogue[self.__test_code], self.__test_valid_catalogue_product)
        
        def demand_callback(tmp_csv_path: Path) -> None:
            demand = read_demand(tmp_csv_path)
            self.assertEqual(demand[self.__test_code], self.__test_valid_demand_product)
        
        write_temp_csv(self.__catalogue_valid_data, callback=catalogue_callback)
        write_temp_csv(self.__demand_valid_data, callback=demand_callback)
    
    def test_empty(self):
        """Tests an empty catalogue and demand file."""
        def catalogue_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(ValueError):
                read_catalogue(tmp_csv_path)
        
        def demand_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(ValueError):
                read_demand(tmp_csv_path)
        
        write_temp_csv(self.__catalogue_empty_data, catalogue_callback)
        write_temp_csv(self.__demand_empty_data, demand_callback)

    def test_single_data_row(self):
        """Accepts a CSV with a header and one data row."""
        catalogue_data = [self.__catalogue_valid_data[0], self.__catalogue_valid_data[1]]
        demand_data = [self.__demand_valid_data[0], self.__demand_valid_data[1]]

        def catalogue_callback(tmp_csv_path: Path) -> None:
            self.assertEqual(read_catalogue(tmp_csv_path)[self.__test_code], self.__test_valid_catalogue_product)

        def demand_callback(tmp_csv_path: Path) -> None:
            self.assertEqual(read_demand(tmp_csv_path)[self.__test_code], self.__test_valid_demand_product)

        write_temp_csv(catalogue_data, catalogue_callback)
        write_temp_csv(demand_data, demand_callback)
    
    def test_duplicate_code(self):
        """Tests a catalogue and a demand file with a duplicated code."""
        def catalogue_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(DuplicateCodeError):
                read_catalogue(tmp_csv_path)
        
        def demand_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(DuplicateCodeError):
                read_demand(tmp_csv_path)
        
        write_temp_csv(self.__catalogue_duplicate_data, callback=catalogue_callback)
        write_temp_csv(self.__demand_duplicate_data, callback=demand_callback)
    
    def test_invalid_field(self):
        """Tests a catalogue and a demand file with invalid fields."""
        def catalogue_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(InvalidFieldsError):
                read_catalogue(tmp_csv_path)
        
        def demand_callback(tmp_csv_path: Path) -> None:            
            with self.assertRaises(InvalidFieldsError):
                read_demand(tmp_csv_path)
        
        write_temp_csv(self.__invalid_fields_data, callback=catalogue_callback)
        write_temp_csv(self.__invalid_fields_data, callback=demand_callback)

