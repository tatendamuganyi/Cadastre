import sqlite3
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.sql import select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date
from geoalchemy2 import Geometry
from sqlalchemy.orm import sessionmaker
from shapely import wkt
from shapely.wkt import loads


engine = create_engine('sqlite:///ZimCadastreDB.db', echo=True, connect_args={'check_same_thread': False})

Base = declarative_base()

class ZimCadastre(Base):
    __tablename__ = 'cadastre'
    id = Column(Integer, primary_key=True)
    RegNumber = Column(String)
    GroupName = Column(String)
    MineName = Column(String)
    ClaimName = Column(String)
    MineralName = Column(String)
    Area = Column(Float)
    SpecifiedArea = Column(Float)
    Units = Column(Float)
    InspectionFee = Column(Float)
    MinesRegion = Column(String)
    RegCertificate = Column(String)
    TransferCertificate = Column(String)
    LatestInspectionSerial = Column(String)
    RegistrationDate = Column(String)
    InspectionDate = Column(String)
    geometry =Column(String)
    points = Column(String)

Session = sessionmaker(bind=engine)
session = Session()

##calling data from the database

def cadastre_df():
    our_cad = session.query(ZimCadastre).order_by(ZimCadastre.RegNumber)
    cadastre_gName = []
    cadastre_mName = []
    cadastre_cName = []
    cadastre_Mineral = []
    cadastre_Area = []
    cadastre_Geom = []
    cadastre_Points = []
    cadastre_regNum = []
    cadastre_regDate = []
    cadastre_inspDate = []

    for cadastre in our_cad:
        cadastre_gName.append(cadastre.GroupName)
        cadastre_mName.append(cadastre.MineName)
        cadastre_cName.append(cadastre.ClaimName)
        cadastre_Mineral.append(cadastre.MineralName)
        cadastre_Area.append(cadastre.Area)
        cadastre_Geom.append(cadastre.geometry)
        cadastre_Points.append(cadastre.points)
        cadastre_regNum.append(cadastre.RegNumber)
        cadastre_regDate.append(cadastre.RegistrationDate)
        cadastre_inspDate.append(cadastre.InspectionDate)

    cadastre_gName = pd.DataFrame(cadastre_gName)
    cadastre_mName = pd.DataFrame(cadastre_mName)
    cadastre_cName = pd.DataFrame(cadastre_cName)
    cadastre_Mineral = pd.DataFrame(cadastre_Mineral)
    cadastre_regNum = pd.DataFrame(cadastre_regNum)
    cadastre_regDate = pd.DataFrame(cadastre_regDate)
    cadastre_inspDate = pd.DataFrame(cadastre_inspDate)
    cadastre_Geom = pd.DataFrame(cadastre_Geom)
    cadastre_Points = pd.DataFrame(cadastre_Points)
    cadastre_Area = pd.DataFrame(cadastre_Area)

    geom_df = pd.concat([cadastre_gName, cadastre_mName, cadastre_cName, cadastre_Mineral, cadastre_regNum,
                         cadastre_regDate, cadastre_inspDate, cadastre_Geom, cadastre_Points, cadastre_Area], axis=1,
                        ignore_index=True)
    geom_df.columns = ['Group Name', 'Mine Name', 'Claim Name', 'Mineral', 'Reg Number', 'Reg Date',
                       'Ins Date', 'geometry', 'Centre Points', 'Area']
    geom_df['geometry'] = geom_df['geometry'].apply(wkt.loads)
    geom = gpd.GeoDataFrame(geom_df, crs='epsg:4326')

    return geom_df