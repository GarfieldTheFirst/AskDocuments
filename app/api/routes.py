import requests
from flask_restx import Resource, fields
from app.api import api
from app import db
from app.models.file_data import \
    ServiceOrder, Scanner, Location, order_types, order_stati
from app.utilities.getip import get_local_ip, get_public_ip
from flask import jsonify


service_order_model = api.model('ServiceOrder', {
        'item_to_be_serviced': fields.String(
            required=True, description='Item to be serviced'),
        'service_to_be_provided': fields.String(
            required=True, description='Service to be provided')
})

move_service_order_model = api.model('Move', {
    'order_number': fields.String(required=True,
                                  description='Order number identifier'),
    'location_name': fields.String(required=True,
                                   description='Name of location to move to')
})

scan_model = api.model('Scan', {
    'mac_address': fields.String(required=True,
                                 description='Mac address of scanner'),
    'order_number': fields.String(required=True,
                                  description='Order number identifier')
})

scanner_model = api.model('Scanner', {
    'scanner_name': fields.String(required=True,
                                  description='Name of scanner'),
    'mac_address': fields.String(required=True,
                                 description='Mac address of scanner'),
    'location_name': fields.String(required=True,
                                   description='Location of scanner')
})

location_model = api.model('Scanner location', {
    'location_name': fields.String(required=True,
                                   description='Name of scanner')
})


@api.route('/service_orders')
class ServiceOrderList(Resource):
    @api.doc('list_service_orders')
    def get(self):
        service_orders = db.session.query(ServiceOrder).all()
        service_order_list = []
        for service_order in service_orders:
            service_order_dict = {
                'id': service_order.id,
                'customer_name': service_order.customer_name,
                'customer_address': service_order.customer_address,
                'location_id': service_order.location_id,
                'last_seen': service_order.last_seen,
                'status': service_order.status,
                'locations':
                    [(item.location_id, item.time_changed)
                     for item in service_order.locations]
            }
            service_order_list.append(service_order_dict)
        return jsonify(service_order_list)

    @api.doc('create_service_order')
    @api.expect(service_order_model)
    def post(self):
        service_order = ServiceOrder(
            order_number=api.payload['order_number'],
            order_type=api.payload['order_type']
            if api.payload['order_type'] in order_types.enums
            else None,
            order_status='received')
        db.session.add(service_order)
        db.session.commit()
        return {'message': 'Service order created successfully'}, 201

    @api.doc('update_service_order')
    @api.expect(service_order_model)
    def patch(self):
        order = db.session.query(ServiceOrder).filter_by(
            order_number=api.payload['order_number']).first()
        order.order_type = api.payload['order_type'] \
            if api.payload['order_type'] in order_types.enums \
            else None
        order.order_status = api.payload['order_status'] \
            if api.payload['order_status'] in order_stati.enums \
            else None
        db.session.commit()
        return {'message': 'Order updated successfully'}, 201


@api.route('/move_service_order')
class MoveServiceOrder(Resource):
    @api.doc('update_service_order_location')
    @api.expect(move_service_order_model)
    def patch(self):
        order = db.session.query(ServiceOrder).filter_by(
            order_number=api.payload['order_number']).first()
        location = db.session.query(Location).filter_by(
            location_name=api.payload['location_name']).first()
        order.move_to_location(location=location)
        db.session.commit()
        return {'message': 'Order updated successfully'}, 201


@api.route('/scanners')
class ScannerList(Resource):
    @api.doc('get_registered_scanners')
    def get(self):
        scanners = db.session.query(Scanner).all()
        scanner_list = []
        for scanner in scanners:
            scanner_dict = {
                'id': scanner.id,
                'scanner_name': scanner.scanner_name,
                'mac_address': scanner.mac_address,
                'location_id': scanner.location_id
            }
            scanner_list.append(scanner_dict)
        return jsonify(scanner_list)

    @api.doc('register_scanner')
    @api.expect(scanner_model)
    def post(self):
        location = db.session.query(
                Location).filter_by(
                    location_name=api.payload['location_name']).first()
        if location is None:
            location_response = None
            try:
                location = Location(location_name=api.payload['location_name'])
                db.session.add(location)
                db.session.commit()
            except Exception as e:
                e.with_traceback(location_response)
        location_id = db.session.query(
                Location).filter_by(
                    location_name=api.payload['location_name']).first().id
        scanner = Scanner(
            scanner_name=api.payload['scanner_name'],
            mac_address=api.payload['mac_address'],
            location_id=location_id)
        db.session.add(scanner)
        db.session.commit()
        return {'message': 'Scanner created successfully'}, 201

    @api.doc('update_scanner')
    @api.expect(scanner_model)
    def patch(self):
        location = db.session.query(
                Location).filter_by(
                    location_name=api.payload['location_name']).first()
        if location is None:
            requests.post(
                url=api.base_url + 'locations',
                json={'location_name': api.payload['location_name']})
        scanner = db.session.query(Scanner).filter_by(
            mac_address=api.payload['mac_address']).first()
        scanner.scanner_name = api.payload['scanner_name']
        scanner.location_id = db.session.query(Location).filter_by(
            location_name=api.payload['location_name']).first().id
        db.session.commit()
        return {'message': 'Scanner updated successfully'}, 200


@api.route('/locations')
class LocationList(Resource):
    @api.doc('get_registered_locations')
    def get(self):
        locations = db.session.query(Location).all()
        locations_list = []
        for location in locations:
            location_dict = {
                'id': location.id,
                'location_name': location.location_name,
                'location_scanners':
                    [scanner.id for scanner in location.scanners],
                'service_orders':
                    [service_order.id for service_order
                     in location.service_orders],
            }
            locations_list.append(location_dict)
        return jsonify(locations_list)

    @api.doc('register_location')
    @api.expect(location_model)
    def post(self):
        location = Location(location_name=api.payload['location_name'])
        db.session.add(location)
        db.session.commit()
        return {'message': 'Location created successfully'}, 201


@api.route('/scan')
class Scans(Resource):
    @api.doc('scan_order_number')
    @api.expect(scan_model)
    def post(self):
        scanner_mac = api.payload['mac_address']
        scanned_order_number = api.payload['order_number']
        scanner = db.session.query(
            Scanner).filter_by(mac_address=scanner_mac).first()
        scanner.scan_service_order(service_order_id=scanned_order_number)
        db.session.commit()
        return {'message': 'Scanned service order successfully'}, 200


@api.route('/ip')
class IpList(Resource):
    @api.doc('get_ips')
    def get(self):
        ip_list = [
            {"local ip": get_local_ip()},
            {"public ip": get_public_ip()}]
        return jsonify(ip_list)
