#!/usr/bin/env python
# coding: utf-8

# In[50]:


#############################################################################################################################################
#Import required libraries
##############################################################################################################################################

import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, Dash #thought I was importing it here but compiler says no..
import dash #was getting a weird error about not importing dash. Importing it here seems to have fixed it. Not sure why yet. Something to look
            #into in the future
import dash_bootstrap_components as dbc
import numpy as np
from plotly.subplots import make_subplots


#############################################################################################################################################
#Load in Data Sets
##############################################################################################################################################
stock_file = "data/S&P 500 Historical Data.csv"
gold_file = "data/exported_gold_data.csv"
inflation_file = "data/cleaned_inflation_data.csv"

#############################################################################################################################################
#Tiday our Stock Data
#Use read_csv to bring in data
#Use copy to keep only date and price column
#Convert price to numeric and remove commas which were causing issues
#Convert date to datetime and format it to match gold price date
#While there shouldn't be any NaN values drop any that may exist
#Only use dates that are greater than or equal to 1970-02
##############################################################################################################################################
dfStock = pd.read_csv(stock_file)
dfStock = dfStock[['Date', 'Price']].copy()
dfStock['Price'] = pd.to_numeric(dfStock['Price'].replace(',', '', regex=True), errors='coerce')
dfStock['Date'] = pd.to_datetime(dfStock['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m')
dfStock = dfStock.dropna().sort_values(by='Date').reset_index(drop=True)
dfStock = dfStock[dfStock['Date'] >= '1970-02']

#############################################################################################################################################
#Tidy our Gold Data
#Use read_csv to bring in data
#not using copy here because this is the data set we are normalizing our others around
#Convert price to numeric and remove commas which were causing issues
#Convert date to datetime and format it to YYYY-MM
#While there shouldn't be any NaN values drop any that may exist
#Only use dates that are greater than or equal to 1970-02
##############################################################################################################################################
dfGold = pd.read_csv(gold_file)
dfGold['Price'] = pd.to_numeric(dfGold['Price'].replace(',', '', regex=True), errors='coerce')
dfGold['Date'] = pd.to_datetime(dfGold['Date'], errors='coerce').dt.strftime('%Y-%m')
dfGold = dfGold.dropna().sort_values(by='Date').reset_index(drop=True)
dfGold = dfGold[dfGold['Date'] >= '1970-02']

#############################################################################################################################################
#Tidy our Inflation Data
#Use read_csv to bring in data
#not using copy here because we already cleaned this data prior to use here
#Convert date to datetime and format it to YYYY-MM
#While there shouldn't be any NaN values drop any that may exist
#Only use dates that are greater than or equal to 1970-02
##############################################################################################################################################
dfInflation = pd.read_csv(inflation_file)
dfInflation = dfInflation[['Date', 'Inflation']]
dfInflation['Date'] = pd.to_datetime(dfInflation['Date'], format='%Y-%m', errors='coerce')
dfInflation = dfInflation.dropna().sort_values(by='Date').reset_index(drop=True)
dfInflation = dfInflation[dfInflation['Date'] >= '1970-02']

#############################################################################################################################################
#Annualized Growth Rate Calculations
#Set Start Date value to first value for Date
#Set End Date value to last value for Date
#Set Years value to the number of years between dates divided my days in a year(accounting for leap years
#from this Stack Overflow post where as is standard they tear the question asker apart....
#https://stackoverflow.com/questions/68778379/does-pandas-account-for-leap-years-when-calculating-dates
#I chose to use 365.25 just to spite the jerk answering the question....
#Set Initial Stock Price value to first value for Price
#Set Final Stock Price value to last value for Price
#Set Annualized Stock Growth value to result of a calculation found here:
#https://towardsdatascience.com/python-vs-excel-compound-annual-growth-rate-cagr-c8dbad46d3e0
#Perform same calculations on Gold Price
##############################################################################################################################################
start_date = pd.to_datetime(dfStock['Date'].iloc[0])
end_date = pd.to_datetime(dfStock['Date'].iloc[-1])
years = (end_date - start_date).days / 365.25

#Stock annualized growth
initial_stock_price = dfStock['Price'].iloc[0]
final_stock_price = dfStock['Price'].iloc[-1]
annualized_stock_growth = ((final_stock_price / initial_stock_price) ** (1 / years) - 1) * 100

#Gold annualized growth
initial_gold_price = dfGold['Price'].iloc[0]
final_gold_price = dfGold['Price'].iloc[-1]
annualized_gold_growth = ((final_gold_price / initial_gold_price) ** (1 / years) - 1) * 100

#Visualization Functions
#This part was quite fun. I can see how building and refining dashboards can be addicting
#once you understand the basic layout and callbacks adding new visuals too way less time
##############################################################################################################################################
#Stock Chart
##############################################################################################################################################
def generate_stock_chart():
    stock_fig = go.Figure()
    stock_fig.add_trace(go.Scatter(
        x=dfStock['Date'], 
        y=dfStock['Price'], 
        mode='lines', 
        name='Stock Price',
        line=dict(color='green')
    ))
    stock_fig.update_layout(title='Stock Prices Over Time', xaxis_title='Date', yaxis_title='Price (USD)')
    return stock_fig

##############################################################################################################################################
#Gold Chart
##############################################################################################################################################
def generate_gold_chart():
    gold_fig = go.Figure()
    gold_fig.add_trace(go.Scatter(
        x=dfGold['Date'], 
        y=dfGold['Price'], 
        mode='lines', 
        name='Gold Price',
        line=dict(color='gold')
    ))
    gold_fig.update_layout(title='Gold Prices Over Time', xaxis_title='Date', yaxis_title='Price (USD)')
    return gold_fig

##############################################################################################################################################
#Inflation Chart
##############################################################################################################################################
def generate_inflation_chart():
    inflation_fig = go.Figure()
    inflation_fig.add_trace(go.Scatter(
        x=dfInflation['Date'], 
        y=dfInflation['Inflation'], 
        mode='lines', 
        name='Inflation Rate',
        line=dict(color='blue')
    ))
    inflation_fig.update_layout(title='Inflation Rate Over Time', xaxis_title='Date', yaxis_title='Inflation Rate (%)')
    return inflation_fig

##############################################################################################################################################
#Gold vs Stocks Chart
##############################################################################################################################################
def generate_comparison_chart():
    comparison_fig = go.Figure()
    comparison_fig.add_trace(go.Scatter(
        x=dfGold['Date'], 
        y=dfGold['Price'], 
        mode='lines', 
        name='Gold Price',
        line=dict(color='gold')
    ))
    comparison_fig.add_trace(go.Scatter(
        x=dfStock['Date'], 
        y=dfStock['Price'], 
        mode='lines', 
        name='Stock Price',
        line=dict(color='green')
    ))
    comparison_fig.update_layout(title='Gold vs Stocks Comparison', xaxis_title='Date', yaxis_title='Price (USD)')
    return comparison_fig

##############################################################################################################################################
#COMBINED ANIMATED GAUGE
##############################################################################################################################################

#I did use AI in part for this, trying to fully implement animations on such a short time frame was difficult. The idea and much of the code
#was written by me. Debugging and tweaking (and dealing with errors) would have taken much longer. In my opinion, this is where AI shines
# when it comes to a developer. Granted you have to understand what you are doing in order for it to understand. But as let's say a "pair 
#programmer that does the scut work on a time crunch is great. And in truth I wanted to create this to learn how animations work.

# determine gauge color to use in below gauges
def determine_color(value):
    if value < 3:  #Low grwoth
        return "red"
    elif 3 <= value < 6:  #  Medium growth
        return "yellow"
    else:  #High growth
        return "green"

def generate_combined_animated_gauge():
    # Maximum value for the axis range
    max_range = 10 #set to 10 for more meaningful visual

    # Create animation frames
    stock_frames = np.linspace(0, annualized_stock_growth, 50)
    gold_frames = np.linspace(0, annualized_gold_growth, 50)


    combined_animated_gauge = make_subplots(
        rows=1, cols=2, 
        specs=[[{'type': 'domain'}, {'type': 'domain'}]],
        
    )

    # first gauge for stock
    combined_animated_gauge.add_trace(go.Indicator(
        mode="gauge+number",
        value=0,  # Start at 0 for animation
        title={'text': "Stock Annualized Growth (%)"},
        gauge={
            'axis': {'range': [0, max_range]},
            'bar': {'color': "black"},  #blackvbar
            'steps': [
                {'range': [0, 3], 'color': "red"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, max_range], 'color': "green"}
            ]
        }
    ), row=1, col=1)

    # first gauge for gold
    combined_animated_gauge.add_trace(go.Indicator(
        mode="gauge+number",
        value=0,  # Start at 0 for animation
        title={'text': "Gold Annualized Growth (%)"},
        gauge={
            'axis': {'range': [0, max_range]},
            'bar': {'color': "black"},  #blackbar
            'steps': [
                {'range': [0, 3], 'color': "red"},
                {'range': [3, 6], 'color': "yellow"},
                {'range': [6, max_range], 'color': "green"}
            ]
        }
    ), row=1, col=2)

    # Add frames for animation
    frames = []
    for stock_value, gold_value in zip(stock_frames, gold_frames):
        frames.append(go.Frame(
            data=[
                go.Indicator(
                    value=stock_value,
                    mode="gauge+number",
                    gauge={
                        'axis': {'range': [0, max_range]},
                        #would be nice to maybe use my original color change idea but with black outline so it's obviouos
                        'bar': {'color': "black"},  #black bar because it stands out. Will experiment with outhers in future.
                        'steps': [
                            {'range': [0, 3], 'color': "red"},
                            {'range': [3, 6], 'color': "yellow"},
                            {'range': [6, max_range], 'color': "green"}
                        ]
                    }
                ),
                go.Indicator(
                    value=gold_value,
                    mode="gauge+number",
                    gauge={
                        'axis': {'range': [0, max_range]},
                        'bar': {'color': "black"},  #black bar
                        'steps': [
                            {'range': [0, 3], 'color': "red"},
                            {'range': [3, 6], 'color': "yellow"},
                            {'range': [6, max_range], 'color': "green"}
                        ]
                    }
                )
            ]
        ))

    #update layout to include play button and adjust margins
    combined_animated_gauge.update_layout(
    title={
        "text": "Annualized Growth %: Stock vs Gold 1970-2023",
        "x": 0.5,
        "y": .95, 
        "xanchor": "center",
        "yanchor": "top",
    },
    margin={
        "t": 100  # top margin up 100 "units" so that layout title does not interfere with subplot titles
    },
        template="plotly",
        updatemenus=[{
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }]
    )

    # adding frames to gauges
    combined_animated_gauge.frames = frames

    return combined_animated_gauge

