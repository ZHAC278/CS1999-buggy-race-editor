from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
app = Flask(__name__)

DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"

BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
   return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
  if request.method == 'GET':
    return render_template("buggy-form.html", buggy=None)
  elif request.method == 'POST':
    msg=""
    buggy_id = request.form['id']
    flag_color = request.form['flag_color']
    flag_color_secondary = request.form['flag_color_secondary']
    flag_pattern = request.form['flag_pattern']
    qty_wheels = request.form['qty_wheels']
    if not qty_wheels.isdigit():
        msg = f"This is not a number!:{qty_wheels}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    elif int(qty_wheels)%2 != 0:
        msg = f"Wheels need to be an even number!:{qty_wheels}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    qty_tyres = request.form['qty_tyres']
    if not qty_tyres.isdigit():
        msg = f"This is not a number!:{qty_tyres}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    if qty_wheels>qty_tyres:
        msg = f"Quantity of tyres must be equal to or greater than the number of wheels! : {qty_tyres}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    tyres = request.form['tyres']
    power_type = request.form['power_type']
    power_units = request.form['power_units']
    if not power_units.isdigit():
        msg = f"This is not a number!:{power_units}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    aux_power_type = request.form['aux_power_type']
    aux_power_units = request.form['aux_power_units']
    if not aux_power_units.isdigit():
        msg = f"This is not a number!:{aux_power_units}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    if (aux_power_type == "fusion" or \
        aux_power_type == "thermo" or \
        aux_power_type == "solar" or \
        aux_power_type == "wind" \
        and int(aux_power_units)>1) :
        msg = f"Only one unit of this power type is allowed:{aux_power_type}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    hamster_booster = request.form['hamster_booster']
    if (power_type != "hamster" and \
        aux_power_type != "hamster" \
        and int(hamster_booster)>0):
        msg = f"Hamster boosters only available with hamster power!"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    armour = request.form['armour']
    attack  = request.form['attack']
    qty_attacks = request.form['qty_attacks']
    if not qty_attacks.isdigit():
        msg = f"This is not a number!:{qty_attacks}"
        return render_template('buggy-form.html', buggy=request.form, msg = msg)
    if (attack == "none" \
        and int(qty_attacks)>0):
            msg = f"You have no offensive capability : Number of attacks in race"
            return render_template('buggy-form.html', buggy=request.form, msg = msg)
    fireproof = request.form['fireproof']
    insulated = request.form['insulated']
    antibiotic = request.form['antibiotic']
    banging = request.form['banging']
    algo = request.form['algo']
    #msg = f"flag-color={flag_color}", #"flag_color_secondary={flag_color_secondary}", "flag_pattern={flag_pattern}", "qty_wheels={qty_wheels}", "qty_tyres={qty_tyres}", "tyres={tyres}", "power_type={power_type}", "power_units={power_units}", "aux_power_type={aux_power_type}", "aux_power_units={aux_power_units}"
    try:
      with sql.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        if buggy_id.isdigit(): 
            cur.execute("UPDATE buggies set flag_color=?, flag_color_secondary=?, flag_pattern=?, qty_wheels=?, qty_tyres=?, tyres=?, power_type=?, power_units=?, aux_power_type=?, aux_power_units=?, hamster_booster=?, armour=?, attack=?, qty_attacks=?, fireproof=?, insulated=?, antibiotic=?, banging=?, algo=? WHERE id=?", (flag_color, flag_color_secondary, flag_pattern, qty_wheels, qty_tyres, tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo, buggy_id))
        else:
            cur.execute("INSERT INTO buggies (flag_color, flag_color_secondary, flag_pattern, qty_wheels, qty_tyres, tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(flag_color, flag_color_secondary, flag_pattern, qty_wheels, qty_tyres, tyres, power_type, power_units, aux_power_type, aux_power_units, hamster_booster, armour, attack, qty_attacks, fireproof, insulated, antibiotic, banging, algo))
        con.commit()
        msg = "Record successfully saved"
    except Exception as e:
      con.rollback()
      msg = "error in update operation" + str(e)
    finally:
      con.close()
      return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies")
  records = cur.fetchall(); 
  buggies=[]
  for record in records:
      buggy={}
      for k in record.keys():
          buggy[k]=record[k]
      price_tyres = {"knobbly":15, "slick":10, "steelband":20, "reactive":40, "maglev":50}
      buggy['cost_tyres'] = price_tyres[record["tyres"]]*int(record["qty_tyres"])
      price_power = {"petrol":4, "fusion":400, "steam":3, "bio":5, "electric":20, "rocket":16, "hamster":3, "thermo":300, "solar":40, "wind":20}
      buggy['cost_primary_power'] = price_power[record["power_type"]]*int(record["power_units"])
      buggy['cost_backup_power'] = price_power[record["aux_power_type"]]*int(record["aux_power_units"])
      price_hamster_booster = 5
      buggy['cost_hamster_booster'] = price_hamster_booster*int(record["hamster_booster"])
      price_armour = {"none":0, "wood":40, "aluminium":200, "thinsteel":100, "thicksteel":200, "titanium":290}
      wheel_value = int(record["qty_wheels"])-4
      if wheel_value>0:
          buggy['cost_armour'] = price_armour[record["armour"]]+(price_armour[record["armour"]]*(wheel_value*0.1))
      else:
          buggy['cost_armour'] = price_armour[record["armour"]]
      price_offence = {"none":0, "spike":5, "flame":20, "charge":28, "biohazard":30}
      buggy['cost_offence'] = price_offence[record["attack"]]*int(record["qty_attacks"])
      price_fireproof = {"yes":70, "no":0}
      buggy['cost_fireproof'] = price_fireproof[record["fireproof"]]
      price_insulated = {"yes":100, "no":0}
      buggy['cost_insulated'] = price_insulated[record["insulated"]]
      price_antibiotic = {"yes":90, "no":0}
      buggy['cost_antibiotic'] = price_antibiotic[record["antibiotic"]]
      price_banging = {"yes":42, "no":0}
      buggy['cost_banging'] = price_banging[record["banging"]]
      buggy['total_cost'] = buggy['cost_tyres']+buggy['cost_primary_power']+buggy['cost_backup_power']+buggy['cost_hamster_booster']+buggy['cost_armour']+buggy['cost_offence']+buggy['cost_fireproof']+buggy['cost_insulated']+buggy['cost_antibiotic']+buggy['cost_banging']
      buggies.append(buggy)
  return render_template("buggy.html", buggies = buggies)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------


@app.route('/edit/<buggy_id>')
def edit_buggy(buggy_id):
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
    record = cur.fetchone(); 
    return render_template("buggy-form.html", buggy=record)
#------------------------------------------------------------
# get JSON from current record
#   this is still probably right, but we won't be
#   using it because we'll be dipping diectly into the
#   database
#------------------------------------------------------------
@app.route('/json')
def summary():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
  return jsonify(
      {k: v for k, v in dict(zip(
        [column[0] for column in cur.description], cur.fetchone())).items()
        if (v != "" and v is not None)
      }
    )

#------------------------------------------------------------
# delete the buggy
#   don't want DELETE here, because we're anticipating
#   there always being a record to update (because the
#   student needs to change that!)
#------------------------------------------------------------
@app.route('/delete/<buggy_id>', methods = ['POST'])
def delete_buggy(buggy_id):
  try:
    msg = "deleting buggy"
    with sql.connect(DATABASE_FILE) as con:
      cur = con.cursor()
      cur.execute("DELETE FROM buggies WHERE id=?", (buggy_id))
      con.commit()
      msg = "Buggy deleted"
  except:
    con.rollback()
    msg = "error in delete operation"
  finally:
    con.close()
    return render_template("updated.html", msg = msg)

@app.route('/poster')
def poster():
    return render_template("poster.html")

if __name__ == '__main__':
   print("start")
   app.run(debug = True, host="0.0.0.0")
   print("finish")
