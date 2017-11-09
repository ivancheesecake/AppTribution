import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import json
import xml.etree.ElementTree as ET


app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'apptribution.db'),
    # DEBUG=True,
    SECRET_KEY='auvyevyevebeeyvyeee',                           #auvyevyevebeeyvyeee
    USERNAME='ttobbA',
    PASSWORD='olletsoC'
))

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/add')
def add():
    db = get_db()
    db.execute('insert into project (riverbasin, proj_name) values (?, ?)',
                 ["Casiligan", "Proyekto"])
    db.commit()
    flash('New entry was successfully posted')
    return "Success!"

@app.route('/add_feature')
def add_feature():
    db = get_db()
    db.execute('insert into feature (bldg_name, feature_id, status, lat, long, proj_id) values (?, ?, ?, ? , ? ,?)',
                 ["LidarOffice", 1, 0, 123, 321, 1])
    db.commit()
    flash('New entry was successfully posted')
    return "Success!"

@app.route('/view')
def view():
    db = get_db()
    cur = db.execute('select * from project')
    entries = cur.fetchall()
    print entries
    print type(entries)
    return str(entries)

@app.route('/view_feature')
def view_feature():
    db = get_db()
    cur = db.execute('select * from feature')
    entries = cur.fetchall()
    print entries
    print type(entries)
    return str(entries)

@app.route("/")
def hello():
    return render_template("startup.html",)

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    # Fetch features based on project id
    project_id = request.args['project']

    db = get_db()
    cur = db.execute('select * from feature where proj_id = (?)',[project_id])
    entries = cur.fetchall()
    # data = map(list,entries)

    entries_dict_list =[]
    # entries_str = "["
    for entry in entries:
        entry_dict = {
        "id":str(entry[0]),
        "bldg_type":str(entry[1]),
        "bldg_name":str(entry[2].encode('utf-8')),
        "feature_id":str(entry[3]),
        "status":str(entry[4]),
        "lat":str(entry[5]),
        "long":str(entry[6]),
        "proj_id":str(entry[7]),
        }
    #     entries_str += '{"id":'+str(entry[0])+'}'

        entries_dict_list.append(entry_dict)
    # print entries_dict_list
    # print jsonify(dict(list(cur.fetchall())))
    # entries_str +="]"
    features_json = json.dumps(entries_dict_list)
    # print entries
    # print features_json
    # print entries_str
    # print data
    # return render_template("main.html",features=data)

    cur = db.execute('select * from project where id = ?',[project_id])
    entries = cur.fetchall()
    project_name = entries[0][2]

    # return entries[0]
    return render_template("main.html",features=features_json,project_name=project_name) 

@app.route("/fetch_projects", methods=['GET', 'POST'])
def fetch_projects():
    db = get_db()
    cur = db.execute('select * from project order by id desc')
    entries = cur.fetchall()
    entries_dict_list =[]
    for entry in entries:
        entry_dict = {"project_id":entry[0],"river_basin":entry[1],"project_name":entry[2],"in_charge":entry[3]}
        entries_dict_list.append(entry_dict)

    # print jsonify(dict(list(cur.fetchall())))
    return jsonify(entries_dict_list)
    # return "HEY"

@app.route("/create_project", methods=['GET', 'POST'])
def create_project():
    
    project_name = request.form['project_name']
    kml_data = request.form['kml_data']
    river_basin = request.form['river_basin']
    in_charge = request.form['in_charge']

    # Create Project

    db = get_db()
    db.execute('insert into project (riverbasin, proj_name,in_charge) values (?, ?, ?)',
                 [river_basin,project_name,in_charge])
    db.commit()

    # Get previous id, assume successful insert 

    cursor = db.execute('select * from project order by id desc limit 1')
    row = cursor.fetchall()
    
    project_id =  row[0][0]

    # Read KML data

    root = ET.fromstring(kml_data)
    elements= list(root.iter('{http://www.opengis.net/kml/2.2}Placemark'))

    features = []

    for element in elements:

        feature_id= element[0][0][0].text
        coordinates = element[1][0].text
        coords = coordinates.split(",")
        latitude = coords[1]
        longitude = coords[0]

        db.execute('insert into feature (bldg_type,bldg_name, feature_id, status, lat, long, proj_id) values (?, ?, ?, ? , ? ,?,?)',
                 ["RS","", feature_id, 0, latitude, longitude, project_id])
    db.commit()    

    cur = db.execute('select * from project order by id desc')
    entries = cur.fetchall()
    entries_dict_list =[]
    for entry in entries:
        entry_dict = {"project_id":entry[0],"river_basin":entry[1],"project_name":entry[2],"in_charge":entry[3]}
        entries_dict_list.append(entry_dict)

    return jsonify(entries_dict_list)
  
