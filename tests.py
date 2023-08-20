import unittest
from app.api import api
from app import create_app, db
from app.models.file_data import Scanner, ServiceOrder, Location, \
    ServiceOrderLocation
from config import TestConfig


class DatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_class=TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        with self.app_context:
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_enterling_locations_into_database(self):
        self.test_registration_location_name = "registration office"
        self.test_processing_location_name = "processing office"
        self.test_outgoing_location_name = "outgoing office"
        locations = [
            Location(location_name=self.test_registration_location_name),
            Location(location_name=self.test_processing_location_name),
            Location(location_name=self.test_outgoing_location_name)]
        for location in locations:
            db.session.add(location)
        db.session.commit()
        test_locations = db.session.query(Location).all()
        test_location_names = list(map(lambda x: x.location_name,
                                       test_locations))
        self.assertIn(self.test_registration_location_name,
                      test_location_names)
        self.assertEqual(len(locations), len(test_location_names))

    def test_entering_scanners_into_database(self):
        self.test_enterling_locations_into_database()
        self.test_registration_scanner_name = "registration scanner"
        self.test_processing_scanner_name = "processing scanner"
        self.test_outgoing_scanner_name = "outgoing scanner"
        test_scanner_registration_location = db.session.query(
            Location).filter_by(
            location_name=self.test_registration_location_name).first()
        test_scanner_processing_location = db.session.query(
            Location).filter_by(
            location_name=self.test_processing_location_name).first()
        test_scanner_outgoing_location = db.session.query(
            Location).filter_by(
            location_name=self.test_outgoing_location_name).first()
        scanners = [Scanner(scanner_name=self.test_registration_scanner_name,
                            mac_address="FFFFFFFFFFFF",
                            location_id=test_scanner_registration_location.id),
                    Scanner(scanner_name=self.test_processing_scanner_name,
                            mac_address="FFFFFFFFFFFE",
                            location_id=test_scanner_processing_location.id),
                    Scanner(scanner_name=self.test_outgoing_scanner_name,
                            mac_address="FFFFFFFFFFFD",
                            location_id=test_scanner_outgoing_location.id)]
        for scanner in scanners:
            db.session.add(scanner)
        db.session.commit()
        test_scanners = db.session.query(Scanner).all()
        test_scanner_names = list(map(lambda x: x.scanner_name,
                                      test_scanners))
        self.assertIn(self.test_registration_scanner_name, test_scanner_names)

    def test_order_registration(self):
        self.test_entering_scanners_into_database()
        self.test_customer_name = "test customer"
        self.test_customer_address = "test address"
        test_registration_scanner = db.session.query(Scanner).filter_by(
            scanner_name=self.test_registration_scanner_name).first()
        test_scanner_registration_location = db.session.query(
            Location).filter_by(
            location_name=self.test_registration_location_name).first()
        self.test_service_order = ServiceOrder(
            customer_name=self.test_customer_name,
            customer_address=self.test_customer_address,
        )
        db.session.add(self.test_service_order)
        db.session.commit()
        self.test_service_order.move_to_location(
            scanner=test_registration_scanner)
        self.assertEqual(self.test_service_order.customer_address,
                         self.test_customer_address)
        self.assertEqual(self.test_service_order.location_id,
                         test_scanner_registration_location.id)

    def test_order_moving_through_stations(self):
        self.test_order_registration()
        scanners = db.session.query(Scanner).all()
        for scanner in scanners:
            scanner.scan_service_order(
                service_order_id=self.test_service_order.id)
            self.assertEqual(
                scanner.location_id,
                self.test_service_order.location_id)
        service_order = db.session.query(ServiceOrder).filter_by(
            id=self.test_service_order.id).first()
        history = db.session.query(ServiceOrderLocation).filter_by(
            service_order_id=service_order.id).all()
        self.assertEqual(len(service_order.locations), len(history))


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class=TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        with self.app_context:
            db.create_all()
        self.client = self.app.test_client()
        self.api = api

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_location_create(self):
        payload = {
            'location_name': 'Location 1'
        }
        response = self.client.post('/api/locations', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'],
                         'Location created successfully')
        location = Location.query.first()
        self.assertIsNotNone(location)
        self.assertEqual(location.location_name, 'Location 1')

    def test_location_list(self):
        self.test_location_create()
        response = self.client.get('/api/locations')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)

    def test_service_order_list(self):
        response = self.client.get('/api/service_orders')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_scanner_list(self):
        response = self.client.get('/api/scanners')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_service_order_create(self):
        payload = {
            'customer_name': 'John Doe',
            'customer_address': '123 Main St',
            # 'item_to_be_serviced': 'Laptop',
            # 'service_to_be_provided': 'Repair'
        }
        response = self.client.post('/api/service_orders', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'],
                         'Service order created successfully')
        service_order = ServiceOrder.query.first()
        self.assertIsNotNone(service_order)
        self.assertEqual(service_order.customer_name, 'John Doe')
        self.assertEqual(service_order.customer_address, '123 Main St')
        # self.assertEqual(service_order.item_to_be_serviced, 'Laptop')
        # self.assertEqual(service_order.service_to_be_provided, 'Repair')

    def test_scanner_create(self):
        payload = {
            'scanner_name': 'Scanner 1',
            'mac_address': '00:11:22:33:44:55',
            'location_name': 'Location 1'
        }
        response = self.client.post('/api/scanners', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'],
                         'Scanner created successfully')
        scanner = Scanner.query.first()
        self.assertIsNotNone(scanner)
        self.assertEqual(scanner.scanner_name, 'Scanner 1')
        self.assertEqual(scanner.mac_address, '00:11:22:33:44:55')
        self.assertEqual(scanner.location_id, Location.query.filter_by(
            location_name='Location 1').first().id)

    def test_scan(self):
        # Create a service order
        payload = {
            'customer_name': 'John Doe',
            'customer_address': '123 Main St',
            'item_to_be_serviced': 'Laptop',
            'service_to_be_provided': 'Repair'
        }
        response = self.client.post('/api/service_orders', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'],
                         'Service order created successfully')
        service_order = ServiceOrder.query.first()
        self.assertIsNotNone(service_order)

        # Create a scanner
        payload = {
            'scanner_name': 'Scanner 1',
            'mac_address': '00:11:22:33:44:55',
            'location_name': 'Location 1'
        }
        response = self.client.post('/api/scanners', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'],
                         'Scanner created successfully')
        scanner = Scanner.query.first()
        self.assertIsNotNone(scanner)

        # Scan the service order with the scanner
        payload = {
            'mac_address': '00:11:22:33:44:55',
            'order_number': str(service_order.id)
        }
        response = self.client.post('/api/scan', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'],
                         'Scanned service order successfully')

        # Check that the service order has been updated
        service_order = ServiceOrder.query.first()
        self.assertIsNotNone(service_order)
        # self.assertEqual(service_order.status, 'In Progress')
        self.assertEqual(service_order.location_id, scanner.location_id)