#############################################################################################################################################
#Dash App
##############################################################################################################################################
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)



#############################################################################################################################################
#Dash App Layout using Bootstrap Rows, Columns, Cards, and Buttons
#I decided to use Bootstrap components because I am already SUPER familiar with them. I have built many websites using Bootstrap CSS and was
#so grateful someone had created this library. Granted, I did not have the time to polish this or in all reality build what I actually had in
# my mind (because of serious time limitations) but I believe it is a good starting point and a great lesson in how to use Dash from a 
# beginners perspective.
#
#for an example see helmegeauga.org and ignore the insecure hosting warning. I built that for a non-profit and of course they hosted it
#insecurely which I am guessing scares away many people who may have found it helpful....
##############################################################################################################################################
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Stock Prices Over Time", className="card-title"),
                dbc.Button("View Chart", id="stock-card-btn", color="primary", outline=True, className="mt-3")
            ])
        ]), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Gold Prices Over Time", className="card-title"),
                dbc.Button("View Chart", id="gold-card-btn", color="primary", outline=True, className="mt-3")
            ])
        ]), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Inflation Rate Over Time", className="card-title"),
                dbc.Button("View Chart", id="inflation-card-btn", color="primary", outline=True, className="mt-3")
            ])
        ]), width=4),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Gold vs Stocks Comparison", className="card-title"),
                dbc.Button("View Chart", id="comparison-card-btn", color="primary", outline=True, className="mt-3")
            ])
        ]), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Animated Gold Growth", className="card-title"),
                dbc.Button("View Chart", id="growth-card-btn", color="primary", outline=True, className="mt-3")
            ])
        ]), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Coming Soon! Yearly Performance: Gold vs Stock", className="card-title"),
                dbc.Button("View Chart", id="stacked-bar-card-btn", color="primary", outline=True, className="mt-3", disabled=True)
            ])
        ]), width=4),
    ], className="mb-4"),
    html.Div(id='visual-container', style={'marginTop': '20px'})  # Add the visual-container here
], fluid=True)

