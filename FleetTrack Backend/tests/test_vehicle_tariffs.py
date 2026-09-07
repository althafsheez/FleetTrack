"""API regression tests using an isolated SQLite database, never the configured MSSQL."""
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Numeric, DateTime, Boolean, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError
from app.main import app
from app.database.session import get_db
from app.generated_models.models import Base
from app.vehicles import repository as vehicles, service
from app.tariffs import repository as tariffs
from app.tariffs.schemas import TariffRatesUpdate


class VehicleTariffAPI(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False})
        metadata = MetaData()
        candidates = {t.name for t in Base.metadata.tables.values() for c in t.c
                      if c.name.lower() in {'vehicleid', 'vehicle', 'sid_vehicle_id', 'takingvehicleid', 'givingvehicleid', 'tariffgroupid'}}
        candidates |= {v[0] for v in service.REFERENCES.values()} | {'VT_Veh_FleetTypeMaster'}
        # Only disposable SQLite tables are created. No generated metadata or MSSQL schema is changed.
        for name in candidates:
            columns = []
            for c in Base.metadata.tables[name].c:
                if c.primary_key or isinstance(c.type, Integer): typ = Integer()
                elif isinstance(c.type, DateTime): typ = DateTime()
                elif isinstance(c.type, Boolean): typ = Boolean()
                elif isinstance(c.type, Numeric): typ = Numeric(18, 5)
                else: typ = String()
                columns.append(Column(c.name, typ, primary_key=c.primary_key, nullable=c.nullable))
            Table(name, metadata, *columns)
        metadata.create_all(self.engine)
        self.db = Session(self.engine)
        for table_name in {x[0] for x in service.REFERENCES.values()} | {'VT_Veh_FleetTypeMaster'}:
            table = metadata.tables[table_name]
            values = {}
            for c in table.c:
                if c.primary_key or not c.nullable:
                    values[c.name] = 1 if isinstance(c.type, Integer) else 'test'
            self.db.execute(table.insert().values(**values))
        self.db.commit()
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app)
        self.payload = dict(ModelId=1, EngineCapacityId=1, Year=2024, PlateCodeId=1, PlateNo='001TEST',
                            RegistrationStartDate='2024-01-01T00:00:00', RegistrationExpiryDate='2027-01-01T00:00:00',
                            InsurancePolicyId=1, InsurancePolicyRecNo=0, InsuranceCompanyId=1, InsuranceTypeId=1,
                            InsuranceExpDate='2027-01-01T00:00:00', TCNoId=1, TypeId=1, FuelCapacity=50,
                            FuelCapacityUnitId=1, ChasisNo='TEST-CHASSIS', EngineNo='TEST-ENGINE',
                            TransmissionId=1, FuelTypeId=1, ColourId=1, SalikTag='001', InitialKmRdg=20,
                            TariffGroupId=1, StatusId=1, CreatedBy=7, VHType='034', Remarks='keep me')

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.db.close()
        self.engine.dispose()

    def create_vehicle(self, **changes):
        r = self.client.post('/vehicles/', json=self.payload | changes)
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()['VehicleId']

    def test_vehicle_crud_search_audit_and_defaults(self):
        vid = self.create_vehicle()
        r = self.client.get(f'/vehicles/{vid}').json()
        self.assertEqual(r['LatestKmRdg'], 20)
        self.assertEqual(r['LastUpdatedBy'], 7)
        self.assertTrue(r['CreatedDate'])
        self.assertEqual(self.client.get('/vehicles/search', params={'fleet_no': '034'}).json()[0]['VehicleId'], vid)
        self.assertEqual(self.client.get('/vehicles/', params={'q': 'CHASSIS'}).json()[0]['VehicleId'], vid)
        self.assertEqual(self.client.get('/vehicles/', params={'plate_no': '%'}).json(), [])
        self.assertEqual(self.client.get('/vehicles/', params={'offset': 1}).json(), [])
        updated = self.client.put(f'/vehicles/{vid}', json={'PlateNo': 'NEW', 'LastUpdatedBy': 8})
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()['Remarks'], 'keep me')
        self.assertEqual(updated.json()['LastUpdatedBy'], 8)
        self.assertEqual(updated.json()['CreatedBy'], 7)
        self.assertEqual(self.client.delete(f'/vehicles/{vid}').status_code, 204)
        self.assertEqual(self.client.get(f'/vehicles/{vid}').status_code, 404)

    def test_preserves_legacy_insurance_type_three_even_when_resubmitted(self):
        vid = self.create_vehicle()
        self.db.execute(vehicles.TABLE.update().where(vehicles.TABLE.c.VehicleId == vid).values(InsuranceTypeId=3))
        self.db.commit()
        for patch_data in [{'Remarks': 'edit'}, {'InsuranceTypeId': 3}]:
            r = self.client.patch(f'/vehicles/{vid}', json=patch_data | {'LastUpdatedBy': 9})
            self.assertEqual(r.status_code, 200, r.text)
            self.assertEqual(r.json()['InsuranceTypeId'], 3)
        self.assertEqual(self.client.post('/vehicles/', json=self.payload | {'InsuranceTypeId': 3}).status_code, 422)

    def test_changed_lookup_and_model_capacity_mismatch_rejected(self):
        vid = self.create_vehicle()
        self.assertEqual(self.client.patch(f'/vehicles/{vid}', json={'InsuranceCompanyId': 999, 'LastUpdatedBy': 7}).status_code, 422)
        table = Base.metadata.tables['VT_Veh_EngineCapacityMaster']
        self.db.execute(table.update().values(ModelId=999))
        self.db.commit()
        self.assertEqual(self.client.post('/vehicles/', json=self.payload).status_code, 422)

    def test_patch_null_and_immutable_fields(self):
        vid = self.create_vehicle()
        for field in ['PlateNo', 'InsuranceTypeId', 'LatestKmRdg']:
            self.assertEqual(self.client.patch(f'/vehicles/{vid}', json={field: None, 'LastUpdatedBy': 7}).status_code, 422)
        self.assertEqual(self.client.patch(f'/vehicles/{vid}', json={'VehicleId': 99, 'LastUpdatedBy': 7}).status_code, 422)
        self.assertEqual(self.client.patch(f'/vehicles/{vid}', json={'Remarks': None, 'LastUpdatedBy': 7}).status_code, 200)
        self.assertIsNone(self.client.get(f'/vehicles/{vid}').json()['Remarks'])

    def test_delete_replacement_reference_is_blocked(self):
        vid = self.create_vehicle()
        table = Base.metadata.tables['VT_Veh_VehicleReplacement']
        self.db.execute(table.insert().values(TakingVehicleId=vid))
        self.db.commit()
        r = self.client.delete(f'/vehicles/{vid}')
        self.assertEqual(r.status_code, 409, r.text)
        self.assertEqual(self.client.get(f'/vehicles/{vid}').status_code, 200)

    def test_tariff_crud_rates_are_independent_and_nullable(self):
        r = self.client.post('/vehicle-tariff-groups/', json={'TariffGroupName': ' Group A '})
        self.assertEqual(r.status_code, 201, r.text)
        gid = r.json()['TariffGroupId']
        self.assertEqual(r.json()['TariffGroupName'], 'Group A')
        rates_url = f'/vehicle-tariff-groups/{gid}/rates'
        initial = self.client.get(rates_url).json()
        for name in TariffRatesUpdate.model_fields:
            self.assertEqual(Decimal(initial[name]), Decimal('0.00'))
        values = {name: '12.34' for name in TariffRatesUpdate.model_fields}
        r = self.client.patch(rates_url, json=values)
        self.assertEqual(r.status_code, 200, r.text)
        for name in values: self.assertEqual(Decimal(r.json()[name]), Decimal('12.34'))
        self.assertEqual(self.client.patch(f'/vehicle-tariff-groups/{gid}', json={'TariffGroupName': 'Renamed'}).status_code, 200)
        self.client.patch(rates_url, json={'DailyRate': None})
        r = self.client.get(rates_url).json()
        self.assertIsNone(r['DailyRate'])
        self.assertEqual(Decimal(r['WeeklyRate']), Decimal('12.34'))
        self.assertEqual(self.client.get('/vehicle-tariff-groups/search', params={'q': 'Renamed'}).json()[0]['TariffGroupId'], gid)
        self.assertEqual(self.client.delete(f'/vehicle-tariff-groups/{gid}').status_code, 204)
        self.assertEqual(self.client.get(rates_url).status_code, 404)

    def test_referenced_group_delete_blocked(self):
        self.create_vehicle()
        self.assertEqual(self.client.delete('/vehicle-tariff-groups/1').status_code, 409)
        self.assertEqual(self.client.get('/vehicle-tariff-groups/1').status_code, 200)

    def test_validation_and_missing_records(self):
        for body in [{'TariffGroupName': '  '}, {'TariffGroupName': 'A', 'DailyRate': 1}]:
            self.assertEqual(self.client.post('/vehicle-tariff-groups/', json=body).status_code, 422)
        for value in ['1.001', 'NaN', 'Infinity', '10000000000000000.00']:
            self.assertEqual(self.client.patch('/vehicle-tariff-groups/1/rates', json={'DailyRate': value}).status_code, 422)
        self.assertEqual(self.client.patch('/vehicle-tariff-groups/1/rates', json={'TariffGroupName': 'bad'}).status_code, 422)
        self.assertEqual(self.client.get('/vehicles/', params={'limit': 0}).status_code, 422)
        self.assertEqual(self.client.delete('/vehicles/999').status_code, 404)
        self.assertEqual(self.client.delete('/vehicle-tariff-groups/999').status_code, 404)
        self.assertEqual(self.client.patch('/vehicle-tariff-groups/999/rates', json={'DailyRate': 1}).status_code, 404)

    def test_group_list_is_complete_search_is_separate_and_put_removed(self):
        self.db.execute(tariffs.TABLE.insert(), [
            {'TariffGroupName': f'Group {i}'} for i in range(105)])
        self.db.commit()
        self.assertEqual(len(self.client.get('/vehicle-tariff-groups/').json()), 106)
        self.assertEqual(len(self.client.get('/vehicle-tariff-groups/search', params={'q': 'Group 104'}).json()), 1)
        self.assertEqual(self.client.get('/vehicle-tariff-groups/search', params={'q': '%'}).json(), [])
        self.assertEqual(self.client.get('/vehicle-tariff-groups/search').status_code, 422)
        self.assertEqual(self.client.put('/vehicle-tariff-groups/1', json={'TariffGroupName': 'A'}).status_code, 405)
        self.assertEqual(self.client.put('/vehicle-tariff-groups/1/rates', json={'DailyRate': '1'}).status_code, 405)

    def test_main_group_patch_and_get_include_every_field(self):
        gid = self.client.post('/vehicle-tariff-groups/', json={'TariffGroupName': 'Full'}).json()['TariffGroupId']
        url = f'/vehicle-tariff-groups/{gid}'
        values = {name: '23.45' for name in TariffRatesUpdate.model_fields}
        r = self.client.patch(url, json=values | {'TariffGroupName': 'Full edited'})
        self.assertEqual(r.status_code, 200, r.text)
        detail = self.client.get(url).json()
        self.assertEqual(set(detail), set(values) | {'TariffGroupId', 'TariffGroupName'})
        for name in values:
            self.assertEqual(Decimal(detail[name]), Decimal('23.45'))
        self.assertEqual(detail['TariffGroupName'], 'Full edited')
        r = self.client.patch(url, json={'DailyRate': '99.00'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['TariffGroupName'], 'Full edited')
        self.assertEqual(Decimal(r.json()['WeeklyRate']), Decimal('23.45'))
        for payload in [{'TariffGroupName': None}, {'TariffGroupName': '   '}, {'TariffGroupId': 999}, {'DailyRate': '1.001'}]:
            self.assertEqual(self.client.patch(url, json=payload).status_code, 422)

    def test_cors_preflight_and_get(self):
        headers = {'Origin': 'http://localhost:3000', 'Access-Control-Request-Method': 'PATCH',
                   'Access-Control-Request-Headers': 'content-type'}
        r = self.client.options('/vehicle-tariff-groups/1', headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['access-control-allow-origin'], 'http://localhost:3000')
        r = self.client.get('/vehicle-tariff-groups/1', headers={'Origin': 'http://localhost:3000'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers['access-control-allow-origin'], 'http://localhost:3000')
        r = self.client.options('/vehicle-tariff-groups/1', headers=headers | {'Origin': 'https://untrusted.example'})
        self.assertEqual(r.status_code, 400)
        self.assertNotIn('access-control-allow-origin', r.headers)

    def test_database_conflict_rolls_back(self):
        with patch.object(self.db, 'commit', side_effect=IntegrityError('insert', {}, Exception('private details'))):
            r = self.client.post('/vehicle-tariff-groups/', json={'TariffGroupName': 'Rollback'})
        self.assertEqual(r.status_code, 409)
        self.assertNotIn('private details', r.text)
        self.assertEqual(self.client.get('/vehicle-tariff-groups/search', params={'q': 'Rollback'}).json(), [])


if __name__ == '__main__':
    unittest.main()
