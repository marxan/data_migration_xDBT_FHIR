#Importing libraries

import pandas as pd
import numpy as np
import json
import logging
#import collections.abc
from source import update


#Read data:
#RAW
Patientenstamm_df = pd.read_csv(r'/Users/marchan/Documents/Git/migration_xDBT_FHIR/data/output_data/xBDT-2.9_21-5_6100Raw.csv')


# NESTING TYPE 1 (one level 1 and one level 2)

Patientenstamm_df_n1 = Patientenstamm_df[Patientenstamm_df['nest_order'].isin([1,4,5,6,7,8,9,10,11,12])]
Patientenstamm_df_n1 = Patientenstamm_df_n1[Patientenstamm_df_n1['Resource'].notna()] 
# Patientenstamm_df_n1 = Patientenstamm_df_n1[Patientenstamm_df_n1['nest_parent'].notna()]


#Level 1 with level 2 (if level 2 comes after level 1)

Patientenstamm_df_n1 = Patientenstamm_df_n1.sort_values(['PatientID','order_Feldkenn'])
Patientenstamm_df_n1['Resource_child_L1'] = Patientenstamm_df_n1['Resource'].shift(-1)
Patientenstamm_df_n1_subset = Patientenstamm_df_n1[Patientenstamm_df_n1['Nesting'] == 'level_1']

Patientenstamm_df_n1 = Patientenstamm_df_n1.iloc[:,:-1].merge(Patientenstamm_df_n1_subset[['Feldkenn','Resource_child_L1']], on='Feldkenn', how='inner')
Patientenstamm_df_n1 = Patientenstamm_df_n1[Patientenstamm_df_n1['Resource_child_L1'].notna()] 


Patientenstamm_df_n1_l1 = Patientenstamm_df_n1.groupby('PatientID').apply(lambda a: a.groupby('Feldkenn').apply(lambda x: dict(zip('_'+ x['Bezeichnung der Feldinhalte'],x['Resource_child_L1']))))

Patientenstamm_df_n1 = pd.DataFrame(Patientenstamm_df_n1_l1).reset_index()
Patientenstamm_df_n1.rename(columns={0:'Resource_child_n1'},inplace=True)

Patientenstamm_df_n1 = pd.merge(Patientenstamm_df_n1[['PatientID','Resource_child_n1','Feldkenn']],Patientenstamm_df[['PatientID','nest_order','Feldkenn','nest_parent','Resource']], how='outer',on=['PatientID','Feldkenn'])



dict_2_n1 = Patientenstamm_df_n1.Resource.to_dict()
dict_1_n1 = Patientenstamm_df_n1.Resource_child_n1.to_dict()

Patientenstamm_df_n1['Resource_dict_n1'] = pd.Series(update(dict_2_n1,dict_1_n1))
Patientenstamm_df_n1 = Patientenstamm_df_n1.loc[Patientenstamm_df_n1['nest_order'].isin([1,4,5,6,7,8,9,10,11,12])]



# NESTING TYPE 2 (one level 1 > several level 2)

#level1_2
Patientenstamm_df_n2 = Patientenstamm_df[Patientenstamm_df['nest_order'].isin([13])]


#level_1
Patientenstamm_df_n2_l1 = Patientenstamm_df_n2[Patientenstamm_df_n2['Nesting'] == 'level_1']
#level2
Patientenstamm_df_n2_l2 = Patientenstamm_df_n2[Patientenstamm_df_n2['Nesting'] == 'level_2']
Patientenstamm_df_n2_l2 = Patientenstamm_df_n2_l2.groupby(['PatientID','nest_order']).apply(lambda x: dict(zip(x['Bezeichnung der Feldinhalte'], x['raw_col'])))
Patientenstamm_df_n2_l2 = pd.DataFrame(Patientenstamm_df_n2_l2).reset_index()
Patientenstamm_df_n2_l2.rename(columns={'PatientID':'PatientID',0:'Resource_child_n'},inplace=True)

#merge level 1 and 2
Patientenstamm_df_n2 = pd.merge(Patientenstamm_df_n2_l1, Patientenstamm_df_n2_l2, on=['PatientID','nest_order'], how='outer')