#############################################################################################################################################
#Callbacks for click events
#This section of code gave me the most errors. Trying to understand what is calling back what, empty callbacks, and other errors. Once I had
#one working however, the others were very easy to add. The n_clicks tracks the number of clicks of a certain button. This must be named n_clicks.
#see https://dash.plotly.com/dash-html-components/button
##############################################################################################################################################
@app.callback(
    Output('visual-container', 'children'),
    [Input('stock-card-btn', 'n_clicks'),
     Input('gold-card-btn', 'n_clicks'),
     Input('inflation-card-btn', 'n_clicks'),
     Input('comparison-card-btn', 'n_clicks'),
     Input('growth-card-btn', 'n_clicks'),
     Input('stacked-bar-card-btn', 'n_clicks')]
)

#############################################################################################################################################
#Dash App Update Visuals. 
#Here again is where I struggled to get things right, but once I did it was much easier adding new items
##############################################################################################################################################
def update_visual(stock_clicks, gold_clicks, inflation_clicks, comparison_clicks, growth_clicks, stacked_bar_clicks):
    ctx = dash.callback_context #what caused my callback to run?
    if not ctx.triggered: #if we don't have a callback trigger then display easter egg
        return html.P("Easter Egg")  # Just an easter egg that is barely visible because of the background

    card_id = ctx.triggered[0]['prop_id'].split('.')[0] #retrieve which btn(card) was clicked by using the prop_id (i.e.-stock-card-btn)

    # Match the button IDs to their respective visualizations
    #Basically just a giant if else statement that will call the graph function on a figure defined above using def.
    if card_id == 'stock-card-btn':
        return dcc.Graph(figure=generate_stock_chart())
    elif card_id == 'gold-card-btn':
        return dcc.Graph(figure=generate_gold_chart())
    elif card_id == 'inflation-card-btn':
        return dcc.Graph(figure=generate_inflation_chart())
    elif card_id == 'comparison-card-btn':
        return dcc.Graph(figure=generate_comparison_chart())
    elif card_id == 'growth-card-btn':
        return dcc.Graph(figure=generate_combined_animated_gauge())
    elif card_id == 'stacked-bar-card-btn':
        return dcc.Graph(figure=generate_stacked_bar_chart())

    return html.P("Invalid selection.")  # error here not sure if this is necessary but in my job we always account for this type of stuff

#############################################################################################################################################
#Start Server to Run App
##############################################################################################################################################

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


