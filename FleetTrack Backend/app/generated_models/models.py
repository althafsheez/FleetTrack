from typing import Any, Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, Column, DECIMAL, DateTime, ForeignKeyConstraint, Identity, Index, Integer, LargeBinary, NCHAR, Numeric, PrimaryKeyConstraint, String, Table, Unicode, text
from sqlalchemy.dialects.mssql import IMAGE, MONEY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


t_CashInOutFlow1 = Table(
    'CashInOutFlow1', Base.metadata,
    Column('accountGroupId', Numeric(18, 0), Identity(), nullable=False)
)


t_Events = Table(
    'Events', Base.metadata,
    Column('eventId', Integer, Identity(start=1, increment=1), nullable=False),
    Column('eventType', Integer),
    Column('customer', Numeric(18, 0)),
    Column('notes', String(500, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('taskDateFrom', DateTime),
    Column('taskDateTo', DateTime),
    Column('status', Integer),
    Column('feedBack', String(500, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('createdDate', DateTime),
    Column('updatedDate', DateTime),
    Column('createdBy', Integer)
)


t_INSALIK = Table(
    'INSALIK', Base.metadata,
    Column('InvoiceNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('SalikTransId', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SalikTime', DateTime),
    Column('TagNo', NCHAR(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Location', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Direction', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Amount', MONEY),
    Column('SurCharge', MONEY),
    Column('PlateCode', Unicode(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PlateNo', Unicode(20, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Status', Boolean, server_default=text('((1))')),
    Column('RTAPostDate', DateTime),
    Column('Type', String(2, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('AUTOID', Integer, Identity(start=1, increment=1), nullable=False)
)


class Options(Base):
    __tablename__ = 'Options'
    __table_args__ = (
        PrimaryKeyConstraint('OPTIONNAME', name='PK_Options'),
    )

    OPTIONNAME: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True)
    OPTIONVALUE: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class PlateCategory(Base):
    __tablename__ = 'Plate_Category'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='PK_Plate_Category'),
    )

    ID: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), primary_key=True)
    CATEGORY: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))


t_RTALogin = Table(
    'RTALogin', Base.metadata,
    Column('TrafficFileID', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('UserName', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Password', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
)


class SalikAccounts(Base):
    __tablename__ = 'Salik_Accounts'
    __table_args__ = (
        PrimaryKeyConstraint('ID', name='PK_Salik_Accounts'),
    )

    ID: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    USERNAME: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    USERPASSWORD: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))


t_Salik_Accounts_AUH = Table(
    'Salik_Accounts_AUH', Base.metadata,
    Column('ID', Integer, Identity(start=1, increment=1), nullable=False),
    Column('USERNAME', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('USERPASSWORD', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_Salik_Invoice_Temp = Table(
    'Salik_Invoice_Temp', Base.metadata,
    Column('TRANSID', Integer),
    Column('SALIKTRANSID', Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('DATEANDTIME', DateTime),
    Column('LOCATION', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('AMOUNT', MONEY),
    Column('SURCHARGE', MONEY),
    Column('PLATENO', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('PLATECODENAME', Unicode(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CONTRACTID', Integer),
    Column('CONTRACTREFNO', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CustomerId', Numeric(18, 0)),
    Column('RBSCustomerCode', Unicode(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CustomerName', Unicode(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Address', Unicode(500, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SalesPersonId', Numeric(18, 0)),
    Column('RBSSPCode', Unicode(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('RTAPostDate', DateTime),
    Column('LPONo', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('UserName', Unicode(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TagNo', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('VH', String(10, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('VehicleId', Integer),
    Column('Source', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
)


class SalikToll(Base):
    __tablename__ = 'Salik_Toll'
    __table_args__ = (
        PrimaryKeyConstraint('TRANSID', name='PK_Salik_Toll'),
        Index('IX_TBL_TOLL_UniqueRecord', 'DATEANDTIME', 'TAGNO', mssql_clustered=False, unique=True)
    )

    TRANSID: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    SALIKTRANSID: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    DATEANDTIME: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    POSTDATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DOWNLOADDATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PLATENO: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    SOURCE: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    TAGNO: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    LOCATION: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    DIRECTION: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    AMOUNT: Mapped[Optional[Any]] = mapped_column(MONEY)
    SALIKUSER: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    PAGEINFO: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ISPOSTED: Mapped[Optional[bool]] = mapped_column(Boolean)
    ISRECENT: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((1))'))
    INVOICENO: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    INVOICEGENDATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


t_SmtpDetails = Table(
    'SmtpDetails', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('HostSmtp', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('HostPort', Integer),
    Column('FromMail', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('FromMailPassword', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('ToMail', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('IsActive', Boolean)
)


class StagingInvoiceHeader(Base):
    __tablename__ = 'Staging_Invoice_Header'
    __table_args__ = (
        PrimaryKeyConstraint('SIH_ID', name='PK_Staging_Invoice_Header'),
    )

    SIH_ID: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    SIH_LOCATION_ID: Mapped[int] = mapped_column(Integer, nullable=False)
    SIH_INVOICE_TYPE: Mapped[str] = mapped_column(String(2, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CREATED_BY: Mapped[int] = mapped_column(Integer, nullable=False)
    CREATED_ON: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    IS_POSTED: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('((0))'))
    SIH_TRANS_ID: Mapped[Optional[int]] = mapped_column(Integer)
    SIH_CONTRACT_ID: Mapped[Optional[int]] = mapped_column(Integer)
    SIH_TOTAL_COST: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    SIH_TAX_AMOUNT: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    SIH_INVOICE_NO: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_DATE_RANGE_REMARKS: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_CONTRACT_NO: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_VEHICLE_NO: Mapped[Optional[str]] = mapped_column(Unicode(20, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_LPO_NO: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_USER_NAME: Mapped[Optional[str]] = mapped_column(Unicode(200, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_CUST_CODE: Mapped[Optional[str]] = mapped_column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_SP_CODE: Mapped[Optional[str]] = mapped_column(String(3, 'SQL_Latin1_General_CP1_CI_AS'))
    SIH_CUST_ID: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    SIH_SP_ID: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))

    Staging_Invoice_Detail: Mapped[list['StagingInvoiceDetail']] = relationship('StagingInvoiceDetail', back_populates='Staging_Invoice_Header')


class TrafficFine(Base):
    __tablename__ = 'Traffic_Fine'
    __table_args__ = (
        PrimaryKeyConstraint('TICKETNO', name='PK_TRAFFIC_FINE'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), nullable=False)
    TICKETNO: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True)
    VEHICLEID: Mapped[int] = mapped_column(Integer, nullable=False)
    TRAFFICFILEID: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    FINEDATETIME: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    AUTHORITY: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    PLATEDETAILS: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    AMOUNT: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    BLACKPOINTS: Mapped[Optional[int]] = mapped_column(Integer)
    FINEDESCRIPTION: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    ACKNOWLEDGMENT: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DOWNLOADDATE: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    PAID: Mapped[Optional[bool]] = mapped_column(Boolean)
    VOUCHERNO: Mapped[Optional[str]] = mapped_column(Unicode(255, 'SQL_Latin1_General_CP1_CI_AS'))
    ISPOSTED: Mapped[Optional[bool]] = mapped_column(Boolean)
    INVOICE_REMARKS: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


t_TripDuration = Table(
    'TripDuration', Base.metadata,
    Column('Id', Integer),
    Column('Duration', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


class UnregisteredVehicle(Base):
    __tablename__ = 'UnregisteredVehicle'
    __table_args__ = (
        PrimaryKeyConstraint('VEHICLEID', name='PK_UnregisteredVehicle'),
    )

    VEHICLEID: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VEHICLENO: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    PLATECODE: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    REGNO: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 0))
    TRAFFICID: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


t_VT_ApplicationUserDesignations = Table(
    'VT_ApplicationUserDesignations', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Name', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_ApplicationUserRoles = Table(
    'VT_ApplicationUserRoles', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Name', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_ApplicationUserStatus = Table(
    'VT_ApplicationUserStatus', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Name', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_ApplicationUsers = Table(
    'VT_ApplicationUsers', Base.metadata,
    Column('UserID', BigInteger, Identity(start=1, increment=1), nullable=False),
    Column('UserName', Unicode(256, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Password', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('FirstName', Unicode(150, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('LastName', Unicode(150, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('DisplayName', Unicode(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Phone1', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Phone2', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('Email', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('Status', Integer, nullable=False),
    Column('UserType', Integer, nullable=False),
    Column('CreatedDate', DateTime, nullable=False),
    Column('UpdateDate', DateTime),
    Column('Designation', Integer, nullable=False),
    Column('UserCode', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False),
    Column('ReportingTo', Integer),
    Column('SalesPersonCode', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('SalesPersonId', Numeric(18, 0))
)


class VTBatteryBrandMaster(Base):
    __tablename__ = 'VT_BatteryBrandMaster'
    __table_args__ = (
        PrimaryKeyConstraint('BatteryBrandId', name='PK_VT_BatteryBrandMaster'),
    )

    BatteryBrandId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    BatteryBrandName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class VTBatterySupplierMaster(Base):
    __tablename__ = 'VT_BatterySupplierMaster'
    __table_args__ = (
        PrimaryKeyConstraint('BatterySupplierId', name='PK_VT_BatterySupplierMaster'),
    )

    BatterySupplierId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    BatterySupplierName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class VTCompanyMaster(Base):
    __tablename__ = 'VT_CompanyMaster'
    __table_args__ = (
        PrimaryKeyConstraint('CompanyId', name='PK_VT_CompanyMaster'),
    )

    CompanyId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    CompanyName: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))


class VTCompanyBranchMaster(Base):
    __tablename__ = 'VT_Company_BranchMaster'
    __table_args__ = (
        PrimaryKeyConstraint('BranchId', name='PK_VT_Company_BranchMaster'),
    )

    BranchId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    BranchName: Mapped[str] = mapped_column(Unicode(150, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CompanyId: Mapped[int] = mapped_column(Integer, nullable=False)

    VT_Company_DepartmentMaster: Mapped[list['VTCompanyDepartmentMaster']] = relationship('VTCompanyDepartmentMaster', back_populates='VT_Company_BranchMaster')


t_VT_ContractClosingExtraCharges = Table(
    'VT_ContractClosingExtraCharges', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('ContractId', Integer),
    Column('SalesDetailItemType', Numeric(18, 0)),
    Column('Amount', DECIMAL(18, 2))
)


class VTContractDocuments(Base):
    __tablename__ = 'VT_ContractDocuments'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_ContractDocuments'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ContractId: Mapped[int] = mapped_column(Integer, nullable=False)
    TempId: Mapped[int] = mapped_column(Integer, nullable=False)
    FileType: Mapped[Optional[str]] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    FileName: Mapped[Optional[str]] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))
    Description: Mapped[Optional[str]] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'))


class VTContractDriverDtls(Base):
    __tablename__ = 'VT_ContractDriverDtls'
    __table_args__ = (
        PrimaryKeyConstraint('ContractDriverId', name='PK_VT_ContractDriverDtls'),
    )

    ContractDriverId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ContractId: Mapped[int] = mapped_column(Integer, nullable=False)
    UserName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Address: Mapped[str] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Mobile: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Email: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DateOfBirth: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    NationalityId: Mapped[str] = mapped_column(NCHAR(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    PassportNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    PassportExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    VisaType: Mapped[int] = mapped_column(Integer, nullable=False)
    VisaExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    DrivingLicenseType: Mapped[int] = mapped_column(Integer, nullable=False)
    DrivingLicenseNo: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DLPlaceOfIssue: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DLIssueDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    DLExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    DriverStatus: Mapped[int] = mapped_column(Integer, nullable=False)
    Phone: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    Fax: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


t_VT_ContractHistory = Table(
    'VT_ContractHistory', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('ContractId', Integer),
    Column('TaskName', Unicode(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('TaskDate', DateTime),
    Column('CreatedBy', Integer),
    Column('CreatedDate', DateTime),
    Column('HistoryType', Integer),
    Column('Remarks', Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
)


class VTContractMaster(Base):
    __tablename__ = 'VT_ContractMaster'
    __table_args__ = (
        PrimaryKeyConstraint('ContractId', name='PK_VT_VehicleContractMaster'),
    )

    ContractId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    RTACode: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ContractType: Mapped[int] = mapped_column(Integer, nullable=False)
    ContractRefNo: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ContractStartDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    ContractExpectedEndDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    ContractActualEndDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    ContractLocId: Mapped[int] = mapped_column(Integer, nullable=False)
    CustomerName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    UserName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Address: Mapped[str] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Phone: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Mobile: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Fax: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Email: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DateOfBirth: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    Nationality: Mapped[str] = mapped_column(NCHAR(3, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    PassportNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False, server_default=text('((0))'))
    PassportExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('(((1900)/(1))/(1))'))
    VisaType: Mapped[int] = mapped_column(Integer, nullable=False)
    VisaExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('(((1900)/(1))/(1))'))
    DrivingLicenseType: Mapped[int] = mapped_column(Integer, nullable=False)
    DrivingLicenseNo: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DLPlaceOfIssue: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DLIssueDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    DLExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    PaymentType: Mapped[int] = mapped_column(Integer, nullable=False)
    Rate: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    DriverCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    AddDriverCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    CDW: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    PAI: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    ExcessKmCharge: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    FuelCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    SalikCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    ExcessInsCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    TrafficCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    MileageCap: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    OtherCharges: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    DiscountType: Mapped[int] = mapped_column(Integer, nullable=False)
    Discount: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    Advance: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    Subtotal: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False, server_default=text('((0))'))
    PaymentMode: Mapped[int] = mapped_column(Integer, nullable=False)
    CreditCardExpiryMonth: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('((0))'))
    CreditCardExpiryYear: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('((0))'))
    Status: Mapped[int] = mapped_column(Integer, nullable=False)
    CustomerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    SalesPersonId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    CreditCardType: Mapped[Optional[int]] = mapped_column(Integer)
    CreditCardNo: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    Remarks: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    RentalInvoiced: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    SalikInvoiced: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    FineInvoiced: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    RepairCharged: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    PenaltyCharged: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    ExcessKmCharged: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    OtherChargesCharged: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('((0))'))
    VehicleId: Mapped[Optional[int]] = mapped_column(Integer)
    NextInvStDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CreatedBy: Mapped[Optional[int]] = mapped_column(Integer)
    CreatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UpdatedBy: Mapped[Optional[int]] = mapped_column(Integer)
    UpdatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CustomerSource: Mapped[Optional[int]] = mapped_column(Integer)
    CustomerType: Mapped[Optional[int]] = mapped_column(Integer)
    ConfirmationRefType: Mapped[Optional[int]] = mapped_column(Integer)
    ConfirmationRefValue: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ContactPerson: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    ContactPersonAddress: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    ContactPersonPhone: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ContactPersonMobile: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ContactPersonFax: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ContactPersonEmail: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    LastInvoiceDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ContractUnder: Mapped[Optional[int]] = mapped_column(Integer)
    IsAdvanceInvoice: Mapped[Optional[bool]] = mapped_column(Boolean)
    BillingType: Mapped[Optional[int]] = mapped_column(Integer)


t_VT_ContractPreTerminationTermsForQuotation = Table(
    'VT_ContractPreTerminationTermsForQuotation', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Terms', Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
)


class VTContractTypeMaster(Base):
    __tablename__ = 'VT_ContractTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('ContractTypeId', name='PK_VT_ContractTypeMaster'),
    )

    ContractTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ContractType: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ContractTypeDesc: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    LatestCount: Mapped[Optional[int]] = mapped_column(Integer)


class VTContractVehicleMaster(Base):
    __tablename__ = 'VT_ContractVehicleMaster'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_ContractVehicleMaster'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ContractId: Mapped[int] = mapped_column(Integer, nullable=False)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    ContractVehicleStatus: Mapped[int] = mapped_column(Integer, nullable=False)
    DatetimeOut: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DatetimeIn: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    KmOut: Mapped[Optional[int]] = mapped_column(Integer)
    KmIn: Mapped[Optional[int]] = mapped_column(Integer)
    FuelLevelIdOut: Mapped[Optional[int]] = mapped_column(Integer)
    FuelLevelIdIn: Mapped[Optional[int]] = mapped_column(Integer)
    DTIN: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CheckedOutBy: Mapped[Optional[int]] = mapped_column(Integer)
    CheckedInBy: Mapped[Optional[int]] = mapped_column(Integer)
    LocationOut: Mapped[Optional[int]] = mapped_column(Integer)
    LocationIn: Mapped[Optional[int]] = mapped_column(Integer)


t_VT_CreditCardType = Table(
    'VT_CreditCardType', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Type', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


class VTDLTypes(Base):
    __tablename__ = 'VT_DLTypes'
    __table_args__ = (
        PrimaryKeyConstraint('DLTypeId', name='PK_VT_DLTypes'),
    )

    DLTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    DLTypeName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


t_VT_DiscountType = Table(
    'VT_DiscountType', Base.metadata,
    Column('DiscountTypeId', Integer, Identity(start=1, increment=1), nullable=False),
    Column('DiscountType', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_FleetAgreementStatus = Table(
    'VT_FleetAgreementStatus', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Status', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


class VTGarageMaster(Base):
    __tablename__ = 'VT_GarageMaster'
    __table_args__ = (
        PrimaryKeyConstraint('GarageId', name='PK_VT_GarageMaster'),
    )

    GarageId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    GarageName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    GarageActive: Mapped[bool] = mapped_column(Boolean, nullable=False)


t_VT_GroupCompanyList = Table(
    'VT_GroupCompanyList', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('RBSCustomerCode', String(50, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('CustomerName', Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
)


class VTHistoryTypeMaster(Base):
    __tablename__ = 'VT_HistoryTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('HistoryTypeId', name='PK_VT_Veh_HistoryTypeMaster'),
    )

    HistoryTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    HistoryTypeName: Mapped[str] = mapped_column(String(250, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


t_VT_Lease_PaymentMode = Table(
    'VT_Lease_PaymentMode', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Name', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)


class VTLookupTable(Base):
    __tablename__ = 'VT_LookupTable'
    __table_args__ = (
        PrimaryKeyConstraint('LookupId', name='PK_VT_LookupTable'),
    )

    LookupId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    LookupValue: Mapped[Optional[int]] = mapped_column(Integer)
    LookupDescription: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    LookupType: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


t_VT_Menu = Table(
    'VT_Menu', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('MenuName', String(collation='SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)


t_VT_Nationality = Table(
    'VT_Nationality', Base.metadata,
    Column('NationalityId', NCHAR(3, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('NationalityName', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_QuotationApprovedBy = Table(
    'VT_QuotationApprovedBy', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('ApprovedBy', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_QuotationDiscountType = Table(
    'VT_QuotationDiscountType', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Type', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_QuotationPaymentTerms = Table(
    'VT_QuotationPaymentTerms', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Terms', Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
)


class VTSmtpDetails(Base):
    __tablename__ = 'VT_SmtpDetails'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_SmtpDetails'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    HostType: Mapped[str] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    PortNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    Hostname: Mapped[str] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    username: Mapped[str] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    password: Mapped[str] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTStatusMaster(Base):
    __tablename__ = 'VT_StatusMaster'
    __table_args__ = (
        PrimaryKeyConstraint('StatusId', name='PK_VT_StatusMaster'),
    )

    StatusId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    StatusName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    StatusTypeId: Mapped[int] = mapped_column(Integer, nullable=False)


class VTStatusTypeMaster(Base):
    __tablename__ = 'VT_StatusTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('StatusTypeId', name='PK_VT_StatusTypeMaster'),
    )

    StatusTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    StatusTypeName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTSubMenuMaster(Base):
    __tablename__ = 'VT_SubMenuMaster'
    __table_args__ = (
        PrimaryKeyConstraint('SubMenuId', name='PK_VT_SubMenuMaster'),
    )

    SubMenuId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    SubMenuName: Mapped[str] = mapped_column(String(200, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    MenuId: Mapped[int] = mapped_column(Integer, nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class VTTyreBrandMaster(Base):
    __tablename__ = 'VT_TyreBrandMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TyreBrandId', name='PK_VT_TyreBrandMaster'),
    )

    TyreBrandId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TyreBrandName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class VTTyreSupplierMaster(Base):
    __tablename__ = 'VT_TyreSupplierMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TyreSupplierId', name='PK_VT_TyreSupplierMaster'),
    )

    TyreSupplierId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TyreSupplierName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Active: Mapped[bool] = mapped_column(Boolean, nullable=False)


t_VT_UserRights = Table(
    'VT_UserRights', Base.metadata,
    Column('UserId', Integer, nullable=False),
    Column('SubMenuId', Integer, nullable=False)
)


t_VT_ValidationTemplate = Table(
    'VT_ValidationTemplate', Base.metadata,
    Column('KMFrom', Integer, nullable=False),
    Column('KMTo', Integer, nullable=False)
)


class VTVehContractStatusMaster(Base):
    __tablename__ = 'VT_VehContractStatusMaster'
    __table_args__ = (
        PrimaryKeyConstraint('VehicleContractStatusId', name='PK_VT_VehContractStatusMaster'),
    )

    VehicleContractStatusId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleContractStatusName: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class VTVehColourMaster(Base):
    __tablename__ = 'VT_Veh_ColourMaster'
    __table_args__ = (
        PrimaryKeyConstraint('ColourId', name='PK_VT_Veh_ColourMaster'),
    )

    ColourId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ColourName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_ColourMaster')


class VTVehEngineCapacityMaster(Base):
    __tablename__ = 'VT_Veh_EngineCapacityMaster'
    __table_args__ = (
        PrimaryKeyConstraint('EngineCapacityId', name='PK_VT_Veh_EngineCapacityMaster'),
    )

    EngineCapacityId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    EngineCapacity: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    ModelId: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVehFleetTypeMaster(Base):
    __tablename__ = 'VT_Veh_FleetTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('FleetTypeId', name='PK_VT_Veh_FleetTypeMaster'),
    )

    FleetTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    FleetTypeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_FleetTypeMaster')


class VTVehFuelCapacityUnitMaster(Base):
    __tablename__ = 'VT_Veh_FuelCapacityUnitMaster'
    __table_args__ = (
        PrimaryKeyConstraint('FuelCapUnitId', name='PK_VT_Veh_FuelCapacityUnitMaster'),
    )

    FuelCapUnitId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    FuelCapUnit: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_FuelCapacityUnitMaster')


class VTVehFuelLevelMaster(Base):
    __tablename__ = 'VT_Veh_FuelLevelMaster'
    __table_args__ = (
        PrimaryKeyConstraint('FuelLevelId', name='PK_VT_Veh_FuelLevelMaster'),
    )

    FuelLevelId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    FuelLevel: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehFuelTypeMaster(Base):
    __tablename__ = 'VT_Veh_FuelTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('FuelTypeId', name='PK_VT_Veh_FuelTypeMaster'),
    )

    FuelTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    FuelTypeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehInsuranceCompanyMaster(Base):
    __tablename__ = 'VT_Veh_InsuranceCompanyMaster'
    __table_args__ = (
        PrimaryKeyConstraint('InsuranceCompanyId', name='PK_VT_Veh_InsuranceCompanyMaster'),
    )

    InsuranceCompanyId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    InsuranceCompanyName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehInsurancePolicyMaster(Base):
    __tablename__ = 'VT_Veh_InsurancePolicyMaster'
    __table_args__ = (
        PrimaryKeyConstraint('InsurancePolicyId', name='PK_VT_Veh_InsurancePolicyMaster'),
    )

    InsurancePolicyId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    InsurancePolicyNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    Status: Mapped[Optional[bool]] = mapped_column(Boolean)


class VTVehInsuranceTypeMaster(Base):
    __tablename__ = 'VT_Veh_InsuranceTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('InsuranceTypeId', name='PK_VT_Veh_InsuranceTypeMaster'),
    )

    InsuranceTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    InsuranceTypeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehLocationMaster(Base):
    __tablename__ = 'VT_Veh_LocationMaster'
    __table_args__ = (
        PrimaryKeyConstraint('LocationId', name='PK_VT_Veh_LocationMaster'),
    )

    LocationId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    LocationName: Mapped[str] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehMakeMaster(Base):
    __tablename__ = 'VT_Veh_MakeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('MakeId', name='PK_VT_Veh_Make'),
    )

    MakeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    MakeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_ModelMaster: Mapped[list['VTVehModelMaster']] = relationship('VTVehModelMaster', back_populates='VT_Veh_MakeMaster')


class VTVehPlateCategoryMaster(Base):
    __tablename__ = 'VT_Veh_PlateCategoryMaster'
    __table_args__ = (
        PrimaryKeyConstraint('PlateCategoryId', name='PK_VT_Veh_PlateCategoryMaster'),
    )

    PlateCategoryId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    PlateCategoryName: Mapped[str] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    StateId: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVehRegNoTypeMaster(Base):
    __tablename__ = 'VT_Veh_RegNoTypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('RegNoTypeId', name='PK_VT_RegNoTypeMaster'),
    )

    RegNoTypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    RegNoTypeValue: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehServiceMaster(Base):
    __tablename__ = 'VT_Veh_ServiceMaster'
    __table_args__ = (
        PrimaryKeyConstraint('ServiceId', name='PK_VT_ServiceMaster'),
    )

    ServiceId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ServiceName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehServiceMovements(Base):
    __tablename__ = 'VT_Veh_ServiceMovements'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_Veh_ServiceMovements'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    ServiceDateTimeIn: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ServiceDateTimeOut: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ServiceKmIn: Mapped[Optional[int]] = mapped_column(Integer)
    ServiceKmOut: Mapped[Optional[int]] = mapped_column(Integer)
    TypeOfWork: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class VTVehStateMaster(Base):
    __tablename__ = 'VT_Veh_StateMaster'
    __table_args__ = (
        PrimaryKeyConstraint('StateId', name='PK_VT_StateMaster'),
    )

    StateId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    StateName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_PlateCodeMaster: Mapped[list['VTVehPlateCodeMaster']] = relationship('VTVehPlateCodeMaster', back_populates='VT_Veh_StateMaster')


class VTVehStatusChangeDetails(Base):
    __tablename__ = 'VT_Veh_StatusChangeDetails'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_Veh_StatusChangeDetails'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[Optional[int]] = mapped_column(Integer)
    VehKm: Mapped[Optional[int]] = mapped_column(Integer)
    DateTimeIn: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    DateTimeOut: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    LocationId: Mapped[Optional[int]] = mapped_column(Integer)
    StatusId: Mapped[Optional[int]] = mapped_column(Integer)
    ContractId: Mapped[Optional[int]] = mapped_column(Integer)
    CreatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CreatedBy: Mapped[Optional[int]] = mapped_column(Integer)


class VTVehTCNoMaster(Base):
    __tablename__ = 'VT_Veh_TCNoMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TCNoId', name='PK_VT_Veh_TCNoMaster'),
    )

    TCNoId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TCNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


class VTVehTariffGroupMaster(Base):
    __tablename__ = 'VT_Veh_TariffGroupMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TariffGroupId', name='PK_VT_Veh_TariffGroupMaster'),
    )

    TariffGroupId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TariffGroupName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    DailyRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    WeeklyRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    MonthlyRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DiscountPercentPerDayDaily: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DiscountPercent3DaysDaily: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DiscountPercent5DaysDaily: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DiscountPercentWeekly: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DiscountPercentMonthly: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    FuelCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    AllowedKmsPerDay: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    ExtraKmCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DailyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    WeeklyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    MonthlyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    DailyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    WeeklyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    MonthlyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))


class VTVehTransmissionMaster(Base):
    __tablename__ = 'VT_Veh_TransmissionMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TransmissionId', name='PK_VT_Veh_TransmissionMaster'),
    )

    TransmissionId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TransmissionName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_TransmissionMaster')


class VTVehTypeMaster(Base):
    __tablename__ = 'VT_Veh_TypeMaster'
    __table_args__ = (
        PrimaryKeyConstraint('TypeId', name='PK_VT_Veh_TypeMaster'),
    )

    TypeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    TypeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)

    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_TypeMaster')


t_VT_Veh_VehicleDocuments = Table(
    'VT_Veh_VehicleDocuments', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('VehicleId', Integer, nullable=False),
    Column('FileType', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('FileName', String(200, 'SQL_Latin1_General_CP1_CI_AS')),
    Column('TempId', Integer, nullable=False),
    Column('Description', String(200, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_VT_Veh_VehicleHistory = Table(
    'VT_Veh_VehicleHistory', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('VehicleId', Integer),
    Column('TaskName', Unicode(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('TaskDate', DateTime),
    Column('CreatedBy', Integer),
    Column('CreatedDate', DateTime),
    Column('HistoryType', Integer),
    Column('Remarks', Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
)


class VTVehVehicleMovLocMaster(Base):
    __tablename__ = 'VT_Veh_VehicleMovLocMaster'
    __table_args__ = (
        PrimaryKeyConstraint('MovLocId', name='PK_VT_Veh_VehicleMovLocMaster'),
    )

    MovLocId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    MovLocName: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)


t_VT_Veh_VehicleMovementType = Table(
    'VT_Veh_VehicleMovementType', Base.metadata,
    Column('Id', Integer, Identity(start=1, increment=1), nullable=False),
    Column('Type', Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
)


class VTVehVehicleMovements(Base):
    __tablename__ = 'VT_Veh_VehicleMovements'
    __table_args__ = (
        PrimaryKeyConstraint('MovementId', name='PK_VT_Veh_VehicleMovements'),
    )

    MovementId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    StaffId: Mapped[int] = mapped_column(Integer, nullable=False)
    StartDatetime: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    EndDatetime: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    LocationFrom: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    LocationTo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    kmFrom: Mapped[int] = mapped_column(Integer, nullable=False)
    kmTo: Mapped[int] = mapped_column(Integer, nullable=False)
    MovementType: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    DiscardedFlag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    movementRemarks: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    UpdatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UpdatedBy: Mapped[Optional[int]] = mapped_column(Integer)
    OverlappingFlag: Mapped[Optional[bool]] = mapped_column(Boolean)
    ReplacementFlag: Mapped[Optional[bool]] = mapped_column(Boolean)
    ServiceFlag: Mapped[Optional[bool]] = mapped_column(Boolean)
    OKFlag: Mapped[Optional[bool]] = mapped_column(Boolean)
    LocId: Mapped[Optional[int]] = mapped_column(Integer)


class VTVehVehicleReplacement(Base):
    __tablename__ = 'VT_Veh_VehicleReplacement'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_Veh_VehicleReplacement'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ContractId: Mapped[Optional[int]] = mapped_column(Integer)
    TakingVehicleId: Mapped[Optional[int]] = mapped_column(Integer)
    TakingDateTime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    TakingKm: Mapped[Optional[int]] = mapped_column(Integer)
    TakingLocation: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    TakingFuel: Mapped[Optional[int]] = mapped_column(Integer)
    TakingVehicleMovement: Mapped[Optional[bool]] = mapped_column(Boolean)
    TakingVehicleDueService: Mapped[Optional[int]] = mapped_column(Integer)
    TakingVehicleRemarks: Mapped[Optional[str]] = mapped_column(Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
    TakingVehicleStatusId: Mapped[Optional[int]] = mapped_column(Integer)
    GivingVehicleId: Mapped[Optional[int]] = mapped_column(Integer)
    GivingDateTime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    GivingKm: Mapped[Optional[int]] = mapped_column(Integer)
    GivingLocation: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    GivingFuel: Mapped[Optional[int]] = mapped_column(Integer)
    GivingVehicleMovement: Mapped[Optional[bool]] = mapped_column(Boolean)
    GivingVehicleDueService: Mapped[Optional[int]] = mapped_column(Integer)
    GivingVehicleRemarks: Mapped[Optional[str]] = mapped_column(Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
    ReplacementReason: Mapped[Optional[str]] = mapped_column(Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
    StaffId: Mapped[Optional[int]] = mapped_column(Integer)
    CreatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CreatedBy: Mapped[Optional[int]] = mapped_column(Integer)
    UpdatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    UpdatedBy: Mapped[Optional[int]] = mapped_column(Integer)
    ReplacementLocation: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    LocId: Mapped[Optional[int]] = mapped_column(Integer)
    GarageId: Mapped[Optional[int]] = mapped_column(Integer)
    ReplacementContractId: Mapped[Optional[int]] = mapped_column(Integer)


class VTVehicleBatteryServiceDtls(Base):
    __tablename__ = 'VT_VehicleBatteryServiceDtls'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VehicleBatteryServiceDtls'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    VehicleServiceId: Mapped[int] = mapped_column(Integer, nullable=False)
    BatteryBrandId: Mapped[int] = mapped_column(Integer, nullable=False)
    BatteryUnitPrice: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    BatteryInvoiceNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    UpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    UpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    BatterySupplierId: Mapped[int] = mapped_column(Integer, nullable=False)
    BatteryWarrantyNo: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class VTVehicleServiceDetails(Base):
    __tablename__ = 'VT_VehicleServiceDetails'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VehicleServiceDetails'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleServiceId: Mapped[int] = mapped_column(Integer, nullable=False)
    ServiceId: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVehicleServiceHeader(Base):
    __tablename__ = 'VT_VehicleServiceHeader'
    __table_args__ = (
        PrimaryKeyConstraint('VehicleServiceId', name='PK_VT_VehicleServiceHeader'),
    )

    VehicleServiceId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    ServiceDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    ServiceKm: Mapped[int] = mapped_column(Integer, nullable=False)
    GarageId: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    UpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    UpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    Remarks: Mapped[Optional[str]] = mapped_column(Unicode(500, 'SQL_Latin1_General_CP1_CI_AS'))
    NextDueService: Mapped[Optional[int]] = mapped_column(Integer)
    AlertDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class VTVehicleTyreServiceDtls(Base):
    __tablename__ = 'VT_VehicleTyreServiceDtls'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VehicleTyreServiceDtls'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    VehicleServiceId: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreQty: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreBrandId: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreUnitPrice: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    UpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    UpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreSupplierId: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVehicleWheelAlignDtls(Base):
    __tablename__ = 'VT_VehicleWheelAlignDtls'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VehicleWheelAlignDtls'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    VehicleServiceId: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreQty: Mapped[int] = mapped_column(Integer, nullable=False)
    UnitPrice: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    SupplierId: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    UpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    UpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVehicleWheelRotationDtls(Base):
    __tablename__ = 'VT_VehicleWheelRotationDtls'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VehicleWheelRotationDtls'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    VehicleId: Mapped[int] = mapped_column(Integer, nullable=False)
    VehicleServiceId: Mapped[int] = mapped_column(Integer, nullable=False)
    TyreQty: Mapped[int] = mapped_column(Integer, nullable=False)
    UnitPrice: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    SupplierId: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    UpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    UpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)


class VTVisaType(Base):
    __tablename__ = 'VT_VisaType'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_VT_VisaType'),
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    Name: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


t_ViewCashBank = Table(
    'ViewCashBank', Base.metadata,
    Column('accountGroupId', Numeric(18, 0), Identity(), nullable=False)
)


class Sysdiagrams(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        PrimaryKeyConstraint('diagram_id', name='PK__sysdiagr__C2B05B6136BEC772'),
        Index('UK_principal_name', 'principal_id', 'name', mssql_clustered=False, unique=True)
    )

    name: Mapped[str] = mapped_column(Unicode(128, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    principal_id: Mapped[int] = mapped_column(Integer, nullable=False)
    diagram_id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    version: Mapped[Optional[int]] = mapped_column(Integer)
    definition: Mapped[Optional[bytes]] = mapped_column(LargeBinary)


class TblAccountGroup(Base):
    __tablename__ = 'tbl_AccountGroup'
    __table_args__ = (
        PrimaryKeyConstraint('accountGroupId', name='PK__tbl_Acco__74C422AE625A9A57'),
    )

    accountGroupId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    accountGroupName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    groupUnder: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    nature: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    affectGrossProfit: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblAccountLedger(Base):
    __tablename__ = 'tbl_AccountLedger'
    __table_args__ = (
        PrimaryKeyConstraint('ledgerId', name='PK_tbl_AccountLedger_1'),
        Index('IX_tbl_AccountLedger', 'ledgerId', 'accountGroupId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_1', 'accountGroupId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_2', 'accountGroupId', 'billByBill', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_3', 'areaId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_4', 'routeId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_5', 'areaId', 'routeId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_6', 'accountGroupId', 'areaId', 'ledgerId', 'routeId', 'billByBill', 'pricinglevelId', mssql_clustered=False),
        Index('IX_tbl_AccountLedger_7', 'pricinglevelId', mssql_clustered=False)
    )

    ledgerId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    accountGroupId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    ledgerNameInArabic: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    emirateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    openingBalance: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    crOrDr: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    mailingName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    address: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    phone: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    mobile: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    email: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    creditPeriod: Mapped[Optional[int]] = mapped_column(Integer)
    creditLimit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    pricinglevelId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    billByBill: Mapped[Optional[bool]] = mapped_column(Boolean)
    tin: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    cst: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    pan: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    routeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bankAccountNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    branchName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    branchCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    areaId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    isCorporate: Mapped[Optional[bool]] = mapped_column(Boolean)
    empId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    Nationality: Mapped[Optional[str]] = mapped_column(NCHAR(3, 'SQL_Latin1_General_CP1_CI_AS'))
    CustomerIdNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    CustomerIdExpiry: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblAdditionalCost(Base):
    __tablename__ = 'tbl_AdditionalCost'
    __table_args__ = (
        PrimaryKeyConstraint('additionalCostId', name='PK__tbl_Addi__D89F761D24092D7A'),
    )

    additionalCostId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblAdvancePayment(Base):
    __tablename__ = 'tbl_AdvancePayment'
    __table_args__ = (
        PrimaryKeyConstraint('advancePaymentId', name='PK__tbl_Adva__1A7BF2355AB9788F'),
    )

    advancePaymentId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 5))
    salaryMonth: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    chequenumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblArea(Base):
    __tablename__ = 'tbl_Area'
    __table_args__ = (
        PrimaryKeyConstraint('areaId', name='PK_tbl_Area'),
    )

    areaId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    areaName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblBankReconciliation(Base):
    __tablename__ = 'tbl_BankReconciliation'
    __table_args__ = (
        PrimaryKeyConstraint('reconcileId', name='PK__tbl_Bank__66CCE65DB90A885B'),
    )

    reconcileId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), primary_key=True)
    ledgerPostingId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    statementDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblBatch(Base):
    __tablename__ = 'tbl_Batch'
    __table_args__ = (
        PrimaryKeyConstraint('batchId', name='PK__tbl_Batc__78CCD773147C05D0'),
    )

    batchId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    batchNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    barcode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    partNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    manufacturingDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expiryDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblBonusDeduction(Base):
    __tablename__ = 'tbl_BonusDeduction'
    __table_args__ = (
        PrimaryKeyConstraint('bonusDeductionId', name='PK_tbl_BonusDeduction'),
        Index('IX_tbl_BonusDeduction', 'employeeId', mssql_clustered=False),
        Index('IX_tbl_BonusDeduction_1', 'employeeId', 'month', mssql_clustered=False),
        Index('IX_tbl_BonusDeduction_2', 'date', 'month', mssql_clustered=False),
        Index('IX_tbl_BonusDeduction_3', 'month', mssql_clustered=False)
    )

    bonusDeductionId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    month: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    bonusAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    deductionAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblBranch(Base):
    __tablename__ = 'tbl_Branch'
    __table_args__ = (
        PrimaryKeyConstraint('branch', name='PK_tbl_Branch'),
    )

    branch: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    branchName: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblBrand(Base):
    __tablename__ = 'tbl_Brand'
    __table_args__ = (
        PrimaryKeyConstraint('brandId', name='PK__tbl_Bran__06B7729946136164'),
    )

    brandId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    brandName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblBudgetDetails(Base):
    __tablename__ = 'tbl_BudgetDetails'
    __table_args__ = (
        PrimaryKeyConstraint('budgetDetailsId', name='PK__tbl_Budg__C2BA2365004BBB48'),
    )

    budgetDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    budgetMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    particular: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblBudgetMaster(Base):
    __tablename__ = 'tbl_BudgetMaster'
    __table_args__ = (
        PrimaryKeyConstraint('budgetMasterId', name='PK__tbl_Budg__060415BC7C7B2A64'),
    )

    budgetMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    budgetName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    type: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    totalDr: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    totalCr: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    fromDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    toDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblCompany(Base):
    __tablename__ = 'tbl_Company'
    __table_args__ = (
        PrimaryKeyConstraint('companyId', name='PK__tbl_Comp__AD5459903E723F9C'),
        Index('IX_tbl_Company', 'currencyId', mssql_clustered=False)
    )

    companyId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    companyName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    mailingName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    address: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    phone: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    mobile: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    emailId: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    web: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    country: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    state: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    pin: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    currencyId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    booksBeginingFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    tin: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    cst: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    pan: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    currentDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    logo: Mapped[Optional[bytes]] = mapped_column(IMAGE)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblCompanyPath(Base):
    __tablename__ = 'tbl_CompanyPath'
    __table_args__ = (
        PrimaryKeyConstraint('companyId', name='PK__tbl_Comp__AD5459903B36AB95'),
        Index('IX_tbl_CompanyPath', 'isDefault', mssql_clustered=False)
    )

    companyId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    companyName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    companyPath: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblContraDetails(Base):
    __tablename__ = 'tbl_ContraDetails'
    __table_args__ = (
        PrimaryKeyConstraint('contraDetailsId', name='PK__tbl_Cont__4D096E75632F8E56'),
    )

    contraDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    contraMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblContraMaster(Base):
    __tablename__ = 'tbl_ContraMaster'
    __table_args__ = (
        PrimaryKeyConstraint('contraMasterId', name='PK__tbl_Cont__0B964F325F5EFD72'),
    )

    contraMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    type: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblCounter(Base):
    __tablename__ = 'tbl_Counter'
    __table_args__ = (
        PrimaryKeyConstraint('counterId', name='PK__tbl_Coun__08A9D0236497E884'),
    )

    counterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    counterName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblCreditCardType(Base):
    __tablename__ = 'tbl_CreditCardType'
    __table_args__ = (
        PrimaryKeyConstraint('creditCardType', name='PK_tbl_CreditCardType'),
    )

    creditCardType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    creditCardTypeName: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))


class TblCreditNoteDetails(Base):
    __tablename__ = 'tbl_CreditNoteDetails'
    __table_args__ = (
        PrimaryKeyConstraint('creditNoteDetailsId', name='PK__tbl_Cred__3A8A913E10F65906'),
    )

    creditNoteDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    creditNoteMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblCreditNoteMaster(Base):
    __tablename__ = 'tbl_CreditNoteMaster'
    __table_args__ = (
        PrimaryKeyConstraint('creditNoteMasterId', name='PK__tbl_Cred__DDC597880D25C822'),
    )

    creditNoteMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))


class TblCurrency(Base):
    __tablename__ = 'tbl_Currency'
    __table_args__ = (
        PrimaryKeyConstraint('currencyId', name='PK__tbl_Curr__DAF0B20A592635D8'),
        Index('IsDefault', 'isDefault', mssql_clustered=False)
    )

    currencyId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    currencySymbol: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    currencyName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    subunitName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    noOfDecimalPlaces: Mapped[Optional[int]] = mapped_column(Integer)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_CurrencyToCopy = Table(
    'tbl_CurrencyToCopy', Base.metadata,
    Column('currencyId', Numeric(18, 0), nullable=False),
    Column('currencySymbol', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('currencyName', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('subunitName', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('noOfDecimalPlaces', Integer),
    Column('narration', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('isDefault', Boolean),
    Column('extraDate', DateTime),
    Column('extra1', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('extra2', String(collation='SQL_Latin1_General_CP1_CI_AS'))
)


class TblCustomerTariff(Base):
    __tablename__ = 'tbl_CustomerTariff'
    __table_args__ = (
        PrimaryKeyConstraint('customerTariffId', name='PK_tbl_CustomerTariff'),
    )

    customerTariffId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    customerTariff: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
    customer: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    dailyRent: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    weeklyRent: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    monthlyRent: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    dailyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    weeklyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    monthlyCDW: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    dailyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    weeklyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    monthlyPAI: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    dailyDriverCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    excessKMcharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    excessInscharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    dailyAdditionalDriverCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    weeklyAdditionalDriverCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    monthlyAdditionalDriverCharges: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    isDiscountable: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblCustomerType(Base):
    __tablename__ = 'tbl_CustomerType'
    __table_args__ = (
        PrimaryKeyConstraint('customerType', name='PK_tbl_CustomerType'),
    )

    customerType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    customerTypeName: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblDailyAttendanceDetails(Base):
    __tablename__ = 'tbl_DailyAttendanceDetails'
    __table_args__ = (
        PrimaryKeyConstraint('dailyAttendanceDetailsId', name='PK__tbl_Dail__990F6D9656E8E7AB'),
    )

    dailyAttendanceDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    dailyAttendanceMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    status: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDailyAttendanceMaster(Base):
    __tablename__ = 'tbl_DailyAttendanceMaster'
    __table_args__ = (
        PrimaryKeyConstraint('dailyAttendanceMasterId', name='PK__tbl_Dail__6FC4FA94531856C7'),
    )

    dailyAttendanceMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDailySalaryVoucherDetails(Base):
    __tablename__ = 'tbl_DailySalaryVoucherDetails'
    __table_args__ = (
        PrimaryKeyConstraint('dailySalaryVoucherDetailsId', name='PK__tbl_Dail__031176C94F47C5E3'),
    )

    dailySalaryVoucherDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    dailySalaryVoucherMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    wage: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    status: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDailySalaryVoucherMaster(Base):
    __tablename__ = 'tbl_DailySalaryVoucherMaster'
    __table_args__ = (
        PrimaryKeyConstraint('dailySalaryVoucherMasterId', name='PK_tbl_DailySalaryVoucherMaster'),
    )

    dailySalaryVoucherMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    salaryDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblDebitNoteDetails(Base):
    __tablename__ = 'tbl_DebitNoteDetails'
    __table_args__ = (
        PrimaryKeyConstraint('debitNoteDetailsId', name='PK__tbl_Debi__42220582469E3CA0'),
    )

    debitNoteDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    debitNoteMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblDebitNoteMaster(Base):
    __tablename__ = 'tbl_DebitNoteMaster'
    __table_args__ = (
        PrimaryKeyConstraint('debitNoteMasterId', name='PK__tbl_Debi__1229ABA914C6E9EA'),
    )

    debitNoteMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblDeliveryNoteDetails(Base):
    __tablename__ = 'tbl_DeliveryNoteDetails'
    __table_args__ = (
        PrimaryKeyConstraint('deliveryNoteDetailsId', name='PK__tbl_Deli__A9A4649E51CFF82A'),
    )

    deliveryNoteDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    deliveryNoteMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    orderDetails1Id: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitConversionId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    quotationDetails1Id: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rackId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    slNo: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDeliveryNoteMaster(Base):
    __tablename__ = 'tbl_DeliveryNoteMaster'
    __table_args__ = (
        PrimaryKeyConstraint('deliveryNoteMasterId', name='PK__tbl_Deli__72FF880F4DFF6746'),
    )

    deliveryNoteMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    orderMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    pricinglevelId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    lrNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    transportationCompany: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    quotationMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDesignation(Base):
    __tablename__ = 'tbl_Designation'
    __table_args__ = (
        PrimaryKeyConstraint('designationId', name='PK__tbl_Desi__197CE32A30C33EC3'),
    )

    designationId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    designationName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    leaveDays: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    advanceAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    salesMan: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblDetails(Base):
    __tablename__ = 'tbl_Details'
    __table_args__ = (
        PrimaryKeyConstraint('detailsId', name='PK_tbl_Details'),
        Index('IX_tbl_Details', 'masterId', mssql_clustered=False)
    )

    detailsId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    masterId: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    text_: Mapped[Optional[str]] = mapped_column('text', String(collation='SQL_Latin1_General_CP1_CI_AS'))
    row: Mapped[Optional[int]] = mapped_column(Integer)
    columns: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    dbf: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    DorH: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    repeat: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    align: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    repeatAll: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    footerRepeatAll: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    textWrap: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    wrapLineCount: Mapped[Optional[int]] = mapped_column(Integer)
    extraFieldName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    fieldsForExtra: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDetailsCopy(Base):
    __tablename__ = 'tbl_DetailsCopy'
    __table_args__ = (
        PrimaryKeyConstraint('detailsId', name='PK_tbl_DetailsCopy'),
        Index('IX_tbl_DetailsCopy', 'masterId', mssql_clustered=False)
    )

    detailsId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    masterId: Mapped[Optional[int]] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    text_: Mapped[Optional[str]] = mapped_column('text', String(collation='SQL_Latin1_General_CP1_CI_AS'))
    row: Mapped[Optional[int]] = mapped_column(Integer)
    columns: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    dbf: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    DorH: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    repeat: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    align: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    repeatAll: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    footerRepeatAll: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    textWrap: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    wrapLineCount: Mapped[Optional[int]] = mapped_column(Integer)
    extraFieldName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    fieldsForExtra: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblDrivingLicenseType(Base):
    __tablename__ = 'tbl_DrivingLicenseType'
    __table_args__ = (
        PrimaryKeyConstraint('licenseType', name='PK_tbl_DrivingLicenseType'),
    )

    licenseType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    licenseTypeName: Mapped[Optional[str]] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))


class TblEmirate(Base):
    __tablename__ = 'tbl_Emirate'
    __table_args__ = (
        PrimaryKeyConstraint('EmirateId', name='PK_tbl_Emirate'),
    )

    EmirateId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    EmirateName: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblEmployee(Base):
    __tablename__ = 'tbl_Employee'
    __table_args__ = (
        PrimaryKeyConstraint('employeeId', name='PK__tbl_Empl__C134C9C125518C17'),
    )

    employeeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    designationId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    employeeCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    dob: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    maritalStatus: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    gender: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    qualification: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    address: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    phoneNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    mobileNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    email: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    joiningDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    terminationDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    bloodGroup: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    passportNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    passportExpiryDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    labourCardNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    labourCardExpiryDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    visaNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    visaExpiryDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    salaryType: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    dailyWage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 5))
    bankName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    branchName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    bankAccountNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    branchCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    panNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    pfNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    esiNumber: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    defaultPackageId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblExchangeRate(Base):
    __tablename__ = 'tbl_ExchangeRate'
    __table_args__ = (
        PrimaryKeyConstraint('exchangeRateId', name='PK__tbl_Exch__DE88B8415CF6C6BC'),
    )

    exchangeRateId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    currencyId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblFields(Base):
    __tablename__ = 'tbl_Fields'
    __table_args__ = (
        PrimaryKeyConstraint('fieldId', name='PK_tbl_Fields'),
        Index('IX_tbl_Fields', 'formId', mssql_clustered=False)
    )

    fieldId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formId: Mapped[Optional[int]] = mapped_column(Integer)
    fieldName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblFieldsCopy(Base):
    __tablename__ = 'tbl_FieldsCopy'
    __table_args__ = (
        PrimaryKeyConstraint('fieldId', name='PK_tbl_FieldsCopy'),
        Index('IX_tbl_FieldsCopy', 'formId', mssql_clustered=False)
    )

    fieldId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formId: Mapped[Optional[int]] = mapped_column(Integer)
    fieldName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblFinanceDetail(Base):
    __tablename__ = 'tbl_FinanceDetail'
    __table_args__ = (
        PrimaryKeyConstraint('financeDetailId', name='PK_tbl_FinanceDetail'),
    )

    financeDetailId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    financeHeaderId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    EMIno: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    PDCId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bankId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    EMIamount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    chequeNo: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))
    EMIDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    isPaid: Mapped[Optional[bool]] = mapped_column(Boolean)
    createdBy: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    createdDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblFinanceHeader(Base):
    __tablename__ = 'tbl_FinanceHeader'
    __table_args__ = (
        PrimaryKeyConstraint('financeHeaderId', name='PK_tbl_FinanceHeader'),
    )

    financeHeaderId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    financeNo: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    docDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    purchaseMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    purchaseDetailId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    assetID: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    purchasedAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    loanAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    monthlyAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    NoOfInstallments: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bankId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNoFrom: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDateFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    createdBy: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    createdDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblFinancialYear(Base):
    __tablename__ = 'tbl_FinancialYear'
    __table_args__ = (
        PrimaryKeyConstraint('financialYearId', name='PK__tbl_Fina__FE30A41137661AB1'),
    )

    financialYearId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    fromDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    toDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblFinancialYearMonthStatus(Base):
    __tablename__ = 'tbl_FinancialYearMonthStatus'
    __table_args__ = (
        PrimaryKeyConstraint('Id', name='PK_tbl_FinancialYearMonthStatus'),
    )

    Id: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    monthId: Mapped[Optional[int]] = mapped_column(Integer)
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    isEnabled: Mapped[Optional[bool]] = mapped_column(Boolean)
    updatedOn: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblFixedAssetCategory(Base):
    __tablename__ = 'tbl_FixedAssetCategory'
    __table_args__ = (
        PrimaryKeyConstraint('faCategoryId', name='PK_tbl_FixedAssetCategory'),
    )

    faCategoryId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    faCategoryName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    faCategoryCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    faDeprMethod: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    faDeprPeriod: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    assetLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    deprLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    accDeprLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    gainOnDisposalLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    lossOnDisposalLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    scrapOnDisposalLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblFixedAssetDeprSchedule(Base):
    __tablename__ = 'tbl_FixedAssetDeprSchedule'
    __table_args__ = (
        PrimaryKeyConstraint('depreciationSchedule', name='PK_FixedAssetDeprSchedule'),
    )

    depreciationSchedule: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    fixedAssetId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    deprLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    accDeprLedgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    periodFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    periodTo: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 4))
    deprAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 4))
    balanceAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 4))
    createdDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblFixedAssetDepreciationDetail(Base):
    __tablename__ = 'tbl_FixedAssetDepreciationDetail'
    __table_args__ = (
        PrimaryKeyConstraint('depreciationDetail', name='PK_tbl_FixedAssetDepreciationDetail'),
    )

    depreciationDetail: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    depreciationHeader: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    Vehicle: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblFixedAssetDepreciationHeader(Base):
    __tablename__ = 'tbl_FixedAssetDepreciationHeader'
    __table_args__ = (
        PrimaryKeyConstraint('depreciationHeader', name='PK_tbl_FixedAssetDepreciationHeader'),
    )

    depreciationHeader: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    depreciationSchedule: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    generatedMonth: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYear: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblFixedAssetDisposalDetails(Base):
    __tablename__ = 'tbl_FixedAssetDisposalDetails'
    __table_args__ = (
        PrimaryKeyConstraint('DisposalId', name='PK_tbl_FixedAssetDisposalDetails'),
    )

    DisposalId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    FixedAssetId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    DisposalType: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    SellingTo: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    SellingPrice: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    SellingDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    AccDepreciation: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    BookValue: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    PendingDepreciation: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    NetBookValue: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    NetProfitOrLoss: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    CreatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    CreatedBy: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblFixedAssetDisposalType(Base):
    __tablename__ = 'tbl_FixedAssetDisposalType'
    __table_args__ = (
        PrimaryKeyConstraint('AssetDisposalTypeId', name='PK_tbl_FixedAssetDisposalType'),
    )

    AssetDisposalTypeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    AssetDisposalType: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblFixedAssetMaster(Base):
    __tablename__ = 'tbl_FixedAssetMaster'
    __table_args__ = (
        PrimaryKeyConstraint('fixedAssetId', name='PK_tbl_FixedAssetMaster'),
    )

    fixedAssetId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    fixedAssetCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    fixedAssetCategory: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    fixedAssetDescription: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    fixedAssetDeprMethod: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    fixedAssetDeprPeriod: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    fixedAssetVehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblForm(Base):
    __tablename__ = 'tbl_Form'
    __table_args__ = (
        PrimaryKeyConstraint('formId', name='PK_tbl_Form'),
    )

    formId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    tableName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblFormCopy(Base):
    __tablename__ = 'tbl_FormCopy'
    __table_args__ = (
        PrimaryKeyConstraint('formId', name='PK_tbl_FormCopy'),
    )

    formId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblGodown(Base):
    __tablename__ = 'tbl_Godown'
    __table_args__ = (
        PrimaryKeyConstraint('godownId', name='PK__tbl_Godo__14F1AFAB51851410'),
    )

    godownId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    godownName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblHoliday(Base):
    __tablename__ = 'tbl_Holiday'
    __table_args__ = (
        PrimaryKeyConstraint('holidayId', name='PK__tbl_Holi__EB855CEF29221CFB'),
    )

    holidayId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    holidayName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblJournalDetails(Base):
    __tablename__ = 'tbl_JournalDetails'
    __table_args__ = (
        PrimaryKeyConstraint('journalDetailsId', name='PK__tbl_Jour__3C76D92F764262CA'),
    )

    journalDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    journalMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    Vehicle: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblJournalMaster(Base):
    __tablename__ = 'tbl_JournalMaster'
    __table_args__ = (
        PrimaryKeyConstraint('journalMasterId', name='PK__tbl_Jour__90D22FBE7271D1E6'),
    )

    journalMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblLedgerPosting(Base):
    __tablename__ = 'tbl_LedgerPosting'
    __table_args__ = (
        PrimaryKeyConstraint('ledgerPostingId', name='PK__tbl_Ledg__730FE2D769FBBC1F'),
        Index('IND1_tbl_LedgerPosting', 'date', 'voucherTypeId', mssql_clustered=False, mssql_include=['ledgerId', 'debit', 'credit'])
    )

    ledgerPostingId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    detailsId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    yearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_MainMenu = Table(
    'tbl_MainMenu', Base.metadata,
    Column('menuId', Integer, Identity(start=1, increment=1), nullable=False),
    Column('menuName', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
)


class TblMaster(Base):
    __tablename__ = 'tbl_Master'
    __table_args__ = (
        PrimaryKeyConstraint('masterId', name='PK_tbl_Master'),
    )

    masterId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formName: Mapped[Optional[int]] = mapped_column(Integer)
    isTwoLineForHedder: Mapped[Optional[bool]] = mapped_column(Boolean)
    isTwoLineForDetails: Mapped[Optional[bool]] = mapped_column(Boolean)
    pageSize1: Mapped[Optional[int]] = mapped_column(Integer)
    pageSizeOther: Mapped[Optional[int]] = mapped_column(Integer)
    blankLneForFooter: Mapped[Optional[int]] = mapped_column(Integer)
    footerLocation: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    lineCountBetweenTwo: Mapped[Optional[int]] = mapped_column(Integer)
    pitch: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    condensed: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    lineCountAfterPrint: Mapped[Optional[int]] = mapped_column(Integer)


class TblMasterCopy(Base):
    __tablename__ = 'tbl_MasterCopy'
    __table_args__ = (
        PrimaryKeyConstraint('masterId', name='PK_tbl_MasterCopy'),
    )

    masterId: Mapped[int] = mapped_column(Integer, primary_key=True)
    formName: Mapped[Optional[int]] = mapped_column(Integer)
    isTwoLineForHedder: Mapped[Optional[bool]] = mapped_column(Boolean)
    isTwoLineForDetails: Mapped[Optional[bool]] = mapped_column(Boolean)
    pageSize1: Mapped[Optional[int]] = mapped_column(Integer)
    pageSizeOther: Mapped[Optional[int]] = mapped_column(Integer)
    blankLneForFooter: Mapped[Optional[int]] = mapped_column(Integer)
    footerLocation: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    lineCountBetweenTwo: Mapped[Optional[int]] = mapped_column(Integer)
    pitch: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    condensed: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    lineCountAfterPrint: Mapped[Optional[int]] = mapped_column(Integer)


class TblModelNo(Base):
    __tablename__ = 'tbl_ModelNo'
    __table_args__ = (
        PrimaryKeyConstraint('modelNoId', name='PK__tbl_Mode__8458D8C94DB4832C'),
    )

    modelNoId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    modelNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblMonthlySalary(Base):
    __tablename__ = 'tbl_MonthlySalary'
    __table_args__ = (
        PrimaryKeyConstraint('monthlySalaryId', name='PK__tbl_Mont__DD79B8643C34F16F'),
    )

    monthlySalaryId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salaryMonth: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblMonthlySalaryDetails(Base):
    __tablename__ = 'tbl_MonthlySalaryDetails'
    __table_args__ = (
        PrimaryKeyConstraint('monthlySalaryDetailsId', name='PK__tbl_Mont__04252B5040058253'),
    )

    monthlySalaryDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    salaryPackageId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    monthlySalaryId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblMonths(Base):
    __tablename__ = 'tbl_Months'
    __table_args__ = (
        PrimaryKeyConstraint('month', name='PK_tbl_Months'),
    )

    month: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    monthName: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblNationality(Base):
    __tablename__ = 'tbl_Nationality'
    __table_args__ = (
        PrimaryKeyConstraint('nationality', name='PK_tbl_Nationality'),
    )

    nationality: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    nationalityName: Mapped[Optional[str]] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))


class TblPDCClearanceMaster(Base):
    __tablename__ = 'tbl_PDCClearanceMaster'
    __table_args__ = (
        PrimaryKeyConstraint('PDCClearanceMasterId', name='PK__tbl_PDCC__D88D38E00955373E'),
    )

    PDCClearanceMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    type: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    againstId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    status: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPDCPayableMaster(Base):
    __tablename__ = 'tbl_PDCPayableMaster'
    __table_args__ = (
        PrimaryKeyConstraint('pdcPayableMasterId', name='PK__tbl_PDCP__D5E696DE01B41576'),
    )

    pdcPayableMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bankId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPDCReceivableMaster(Base):
    __tablename__ = 'tbl_PDCReceivableMaster'
    __table_args__ = (
        PrimaryKeyConstraint('pdcReceivableMasterId', name='PK__tbl_PDCR__A14C5E250584A65A'),
    )

    pdcReceivableMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bankId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPartyBalance(Base):
    __tablename__ = 'tbl_PartyBalance'
    __table_args__ = (
        PrimaryKeyConstraint('partyBalanceId', name='PK__tbl_Part__69824BB71C680BB2'),
        Index('IND1_tbl_PartyBalance', 'date', mssql_clustered=False, mssql_include=['ledgerId', 'againstVoucherTypeId', 'againstVoucherNo', 'againstInvoiceNo', 'debit', 'credit', 'extra1']),
        Index('IND2_tbl_PartyBalance', 'ledgerId', 'date', mssql_clustered=False, mssql_include=['againstVoucherTypeId', 'againstVoucherNo', 'againstInvoiceNo', 'debit', 'credit', 'extra1'])
    )

    partyBalanceId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    againstVoucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    againstVoucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    againstInvoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    referenceType: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    debit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    credit: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    creditPeriod: Mapped[Optional[int]] = mapped_column(Integer)
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    contractId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


t_tbl_PartyBalance_Unposted = Table(
    'tbl_PartyBalance_Unposted', Base.metadata,
    Column('partyBalanceId', Numeric(18, 0), Identity(start=1, increment=1), nullable=False),
    Column('date', DateTime),
    Column('ledgerId', Numeric(18, 0)),
    Column('voucherTypeId', Numeric(18, 0)),
    Column('voucherNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('againstVoucherTypeId', Numeric(18, 0)),
    Column('againstVoucherNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('invoiceNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('againstInvoiceNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('referenceType', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('debit', DECIMAL(18, 5)),
    Column('credit', DECIMAL(18, 5)),
    Column('creditPeriod', Integer),
    Column('exchangeRateId', Numeric(18, 0)),
    Column('financialYearId', Numeric(18, 0)),
    Column('extraDate', DateTime),
    Column('extra1', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('extra2', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('contractId', Numeric(18, 0))
)


class TblPayHead(Base):
    __tablename__ = 'tbl_PayHead'
    __table_args__ = (
        PrimaryKeyConstraint('payHeadId', name='PK__tbl_PayH__1BAC6FBD2CF2ADDF'),
    )

    payHeadId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    payHeadName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    type: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPaymentDetails(Base):
    __tablename__ = 'tbl_PaymentDetails'
    __table_args__ = (
        PrimaryKeyConstraint('paymentDetailsId', name='PK__tbl_Paym__2549CB8A6AD0B01E'),
    )

    paymentDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    paymentMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    Vehicle: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblPaymentMaster(Base):
    __tablename__ = 'tbl_PaymentMaster'
    __table_args__ = (
        PrimaryKeyConstraint('paymentMasterId', name='PK__tbl_Paym__F6D0847167001F3A'),
    )

    paymentMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblPaymentMode(Base):
    __tablename__ = 'tbl_PaymentMode'
    __table_args__ = (
        PrimaryKeyConstraint('paymentMode', name='PK_tbl_PaymentMode'),
    )

    paymentMode: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    paymentModeName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPhysicalStockDetails(Base):
    __tablename__ = 'tbl_PhysicalStockDetails'
    __table_args__ = (
        PrimaryKeyConstraint('physicalStockDetailsId', name='PK__tbl_Phys__A94165330ED9066A'),
    )

    physicalStockDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    physicalStockMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitConversionId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rackId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    slno: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPhysicalStockMaster(Base):
    __tablename__ = 'tbl_PhysicalStockMaster'
    __table_args__ = (
        PrimaryKeyConstraint('physicalStockMasterId', name='PK__tbl_Phys__7367DF7A0B087586'),
    )

    physicalStockMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPrepaymentSchedule(Base):
    __tablename__ = 'tbl_PrepaymentSchedule'
    __table_args__ = (
        PrimaryKeyConstraint('prepaymentSchedule', name='PK_tbl_PrepaymentSchedule'),
    )

    prepaymentSchedule: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    prepaymentLedger: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    expenseLedger: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    periodFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    periodTo: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    prepaidAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    createdDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblPrepayments(Base):
    __tablename__ = 'tbl_Prepayments'
    __table_args__ = (
        PrimaryKeyConstraint('prepayment', name='PK_tbl_Prepayments'),
    )

    prepayment: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    prepaymentSchedule: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    generatedAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 2))
    generatedMonth: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYear: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    createdDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblPriceList(Base):
    __tablename__ = 'tbl_PriceList'
    __table_args__ = (
        PrimaryKeyConstraint('pricelistId', name='PK__tbl_Pric__81BD4B85278EDA44'),
        Index('IX_tbl_PriceList', 'batchId', mssql_clustered=False),
        Index('IX_tbl_PriceList_1', 'pricinglevelId', mssql_clustered=False),
        Index('IX_tbl_PriceList_2', 'productId', mssql_clustered=False),
        Index('IX_tbl_PriceList_3', 'unitId', mssql_clustered=False),
        Index('IX_tbl_PriceList_4', 'batchId', 'productId', 'pricinglevelId', mssql_clustered=False)
    )

    pricelistId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    pricinglevelId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPricingLevel(Base):
    __tablename__ = 'tbl_PricingLevel'
    __table_args__ = (
        PrimaryKeyConstraint('pricinglevelId', name='PK__tbl_Pric__84E896EA23BE4960'),
    )

    pricinglevelId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    pricinglevelName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPrivilege(Base):
    __tablename__ = 'tbl_Privilege'
    __table_args__ = (
        PrimaryKeyConstraint('privilegeId', name='PK_tbl_Privilege'),
    )

    privilegeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    formName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    action: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    roleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    exatra1: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblProduct(Base):
    __tablename__ = 'tbl_Product'
    __table_args__ = (
        PrimaryKeyConstraint('productId', name='PK__tbl_Prod__2D10D16A1FEDB87C'),
    )

    productId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    productCode: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    productName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    groupId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    brandId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    sizeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    modelNoId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxapplicableOn: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    purchaseRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    salesRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    mrp: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    minimumStock: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    maximumStock: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    reorderLevel: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rackId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    isallowBatch: Mapped[Optional[bool]] = mapped_column(Boolean)
    ismultipleunit: Mapped[Optional[bool]] = mapped_column(Boolean)
    isBom: Mapped[Optional[bool]] = mapped_column(Boolean)
    isopeningstock: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    isInventoryItem: Mapped[Optional[bool]] = mapped_column(Boolean)
    isshowRemember: Mapped[Optional[bool]] = mapped_column(Boolean)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    partNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblProductGroup(Base):
    __tablename__ = 'tbl_ProductGroup'
    __table_args__ = (
        PrimaryKeyConstraint('groupId', name='PK__tbl_Prod__88C1034D10AB74EC'),
        Index('IX_tbl_ProductGroup', 'groupUnder', mssql_clustered=False)
    )

    groupId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    groupName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    groupUnder: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblPurchaseBillTax(Base):
    __tablename__ = 'tbl_PurchaseBillTax'
    __table_args__ = (
        PrimaryKeyConstraint('purchaseBillTaxId', name='PK__tbl_Purc__1B87331A27D9BE5E'),
    )

    purchaseBillTaxId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    purchaseMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPurchaseDetails(Base):
    __tablename__ = 'tbl_PurchaseDetails'
    __table_args__ = (
        PrimaryKeyConstraint('purchaseDetailsId', name='PK__tbl_Purc__67AF05292BAA4F42'),
    )

    purchaseDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    purchaseMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    orderDetailsId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    vehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grossAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    slNo: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPurchaseMaster(Base):
    __tablename__ = 'tbl_PurchaseMaster'
    __table_args__ = (
        PrimaryKeyConstraint('purchaseMasterId', name='PK__tbl_Purc__9D353EFC20389C96'),
    )

    purchaseMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    vendorInvoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    vendorInvoiceDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    creditPeriod: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    purchaseAccount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    purchaseOrderMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalTax: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    billDiscount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grandTotal: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    lrNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    transportationCompany: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)
    isMiscPurchase: Mapped[Optional[bool]] = mapped_column(Boolean)
    isFaPurchase: Mapped[Optional[bool]] = mapped_column(Boolean)
    isInvPurchase: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblPurchaseOrderDetails(Base):
    __tablename__ = 'tbl_PurchaseOrderDetails'
    __table_args__ = (
        PrimaryKeyConstraint('purchaseOrderDetailsId', name='PK__tbl_Purc__BDE1867C70547F4A'),
    )

    purchaseOrderDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    purchaseOrderMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    itemDescription: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    vehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    slNo: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblPurchaseOrderMaster(Base):
    __tablename__ = 'tbl_PurchaseOrderMaster'
    __table_args__ = (
        PrimaryKeyConstraint('purchaseOrderMasterId', name='PK__tbl_Purc__DAD68F806C83EE66'),
    )

    purchaseOrderMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    dueDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    cancelled: Mapped[Optional[bool]] = mapped_column(Boolean)
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblQuickLaunchItems(Base):
    __tablename__ = 'tbl_QuickLaunchItems'
    __table_args__ = (
        PrimaryKeyConstraint('quickLaunchItemsId', name='PK_tbl_QuickLaunchItems'),
    )

    quickLaunchItemsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    itemsName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    status: Mapped[Optional[bool]] = mapped_column(Boolean)
    extra1: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblRack(Base):
    __tablename__ = 'tbl_Rack'
    __table_args__ = (
        PrimaryKeyConstraint('rackId', name='PK__tbl_Rack__B34912495555A4F4'),
    )

    rackId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    rackName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblReceiptDetails(Base):
    __tablename__ = 'tbl_ReceiptDetails'
    __table_args__ = (
        PrimaryKeyConstraint('receiptDetailsId', name='PK__tbl_Rece__C0FF33FB6EA14102'),
    )

    receiptDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    receiptMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    chequeNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    chequeDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblReceiptMaster(Base):
    __tablename__ = 'tbl_ReceiptMaster'
    __table_args__ = (
        PrimaryKeyConstraint('receiptMasterId', name='PK__tbl_Rece__B974C2984925A390'),
    )

    receiptMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblReminder(Base):
    __tablename__ = 'tbl_Reminder'
    __table_args__ = (
        PrimaryKeyConstraint('reminderId', name='PK_tbl_Reminder'),
    )

    reminderId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    fromDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    toDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    remindAbout: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblRole(Base):
    __tablename__ = 'tbl_Role'
    __table_args__ = (
        PrimaryKeyConstraint('roleId', name='PK_tbl_Role'),
    )

    roleId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    role: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblRoute(Base):
    __tablename__ = 'tbl_Route'
    __table_args__ = (
        PrimaryKeyConstraint('routeId', name='PK_tbl_Route'),
        Index('IX_tbl_Route', 'areaId', mssql_clustered=False)
    )

    routeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    routeName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    areaId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalaryPackage(Base):
    __tablename__ = 'tbl_SalaryPackage'
    __table_args__ = (
        PrimaryKeyConstraint('salaryPackageId', name='PK__tbl_Sala__B78BCF693493CFA7'),
    )

    salaryPackageId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salaryPackageName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalaryPackageDetails(Base):
    __tablename__ = 'tbl_SalaryPackageDetails'
    __table_args__ = (
        PrimaryKeyConstraint('salaryPackageDetailsId', name='PK__tbl_Sala__993415083864608B'),
    )

    salaryPackageDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salaryPackageId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    payHeadId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalaryVoucherDetails(Base):
    __tablename__ = 'tbl_SalaryVoucherDetails'
    __table_args__ = (
        PrimaryKeyConstraint('salaryVoucherDetailsId', name='PK__tbl_Sala__054D02EE47A6A41B'),
    )

    salaryVoucherDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salaryVoucherMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    bonus: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    deduction: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    advance: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    lop: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    salary: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    status: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalaryVoucherMaster(Base):
    __tablename__ = 'tbl_SalaryVoucherMaster'
    __table_args__ = (
        PrimaryKeyConstraint('salaryVoucherMasterId', name='PK__tbl_Sala__B363606243D61337'),
    )

    salaryVoucherMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    month: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    IsGenerated: Mapped[Optional[bool]] = mapped_column(Boolean)
    IsPaid: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblSalesBillTax(Base):
    __tablename__ = 'tbl_SalesBillTax'
    __table_args__ = (
        PrimaryKeyConstraint('salesBillTaxId', name='PK__tbl_Sale__3E4B1B27334B710A'),
    )

    salesBillTaxId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salesMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalesDetailItemType(Base):
    __tablename__ = 'tbl_SalesDetailItemType'
    __table_args__ = (
        PrimaryKeyConstraint('ItemType', name='PK_tbl_SalesDetailItemType'),
    )

    ItemType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ItemTypeName: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    ItemTypeNameArabic: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    VoucherType: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    IsActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    TaxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    updatedDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    updatedBy: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblSalesDetails(Base):
    __tablename__ = 'tbl_SalesDetails'
    __table_args__ = (
        PrimaryKeyConstraint('salesDetailsId', name='PK__tbl_Sale__541370DA371C01EE'),
    )

    salesDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salesMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    itemTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    vehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    discount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grossAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    netAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    slNo: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_SalesDetails_Deleted = Table(
    'tbl_SalesDetails_Deleted', Base.metadata,
    Column('salesDetailsId', Numeric(18, 0), nullable=False),
    Column('salesMasterId', Numeric(18, 0)),
    Column('itemTypeId', Numeric(18, 0)),
    Column('vehicleId', Numeric(18, 0)),
    Column('description', Unicode(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('qty', DECIMAL(18, 5)),
    Column('rate', DECIMAL(18, 5)),
    Column('unitId', Numeric(18, 0)),
    Column('discount', DECIMAL(18, 5)),
    Column('taxId', Numeric(18, 0)),
    Column('taxAmount', DECIMAL(18, 5)),
    Column('grossAmount', DECIMAL(18, 5)),
    Column('netAmount', DECIMAL(18, 5)),
    Column('amount', DECIMAL(18, 5)),
    Column('slNo', Integer),
    Column('extraDate', DateTime),
    Column('extra1', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('extra2', String(collation='SQL_Latin1_General_CP1_CI_AS'))
)


t_tbl_SalesInvoiceBillingType = Table(
    'tbl_SalesInvoiceBillingType', Base.metadata,
    Column('invoiceTypeId', Integer, Identity(start=1, increment=1), nullable=False),
    Column('invoiceTypeName', String(20, 'SQL_Latin1_General_CP1_CI_AS'))
)


class TblSalesMaster(Base):
    __tablename__ = 'tbl_SalesMaster'
    __table_args__ = (
        PrimaryKeyConstraint('salesMasterId', name='PK__tbl_Sale__036BDC222F7AE026'),
    )

    salesMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    creditPeriod: Mapped[int] = mapped_column(Integer, nullable=False)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    lpoNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    salesAccount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    customerName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    additionalCost: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    billDiscount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grandTotal: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    POS: Mapped[Optional[bool]] = mapped_column(Boolean)
    counterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    contractId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    contractRefNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    trafficFineNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)
    vehicleNos: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_SalesMaster_Deleted = Table(
    'tbl_SalesMaster_Deleted', Base.metadata,
    Column('salesMasterId', Numeric(18, 0), nullable=False),
    Column('voucherNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('invoiceNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('voucherTypeId', Numeric(18, 0)),
    Column('suffixPrefixId', Numeric(18, 0)),
    Column('date', DateTime),
    Column('creditPeriod', Integer, nullable=False),
    Column('lpoNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('ledgerId', Numeric(18, 0)),
    Column('employeeId', Numeric(18, 0)),
    Column('salesAccount', Numeric(18, 0)),
    Column('narration', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('customerName', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('exchangeRateId', Numeric(18, 0)),
    Column('taxAmount', DECIMAL(18, 5)),
    Column('additionalCost', DECIMAL(18, 5)),
    Column('billDiscount', DECIMAL(18, 5)),
    Column('grandTotal', DECIMAL(18, 5)),
    Column('totalAmount', DECIMAL(18, 5)),
    Column('userId', Numeric(18, 0)),
    Column('POS', Boolean),
    Column('counterId', Numeric(18, 0)),
    Column('financialYearId', Numeric(18, 0)),
    Column('extraDate', DateTime),
    Column('extra1', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('extra2', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('contractId', Numeric(18, 0)),
    Column('contractRefNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('trafficFineNo', String(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('isPosted', Boolean),
    Column('vehicleNos', String(collation='SQL_Latin1_General_CP1_CI_AS'))
)


class TblSalesQuotationDetails(Base):
    __tablename__ = 'tbl_SalesQuotationDetails'
    __table_args__ = (
        PrimaryKeyConstraint('quotationDetailsId', name='PK__tbl_Sale__5875C12861123BBA'),
    )

    quotationDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    quotationMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    itemDescription: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    slno: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalesQuotationMaster(Base):
    __tablename__ = 'tbl_SalesQuotationMaster'
    __table_args__ = (
        PrimaryKeyConstraint('quotationMasterId', name='PK__tbl_Sale__8D6FDEBD5D41AAD6'),
    )

    quotationMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    pricinglevelId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    approved: Mapped[Optional[bool]] = mapped_column(Boolean)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblSalesReturnBillTax(Base):
    __tablename__ = 'tbl_SalesReturnBillTax'
    __table_args__ = (
        PrimaryKeyConstraint('salesReturnBillTaxId', name='PK__tbl_Sale__5BD749863EBD23B6'),
    )

    salesReturnBillTaxId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salesReturnMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalesReturnDetails(Base):
    __tablename__ = 'tbl_SalesReturnDetails'
    __table_args__ = (
        PrimaryKeyConstraint('salesReturnDetailsId', name='PK__tbl_Sale__0C252C0D428DB49A'),
    )

    salesReturnDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    salesReturnMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    itemTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    vehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    description: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    discount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grossAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    netAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    salesDetailsId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    slNo: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSalesReturnMaster(Base):
    __tablename__ = 'tbl_SalesReturnMaster'
    __table_args__ = (
        PrimaryKeyConstraint('salesReturnMasterId', name='PK__tbl_Sale__DB499E433AEC92D2'),
    )

    salesReturnMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    salesMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    salesAccount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    discount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grandTotal: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isPosted: Mapped[Optional[bool]] = mapped_column(Boolean)


class TblService(Base):
    __tablename__ = 'tbl_Service'
    __table_args__ = (
        PrimaryKeyConstraint('serviceId', name='PK__tbl_Serv__455070DF70099B30'),
    )

    serviceId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    serviceName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    serviceCategoryId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblServiceCategory(Base):
    __tablename__ = 'tbl_ServiceCategory'
    __table_args__ = (
        PrimaryKeyConstraint('serviceCategoryId', name='PK__tbl_Serv__77EC43563AA1AEB8'),
    )

    serviceCategoryId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    categoryName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblServiceDetails(Base):
    __tablename__ = 'tbl_ServiceDetails'
    __table_args__ = (
        PrimaryKeyConstraint('serviceDetailsId', name='PK__tbl_Serv__E8F292C47DE38492'),
    )

    serviceDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    serviceMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    serviceId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    measure: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblServiceMaster(Base):
    __tablename__ = 'tbl_ServiceMaster'
    __table_args__ = (
        PrimaryKeyConstraint('serviceMasterId', name='PK__tbl_Serv__BF261C547A12F3AE'),
    )

    serviceMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    ledgerId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    totalAmount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    userId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    creditPeriod: Mapped[Optional[int]] = mapped_column(Integer)
    serviceAccount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    employeeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    customer: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    discount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    grandTotal: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))


class TblSettings(Base):
    __tablename__ = 'tbl_Settings'
    __table_args__ = (
        PrimaryKeyConstraint('settingsId', name='PK_tbl_Settings'),
    )

    settingsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    settingsName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    status: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSettingsToCopy(Base):
    __tablename__ = 'tbl_SettingsToCopy'
    __table_args__ = (
        PrimaryKeyConstraint('settingsId', name='PK_tbl_SettingsToCopy'),
    )

    settingsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    settingsName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    status: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSize(Base):
    __tablename__ = 'tbl_Size'
    __table_args__ = (
        PrimaryKeyConstraint('sizeId', name='PK__tbl_Size__55B1E55749E3F248'),
    )

    sizeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    size: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblStandardRate(Base):
    __tablename__ = 'tbl_StandardRate'
    __table_args__ = (
        PrimaryKeyConstraint('standardRateId', name='PK__tbl_Stan__F75A1E8460C757A0'),
        Index('IX_tbl_StandardRate', 'batchId', mssql_clustered=False),
        Index('IX_tbl_StandardRate_1', 'productId', mssql_clustered=False),
        Index('IX_tbl_StandardRate_2', 'unitId', mssql_clustered=False)
    )

    standardRateId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    applicableFrom: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    applicableTo: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblStockJournalDetails(Base):
    __tablename__ = 'tbl_StockJournalDetails'
    __table_args__ = (
        PrimaryKeyConstraint('stockJournalDetailsId', name='PK__tbl_Stoc__3224B9A70737E4A2'),
    )

    stockJournalDetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    stockJournalMasterId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    vehicleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    qty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitConversionId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rackId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    amount: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    consumptionOrProduction: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    slno: Mapped[Optional[int]] = mapped_column(Integer)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblStockJournalMaster(Base):
    __tablename__ = 'tbl_StockJournalMaster'
    __table_args__ = (
        PrimaryKeyConstraint('stockJournalMasterId', name='PK__tbl_Stoc__8B1D7000036753BE'),
    )

    stockJournalMasterId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffixPrefixId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    additionalCost: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    exchangeRateId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblStockPosting(Base):
    __tablename__ = 'tbl_StockPosting'
    __table_args__ = (
        PrimaryKeyConstraint('stockPostingId', name='PK__tbl_Stoc__CAEC17F7158603F9'),
    )

    stockPostingId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    voucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    invoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    batchId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    godownId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    rackId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    againstVoucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    againstInvoiceNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    againstVoucherNo: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    inwardQty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    outwardQty: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    financialYearId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblSuffixPrefix(Base):
    __tablename__ = 'tbl_SuffixPrefix'
    __table_args__ = (
        PrimaryKeyConstraint('suffixprefixId', name='PK__tbl_Suff__5876721373DA2C14'),
    )

    suffixprefixId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    fromDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    toDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    startIndex: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    prefix: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    suffix: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    widthOfNumericalPart: Mapped[Optional[int]] = mapped_column(Integer)
    prefillWithZero: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblTax(Base):
    __tablename__ = 'tbl_Tax'
    __table_args__ = (
        PrimaryKeyConstraint('taxId', name='PK__tbl_Tax__24D2883933008CF0'),
        Index('IX_tbl_Tax', 'applicableOn', mssql_clustered=False),
        Index('IX_tbl_Tax_1', 'taxId', mssql_clustered=False)
    )

    taxId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    taxName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    applicableOn: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    rate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    calculatingMode: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblTaxDetails(Base):
    __tablename__ = 'tbl_TaxDetails'
    __table_args__ = (
        PrimaryKeyConstraint('taxdetailsId', name='PK__tbl_TaxD__B3B4F7A536D11DD4'),
        Index('grp01', 'selectedtaxId', 'taxId', 'taxdetailsId', mssql_clustered=False),
        Index('selectedtaxId', 'selectedtaxId', mssql_clustered=False),
        Index('taxId', 'taxId', mssql_clustered=False)
    )

    taxdetailsId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    selectedtaxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_TransactionHistory = Table(
    'tbl_TransactionHistory', Base.metadata,
    Column('Id', Numeric(18, 0), Identity(start=1, increment=1), nullable=False),
    Column('taskName', Unicode(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('amount', DECIMAL(18, 5)),
    Column('voucherTypeId', Numeric(18, 0)),
    Column('voucherNo', Unicode(collation='SQL_Latin1_General_CP1_CI_AS')),
    Column('updatedBy', Numeric(18, 0)),
    Column('updatedOn', DateTime)
)


class TblUnit(Base):
    __tablename__ = 'tbl_Unit'
    __table_args__ = (
        PrimaryKeyConstraint('unitId', name='PK__tbl_Unit__55D792354242D080'),
    )

    unitId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    unitName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    noOfDecimalplaces: Mapped[Optional[int]] = mapped_column(Integer)
    formalName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class TblUnitConvertion(Base):
    __tablename__ = 'tbl_UnitConvertion'
    __table_args__ = (
        PrimaryKeyConstraint('unitconversionId', name='PK__tbl_Unit__07076F271C1D2798'),
    )

    unitconversionId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    productId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    unitId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    conversionRate: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(18, 5))
    quantities: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblUser(Base):
    __tablename__ = 'tbl_User'
    __table_args__ = (
        PrimaryKeyConstraint('userId', name='PK_tbl_User'),
    )

    userId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    userName: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    password: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    active: Mapped[Optional[bool]] = mapped_column(Boolean)
    roleId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblVehicleContractType(Base):
    __tablename__ = 'tbl_VehicleContractType'
    __table_args__ = (
        PrimaryKeyConstraint('contractType', name='PK_tbl_VehicleContractType'),
    )

    contractType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    contractTypeName: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    contractTypeCode: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))


class TblVisaType(Base):
    __tablename__ = 'tbl_VisaType'
    __table_args__ = (
        PrimaryKeyConstraint('visaType', name='PK_tbl_VisaType'),
    )

    visaType: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    visaTypeName: Mapped[Optional[str]] = mapped_column(String(100, 'SQL_Latin1_General_CP1_CI_AS'))


class TblVoucherType(Base):
    __tablename__ = 'tbl_VoucherType'
    __table_args__ = (
        PrimaryKeyConstraint('voucherTypeId', name='PK__tbl_Vouc__96246DEA68687968'),
    )

    voucherTypeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherTypeName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    typeOfVoucher: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    methodOfVoucherNumbering: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isTaxApplicable: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    masterId: Mapped[Optional[int]] = mapped_column(Integer)
    declaration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading3: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading4: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblVoucherTypeTax(Base):
    __tablename__ = 'tbl_VoucherTypeTax'
    __table_args__ = (
        PrimaryKeyConstraint('voucherTypeTaxId', name='PK__tbl_Vouc__BD57380E6C390A4C'),
        Index('grp1', 'taxId', 'voucherTypeId', 'voucherTypeTaxId', mssql_clustered=False),
        Index('grp2', 'voucherTypeTaxId', 'taxId', mssql_clustered=False),
        Index('taxId', 'taxId', mssql_clustered=False),
        Index('voucherTypeTaxId', 'voucherTypeTaxId', mssql_clustered=False)
    )

    voucherTypeTaxId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    voucherTypeId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    taxId: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(18, 0))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


class TblVoucherTypeToCopy(Base):
    __tablename__ = 'tbl_VoucherTypeToCopy'
    __table_args__ = (
        PrimaryKeyConstraint('voucherTypeId', name='PK_tbl_VoucherTypeToCopy'),
    )

    voucherTypeId: Mapped[decimal.Decimal] = mapped_column(Numeric(18, 0), primary_key=True)
    voucherTypeName: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    typeOfVoucher: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    methodOfVoucherNumbering: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isTaxApplicable: Mapped[Optional[bool]] = mapped_column(Boolean)
    narration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extraDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    extra1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    extra2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    isActive: Mapped[Optional[bool]] = mapped_column(Boolean)
    isDefault: Mapped[Optional[bool]] = mapped_column(Boolean)
    masterId: Mapped[Optional[int]] = mapped_column(Integer)
    declaration: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading1: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading2: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading3: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))
    heading4: Mapped[Optional[str]] = mapped_column(String(collation='SQL_Latin1_General_CP1_CI_AS'))


t_tbl_fixedAssetDeprMethod = Table(
    'tbl_fixedAssetDeprMethod', Base.metadata,
    Column('deprMethodId', Numeric(18, 0), Identity(start=1, increment=1), nullable=False),
    Column('deprMethodName', Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))
)


t_vwMaxRate = Table(
    'vwMaxRate', Base.metadata,
    Column('max', DECIMAL(18, 5)),
    Column('date', DateTime)
)


t_vwMinRate = Table(
    'vwMinRate', Base.metadata,
    Column('min', DECIMAL(18, 5)),
    Column('date', DateTime)
)


class StagingInvoiceDetail(Base):
    __tablename__ = 'Staging_Invoice_Detail'
    __table_args__ = (
        ForeignKeyConstraint(['SID_SIH_ID'], ['Staging_Invoice_Header.SIH_ID'], name='FK_SIH_SID'),
        PrimaryKeyConstraint('SID_ID', name='PK_Staging_Invoice_Detail')
    )

    SID_ID: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    SID_SIH_ID: Mapped[int] = mapped_column(Integer, nullable=False)
    SID_LINE_NO: Mapped[int] = mapped_column(Integer, nullable=False)
    SID_DESCRIPTION: Mapped[str] = mapped_column(Unicode(900, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    SID_AMOUNT: Mapped[decimal.Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    SID_VEHICLE_ID: Mapped[Optional[int]] = mapped_column(Integer)
    SID_PCD: Mapped[Optional[str]] = mapped_column(String(8, 'SQL_Latin1_General_CP1_CI_AS'))
    SID_VH: Mapped[Optional[str]] = mapped_column(String(10, 'SQL_Latin1_General_CP1_CI_AS'))

    Staging_Invoice_Header: Mapped['StagingInvoiceHeader'] = relationship('StagingInvoiceHeader', back_populates='Staging_Invoice_Detail')


class VTCompanyDepartmentMaster(Base):
    __tablename__ = 'VT_Company_DepartmentMaster'
    __table_args__ = (
        ForeignKeyConstraint(['BranchId'], ['VT_Company_BranchMaster.BranchId'], name='FK_VT_Company_DepartmentMaster_VT_Company_BranchMaster'),
        PrimaryKeyConstraint('DeptId', name='PK_VT_Company_DepartmentMaster')
    )

    DeptId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    DeptName: Mapped[str] = mapped_column(Unicode(150, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    BranchId: Mapped[int] = mapped_column(Integer, nullable=False)

    VT_Company_BranchMaster: Mapped['VTCompanyBranchMaster'] = relationship('VTCompanyBranchMaster', back_populates='VT_Company_DepartmentMaster')


class VTVehModelMaster(Base):
    __tablename__ = 'VT_Veh_ModelMaster'
    __table_args__ = (
        ForeignKeyConstraint(['MakeId'], ['VT_Veh_MakeMaster.MakeId'], name='FK_VT_Veh_ModelMaster_VT_Veh_MakeMaster'),
        PrimaryKeyConstraint('ModelId', name='PK_VT_Veh_ModelMaster')
    )

    ModelId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ModelName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    MakeId: Mapped[int] = mapped_column(Integer, nullable=False)

    VT_Veh_MakeMaster: Mapped['VTVehMakeMaster'] = relationship('VTVehMakeMaster', back_populates='VT_Veh_ModelMaster')
    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_ModelMaster')


class VTVehPlateCodeMaster(Base):
    __tablename__ = 'VT_Veh_PlateCodeMaster'
    __table_args__ = (
        ForeignKeyConstraint(['PlateCategoryId'], ['VT_Veh_StateMaster.StateId'], name='FK_VT_Veh_PlateCodeMaster_VT_Veh_StateMaster'),
        PrimaryKeyConstraint('PlateCodeId', name='PK_VT_PlateCodeMaster')
    )

    PlateCodeId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    PlateCodeName: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    PlateCategoryId: Mapped[int] = mapped_column(Integer, nullable=False)
    Code: Mapped[Optional[str]] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'))

    VT_Veh_StateMaster: Mapped['VTVehStateMaster'] = relationship('VTVehStateMaster', back_populates='VT_Veh_PlateCodeMaster')
    VT_Veh_VehicleMaster: Mapped[list['VTVehVehicleMaster']] = relationship('VTVehVehicleMaster', back_populates='VT_Veh_PlateCodeMaster')


class VTVehVehicleMaster(Base):
    __tablename__ = 'VT_Veh_VehicleMaster'
    __table_args__ = (
        ForeignKeyConstraint(['ColourId'], ['VT_Veh_ColourMaster.ColourId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_ColourMaster'),
        ForeignKeyConstraint(['FuelCapacityUnitId'], ['VT_Veh_FuelCapacityUnitMaster.FuelCapUnitId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_FuelCapacityUnitMaster'),
        ForeignKeyConstraint(['FuelCapacityUnitId'], ['VT_Veh_FleetTypeMaster.FleetTypeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_FleetTypeMaster'),
        ForeignKeyConstraint(['ModelId'], ['VT_Veh_ModelMaster.ModelId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_ModelMaster'),
        ForeignKeyConstraint(['PlateCodeId'], ['VT_Veh_PlateCodeMaster.PlateCodeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_PlateCodeMaster'),
        ForeignKeyConstraint(['TransmissionId'], ['VT_Veh_TransmissionMaster.TransmissionId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_TransmissionMaster'),
        ForeignKeyConstraint(['TypeId'], ['VT_Veh_TypeMaster.TypeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_TypeMaster'),
        PrimaryKeyConstraint('VehicleId', name='PK_VT_Veh_VehicleMaster')
    )

    VehicleId: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1), primary_key=True, autoincrement=True)
    ModelId: Mapped[int] = mapped_column(Integer, nullable=False)
    EngineCapacityId: Mapped[int] = mapped_column(Integer, nullable=False)
    Year: Mapped[int] = mapped_column(Integer, nullable=False)
    PlateCodeId: Mapped[int] = mapped_column(Integer, nullable=False)
    PlateNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    RegistrationStartDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    RegistrationExpiryDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    InsurancePolicyId: Mapped[int] = mapped_column(Integer, nullable=False)
    InsurancePolicyRecNo: Mapped[int] = mapped_column(Integer, nullable=False)
    InsuranceExpDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    InsuranceCompanyId: Mapped[int] = mapped_column(Integer, nullable=False)
    InsuranceTypeId: Mapped[int] = mapped_column(Integer, nullable=False)
    TCNoId: Mapped[int] = mapped_column(Integer, nullable=False)
    TypeId: Mapped[int] = mapped_column(Integer, nullable=False)
    FuelCapacity: Mapped[int] = mapped_column(Integer, nullable=False)
    FuelCapacityUnitId: Mapped[int] = mapped_column(Integer, nullable=False)
    ChasisNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    EngineNo: Mapped[str] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    TransmissionId: Mapped[int] = mapped_column(Integer, nullable=False)
    FuelTypeId: Mapped[int] = mapped_column(Integer, nullable=False)
    ColourId: Mapped[int] = mapped_column(Integer, nullable=False)
    SalikTag: Mapped[str] = mapped_column(Unicode(100, 'SQL_Latin1_General_CP1_CI_AS'), nullable=False)
    InitialKmRdg: Mapped[int] = mapped_column(Integer, nullable=False)
    LatestKmRdg: Mapped[int] = mapped_column(Integer, nullable=False)
    TariffGroupId: Mapped[int] = mapped_column(Integer, nullable=False)
    StatusId: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    LastUpdatedBy: Mapped[int] = mapped_column(Integer, nullable=False)
    LastUpdatedDate: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    LocationToRemove: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    Remarks: Mapped[Optional[str]] = mapped_column(Unicode(collation='SQL_Latin1_General_CP1_CI_AS'))
    NextDueService: Mapped[Optional[int]] = mapped_column(Integer)
    AlertDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    BranchId: Mapped[Optional[int]] = mapped_column(Integer)
    LocId: Mapped[Optional[int]] = mapped_column(Integer)
    FuelLevel: Mapped[Optional[int]] = mapped_column(Integer)
    VHType: Mapped[Optional[str]] = mapped_column(Unicode(50, 'SQL_Latin1_General_CP1_CI_AS'))

    VT_Veh_ColourMaster: Mapped['VTVehColourMaster'] = relationship('VTVehColourMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_FuelCapacityUnitMaster: Mapped['VTVehFuelCapacityUnitMaster'] = relationship('VTVehFuelCapacityUnitMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_FleetTypeMaster: Mapped['VTVehFleetTypeMaster'] = relationship('VTVehFleetTypeMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_ModelMaster: Mapped['VTVehModelMaster'] = relationship('VTVehModelMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_PlateCodeMaster: Mapped['VTVehPlateCodeMaster'] = relationship('VTVehPlateCodeMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_TransmissionMaster: Mapped['VTVehTransmissionMaster'] = relationship('VTVehTransmissionMaster', back_populates='VT_Veh_VehicleMaster')
    VT_Veh_TypeMaster: Mapped['VTVehTypeMaster'] = relationship('VTVehTypeMaster', back_populates='VT_Veh_VehicleMaster')
