import pandas as pd
import os

#repo_base = os.path.dirname(os.getcwd())
#sets_folder = repo_base + '\\starwars\\sets\\'
#output_sets_folder = repo_base + '\\starwars\\new_sets\\'
repo_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f'repo_base: {repo_base}')
sets_folder = os.path.join(repo_base, 'starwars', 'sets') + '\\'
output_sets_folder = os.path.join(repo_base, 'starwars', 'new_sets') + '\\'
print(sets_folder)
print(f'sets_folder exists: {os.path.exists(sets_folder)}')

sets_files_list = [os.path.join(sets_folder, f) for f in os.listdir(sets_folder) if f.endswith('.txt')]
print(sets_files_list)

for sets_file in sets_files_list:
    print(f'\n\nsets_file: {sets_file}')
    
    # Read integers as integers (not floats) by setting dtype or using convert_dtypes
    set_df = pd.read_csv(sets_file, sep='\t', encoding='latin-1')
    
    # Fix 1: Convert any float columns that are whole numbers back to integers
    for col in set_df.columns:
        if set_df[col].dtype == 'float64':
            if set_df[col].dropna().apply(float.is_integer).all():
                set_df[col] = set_df[col].astype('Int64')  # capital I = nullable integer

    set_df['DraftRarity'] = ''
    
    output_file_name = os.path.basename(sets_file)
    
    # Fix 2: quoting=3 is csv.QUOTE_NONE, plus an escapechar to avoid errors
    set_df.to_csv(
        output_sets_folder + output_file_name,
        sep='\t',
        encoding='latin-1',
        index=False,
        quoting=3,        # csv.QUOTE_NONE — no text qualifiers added
        escapechar=None   # required when quoting=QUOTE_NONE
    )
    
    print(f'\nwritten new sets file {sets_file}')