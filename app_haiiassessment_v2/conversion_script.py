import pandas as pd
import numpy as np



def split_csv(file_path, uuiddir):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, sep=',')


    basepath = "./uploads/" + uuiddir + "/"

    # Get lists of columns that start with "H", "CONF-H", "FH", and "CONF-FH"
    risposteiniziali_cols = [col for col in df.columns if col.startswith('H')]
    confidenzainiziale_cols = [col for col in df.columns if col.startswith('CONF-H')]
    rispostefinali_cols = [col for col in df.columns if col.startswith('FH')]
    confidenzafinali_cols = [col for col in df.columns if col.startswith('CONF-FH')]

    # Create new DataFrames with only the desired columns
    df_risposte_h1 = df[risposteiniziali_cols]
    df_confidenza_h1 = df[confidenzainiziale_cols]
    df_risposte_fh = df[rispostefinali_cols]
    df_confidenza_fh = df[confidenzafinali_cols]

    # Write these DataFrames to new CSV files
    df_risposte_h1.to_csv(basepath + 'h1.csv', index=False, sep=',')
    df_confidenza_h1.to_csv(basepath + 'conf-h1.csv', index=False, sep=',')
    df_risposte_fh.to_csv(basepath + 'fh.csv', index=False, sep=',')
    df_confidenza_fh.to_csv(basepath + 'conf-fh.csv', index=False, sep=',')
    print("split_csv executed")

def compare_csvs(multiline_file_path, singleline_file_path, output_file_path):
    # Load the CSV files into pandas DataFrames


    df_multiline = pd.read_csv(multiline_file_path, sep=',', header=None)

    # Check if the multiline DataFrame has only one row
    if len(df_multiline) == 1:
        # Broadcast single-line DataFrame to the shape of the multi-line DataFrame
        df_multiline = pd.read_csv(multiline_file_path, sep=',', header=None)
    else:
        # Load single-line DataFrame as usual
        df_multiline = pd.read_csv(multiline_file_path, sep=',', skiprows=1, header=None)

    df_singleline = pd.read_csv(singleline_file_path, sep=',', header=None)

    # Read headers from multiline_file
    headers = pd.read_csv(multiline_file_path, sep=',', nrows=0).columns.tolist()

    # Ensure the single-line DataFrame is broadcastable to the shape of the multi-line DataFrame
    df_singleline = pd.concat([df_singleline]*len(df_multiline), ignore_index=True)

    # Check if cells in both dataframes are empty
    empty_cells = df_multiline.isnull() | df_singleline.isnull()

    # Compare the two DataFrames, considering empty cells
    df_comparison = (df_multiline == df_singleline).astype(int).where(~empty_cells, other=np.nan)

    # Prepend headers to df_comparison
    df_comparison.columns = headers

    # Write the comparison DataFrame to a new CSV file
    df_comparison.to_csv(output_file_path, index=False, sep=',')

    print("compare_csvs executed")

def check_and_get_additional_columns(h1_file_path):
    # Load the CSV file into pandas DataFrame to check column names
    df_h1 = pd.read_csv(h1_file_path, sep=',', nrows=1)  # Read only first row to get column names

    # Check if required columns are present
    required_columns = ['Type_AI', 'Type_H', 'Study', 'Complexity']
    additional_columns = []
    for column in required_columns:
        if column in df_h1.columns:
            additional_columns.append(column)


    return additional_columns

def create_reliances(h1_path, h1_file_path, ai_file_path, fh_file_path, output_file_path):
    # Load the CSV files into pandas DataFrames, skipping the first row (header)
    add_df = pd.read_csv(h1_path, sep=',')
    df_h1 = pd.read_csv(h1_file_path, sep=',', skiprows=1, header=None)
    df_ai = pd.read_csv(ai_file_path, sep=',', skiprows=1, header=None)
    df_fh = pd.read_csv(fh_file_path, sep=',', skiprows=1, header=None)

    # Check and get additional columns from h1_file_path
    additional_columns = check_and_get_additional_columns(h1_path)

    columns = ['id', 'HD1', 'AI', 'FHD'] + additional_columns

    # Create an empty DataFrame for the output
    df_reliances = pd.DataFrame(np.empty((df_h1.shape[0]*df_h1.shape[1], len(columns))), columns=columns)

    # Iterate over the rows and columns of df_h1
    for i in range(len(df_h1)):
        for j in range(len(df_h1.columns)):
            # Get the corresponding values from df_h1, df_ai, and df_fh
            df_reliances.loc[i*len(df_h1.columns) + j, "id"] = i
            df_reliances.loc[i*len(df_h1.columns) + j, "HD1"] = df_h1.iloc[i, j]
            df_reliances.loc[i*len(df_h1.columns) + j, "AI"] = df_ai.iloc[0, j]
            df_reliances.loc[i*len(df_h1.columns) + j, "FHD"] = df_fh.iloc[i, j]


    for i in df_reliances["id"].unique():
        for j in additional_columns:
            df_reliances.loc[df_reliances["id"] == i, j] = add_df.loc[add_df["ID"] == i+1, j].values[0]

    # Write df_reliances to a new CSV file
    columns_to_convert = df_reliances.columns.difference(['Type_AI', 'Type_H', 'Study'])

    # Convert only numeric columns to integers
    df_reliances[columns_to_convert] = df_reliances[columns_to_convert].astype(int)
    df_reliances.dropna().to_csv(output_file_path, index=False, sep=',')
    print("create_reliances executed")
    print(df_reliances.dropna())
    return output_file_path


def convert_csv(h1_path,ai_path,groundtruth_path, uuiddir):


    basepath = "./uploads/" + uuiddir + "/"

    split_csv(h1_path, uuiddir)

    # Define the paths to your CSV files
    multiline_file_path = basepath + 'h1.csv'  # replace with your file path
    singleline_file_path = ai_path  # replace with your file path
    output_file_path = basepath + 'agreementh1ai.csv'  # replace with your desired output file path
    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = basepath + 'h1.csv'  # replace with your file path
    singleline_file_path = groundtruth_path  # replace with your file path
    output_file_path = basepath + 'accuratezze-h1.csv'  # replace with your desired output file path
    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = ai_path  # replace with your file path
    singleline_file_path = groundtruth_path  # replace with your file path
    output_file_path = basepath + 'accuratezze-ai.csv'  # replace with your desired output file path
    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = basepath + 'fh.csv'  # replace with your file path
    singleline_file_path = groundtruth_path  # replace with your file path
    output_file_path = basepath + 'accuratezze-fh.csv'  # replace with your desired output file path
    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    # Define the paths to your CSV files
    h1_file_path = basepath + 'accuratezze-h1.csv'  # replace with your file path
    ai_file_path = basepath + 'accuratezze-ai.csv'  # replace with your file path
    fh_file_path = basepath + 'accuratezze-fh.csv'  # replace with your file path
    output_file_path = basepath + "final_reliances.csv"  # replace with your desired output file path
    # Call the function
    rels = create_reliances(h1_path, h1_file_path, ai_file_path, fh_file_path, output_file_path)



    print(rels)
    return rels