#save nested col (levels 1 and 2) as dictionary
Patientenstamm_df_n2 = Patientenstamm_df_n2.groupby(['PatientID','Feldkenn'])[['Bezeichnung der Feldinhalte','Resource_child_n']].apply(lambda x: dict(zip('_'+ x['Bezeichnung der Feldinhalte'],x['Resource_child_n'])))
Patientenstamm_df_n2 = pd.DataFrame(Patientenstamm_df_n2).reset_index()
Patientenstamm_df_n2.rename(columns={0:'Resource_child_n2'},inplace=True)
Patientenstamm_df_n2 = pd.merge(Patientenstamm_df_n2[['PatientID','Resource_child_n2','Feldkenn']],Patientenstamm_df[['PatientID','nest_order','Feldkenn','Resource']], how='outer',on=['PatientID','Feldkenn'])


dict_2_n2 = Patientenstamm_df_n2.Resource.to_dict()
dict_1_n2 = Patientenstamm_df_n2.Resource_child_n2.to_dict()

Patientenstamm_df_n2['Resource_dict_n2'] = pd.Series(update(dict_2_n2,dict_1_n2))

Patientenstamm_df_n2 = Patientenstamm_df_n2.loc[Patientenstamm_df_n2['nest_order'].isin([13])]

# NESTING TYPE 3 (one level 1 > seveal level 2 > several level 3)


#### Filtering
#level1_2_3
Patientenstamm_df_n3 = Patientenstamm_df[Patientenstamm_df['nest_order'].isin([2,3])]


#level_1
Patientenstamm_df_n3_l1_filter = Patientenstamm_df_n3.loc[Patientenstamm_df_n3['Nesting'] == 'level_1', ['PatientID','nest_order','nest_parent','Resource','Bezeichnung der Feldinhalte','order_Feldkenn']]

#level2
Patientenstamm_df_n3_l2_filter = Patientenstamm_df_n3[Patientenstamm_df_n3['Nesting'] == 'level_2']

#level3
Patientenstamm_df_n3_l3_filter = Patientenstamm_df_n3[Patientenstamm_df_n3['Nesting'] == 'level_3']




############## Dictionary nesting (level 1 - level 2 and level 2 - level 3)

#### Dictionary

#level 2
Patientenstamm_df_n3_l2 = Patientenstamm_df_n3_l2_filter.groupby(['PatientID','nest_order']).apply(lambda x: x.sort_values(['order_Feldkenn'])).reset_index(drop=True)
Patientenstamm_df_n3_l2 = Patientenstamm_df_n3_l2.groupby(['PatientID','nest_order']).apply(lambda x: dict(zip(x['Bezeichnung der Feldinhalte'], x['raw_col'])))
Patientenstamm_df_n3_l2 = pd.DataFrame(Patientenstamm_df_n3_l2).reset_index()
Patientenstamm_df_n3_l2.rename(columns={0:'Resource_child_n3_l2'},inplace=True)

#Rejoin the nest_parent and Bezeichnung der Feldinhalte (from the Patientenstamm_df)
Patientenstamm_df_n3_l2 = Patientenstamm_df_n3_l2.merge(Patientenstamm_df[['PatientID','nest_order','nest_parent','Bezeichnung der Feldinhalte','order_Feldkenn','Nesting']], on=['PatientID','nest_order'], how='inner')


# level 3
Patientenstamm_df_n3_l3 = Patientenstamm_df_n3_l3_filter.groupby(['PatientID','nest_order']).apply(lambda x: x.sort_values(['order_Feldkenn'])).reset_index(drop=True)
Patientenstamm_df_n3_l3 = Patientenstamm_df_n3_l3_filter.groupby(['PatientID','nest_order']).apply(lambda x: dict(zip(x['Bezeichnung der Feldinhalte'], x['raw_col'])))
Patientenstamm_df_n3_l3 = pd.DataFrame(Patientenstamm_df_n3_l3).reset_index()
Patientenstamm_df_n3_l3.rename(columns={0:'Resource_child_n3_l3'},inplace=True)

#Rejoin the nest_parent and Bezeichnung der Feldinhalte (from the Patientenstamm_df)
Patientenstamm_df_n3_l3 = Patientenstamm_df_n3_l3.merge(Patientenstamm_df[['PatientID','nest_order','nest_parent','Bezeichnung der Feldinhalte','order_Feldkenn']], on=['PatientID','nest_order'], how='inner')

# level 3 --> Add "_" column to level 3 so it can be subnested to level 2 afterwards
Patientenstamm_df_n3_l3 = Patientenstamm_df_n3_l3.groupby(['PatientID','nest_order','nest_parent'])[['Bezeichnung der Feldinhalte','Resource_child_n3_l3']].apply(lambda x: dict(zip('_'+ x['Bezeichnung der Feldinhalte'],x['Resource_child_n3_l3'])))
Patientenstamm_df_n3_l3 = pd.DataFrame(Patientenstamm_df_n3_l3).reset_index()
Patientenstamm_df_n3_l3.rename(columns={0:'Resource_child_n3_l3'},inplace=True)




