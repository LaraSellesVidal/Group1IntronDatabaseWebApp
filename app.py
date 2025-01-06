from flask import Flask, request, render_template, url_for, make_response
import pandas as pd
from flaskwebgui import FlaskUI
import sys, os

try:
   os.chdir(sys._MEIPASS)
except AttributeError:
   os.chdir(os.getcwd())

app = Flask(__name__)
df = pd.read_csv('./static/intronDatabaseDF.tsv.xz', sep='\t', compression='xz')

@app.template_filter('max')
def max_filter(value, arg):
    return max(value, arg)

@app.template_filter('min')
def min_filter(value, arg):
    return min(value, arg)

@app.template_filter('range')
def range_filter(start, end):
    return range(start, end)

@app.route('/', methods=['GET', 'POST'])
def search():

    results = df.copy()  # start with the entire dataframe
    organism = request.args.get('organism')
    subtypes = request.args.getlist('subtype')
    organismTypes = request.args.getlist('organismType')
    if subtypes:
        results = results[results['intronSubtype'].isin(subtypes)]
    if organism:
        organism = organism.strip()
        results = results[results['organism'].str.contains(organism, case=False)]
    if organismTypes:
        results = results[results['organismType'].isin(organismTypes)]

    page = request.args.get('page', 1, type=int)
    per_page = 100  
    total_pages = len(results) // per_page + (1 if len(results) % per_page > 0 else 0)

    if 'download' in request.form:
        # Convert the filtered results to CSV
        csv = results.to_csv(index=False, sep='\t')
        # Create a response
        response = make_response(csv)
        # Set the TSV mime type
        #response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Type'] = 'tab-separated-values'
        # Set the download header
        response.headers['Content-Disposition'] = 'attachment; filename=filtered_introns.tsv'
        return response

    start = (page - 1) * per_page
    end = start + per_page

    results = results.iloc[start:end]

    num_pages_before = 2
    num_pages_after = 2
    range_start = max(1, page - num_pages_before)
    range_end = min(total_pages, page + num_pages_after)

    intron_subtypes = df['intronSubtype'].unique().tolist()
    intron_organismTypes = df['organismType'].unique().tolist()

    return render_template('search.html', results=results.to_dict('records'), df=df, total_pages=total_pages, current_page=page,
                           range_start=range_start, range_end=range_end, intron_subtypes=intron_subtypes, intron_organismTypes=intron_organismTypes)
