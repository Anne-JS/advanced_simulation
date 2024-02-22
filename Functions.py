import pandas as pd


def clean_lon_lat_bmms(df, road_ranges):
    """
    Cleaning the BMMS_overview file while using the road_ranges df which is created from the _roads.tsv file. 
    Cleans:     Interpolates 0's and NaN's values in the lon lat columns
                Fixes bridges where lon and lat are switched up
                Fixes Typo's values in the lon lat columns

    """
    df = interpolate_or_assign_on_same_road(df)
    df = df.sort_values(by=['road', 'km'])
    # Identify rows with NaN or 0 in either 'lat' or 'lon'
    rows_with_invalid_values = df[(df['lat'].isna() | df['lat'] == 0) | (df['lon'].isna() | df['lon'] == 0)]

    # Store these rows in a separate DataFrame if you want to use them later
    deleted_rows = rows_with_invalid_values.copy()

    # Drop the rows from the original DataFrame
    df = df.loc[~((df['lat'].isna() | df['lat'] == 0) | (df['lon'].isna() | df['lon'] == 0))].reset_index(drop=True)

    df.loc[df['width'] > 45, df.select_dtypes(include=['number']).columns] = df.loc[df['width'] > 45,  df.select_dtypes(include=['number']).columns] / 100

    for index, row in df.iterrows():
        # max and min lon/lat for Bangladesh
        # When outside of these ranges the lon lat are switched around.
        if row.lat > 27 and row.lon < 88:
            lat = row.lat
            lon = row.lon
            df.loc[index, 'lat'] = lon
            df.loc[index, 'lon'] = lat

    prev_row = None
    for index, row in df.iterrows():
        # If it's not the first item of the Excel
        if prev_row is not None:
            # If it's not the first bmms of the road
            if row['road'] == prev_row['road']:
                # If latitude is more than 0.3 degree from previous bmms on same road
                # Otherwise it is probably a typo
                # Check if either value is NaN or 0
                if pd.notna(row['km']) and pd.notna(prev_row['km']) and row['km'] != 0 and prev_row['km'] != 0:
                    distance = row['km'] - prev_row['km']
                    # You can now proceed with using 'distance' for further calculations or conditions
                else:
                    # Handle the case where the condition is not met (e.g., set distance to None or skip)
                    distance = 5

                if not road_ranges[road_ranges['road'] == row['road']]['min_lon'].empty:
                    if row['lat'] < road_ranges[road_ranges['road'] == row['road']]['min_lat'].iloc[0] or row['lat'] > road_ranges[road_ranges['road'] == row['road']]['max_lat'].iloc[0]:
                        if row['lat'] < prev_row['lat'] - 0.05 or row['lat'] > prev_row['lat'] + 0.05:
                            df.loc[index, 'lat'] = prev_row['lat']
                    elif distance > 40:
                        if row['lat'] < prev_row['lat'] - 0.45 or row['lat'] > prev_row['lat'] + 0.45:
                            df.loc[index, 'lat'] = prev_row['lat']
                    elif distance > 25 and distance < 40:
                        if row['lat'] < prev_row['lat'] - 0.20 or row['lat'] > prev_row['lat'] + 0.20:
                            df.loc[index, 'lat'] = prev_row['lat']
                    elif distance > 10 and distance < 25:
                        if row['lat'] < prev_row['lat'] - 0.10 or row['lat'] > prev_row['lat'] + 0.10:
                            df.loc[index, 'lat'] = prev_row['lat']
                    elif distance > 0 and distance < 10:
                        if row['lat'] < prev_row['lat'] - 0.05 or row['lat'] > prev_row['lat'] + 0.05:
                            df.loc[index, 'lat'] = prev_row['lat']
                else:
                    if row['lat'] < prev_row['lat'] - 0.45 or row['lat'] > prev_row['lat'] + 0.45:
                        df.loc[index, 'lat'] = prev_row['lat']

                # If longitude is more than 0.3 degree from previous bmms on same road
                # Otherwise it is probably a typo
                if not road_ranges[road_ranges['road'] == row['road']]['min_lon'].empty:
                    if row['lon'] < road_ranges[road_ranges['road'] == row['road']]['min_lon'].iloc[0] or row['lon'] > road_ranges[road_ranges['road'] == row['road']]['max_lon'].iloc[0]:
                        if row['lon'] < prev_row['lon'] - 0.05 or row['lon'] > prev_row['lon'] + 0.05:
                            df.loc[index, 'lon'] = prev_row['lon']
                    elif distance > 40:
                        if row['lon'] < prev_row['lon'] - 0.45 or row['lon'] > prev_row['lon'] + 0.45:
                            df.loc[index, 'lon'] = prev_row['lon']
                    elif distance > 25 and distance < 40:
                        if row['lon'] < prev_row['lon'] - 0.20 or row['lon'] > prev_row['lon'] + 0.20:
                            df.loc[index, 'lon'] = prev_row['lon']
                    elif distance > 10 and distance < 25:
                        if row['lon'] < prev_row['lon'] - 0.10 or row['lon'] > prev_row['lon'] + 0.10:
                            df.loc[index, 'lon'] = prev_row['lon']
                    elif distance > 0 and distance < 10:
                        if row['lon'] < prev_row['lon'] - 0.05 or row['lon'] > prev_row['lon'] + 0.05:
                            df.loc[index, 'lon'] = prev_row['lon']
                else:
                    if row['lon'] < prev_row['lon'] - 0.27 or row['lon'] > prev_row['lon'] + 0.27:
                        df.loc[index, 'lon'] = prev_row['lon']


            # if it is the first bmms on the road
            else:
                # If the road exists in the road ranges
                if not road_ranges[road_ranges['road'] == row['road']]['min_lat'].empty:
                    # Look whether the bridge is on the range we have for the road
                    if row['lat'] < road_ranges[road_ranges['road'] == row['road']]['min_lat'].iloc[0] or row['lat'] > road_ranges[road_ranges['road'] == row['road']]['max_lat'].iloc[0]:
                        next_three_lat = 0
                        count = 0
                        # Check the latitude of the three following bridges on same road
                        for i in range(1, 4):
                            if df.loc[index+i, 'road'] == row.road:
                                next_three_lat += df.loc[index+i, 'lat']
                                count += 1
                        # prevent divide by zero
                        if count != 0:
                            avg_lat = next_three_lat/count
                            if row['lat'] < avg_lat - 0.3 or row['lat'] > avg_lat + 0.3:
                                # change dataframe lat to new value
                                df.loc[index, 'lat'] = avg_lat

                # If the road exists in the road ranges
                if not road_ranges[road_ranges['road'] == row['road']]['min_lon'].empty:
                    # Look whether the bridge is on the range we have for the road
                    if row['lon'] < road_ranges[road_ranges['road'] == row['road']]['min_lon'].iloc[0] or row['lon'] > road_ranges[road_ranges['road'] == row['road']]['max_lon'].iloc[0]:
                        next_three_lon = 0
                        count = 0
                        # Check the longitude of the three following bridges on same road
                        for i in range(1, 4):
                            if df.loc[index + i, 'road'] == row.road:
                                next_three_lon += df.loc[index + i, 'lon']
                                count += 1
                        # prevent divide by zero
                        if count != 0:
                            avg_lon = next_three_lon / count
                            if row['lon'] < avg_lon - 0.3 or row['lon'] > avg_lon + 0.3:
                                df.loc[index, 'lon'] = avg_lon

        # set previous values
        prev_row = df.loc[index]
    return df

