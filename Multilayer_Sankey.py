'''
DS3500 HW1:    Museum of Contemporary Art
Tianyang Bao   001467761'''

import plotly.graph_objects as go
import json
import pandas as pd
from math import floor

def file_import(file,columns):
    #Read in the json file and convert to pandas dataframe
    json_file = json.load(open(file, 'r'))
    art_df = pd.DataFrame.from_dict(json_file)
    #Dataframe containing necessary columns - can be adjusted via user input collection
    art_df = art_df[columns]
    
    #Derive artist's birth decade from begindate
    art_df['Decade'] = art_df.BeginDate.apply(lambda x: floor(x/10)*10)
    
    #Removing decade of 0 since they are unknown
    art_df = art_df[(art_df.Decade != 0)] 
    #Lowercase Gender and remove None vals
    art_df['Gender'] = art_df['Gender'].str.lower()
    art_df = art_df[(art_df.Gender != 'None')] 
    #Clean Nationality for Unknown vals
    art_df = art_df[(art_df.Nationality != 'Nationality unknown')] 
    
    #Return the dataframe after cleaning work
    return art_df

def code_mapping(df, src, targ):
    """map labels in src and targ columns into integers """
    labels = list(df[src]) + list(df[targ])
   
    codes = list(range(len(labels)))

    lcmap = dict(zip(labels, codes))

    df = df.replace({src:lcmap, targ:lcmap})
    return df, labels

def make_sankey(df, src, targ, vals=None,**kwargs):
    df, labels = code_mapping(df,src,targ)
    
    if vals:
        value = df[vals]
    else:
        value = [1]*df.shape[0]
    #specify source MUST target value as key names
    link = {'source':df[src],'target':df[targ],'value':value}

    pad = kwargs.get('pad',100)
    thickness = kwargs.get('thickness',10)
    line_color = kwargs.get('color','black')
    width = kwargs.get('width',4)
    
    node = {'label':labels, 
            'pad':pad, 'thickness':thickness,
            'line':{'color':'black','width':width}}

    sk =go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.show()

def gb_prod(df,src,targ,gb_index,threshold):
    #Generate counts column by groupby
    gb_df = df.groupby([src,targ ]).size().reset_index(name=gb_index)
    #Filter the dataframe by counts>= threshold; threshold can be adjusted via input collection
    gb_df = gb_df[(gb_df.counts >= threshold)]
    return gb_df

def multi_df(df,src,targ,gb_index,threshold,src_coln,targ_coln):
    #Concatenate all source items: Nationality + Gender into a list
    src_items = []
    for each in src:
        src_items += list(df[each])
        
    #Concatenate all target items: Gender + Decade into a list
    targ_items = []
    for item in targ:
        targ_items += list(df[item])
    
    #Create a new dataframe containing source and target items where columns are names as src_coln and targ_coln
    mul_df = pd.DataFrame(src_items,columns=[src_coln])
    mul_df[targ_coln]=targ_items

    #Generate the counts column by groupby function
    mul_df = mul_df.groupby([src_coln, targ_coln]).size().reset_index(name=gb_index)
    mul_df = mul_df[(mul_df.counts >= threshold)]
    return mul_df

def main():
    
    #firstly, collect inputs for diagram generation process
    # Nationality Gender BeginDate
    columns = list(input('What are the columnns you want to include? \nPlease seperate them by space. ').split())
    f_mul_ind = input('What are source columns? \nPlease seperate them by space. ').split()# Nationality Gender
    t_mul_ind = input('What are target columns? \nPlease seperate them by space. ').split()# Gender Decade
    gb_index = input('How do you want to group the dataframe? ')# counts
    threshold = int(input('What is the numeric threshold? '))# 20
    file = input('What is the file in use? ')# Artists.json

    #Import the artists file and clean it for lower cases, None values, and Unknown vals
    sank_df = file_import(file,columns)
    
    #Generate Nationality->Gender diagram
    nat_gen_df = gb_prod(sank_df,f_mul_ind[0],t_mul_ind[0],gb_index,threshold)
    make_sankey(nat_gen_df,f_mul_ind[0],t_mul_ind[0],gb_index)
    
    #Generate Gender->Decade diagram
    gen_deca_df = gb_prod(sank_df,f_mul_ind[1],t_mul_ind[1],gb_index,threshold)
    make_sankey(gen_deca_df,f_mul_ind[1],t_mul_ind[1],gb_index)
    
    #Generate Nationality->Decade diagram
    nat_deca_df = gb_prod(sank_df,f_mul_ind[0],t_mul_ind[1],gb_index,threshold)
    make_sankey(nat_deca_df,f_mul_ind[0],t_mul_ind[1],gb_index)
    
    #Generate Multilayer Sankey Diagram Nationality->Gender->Decade
    mul_df = multi_df(sank_df,f_mul_ind,t_mul_ind,gb_index,threshold,'Nat_Gen','Gen_Deca')
    make_sankey(mul_df,'Nat_Gen','Gen_Deca','counts')
    
if __name__ == "__main__":
    main()
