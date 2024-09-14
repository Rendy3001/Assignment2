import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt


@st.cache_data  # Cache the function to enhance performance
def load_data():

    file_path = 'https://github.com/aaubs/ds-master/raw/main/data/assignments_datasets/FINDEX/WLD_2021_FINDEX_v03_M_csv.zip'

    data_cleaned = pd.read_csv(file_path,  encoding='latin-1')

    # Create age groups and add as a new column
    bin_edges = [18, 25, 35, 45, 60]  
    bin_labels = ['18-24', '25-34', '35-44', '45-59']  
    data_cleaned['AgeGroup'] = pd.cut(data_cleaned['age'], bins=bin_edges, labels=bin_labels, right=False)

    #Create education labels and add as a new column
    labels = {1: 'Primary School or Less', 2: 'Secondary School', 3: 'Tertiary Education or More'}
    data_cleaned['educ_label'] = data_cleaned['educ'].map(labels)
    data_cleaned.educ_label.unique()
   
    #Create gender labels
    labels = {1: 'Female', 2: 'Male'}
    data_cleaned['Gender'] = data_cleaned['female'].map(labels)
    data_cleaned.Gender.unique()

    #Create labels for digital payments
    labels = {0: 'No digital payments', 1:'There are digital payments'}
    data_cleaned['DigitalPayments'] = data_cleaned['anydigpayment'].map(labels)
    data_cleaned.DigitalPayments.unique()


    return data_cleaned

data_cleaned = load_data()


#Title and side bar
st.title('Findings from FINDEX database 📈')
st.sidebar.header('Filters 📊')
st.markdown("""
            The Global Findex database is the most comprehensive dataset on adult financial behaviors worldwide, capturing insights into how individuals save, borrow, make payments, and manage financial risks. Initiated by the World Bank in 2011, the dataset is based on nationally representative surveys of over 150,000 adults across more than 140 economies. The 2021 edition provides updated indicators on the use of both formal and informal financial services.
""")


#Sidebar filter: Age group
selected_age_group = st.sidebar.multiselect('Select Age Groups 🕰️', data_cleaned['AgeGroup'].unique().tolist(), default=data_cleaned['AgeGroup'].unique().tolist())
if not selected_age_group:
    st.warning('Please select an age group from the sidebar')
    st.stop()
filtered_dataframe = data_cleaned[data_cleaned['AgeGroup'].isin(selected_age_group)]


#Sidebar filer: Education level
education = data_cleaned['educ_label'].unique().tolist()
select_education = st.sidebar.multiselect('Select Education 🧑‍🎓', education, default=education)
if not select_education:
    st.warning("Please select an education level")
    st.stop()
filtered_dataframe = filtered_dataframe[filtered_dataframe['educ_label'].isin(select_education)]

#Sidebar filter: Income group
selected_income = st.sidebar.multiselect('Select income 💰', data_cleaned['inc_q'].unique().tolist(), default = data_cleaned['inc_q'].unique().tolist())
if not selected_income:
    st.warning('Please select an income group from the sidebar')
    st.stop()
filtered_dataframe = data_cleaned[data_cleaned['inc_q'].isin(selected_income)]


# Dropdown to select the type of visualization
visualization_option = st.selectbox(
    'Select Visualization', 
    ['Distribution by Gender 🧑', 
    'Proportion of People Who Save by Education Level and Income Quantile 🤑', 
    'Proportion of People Who Borrow by Education Level and Income Quantile 💸',
    'Digital payments across regions 📱']
)

#Visualizations
if visualization_option == 'Distribution by Gender 🧑':
    
    # Pie chart for attrition distribution by gender
    pie_chart_data = filtered_dataframe['Gender'].value_counts().reset_index()
    pie_chart_data.columns = ['Gender', 'count']

    chart = alt.Chart(pie_chart_data).mark_arc().encode(
        theta='count:Q',
        color='Gender:N',
        tooltip=['Gender', 'count']
    ).properties(
        title='Distribution by Gender',
        width=300,
        height=300
    )
    st.altair_chart(chart, use_container_width=True)

elif visualization_option == 'Proportion of People Who Save by Education Level and Income Quantile 🤑':

    saving_by_educ_income = filtered_dataframe.groupby(['educ_label', 'inc_q'])['saved'].mean().reset_index()

    # Create the heatmap
    heatmap = alt.Chart(saving_by_educ_income).mark_rect().encode(
        x=alt.X('inc_q:N', title='Income Quantile'),
        y=alt.Y('educ_label:N', title='Education Level'),
        color=alt.Color('saved:Q', scale=alt.Scale(scheme='blues'), title='Proportion Saved'), 
        tooltip=['educ_label', 'inc_q', alt.Tooltip('saved:Q', format='.2f')] 
    ).properties(
        title='Proportion of People Who Save by Education Level and Income Quantile',
        width=400,
        height=300
    )

    st.altair_chart(heatmap, use_container_width=True)

elif visualization_option == 'Proportion of People Who Borrow by Education Level and Income Quantile 💸':

    saving_by_educ_income = filtered_dataframe.groupby(['educ_label', 'inc_q'])['borrowed'].mean().reset_index()

    # Create the heatmap
    heatmap = alt.Chart(saving_by_educ_income).mark_rect().encode(
        x=alt.X('inc_q:N', title='Income Quantile'),
        y=alt.Y('educ_label:N', title='Education Level'),
        color=alt.Color('borrowed:Q', scale=alt.Scale(scheme='reds'), title='Proportion Borrowed'), 
        tooltip=['educ_label', 'inc_q', alt.Tooltip('borrowed:Q', format='.2f')] 
    ).properties(
        title='Proportion of People Who Borrow by Education Level and Income Quantile',
        width=400,
        height=300
    )

    st.altair_chart(heatmap, use_container_width=True)

elif visualization_option == 'Digital payments across regions 📱':
   # Group by region and calculate the mean digital payment usage
    region_digital_counts = filtered_dataframe.groupby('regionwb')['anydigpayment'].mean().reset_index()

    count_chart = alt.Chart(filtered_dataframe).mark_bar().encode(
        x=alt.X('regionwb:N', title='Region', sort='-y'),
        y=alt.Y('count():Q', title='Count'),
        color='DigitalPayments:N',
        tooltip=['regionwb', 'count()']
    ).properties(
        title='Digital Payments by Region',
        width=500,
        height=300
    ).configure_axisX(
        labelAngle=-45
     )

    st.altair_chart(count_chart, use_container_width=True)

# Display dataset overview
st.header("Dataset Overview")
st.dataframe(filtered_dataframe)

# Insights from Visualization
with st.expander("Insights from Visualization 🧠"):
    st.markdown("""
    1. **Distribution by Gender** - The 'Distribution by gender' pie chart showcases distribution by gender.
    2. **Saving by Education Level and Income Quantile** - The 'Proportion of People Who Save by Education Level and Income Quantile' visualizes how people save money based on their education and income.
    3. **Borrowing by Education Level and Income Quantile** - The 'Proportion of People Who Borrow by Education Level and Income Quantile' visualizes how people borrow money based on their education and income.
    4. **Digital payments** - The 'Digital payments across regions' show if there are any digital payments happening across regions.
    """)

#Recommendations
with st.expander("Recommendations for Action 🌟"):
    st.markdown("""
    **Digitalization growth** - The recommendation would be to introduce more digital product in the regions with high number of digital payments.
    """)

