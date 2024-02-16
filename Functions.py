import pandas as pd

def clean_lon_lat_bmms(df):
    for index, row in df.iterrows():
        if row.lat > 27 or row.lon < 88:
            lat = row.lat
            lon = row.lon
            df.loc[index, 'lat'] = lon
            df.loc[index, 'lon'] = lat
            print(f'road {row.road} at index {index} changed from lat {lat} to lat {lon}')
    prev_row = None
    for index, row in df.iterrows():
        if prev_row is not None:
            if row['road'] == prev_row['road']:
                if row['lat'] < prev_row['lat'] - 0.5 or row['lat'] > prev_row['lat'] + 0.5:
                    print(
                        f"on road {row['road']} with the index,name {index} {row['name']} the old latitude was {row['lat']} while previous was {prev_row['lat']}")
                    df.loc[index, 'lat'] = prev_row['lat']
                if row['lon'] < prev_row['lon'] - 0.5 or row['lon'] > prev_row['lon'] + 0.5:
                    print(
                        f"on road {row['road']} with the name {index} {row['name']} the old longitude was {row['lon']} while previous was {prev_row['lon']}")
                    df.loc[index, 'lon'] = prev_row['lon']
        prev_row = df.loc[index]
    return df


def clean_lon_lat_roads(df):
    prev_row = None
    for index, row in df.iterrows():
        if prev_row is not None:
            if row['road'] == prev_row['road']:
                if row['lat'] < prev_row['lat'] - 0.5 or row['lat'] > prev_row['lat'] + 0.5:
                    print(f"on road {row['road']} with the index,name {index} {row['name']} the old latitude was {row['lat']} while previous was {prev_row['lat']}")
                    df.loc[index, 'lat'] = prev_row['lat']
                if row['lon'] < prev_row['lon'] - 0.5 or row['lon'] > prev_row['lon'] + 0.5:
                    print(f"on road {row['road']} with the name {index} {row['name']} the old longitude was {row['lon']} while previous was {prev_row['lon']}")
                    df.loc[index, 'lon'] = prev_row['lon']
        prev_row = df.loc[index]
    return df

def lon_lat_errors_tsv(df):
    columns = df.columns
    index_changes = []
    for index, row in df.iterrows():
        prev_lat = None
        prev_lon = None
        for i, col in enumerate(df.columns, 0):
            if i % 3 ==2:
                if prev_lat is not None:
                    if row[col] > 40:
                        lat = row[col]
                        lon = row.iloc[i+1]
                        df.loc[index, col] = lon
                        df.iloc[index, i+1] = lat
                        index_changes.append((index, i, row[col], lon))
                    elif row[col] < prev_lat - 0.5 or row[col] > prev_lat+ 0.5:
                        df.loc[index, col] = prev_lat
                        index_changes.append((index, i, row[col], prev_lat))
                prev_lat = df.loc[index, col]
            if i % 3 == 0 and i != 0:
                if prev_lon is not None:
                    if row[col] < prev_lon - 0.5 or row[col] > prev_lon+ 0.5:
                        df.loc[index, col] = prev_lon
                        index_changes.append((index, i, row[col], prev_lon))
                prev_lon = df.loc[index, col]
    print(index_changes)
    return df

def restructure_df(df):
    #importing the tsv file with appropriate delimiter, suppress low memory warning
    #df_rds = pd.read_csv("tsv_file", delimiter='\t', low_memory = False)

    #construct empty list for the data
    restructured_data = []

    #iterate over the rows and each index
    for index, row in df.iterrows():
        road_name = row['road']
        #iterate over columns in groups of 3
        for i in range(1, len(df.columns), 3):
            try:
                #identify lsrp, lat and lon
                lsrp = row[i]
                lat = row[i + 1]
                lon = row[i + 2]
                #add the data to the list
                if pd.notnull(lsrp):
                    restructured_data.append([road_name, lsrp, lat, lon])
            except IndexError:
                #break if the end of the row is reached
                break

    #construct the dataframe
    df_restructured = pd.DataFrame(restructured_data, columns=['road', 'lsrp', 'lat', 'lon'])

    return df_restructured

def road_range_lon_lat(df):
    df_road_range = pd.DataFrame(columns = ['road', 'min_lat', 'max_lat', 'min_lon', 'max_lon'])
    for index, row in df.iterrows():
        # Check if the road is already in df_road_range
        if row['road'] in df_road_range['road'].values:
            # Find the index of the existing road entry in df_road_range
            road_index = df_road_range[df_road_range['road'] == row['road']].index[0]

            # Update min and max latitude and longitude if necessary
            df_road_range.at[road_index, 'min_lat'] = min(df_road_range.at[road_index, 'min_lat'], row['lat'])
            df_road_range.at[road_index, 'max_lat'] = max(df_road_range.at[road_index, 'max_lat'], row['lat'])
            df_road_range.at[road_index, 'min_lon'] = min(df_road_range.at[road_index, 'min_lon'], row['lon'])
            df_road_range.at[road_index, 'max_lon'] = max(df_road_range.at[road_index, 'max_lon'], row['lon'])
        else:
            # If not, append a new row with the current values
            new_row = {'road': row['road'],
                       'min_lat': row['lat'], 'max_lat': row['lat'],
                       'min_lon': row['lon'], 'max_lon': row['lon']}
            df_road_range = df_road_range.append(new_row, ignore_index=True)
    return df_road_range

