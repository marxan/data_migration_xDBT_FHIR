#Importing libraries

import pandas as pd
import numpy as np
import json
import logging
import collections.abc


#1.1. Open the data and store it in an array

file = open("/Users/marchan/Documents/Git/migration_xDBT_FHIR/data/input_data/x03985126500.txt", 'r')
data = pd.DataFrame({"raw_col": file})
data['raw_col'] = data['raw_col'].str[3:-1]

# Create labels for each block
data['block_label'] = data['raw_col'].str[:9]
data['block_label'] = data['block_label'].apply(lambda x: x[4:] if x[:4] == '8000' else np.nan)
data['block_label'].fillna(method='ffill', inplace=True)

#-----Block 6100: Patientenstamm
#-------------------------------
# 2.1. Reading columns for block 6100:
# Read reference table (from document "xBDT-2.9_21-5")
Patientenstamm_ref = pd.read_csv("/Users/marchan/Documents/Git/migration_xDBT_FHIR/data/input_data/xBDT-2.9_21-5_6100.csv")

Patientenstamm_ref = Patientenstamm_ref.reset_index(drop=True).rename_axis('order_Feldkenn').reset_index()
Patientenstamm_ref.order_Feldkenn =  (Patientenstamm_ref['order_Feldkenn'] + 1)

# Column Bezeichnung der Inhalte hast repeated values ('Wohnort des Vers.', 'Weitere freie Kategorien mit zugehörigem Inhalt' and 'Arztkennzeichnung') so I renamed them
Patientenstamm_ref = Patientenstamm_ref.sort_values('order_Feldkenn')

# 2.2. Prepare the ref and raw data
Patientenstamm_raw = data[data['block_label'] == '6100'].reset_index(drop=True)
# Drop raw records that cannot be categorized
Patientenstamm_drop_list = np.setdiff1d(Patientenstamm_raw['raw_col'].str[:4],Patientenstamm_ref.Feldkenn)
Patientenstamm_raw_dropped = Patientenstamm_raw[~Patientenstamm_raw['raw_col'].str[:4].isin(Patientenstamm_drop_list)]
#check
# Patientenstamm_raw_dropped.Feldkenn.isin(Patientenstamm_drop_list).value_counts()
print('Raw records (rows) to drop because not found on ref dataframe:',np.setdiff1d(Patientenstamm_raw['raw_col'].str[:4],Patientenstamm_ref.Feldkenn))
#Save records that are not found in the ref data:
logging.basicConfig(filename='unkown_data6100.log', encoding='utf-8', level=logging.DEBUG)
unknown_feldkenn = np.setdiff1d(data['raw_col'].str[:4],Patientenstamm_ref.Feldkenn)
logging.info("NOWHERE in the reference data(neither within other blocks): {'3721', '3722', '3723', '3725', '3720', '3724'}")


# Merge ref and raw on Patientenstamm_raw['block_label']
Patientenstamm_raw_dropped['Feldkenn'] = Patientenstamm_raw_dropped['raw_col'].str[:4]


Patientenstamm_ref_raw = Patientenstamm_ref.merge(Patientenstamm_raw_dropped[['raw_col','Feldkenn']], on='Feldkenn', how='inner')

#create a placeholder for the n patients IDs (raw ref data)
Patientenstamm_ref_raw['PatientID'] = Patientenstamm_ref_raw.groupby(['order_Feldkenn']).cumcount()+1

Patientenstamm_ref_raw = Patientenstamm_ref_raw.loc[:,['PatientID','order_Feldkenn','Nesting','nest_order','nest_parent','Feldkenn','Bezeichnung der Feldinhalte','raw_col']]
Patientenstamm_ref_raw[['PatientID','order_Feldkenn']] = Patientenstamm_ref_raw.loc[:,['PatientID','order_Feldkenn']].astype('int').sort_values(['PatientID','order_Feldkenn'])
Patientenstamm_ref_raw['raw_col'] =  Patientenstamm_ref_raw['raw_col'].str[4:]
Patientenstamm_ref_raw = Patientenstamm_ref_raw.sort_values(['PatientID','nest_order','nest_parent'])

Patientenstamm_ref_raw = Patientenstamm_ref_raw[Patientenstamm_ref_raw.raw_col.notna()]


Patientenstamm_ref_raw_dict = Patientenstamm_ref_raw.groupby('PatientID').apply(lambda a: a.groupby('Feldkenn').apply(lambda x: dict(zip((x['Bezeichnung der Feldinhalte']), x['raw_col']))))

Patientenstamm_ref_raw_dict_df = pd.DataFrame(Patientenstamm_ref_raw_dict).reset_index()
Patientenstamm_ref_raw_dict_df.rename(columns={0:'Resource'},inplace=True)

Patientenstamm_df = pd.merge(Patientenstamm_ref_raw, Patientenstamm_ref_raw_dict_df, on=['Feldkenn','PatientID'], how='left')
Patientenstamm_df  = Patientenstamm_df.astype(str)
Patientenstamm_df.to_csv('/Users/marchan/Documents/Git/migration_xDBT_FHIR/data/output_data/xBDT-2.9_21-5_6100Raw.csv',index=False)




