import pandas as pd
import numpy as np
import sys
import os

def smart_read_csv(file_path, sep=','):
    """Legge un CSV gestendo righe vuote e valori mancanti."""
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        if any(c.isalpha() for c in first_line):
            df = pd.read_csv(file_path, sep=sep, skiprows=1, header=None)
        else:
            df = pd.read_csv(file_path, sep=sep, header=None)
        df = df.dropna(how='all')  # Rimuove righe completamente vuote
        df = df.dropna()  # Rimuove righe con valori mancanti
        return df
    except Exception as e:
        raise ValueError(f"Errore nel caricamento di {file_path}: {e}")

def replicate_special_columns(df):
    """
    Replica 'type_AI', 'type_H' e 'Study' per ogni riga con lo stesso ID.
    """
    special_columns = ["type_AI", "type_H", "Study"]

    for col in special_columns:
        if col in df.columns:
            df[col] = df[col].ffill()  # Riempie i valori mancanti con il precedente

    return df

def split_csv(file_path):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, sep=',')

    # Get lists of columns that start with "ACCURATEZZA" and "CONFIDENZA"
    risposteiniziali_cols = [col for col in df.columns if col.startswith('H')]
    confidenzainiziale_cols = [col for col in df.columns if col.startswith('C')]
    rispostefinali_cols = [col for col in df.columns if col.startswith('FH')]
    confidenzafinali_cols = [col for col in df.columns if col.startswith('FC')]

    missing_columns = []
    if not risposteiniziali_cols:
        missing_columns.append("H (risposte iniziali)")
    if not rispostefinali_cols:
        missing_columns.append("FH (risposte finali)")
    if missing_columns:
        raise ValueError(f"ERROR: Mancano le seguenti colonne nel dataset: {', '.join(missing_columns)}")

    all_relevant_cols = risposteiniziali_cols + rispostefinali_cols
    if confidenzainiziale_cols:
        all_relevant_cols += confidenzainiziale_cols
    if confidenzafinali_cols:
        all_relevant_cols+=confidenzafinali_cols
    for col in all_relevant_cols:
        df = df[pd.to_numeric(df[col], errors='coerce').notnull()]


    # # Check for non-numerical values in the relevant columns
    # for col in all_relevant_cols:
        # if not pd.to_numeric(df[col], errors='coerce').notnull().all():
            # raise ValueError(f"Non-numerical value found in column '{col}'")

    # Remove rows with non-numerical values in relevant columns
    for col in all_relevant_cols:
        df = df[pd.to_numeric(df[col], errors='coerce').notnull()]

    if confidenzainiziale_cols:
        df_confidenza_h1 = df[confidenzainiziale_cols]
        df_confidenza_h1.to_csv('conf-h1.csv', index=False, sep=',')

    if confidenzafinali_cols:
        df_confidenza_fh = df[confidenzafinali_cols]
        df_confidenza_fh.to_csv('conf-fh.csv', index=False, sep=',')
    # Create new DataFrames with only the desired columns
    df_risposte_h1 = df[risposteiniziali_cols]
    df_risposte_fh = df[rispostefinali_cols]
    # Write these DataFrames to new CSV files
    df_risposte_h1.to_csv('h1.csv', index=False, sep=',')
    df_risposte_fh.to_csv('fh.csv', index=False, sep=',')
    print("split_csv executed")

def compare_csvs(multiline_file_path, singleline_file_path, output_file_path):
    # Load the CSV files into pandas DataFrames
    df_multiline = pd.read_csv(multiline_file_path, sep=',', skiprows=1, header=None)
    df_singleline = pd.read_csv(singleline_file_path, sep=',', skiprows=1, header=None)

    print(df_multiline.columns)
    print(df_singleline.columns)

    # Read headers from multiline_file
    headers = pd.read_csv(multiline_file_path, sep=',', nrows=0).columns.tolist()

    # Check if number of columns match
    if len(df_multiline.columns) != len(df_singleline.columns):
        if len(df_singleline.columns) > len(df_multiline.columns) and multiline_file_path.endswith('h1.csv'):
          raise ValueError('Missing Human Decision column(s) starting with "H"')
        if len(df_singleline.columns) > len(df_multiline.columns) and multiline_file_path.endswith('fh.csv'):
          raise ValueError('Missing Final Human Decision column(s) starting with "FH"')
        if len(df_multiline.columns) > len(df_singleline.columns) and multiline_file_path.endswith('h1.csv'):
          raise ValueError('Missing AI decision column(s)')
        raise ValueError(
           f"Number of columns mismatch between '{multiline_file_path}' and '{singleline_file_path}'. "
            f"'{multiline_file_path}' has {len(df_multiline.columns)} columns, "
            f"'{singleline_file_path}' has {len(df_singleline.columns)} columns."
        )

    # Assign headers to both DataFrames
    #df_multiline.columns = headers
    #df_singleline.columns = headers[:len(df_singleline.columns)]



    # Check for missing columns in df_singleline compared to df_multiline
    missing_cols = set(df_multiline.columns) - set(df_singleline.columns)
    if missing_cols:
        raise ValueError(f"Missing columns in '{singleline_file_path}': {list(missing_cols)}")

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

