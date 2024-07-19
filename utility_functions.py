import runpy
import re
import textwrap

# Function to run the script dynamically
def run_script(script_name):
    runpy.run_path(script_name)

def sort_alfanumeric(df, column_name):
    """
    Sorts a DataFrame alphanumerically based on the numbers within the specified column.

    Parameters:
    df (pd.DataFrame): The DataFrame to sort.
    column_name (str): The name of the column to sort.

    Returns:
    pd.DataFrame: The sorted DataFrame.
    """
    # Function to extract numerical part from the string
    def extract_number(text):
        match = re.search(r'\d+', text)
        return int(match.group()) if match else float('inf')  # Use float('inf') to push non-number strings to the end

    # Create a new column with extracted numerical values
    df['numeric_part'] = df[column_name].apply(extract_number)

    # Sort DataFrame based on the numerical part
    df_sorted = df.sort_values(by='numeric_part')

    # Drop the temporary numeric part column
    df_sorted = df_sorted.drop(columns='numeric_part').reset_index(drop=True)

    return df_sorted

def wrap_labels(labels, width=20):
    """
    Wrap long labels to fit within the specified width.
    
    Parameters:
    labels (list): The list of labels to wrap.
    width (int): The maximum width of each line.
    
    Returns:
    list: The list of wrapped labels.
    """
    return ['<br>'.join(textwrap.wrap(label, width)) for label in labels]

def emphasize_numbers(s):
    """
    Emphasizes numbers in the string by duplicating them to give more weight to numerical parts,
    and removes the string 'DONNEE ENVIRONNEMENTALE PAR DEFAUT'.
    """
    # Remove 'DONNEE ENVIRONNEMENTALE PAR DEFAUT'
    s = s.replace('DONNEE ENVIRONNEMENTALE PAR DEFAUT', '')
    numbers = re.findall(r'\d+', s)
    for number in numbers:
        s = s.replace(number, number * 2)
    return s

def count_repeated_elements(df, column1, column2):
    """
    Counts the total number of times elements are repeated in column1 with different values in column2.

    Parameters:
    df (pd.DataFrame): The DataFrame to search.
    column1 (str): The column to search for repeated elements.
    column2 (str): The column to check for different values.

    Returns:
    int: The sum of the times elements are repeated in column1 with different values in column2.
    """
    # Group by column1 and count unique values in column2
    grouped = df.groupby(column1)[column2].nunique()

    # Find elements that have more than one unique value in column2
    repeated_elements = grouped[grouped > 1]

    # Calculate the sum of times elements are repeated with different values in column2
    total_repeats = repeated_elements.sum()

    return total_repeats