@app.route("/update_feature", methods=['GET', 'POST'])
def update_feature():

    id = request.form['id']
    bldg_type = request.form['bldg_type']
    bldg_name = request.form['bldg_name']
    status = request.form['status']

    db = get_db()
    db.execute('update feature set bldg_type = ?, bldg_name = ?, status = ? where id = ? ',
                 [bldg_type,bldg_name,status,id])
    db.commit()

    success = {"success":"true"}
    return jsonify(success)

@app.route("/export", methods=['GET', 'POST'])
def export():

    project_id = request.form['project_id']

    db = get_db()

    cur = db.execute('select proj_name from project where id = ?',[project_id])
    entries = cur.fetchall()

    project_name = entries[0][0]

    cur = db.execute('select * from feature where proj_id = ?',[project_id])
    entries = cur.fetchall()

    # print entries

    outStr = "id,bldg_type,bldg_name,feature_id,status,lat,lng,project_id\n"
    
    for entry in entries:
        outStr+= str(entry[0])+","+str(entry[1])+","+entry[2].encode('utf-8')+","+str(entry[3])+","+str(entry[4])+","+str(entry[5])+","+str(entry[6])+","+str(entry[7])+"\n"

    with open("E:/Attribution/AppTribution_CSV/"+project_name.replace("*","")+".csv","w") as f:
        f.write(outStr)


    success = {"success":"true"}
    return jsonify(success)

@app.route("/export_everything", methods=['GET', 'POST'])
def export_everything():

    rb = request.args.get("rb")
    print rb

    outStr = "id,bldg_type,bldg_name,feature_id,status,lat,lng,project_id\n"
   

    db = get_db()

    cur = db.execute('select id from project where riverbasin = ?',[rb])
    entries = cur.fetchall()

    for entry in entries:
        print entry[0]
        cur = db.execute('select * from feature where proj_id = ?',[entry[0]])
        entries_loob = cur.fetchall()

        for entry_loob in entries_loob:
            outStr+= str(entry_loob[0])+","+str(entry_loob[1])+","+entry_loob[2].encode('utf-8').replace(","," ")+","+str(entry_loob[3])+","+str(entry_loob[4])+","+str(entry_loob[5])+","+str(entry_loob[6])+","+str(entry_loob[7])+"\n"

    # # print entries
    with open("E:/Attribution/AppTribution_CSV/"+rb+".csv","w") as f:
        f.write(outStr)

    # success = {"success":"true"}
    # return jsonify(success)
    return "Successfully exported "+rb

@app.route("/delete", methods=['GET', 'POST'])
def delete():

    project_id = request.form['project_id']

    db = get_db()

    db.execute('delete from feature where proj_id= ?',[project_id])
    db.commit()   
    db.execute('delete from project where id = ?',[project_id])
    db.commit()   

    cur = db.execute('select * from project order by id desc')
    entries = cur.fetchall()
    entries_dict_list =[]
    for entry in entries:
        entry_dict = {"project_id":entry[0],"river_basin":entry[1],"project_name":entry[2],"in_charge":entry[3]}
        entries_dict_list.append(entry_dict)

    # print jsonify(dict(list(cur.fetchall())))
    return jsonify(entries_dict_list)

@app.route("/assign_project", methods=['GET', 'POST'])
def assign_project():

    project_id = request.form['project_id']
    in_charge = request.form['in_charge']
    # bldg_type = request.form['bldg_type']
    # bldg_name = request.form['bldg_name']
    # status = request.form['status']

    print project_id
    print in_charge
    db = get_db()
    # cur = db.execute('select in_charge from project')
    # entries = cur.fetchall()
    db.execute('update project set in_charge = ? where id = ? ',
                 [in_charge,project_id])
    db.commit()
    # print entries

    cur = db.execute('select * from project order by id desc')
    entries = cur.fetchall()
    entries_dict_list =[]
    for entry in entries:
        entry_dict = {"project_id":entry[0],"river_basin":entry[1],"project_name":entry[2],"in_charge":entry[3]}
        entries_dict_list.append(entry_dict)

    return jsonify(entries_dict_list)

@app.route("/mark_finished", methods=['GET', 'POST'])
def mark_finished():

    project_id = request.form['project_id']
    # in_charge = request.form['in_charge']
    # bldg_type = request.form['bldg_type']
    # bldg_name = request.form['bldg_name']
    # status = request.form['status']

    print project_id

    db = get_db()

    cur = db.execute('select proj_name from project where id = ?',[project_id])
    entries = cur.fetchall()
    new_name =  "*"+entries[0][0]

    db.execute('update project set proj_name = ? where id = ? ',
                 [new_name,project_id])
    db.commit()


    cur = db.execute('select * from project order by id desc')
    entries = cur.fetchall()
    entries_dict_list =[]
    for entry in entries:
        entry_dict = {"project_id":entry[0],"river_basin":entry[1],"project_name":entry[2],"in_charge":entry[3]}
        entries_dict_list.append(entry_dict)

    return jsonify(entries_dict_list)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',threaded=True)