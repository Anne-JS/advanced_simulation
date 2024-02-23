import Functions as F

""""
Run this script to clean the BMMMS_overview.xlsx and _roads.tsv files. 
Output will be BMMS_overiew_new.xlsx and _roads_new.tsv
"""

def main():
    bmms, df_rds, df_road_ranges, df_rds_restructured = F.clean(input/'BMMS_overview.xlsx', input/'_roads.tsv')
    F.make_files(bmms, df_rds)
    return bmms, df_rds, df_road_ranges, df_rds_restructured


main()