#merge level 2 and 3
Patientenstamm_df_n3_l2l3 = pd.merge(Patientenstamm_df_n3_l2, Patientenstamm_df_n3_l3, on=['PatientID','nest_order','nest_parent'], how='outer')
Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3.sort_values(['PatientID','order_Feldkenn'])




# #save nested col (levels 2 and 3) as dictionary
Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3.groupby(['PatientID','nest_order']).apply(lambda x: x.sort_values(['order_Feldkenn'])).reset_index(drop=True)
#Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3[Patientenstamm_df_n3_l2l3.nest_parent.notna()]

# level 3 + 2 --> Add "_" column to level 3 + 2 so it can be subnested to level 1 afterwards
Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3[Patientenstamm_df_n3_l2l3['Nesting'].isin(['level_2','level_3'])]
Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3[Patientenstamm_df_n3_l2l3.nest_parent.notna()]


Patientenstamm_df_n3_l2l3 = Patientenstamm_df_n3_l2l3.groupby(['PatientID','nest_order']).apply(lambda x: update(x['Resource_child_n3_l2'],x['Resource_child_n3_l3']))
Patientenstamm_df_n3_l2l3 = pd.DataFrame(Patientenstamm_df_n3_l2l3).reset_index()
Patientenstamm_df_n3_l2l3.rename(columns={'Resource_child_n3_l2':'Resource_child_n3_l2l3'},inplace=True)


Patientenstamm_df_n3 = pd.merge(Patientenstamm_df_n3_l2l3, Patientenstamm_df_n3_l1_filter, on=['PatientID','nest_order'], how='outer')

Patientenstamm_df_n3 = Patientenstamm_df_n3.groupby(['PatientID','nest_order']).apply(lambda x: update(x['Resource'],x['Resource_child_n3_l2l3']))
Patientenstamm_df_n3 = pd.DataFrame(Patientenstamm_df_n3).reset_index()
Patientenstamm_df_n3.rename(columns={'Resource':'Resource_dict_n3'},inplace=True)


Patientenstamm_df_n0 = Patientenstamm_df[Patientenstamm_df['nest_order']==0]


Patientenstamm_df_01 = pd.merge(Patientenstamm_df_n1[['PatientID','Resource_dict_n1','nest_order']],Patientenstamm_df_n0[['PatientID','Resource','nest_order']], how='outer',on=['PatientID','nest_order'])
Patientenstamm_df_012 = pd.merge(Patientenstamm_df_01[['PatientID','Resource_dict_n1','nest_order','Resource']],Patientenstamm_df_n2[['PatientID','Resource_dict_n2','nest_order']], how='outer',on=['PatientID','nest_order'])
Patientenstamm_df_0123 = pd.merge(Patientenstamm_df_012,Patientenstamm_df_n3[['PatientID','Resource_dict_n3','nest_order']], how='outer',on=['PatientID','nest_order'])

#Create DICTIONARY COLUMN:
Patientenstamm_df_0123['resource_dict'] = np.where(Patientenstamm_df_0123['nest_order'] == 0, Patientenstamm_df_0123['Resource'], np.where(Patientenstamm_df_0123['nest_order'].isin([1,4,5,6,7,8,9,10,11,12]), Patientenstamm_df_0123['Resource_dict_n1'], np.where(Patientenstamm_df_0123['nest_order']== 13,Patientenstamm_df_0123['Resource_dict_n2'], Patientenstamm_df_0123['Resource_dict_n3'])))

#JSON DUMPS
Patientenstamm_df2json = Patientenstamm_df_0123.loc[:,['PatientID','resource_dict']].dropna()
Patientenstamm_df2json_dict = Patientenstamm_df2json.groupby('PatientID')[['PatientID','resource_dict']].apply(lambda x: dict(zip(x['PatientID'],x['resource_dict'])))
Patientenstamm_df2json_dict_vals = Patientenstamm_df2json_dict.values.tolist()
# print(json.dumps(Patientenstamm_df2json_dict_vals))

# with open('/Users/marchan/Documents/Git/migration_xDBT_FHIR/output_data/xBDT-2.9_21-5_6100vals.json', 'w') as json_file:
#   json.dump(Patientenstamm_df2json_dict_vals, json_file, sort_keys=True, indent=4)












