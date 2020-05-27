from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jsonpify import jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+pg8000://postgres:J4sB%P8bwA@34.86.211.235'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.debug = True

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Invoices Class / Model
class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    contractor = db.Column(db.String(200))
    invoice_amount = db.Column(db.Float)

    def __init__(self, contractor, invoice_amount):
        self.contractor = contractor
        self.invoice_amount = invoice_amount

# Invoices Schema
class InvoiceSchema(ma.Schema):
    class Meta:
        fields = ('id', 'contractor', 'invoice_amount')


# Init Schema
invoice_schema = InvoiceSchema() #no need for strict keyword, schemas always strict
invoices_schema = InvoiceSchema(many=True)

# Create an Invoice
@app.route('/invoice', methods=['POST'])
@cross_origin()
def add_invoice():
    contractor = request.json['contractor']
    invoice_amount = request.json['invoice_amount']

    new_invoice = Invoice(contractor, invoice_amount)

    db.session.add(new_invoice)
    db.session.commit()

    return invoice_schema.jsonify(new_invoice)

# Delete an Invoice
@app.route('/invoice', methods=['DELETE'])
@cross_origin()
def delete_invoice():
    id = request.json['id']

    del_invoice = Invoice.query.filter_by(id=id).one()

    db.session.delete(del_invoice)
    db.session.commit()

    return invoice_schema.jsonify(del_invoice)

# Get all Invoices
@app.route('/invoice', methods=['GET'])
@cross_origin()
def get_invoices():
    all_invoices = Invoice.query.all()
    result = invoices_schema.dump(all_invoices)
    return jsonify(result)

@app.route('/', methods=['GET'])
def hello():
    return jsonify('Hello')

if __name__ == '__main__':
    app.run()
