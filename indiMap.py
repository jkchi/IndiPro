#!/usr/bin/env python
# coding: utf-8

# In[515]:


import pandas as pd
import altair as alt
import streamlit



state_map = 'https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json'
disSitu = pd.read_csv('disDataClean.csv',index_col = 0)
#disSitu = pd.read_csv('disData.csv')
#disSitu = disSitu[['Year', 'LocationAbbr', 'LocationDesc','Response',  'Data_Value','Number', 'WeightedNumber','LocationID']]
#disSitu.columns = ['year', 'LocationAbbr', 'state','Disability_Type',  'Disability_Percent','Number', 'Estimated_Number','id']
#HSSFilter = ['HHS Region 1','HHS Region 2','HHS Region 3','HHS Region 4','HHS Region 5',
             #'HHS Region 6','HHS Region 7','HHS Region 8','HHS Region 9','Guam','Puerto Rico'] 
#disSitu = disSitu.loc[ ~disSitu['LocationDesc'].isin(HSSFilter)] 
#disSitu['Disability_Percent'] = disSitu['Disability_Percent'] /100
#disSitu.to_csv("disDataClean.csv")


# In[516]:


disSituType = disSitu.loc[ disSitu['Disability_Type'].isin(['No Disability','Any Disability'])]
yearList = [2016, 2017, 2018,2019, 2020]


# noticing when using selecctionmult this will cause a graph size bug
click = alt.selection(type="single",fields=['state'],init = {'state':'United States, DC & Territories'} )

selectionGroupYear = alt.selection_single(
    fields=['year'],
    init={'year': yearList[0]},
    bind=alt.binding_select(options = yearList,name='Select year '),
    on="keyup",
    clear="false"
)

states = alt.topo_feature(state_map, 'states')

map = alt.Chart(disSitu).mark_geoshape(stroke='black', strokeWidth = 0.2
                           ).encode(color = alt.Color( 'Disability_Percent', 
                                              scale = alt.Scale(     
                                              scheme='reds', domain=[0.2, 0.4]
                                              ),
                                              
                                              legend = alt.Legend(title= ['Estimated Disability', 'Population by Percent'],format = '.0%',titlePadding = 20,orient = 'left')),
                                              opacity=alt.condition(click, alt.value(1), alt.value(0.7)),
                                              tooltip=['state', alt.Tooltip('Disability_Percent:Q',format = '.1%'),alt.Tooltip('Estimated_Number:Q')],
                                              ).add_selection(selectionGroupYear,click
                           ).transform_filter(alt.datum.Disability_Type == 'Any Disability'
                           ).transform_filter(selectionGroupYear 
                           ).transform_lookup(lookup='id', 
                                              from_ = alt.LookupData(states, 
                                                                     key='id', 
                                                                     fields=["type", "properties", "geometry"])
                           ).project(type='albersUsa').properties(width = 500)

map = map.encode(
  strokeWidth=alt.condition(click, alt.value(0.6), alt.value(0.2))
)

barTotal = alt.Chart(disSitu).mark_bar().encode(
    x=alt.X('Disability_Percent:Q',title='Estimated Disability Population by Percent'),
    color= alt.Color('Disability_Type',legend = None ),
    tooltip =['state', alt.Tooltip('Disability_Percent',format = '.1%'),'Disability_Type' ],
    
    y=alt.Y('Disability_Type',title = '')).add_selection(selectionGroupYear,click
                           ).transform_filter( alt.datum.Disability_Type != 'Any Disability'
                           ).transform_filter( alt.datum.Disability_Type != 'No Disability'
                           ).transform_filter(selectionGroupYear & click).properties(width = 500)

barType = alt.Chart(disSituType).mark_bar().encode(
    y=alt.Y('Disability_Percent:Q',title='Estimated Disability Population by Percent'),
    color = alt.Color('Disability_Type',scale = alt.Scale(scheme='greys')),
    tooltip =['state', alt.Tooltip('Disability_Percent',format = '.1%'),'Disability_Type' ],
    x=alt.X('Disability_Type',title = '')).add_selection(selectionGroupYear,click
                           ).transform_filter(selectionGroupYear & click).properties(width = 75)

final = ((map & barTotal)|barType).properties(title = 'American Disability Demographic').configure_title(fontSize = 25,align = "center").configure_axisX(labelFontSize = 15,titleFontSize = 14,labelLimit = 500
                                                                                                                     ).configure_axisY(labelFontSize = 12,titleFontSize = 14,labelLimit = 500)

final

