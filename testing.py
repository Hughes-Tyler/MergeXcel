import pandas as pd

file1 = pd.read_excel('PyMerge Test 1.xlsx')

file1_headers = file1.columns


# print(file1)

file2 = pd.read_excel('PyMerge Test 2.xlsx')

file2_headers = file2.columns

# print(file2)

common_headers = list(set(file1_headers).intersection(file2_headers))

print("Common headers between the two files:")
for header in common_headers:
    print(header)

selected_headers = []
print("Enter the headers you want to include in the merged file (separated by commas): ")
user_input = "Customer, People, Brand"
selected_headers = [header.strip() for header in user_input.split(",")]

# Create merged DataFrame with selected headers
merged_df = pd.concat([file1[selected_headers], file2[selected_headers]], ignore_index=True)

# Print the merged DataFrame
print("Merged DataFrame with selected headers:")
print(merged_df)
