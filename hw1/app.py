from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.errorhandler(404)
def error_occured(error):
    app.logger.error('Page not found!!!')
    return render_template('page_not_found.html'),404

@app.route('/', methods=['GET','POST'])
def show_table():
    if (request.method=='GET'):

        return render_template('show_table.html', article=None)
    
    elif (request.method=='POST'):

        page = request.form['pagenumber']
        items_per_page = request.form['pagesize']
        offset = (int(page) - 1) * int(items_per_page)
        
        start_date = request.form['startdate'] + " 00:00:00"
        end_date = request.form['enddate'] + " 23:59:59"
        press = request.form['press']

        with sqlite3.connect('maindb.db') as conn:
            cursor = conn.cursor()
            script = """
            SELECT * FROM article
            WHERE date BETWEEN ? and ? AND press = ? 
            ORDER BY date
            LIMIT ? OFFSET ?
            """
            cursor.execute(script, (start_date, end_date, press, items_per_page, offset))
            article = cursor.fetchall()

        return render_template('show_table.html', article=article)


if __name__ == '__main__':
    app.run(debug=True)