
# Import packages from pyshiny express and the python standard library
from shiny import reactive, render
from shiny.express import ui
import random
import pandas as pd
import plotly.express as px
from datetime import datetime
from collections import deque
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

# If working locally, add the following to requirements.txt
# faicons
# shiny
# shinylive

# --------------------------------------------
# SET UP THE REACTIVE CONTENT
# --------------------------------------------

# --------------------------------------------
# PLANNING: We want to get a fake temperature and 
# Time stamp every N seconds. 
# For now, we'll avoid storage and just 
# Try to get the fake live data working and sketch our app. 
# We can do all that with one reactive calc.
# Use constants for update interval so it's easy to modify.
# ---------------------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------
UPDATE_INTERVAL_SECS: int = 5
# --------------------------------------------

# Initialize a REACTIVE VALUE with a common data structure
# The reactive value is used to store state (information)
# Used by all the display components that show this live data.
# This reactive value is a wrapper around a DEQUE of readings

# --------------------------------------------
DEQUE_SIZE: int = 30
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))
#---------------------------------------------

# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.

# It returns everything needed to display the data.
# Very easy to expand or modify.
# (I originally looked at REACTIVE POLL, but this seems to work better.)
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():

    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Data generation logic. Get random between -18 and -16 C, rounded to 1 decimal place
    temp = round(random.uniform(-18, -16), 1)

    # Get a timestamp for "now" and use string format strftime() method to format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # get the deque and append the new entry
    reactive_value_wrapper.get().append(new_dictionary_entry)

    # Get a snapshot of the current deque for any further processing
    deque_snapshot = reactive_value_wrapper.get()

    # For Display: Convert deque to DataFrame for display
    df = pd.DataFrame(deque_snapshot)

    # For Display: Get the latest dictionary entry
    latest_dictionary_entry = new_dictionary_entry

    # Return a tuple with everything we need
    # Every time we call this function, we'll get all these values
    return deque_snapshot, df, latest_dictionary_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI

ui.page_opts(title="Pinkston's PyShiny Project with Live Data", fillable=True, style="background-color: silver")

# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open", bg="silver"):
    ui.h2("Antarctic Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings in Antarctica.",
        class_="text-center",
    )

    ui.hr()
    ui.h6("Links")
    ui.a(
        "GitHub Source",
        href="https://github.com/james-0177/cintel-05-cintel/",
        target="_blank",
    )
    ui.a(
        "GitHub App",
        href="https://github.com/james-0177/cintel-05-cintel/blob/main/dashboard/app.py",
        target="_blank",
    )
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank",)
    

#---------------------------------------------------------------------
# In Shiny Express, everything not in the sidebar is in the main panel
#---------------------------------------------------------------------

with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("snowflake"),
        theme="bg-gradient-blue-purple",
    ):

        "Current Temperature"

        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"

        "warmer than usual"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

with ui.layout_columns():
    with ui.card():
        ui.card_header("Temperature Readings")
        @render.data_frame
        def display_df():
            """Get the latest data and return a dataframe with current data"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)
            return render.DataGrid(df, width="100%")

with ui.layout_columns():
    with ui.card():
        ui.card_header("Temperature Distribution")
        @render_plotly
        def display_plot():
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            if not df.empty:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                fig = px.scatter(df,
                                 x="timestamp",
                                 y="temp",
                                 title="Temperature Readings with Regression Line",
                                 labels={"temp": "Temperature (C)", "timestamp": "Time"},
                                 color_discrete_sequence=["dimgrey"])
                x_vals = range(len(df))
                y_vals = df["temp"]
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')
                fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (C)")
            return fig
