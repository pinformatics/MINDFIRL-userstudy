from flask import Flask, render_template, redirect, url_for
app = Flask(__name__)

@app.route('/')
def show_record_linkages():
    return render_template('record_linkage.html')

@app.route('/record_linkage')
def show_record_linkage_task():
    pairs = list()
    pairs.append(['1','','206','NELSON','MITCHELL','1459','03/13/1975','M','B','','******','********___','03/13/1975','*','*','34','6','0'])
    pairs.append(['1','1000142704','174','NELSON','MITCHELL SR','1314','07/03/1949','M','B','1000142704','******','******** SR','07/03/1949','*','*','34','6','0'])
    return render_template('record_linkage_d.html', pairs=pairs)

@app.route('/select')
def select_panel():
    return render_template('select_panel2.html')

@app.route('/instructions')
def show_instructions():
    return render_template('instructions.html')

@app.route('/introduction')
def show_introduction():
    return render_template('introduction.html')

@app.route('/instructions2')
def show_instructions2():
    return render_template('instructions2.html')

@app.route('/test')
def test():
    return render_template('bootstrap_test.html')

@app.route('/next')
def next():
    return redirect(url_for('show_instructions'))

@app.route('/instructions/base_mode')
def show_instruction_base_mode():
    return render_template('instruction_base_mode.html')

@app.route('/practice/base_mode')
def show_pratice_base_mode():
    return render_template('practice_base_mode.html')

@app.route('/display_modes')
def show_display_modes():
    pairs = list()
    pairs.append(['1','','206','NELSON','MITCHELL','1459','03/13/1975','M','B','','******','********___','03/13/1975','*','*','34','6','0'])
    pairs.append(['1','1000142704','174','NELSON','MITCHELL SR','1314','07/03/1949','M','B','1000142704','******','******** SR','07/03/1949','*','*','34','6','0'])
    return render_template('display_mode.html', pairs=pairs)

@app.route('/regex_showcase')
def regex_showcase():
    pairs = list()
    pairs.append(['1','','206','NELSON','MITCHELL','1459','03/13/1975','M','B','','******','********___','03/13/1975','*','*','34','6','0'])
    pairs.append(['1','1000142704','174','NELSON','MITCHELL SR','1314','07/03/1949','M','B','1000142704','******','******** SR','07/03/1949','*','*','34','6','0'])
    return render_template('regex_showcase.html', pairs=pairs)