def find_nonzero_nonnan_on_same_road(series, road_series, index, direction='next'):
    """
    Find the next or previous non-zero, non-NaN value in a series for the same road.
    """
    step = 1 if direction == 'next' else -1
    current_road = road_series.iloc[index]
    i = index + step
    while 0 <= i < len(series):
        if road_series.iloc[i] != current_road or (not pd.isna(series.iloc[i]) and series.iloc[i] != 0):
            break
        i += step
    if 0 <= i < len(series) and road_series.iloc[i] == current_road:
        return series.iloc[i]
    return None

def interpolate_or_assign_on_same_road(df, lat_col='lat', lon_col='lon', road_col='road'):
    """
    interpolate between the previous and next value if an identified value is 0
    if this doesn't work, it will assign the previous value, otherwise the next value (on the same road)
    """

    for i in range(1, len(df) - 1):  # Exclude first and last index to avoid out-of-bounds errors
        # interpolate lat values
        if pd.isna(df[lat_col].iloc[i]) or df[lat_col].iloc[i] == 0:
            prev_lat = find_nonzero_nonnan_on_same_road(df[lat_col], df[road_col], i, 'prev')
            next_lat = find_nonzero_nonnan_on_same_road(df[lat_col], df[road_col], i, 'next')
            if prev_lat is not None and next_lat is not None:
                df.at[i, lat_col] = (prev_lat + next_lat) / 2
            elif prev_lat is not None:
                df.at[i, lat_col] = prev_lat
            elif next_lat is not None:  # New condition to use next value if previous is not available
                df.at[i, lat_col] = next_lat

        # interpolate lon values
        if pd.isna(df[lon_col].iloc[i]) or df[lon_col].iloc[i] == 0:
            prev_lon = find_nonzero_nonnan_on_same_road(df[lon_col], df[road_col], i, 'prev')
            next_lon = find_nonzero_nonnan_on_same_road(df[lon_col], df[road_col], i, 'next')
            if prev_lon is not None and next_lon is not None:
                df.at[i, lon_col] = (prev_lon + next_lon) / 2
            elif prev_lon is not None:
                df.at[i, lon_col] = prev_lon
            elif next_lon is not None:  # New condition to use next value if previous is not available
                df.at[i, lon_col] = next_lon

    return df

