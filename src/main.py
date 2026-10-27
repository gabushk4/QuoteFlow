if __package__:
	from .utils.csv_reader import read_catalogue, read_demand
else:
	from utils.csv_reader import read_catalogue, read_demand

if __name__ == "__main__":
	catalogue = read_catalogue()
	demands = read_demand()
	
	