def create_reliances(h1_file_path, ai_file_path, fh_file_path, output_file_path, c1_file_path=None, fc_file_path=None ):
    # Load the CSV files into pandas DataFrames, skipping the first row (header)
    df_h1 = pd.read_csv(h1_file_path, sep=',', skiprows=1, header=None)
    df_ai = pd.read_csv(ai_file_path, sep=',', skiprows=1, header=None)
    df_fh = pd.read_csv(fh_file_path, sep=',', skiprows=1, header=None)

    df_c1 = None
    df_fc = None
    if c1_file_path is not None:
        df_c1 = pd.read_csv(c1_file_path, sep=',', skiprows=1, header=None)
    if fc_file_path is not None:
        df_fc = pd.read_csv(fc_file_path, sep=',', skiprows=1, header=None)


    # Create an empty DataFrame for the output
    df_reliances = pd.DataFrame(np.empty((df_h1.shape[0]*df_h1.shape[1], 6)), columns=['id','HD1', 'AI', 'FHD', "C", "FC"])

    # Iterate over the rows and columns of df_h1
    for i in range(len(df_h1)):
        for j in range(len(df_h1.columns)):
            # Get the corresponding values from df_h1, df_ai, and df_fh
            df_reliances.loc[i*len(df_h1.columns) + j, "id"] = i
            df_reliances.loc[i*len(df_h1.columns) + j, "HD1"] = df_h1.iloc[i, j]
            df_reliances.loc[i*len(df_h1.columns) + j, "AI"] = df_ai.iloc[0, j]
            df_reliances.loc[i*len(df_h1.columns) + j, "FHD"] = df_fh.iloc[i, j]

            if df_c1 is not None:
                try:
                    df_reliances.loc[i*len(df_h1.columns) + j, "C"] = df_c1.iloc[i, j]
                except IndexError:
                    missing_column_name = df_reliances.columns[df_reliances.columns.get_loc("C")]  # Get the name of the column being assigned ('C' in this case)
                    #raise IndexError(f"Expected column '{missing_column_name}' with index {j} in '{c1_file_path}' was not found.")
                    raise IndexError('Missing Confidence column(s) starting with "C"')

            if df_fc is not None:
                try:
                    df_reliances.loc[i*len(df_h1.columns) + j, "FC"] = df_fc.iloc[i, j]
                except IndexError:
                    missing_column_name = df_reliances.columns[df_reliances.columns.get_loc("FC")]  # Get the name of the column being assigned ('FC' in this case)
                    #raise IndexError(f"Expected column '{missing_column_name}' with index {j} in '{fc_file_path}' was not found.")
                    raise IndexError('Missing Final Confidence column(s) starting with "FC"')

    # Write df_reliances to a new CSV file
    df_reliances = df_reliances.dropna()
    df_reliances = df_reliances.astype(int)
    df_reliances.to_csv(output_file_path, index=False, sep=',')

    print("create_reliances executed")
    return df_reliances

def convert_csv(h1_path,ai_path,groundtruth_path):

    basepath = ''
    split_csv(h1_path)

    if len(pd.read_csv(ai_path, sep=',', skiprows=1, header=None).columns) > len(pd.read_csv(groundtruth_path, sep=',', skiprows=1, header=None).columns):
      raise ValueError('Missing GroundTruth(s)')

    # Define the paths to your CSV files
    multiline_file_path = basepath + 'h1.csv'  # replace with your file path
    singleline_file_path = basepath + ai_path  # replace with your file path

    # Define the path to the output CSV file
    output_file_path = basepath + 'agreementh1ai.csv'  # replace with your desired output file path

    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = basepath + 'h1.csv'  # replace with your file path
    singleline_file_path = basepath + groundtruth_path  # replace with your file path

    # Define the path to the output CSV file
    output_file_path = basepath + 'accuratezze-h1.csv'  # replace with your desired output file path

    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = basepath + ai_path  # replace with your file path
    singleline_file_path = basepath + groundtruth_path  # replace with your file path

    # Define the path to the output CSV file
    output_file_path = basepath + 'accuratezze-ai.csv'  # replace with your desired output file path

    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)

    multiline_file_path = basepath + 'fh.csv'  # replace with your file path
    singleline_file_path = basepath + groundtruth_path  # replace with your file path

    # Define the path to the output CSV file
    output_file_path = basepath + 'accuratezze-fh.csv'  # replace with your desired output file path

    # Call the function
    compare_csvs(multiline_file_path, singleline_file_path, output_file_path)



    # Define the paths to your CSV files
    h1_file_path = basepath + 'accuratezze-h1.csv'  # replace with your file path
    ai_file_path = basepath + 'accuratezze-ai.csv'  # replace with your file path
    fh_file_path = basepath + 'accuratezze-fh.csv'  # replace with your file path
    c1_file_path = basepath + 'conf-h1.csv'
    fc_file_path = basepath + 'conf-fh.csv'

    # Define the path to the output CSV file
    # file_path = responses_file
    file_path = ''
    output_file_path = basepath + file_path + '_reliances.csv'  # replace with your desired output file path

    # Call the function
    rel = create_reliances(h1_file_path, ai_file_path, fh_file_path, output_file_path, c1_file_path, fc_file_path)
    print('executed')
    return rel