def lon_lat_errors_tsv(df):
    index_changes = []
    for index, row in df.iterrows():
        prev_lat = None
        prev_lon = None
        for i, col in enumerate(df.columns, 0):
            if i % 3 == 2:
                if prev_lat is not None:
                    if row[col] > 40:
                        lat = row[col]
                        lon = row.iloc[i+1]
                        df.loc[index, col] = lon
                        df.iloc[index, i+1] = lat
                        index_changes.append((index, i, row[col], lon))
                    elif row[col] < prev_lat - 0.1 or row[col] > prev_lat + 0.1:
                        df.loc[index, col] = prev_lat
                        index_changes.append((index, i, row[col], prev_lat))
                prev_lat = df.loc[index, col]
            if i % 3 == 0 and i != 0:
                if prev_lon is not None:
                    if row[col] < prev_lon - 0.1 or row[col] > prev_lon + 0.1:
                        df.loc[index, col] = prev_lon
                        index_changes.append((index, i, row[col], prev_lon))
                prev_lon = df.loc[index, col]
    # print(index_changes)
    return df


def restructure_df(df):
    # construct empty list for the data
    restructured_data = []

    # iterate over the rows and each index
    for index, row in df.iterrows():
        road_name = row['road']
        # iterate over columns in groups of 3
        for i in range(1, len(df.columns), 3):
            try:
                # identify lsrp, lat and lon
                lsrp = row[i]
                lat = row[i + 1]
                lon = row[i + 2]
                # add the data to the list
                if pd.notnull(lsrp):
                    restructured_data.append([road_name, lsrp, lat, lon])
            except IndexError:
                # break if the end of the row is reached
                break

    # construct the dataframe
    df_restructured = pd.DataFrame(restructured_data, columns=['road', 'lsrp', 'lat', 'lon'])

    return df_restructured


def road_range_lon_lat(df):
    road_ranges = {}  # Use a dictionary to track road ranges

    for index, row in df.iterrows():
        road = row['road']
        lat = row['lat']
        lon = row['lon']

        if road not in road_ranges:
            # Initialize the road entry with current row's lat and lon as both min and max
            road_ranges[road] = {'road': road, 'min_lat': lat, 'max_lat': lat, 'min_lon': lon, 'max_lon': lon}
        else:
            # Update min and max latitudes and longitudes if necessary
            road_ranges[road]['min_lat'] = min(road_ranges[road]['min_lat'], lat)
            road_ranges[road]['max_lat'] = max(road_ranges[road]['max_lat'], lat)
            road_ranges[road]['min_lon'] = min(road_ranges[road]['min_lon'], lon)
            road_ranges[road]['max_lon'] = max(road_ranges[road]['max_lon'], lon)

    # Convert the road_ranges dictionary to a DataFrame
    rows_list = list(road_ranges.values())
    df_road_range = pd.DataFrame(rows_list)

    return df_road_range


def clean(bmms_file_excel, roads_tsv_file):
    bmms = pd.read_excel(bmms_file_excel)
    df_rds = pd.read_csv(roads_tsv_file, delimiter='\t', low_memory=False)
    df_rds = lon_lat_errors_tsv(df_rds)
    df_rds_restructured = restructure_df(df_rds)
    df_road_ranges = road_range_lon_lat(df_rds_restructured)
    bmms = clean_lon_lat_bmms(bmms, df_road_ranges)
    return bmms, df_rds, df_road_ranges, df_rds_restructured


def first_restructure(bmms_file_excel, roads_tsv_file):
    bmms = pd.read_excel(bmms_file_excel)
    df_rds = pd.read_csv(roads_tsv_file, delimiter='\t', low_memory=False)
    df_rds = lon_lat_errors_tsv(df_rds)
    df_rds_restructured = restructure_df(df_rds)
    return bmms, df_rds, df_rds_restructured


def second_restructure(bmms_file_excel, roads_tsv_file):
    bmms = pd.read_excel(bmms_file_excel)
    df_rds = pd.read_csv(roads_tsv_file, delimiter='\t', low_memory=False)
    df_rds = lon_lat_errors_tsv(df_rds)
    df_rds_restructured = restructure_df(df_rds)
    df_road_ranges = road_range_lon_lat(df_rds_restructured)
    return bmms, df_rds, df_road_ranges, df_rds_restructured


def make_files(bmms, df_rds):
    bmms.to_excel('BMMS_overview_new.xlsx', index=False, sheet_name='BMMS_overview')
    df_rds.to_csv('_roads_new.tsv', sep='\t', index=False)
    return bmms, df_rds
