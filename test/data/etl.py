# read files
# extract 10 lines
# combine the first and last name
# Print the result

import pandas as pd

def extract_csv():
    # extract 10 lines
    # using boto3
    path="test/data/linkedin_data.csv"
    dataframe = pd.read_csv(path, delimiter=',').head(10)

    return dataframe

    


def transformation_logic(dataframe):
    # combine the first and last name
    
    dataframe["full_name"] = dataframe["First Name"] + dataframe["Last Name"]

    print(dataframe["full_name"])

def pipeline():
    dataframe = extract_csv()
    transformation_logic(dataframe)
