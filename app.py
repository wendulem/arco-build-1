from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jsonpify import jsonify
from flask_cors import CORS, cross_origin
import os

application = app = Flask(__name__)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://' + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] + '@' + os.environ['RDS_HOSTNAME'] + ':' + os.environ['RDS_PORT'] + '/' + os.environ['RDS_DB_NAME']
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.debug = True

db = SQLAlchemy(app)

ma = Marshmallow(app)

class PC(db.Model):
    __tablename__ = 'pc'
    project_id = db.Column(db.String(100), db.ForeignKey('project.id'), primary_key = True)
    contractor_id = db.Column(db.Integer(), db.ForeignKey('contractor.id'), primary_key = True)
    invoices = db.relationship('Invoice', backref = 'pc')

# Project Class / Model
class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    contractors = db.relationship('Contractor', secondary = 'pc', backref = db.backref('projects', lazy = 'dynamic'))
    def __init__(self, id, name, location):
        self.id = id
        self.name = name
        self.location = location

class Contractor(db.Model):
    __tablename__ = 'contractor'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Invoice(db.Model):
    __tablename__ = 'invoice'
    __table_args__ = (db.ForeignKeyConstraint(['project_id','contractor_id'],['pc.project_id', 'pc.contractor_id']),)
    id = db.Column(db.Float(), primary_key=True)
    name = db.Column(db.DateTime())
    amount =  db.Column(db.Integer())
    project_id = db.Column(db.String(100))
    contractor_id = db.Column(db.Integer())
    def __init__(self, id, date, amount, project_id, contractor_id):
        self.id = id
        self.date = date
        self.amount = amount
        self.project_id = project_id
        self.contractor_id = contractor_id

# Project Schema
class ProjectSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'location')

# Project Schema
class ContractorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

class InvoiceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'date', 'amount')

# Init Schema
project_schema = ProjectSchema() #no need for strict keyword, schemas always strict
projects_schema = ProjectSchema(many=True)
contractor_schema = ContractorSchema() #no need for strict keyword, schemas always strict
contractors_schema = ContractorSchema(many=True)
invoice_schema = InvoiceSchema() #no need for strict keyword, schemas always strict
invoices_schema = InvoiceSchema(many=True)
        
# Base
@app.route('/', endpoint='base', methods=['GET'])
@cross_origin()
def base():
    return jsonify('Endpoints: /project, /contractor, /invoice')

# Add a Project
@app.route('/project', endpoint='add_project', methods=['POST'])
@cross_origin()
def add_project():
    id = request.json['id']
    name = request.json['name']
    location = request.json['location']
    new_project = Project(id, name, location)
    db.session.add(new_project)
    db.session.commit()
    return project_schema.jsonify(new_project)

# Get Projects
@app.route('/project', endpoint='get_projects', methods=['GET'])
@cross_origin()
def get_projects():
    all_projects = Project.query.all()
    result = projects_schema.dump(all_projects)
    return jsonify(result)

# Add a Contractor
@app.route('/contractor', endpoint='add_contractor', methods=['POST'])
@cross_origin()
def add_contractor():
    id = request.json['id']
    name = request.json['name']
    project = Project.query.filter_by(id = request.json['project_id']).one()
    new_contractor = Contractor(id, name)
    project.contractors.append(new_contractor)
    db.session.add(project)
    db.session.add(new_contractor)
    db.session.commit()
    return contractor_schema.jsonify(new_contractor)

# Get Contractors
@app.route('/contractor', endpoint='get_contractors', methods=['GET'])
@cross_origin()
def get_contractors():
    project = request.args.get('project')
    if(project == None):
        all_contractors = Contractor.query.all()
    else:
        project = Project.query.filter_by(id = project).one()
        all_contractors = project.contractors
    result = contractors_schema.dump(all_contractors)
    return jsonify(result)

# Get Invoices
@app.route('/invoice', endpoint='get_invoices', methods=['GET'])
@cross_origin()
def get_invoices():
    project = request.args.get('project')
    contractor = request.args.get('contractor')
    all_invoices = Invoice.query.all()
    result = invoices_schema.dump(all_invoices)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
