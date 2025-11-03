import pandas as pd
import os

# File paths
kdrama_file = os.path.join(os.path.dirname(__file__), "kdrama_dataset.csv")
output_file = os.path.join(os.path.dirname(__file__), "kdrama_dataset_renamed.csv")

# Read the kdrama_dataset.csv
df_kdrama = pd.read_csv(kdrama_file)

# Column mapping from kdrama_dataset to dramalist format
# dramalist_all_dramas headers: title, alternate_names, description, publisher, country, genres, rating_value, rating_count, date_published, keywords, actors
# kdrama_dataset headers: Title, Also Known As, Written By, Director, Cast, Genre, Network, Episodes, Release Dates, Release Years, Poster, Description

column_mapping = {
    "Title": "title",
    "Also Known As": "alternate_names",
    "Description": "description",
    "Network": "publisher",
    "Genre": "genres",
    "Cast": "actors",
    "Release Dates": "date_published",
    "Poster": "url",  # Using Poster for url since dramalist has url field
}

# Update column names to match the format
column_mapping.update(
    {
        "Written By": "written_by",
        "Director": "director",
        "Episodes": "episodes",
        "Release Years": "release_years",
    }
)

# Rename columns again after updating the mapping
df_renamed = df_kdrama.rename(columns=column_mapping)

# Add missing columns with empty values
missing_columns = ["country", "rating_value", "rating_count", "keywords"]
for col in missing_columns:
    if col not in df_renamed.columns:
        df_renamed[col] = ""

# Reorder columns to match dramalist format, preserving order and adding extra columns at the end
dramalist_columns = [
    "title",
    "alternate_names",
    "description",
    "publisher",
    "country",
    "genres",
    "rating_value",
    "rating_count",
    "date_published",
    "keywords",
    "actors",
]

# Keep only columns that exist and are in dramalist format
final_columns = [col for col in dramalist_columns if col in df_renamed.columns]

# Add any remaining columns that weren't in the target format at the end
remaining_cols = [col for col in df_renamed.columns if col not in dramalist_columns]
final_columns.extend(remaining_cols)

df_final = df_renamed[final_columns]

# Save the renamed dataset
df_final.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Renamed dataset saved to: {output_file}")
print(f"Original rows: {len(df_kdrama)}")
print(f"Final rows: {len(df_final)}")
print(f"Final columns: {list(df_final.columns)}")
