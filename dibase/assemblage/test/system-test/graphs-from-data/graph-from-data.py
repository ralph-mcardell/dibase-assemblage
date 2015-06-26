#! /usr/bin/python3
# v3.4+
"""
System Tests for dibase.assemblage: 'build' style tests.

Using a made up build chain starting with some test CSV files from
  https://support.spatialkey.com/spatialkey-sample-csv-data/

First munge the raw test data using functions specific to each dataset to
produce sets of data grouped by some criteria such USA state and write out
the results as a CSV file for each group and a 'master' CSV file naming the
groups and their files with one name,file per record.

Next process each master-plus-associated-group file set to produce a combined
'object' file (or files) as a Python selves file-set.

Complete this initial target by combining (linking) the separate shelves into
a single master shelf 'library'.

Finally create a set of program files that when built access datasets from the
shelf 'library' to create bar charts using HTML5/SVG.
"""
import unittest

import os,sys
project_root_dir =  os.path.dirname(
                      os.path.dirname(
                        os.path.dirname(
                          os.path.dirname(
                            os.path.dirname(
                              os.path.dirname(os.path.realpath(__file__)
                              )# this directory
                            )  # system_test directory 
                          )    # test directory 
                        )      # assemblage directory 
                      )        # dibase directory 
                    )          # project directory
if project_root_dir not in sys.path:
  sys.path.insert(0, project_root_dir)
from dibase.assemblage.assemblage import Assemblage
from dibase.assemblage.blueprint import Blueprint
from dibase.assemblage.component import Component
from dibase.assemblage.filecomponent import FileComponent
from dibase.assemblage.digestcache import DigestCache
from dibase.assemblage.shelfdigeststore import ShelfDigestStore

import csv
import logging
import shelve

class build: # action class
  @staticmethod
  def queryProcessElements(element): 
    return True   # we want to build elements we depend on
  @staticmethod
  def queryDoAfterElementsActions(element):
     # we want to build ourself after elements we need have been if we need to
    return element.doesNotExist() or element.isOutOfDate()

class CSVDataMunger(FileComponent):
  def __init__(self, name, assemblage, elements=[], logger=None, transformer=None):
    '''
    Passes all parameters but transformer on to the Component base.
    The transformer parameter should specify a data transformation callable.
    Expects to munge exactly 1 (sub-)element representing the CSV file to munge
    data from.
    '''
    self.inputFilePath = None
    for e in elements:
      if type(e) is FileComponent:
        if self.inputFilePath:
          raise RuntimeError("CSVDataMunger: more than 1 input FileComponent elements provided")
        self.inputFilePath = e.normalisedPath()
    if not self.inputFilePath:
      raise RuntimeError("CSVDataMunger: No input FileComponent element provided" )
    super().__init__(name,assemblage,elements,logger)
    self.xform = transformer

  def doesNotExist(self):
    return not os.path.exists(str(self))

  def build_afterElementsActions(self):
    '''
    build action action-steps to be performed after this element's elements
    have applied the build action.
    
    The actions are:
      - read the CSV file into memory as a CSV map
      - pass the CSV map to the transformer function which should
        return another map in the form:
          { '' : (dataset-name', 'dataset file name')
          , 'grpname-0' : { '' : ('group 0 name', 'group 0 file name')
                          ,'field-0' : value-0
                          , field-1' : value-1
                          , ...
                          , 'field-n' : value-n
                          }
          , 'grpname-1' : { '' : ('group 1 name', 'group 1 file name')
                          ,'field-0' : value-0
                          , field-1' : value-1
                          , ...
                          , 'field-n' : value-n
                          }
          , ...
          , 'grpname-n' : { '' : ('group n name', 'group n file name')
                          ,'field-0' : value-0
                          , field-1' : value-1
                          , ...
                          , 'field-n' : value-n
                          }
          }
      - walk the map of maps and write a CVS file for each group map and
        a master dataset CSV file with records giving the group names and
        file pathnames - with the first record giving the dataset name.
    '''
    data_to_write = {}
    path = self.inputFilePath
    self.debug("Reading raw data from CSV file: '%s'" % path )
    with open(path) as csvfile:
      dialect = csv.Sniffer().sniff(csvfile.read(4096))
      csvfile.seek(0)
      reader = csv.reader(csvfile, dialect)
      data_to_write = self.xform(reader)
#      self.debug("Data to be written to CSV files:\n%s" % str(data_to_write))
    main_filename = str(self)
    outfilename_stem = os.path.splitext(main_filename)[0]
    self.debug("Writing output data to main file %(m)s and member files with names starting '%(s)s'" 
                % {'m':main_filename, 's': outfilename_stem}
              )
    with open(main_filename,'w', newline='') as mainfile:
      main_writer = csv.writer(mainfile)
      main_writer.writerow(['Group','Member','File'])
      for grp_name,grp_data in data_to_write.items():
        if grp_name=='__METADATA__':
          main_writer.writerow([grp_name,outfilename_stem, grp_data['__TITLE__']])
        else:
            for mbr_name,mbr_data in grp_data.items():
              mbr_filename = '.'.join([outfilename_stem,mbr_data['__FILE__'],'csv'])
              with open(mbr_filename,'w', newline='') as mbrfile:
                mbr_writer = csv.writer(mbrfile)
                mbr_writer.writerow(['Price'])
                for price in mbr_data['__DATA__']:
                  mbr_writer.writerow([price])
              main_writer.writerow([grp_name,mbr_name,mbr_filename])
    self.assemblage().digestCache().writeBack()

class CSVGroupDataCompiler(FileComponent):
  def __init__(self, name, assemblage, elements=[], logger=None):
    self.inputFilePath = None
    for e in elements:
      if type(e) is CSVDataMunger:
        if self.inputFilePath:
          raise RuntimeError("CSVGroupDataCompiler: more than 1 input CSVDataMunger elements provided")
        self.inputFilePath = e.normalisedPath()
    if not self.inputFilePath:
      raise RuntimeError("CSVGroupDataCompiler: No input CSVDataMunger element provided" )
    super().__init__(name,assemblage,elements,logger)

  def doesNotExist(self):
    does_not_exist = not os.path.exists('.'.join([str(self),'dat'])) # shelves use 3 files .dat, .bak and .dir
    self.debug("Target file(s) '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist

  def build_afterElementsActions(self):
    '''
    Reads main group data CSV file and all sub-files listed within it.
    Constructs a Python shelve persistent map of this data as the output
    file.
    '''
    data_to_write = {}
    path = self.inputFilePath
    self.debug("Processing main group data from CSV file: '%s'" % path )
    main_name = None
    with open(path) as main_csvfile:
      dialect = csv.Sniffer().sniff(main_csvfile.read(4096))
      main_csvfile.seek(0)
      main_reader = csv.DictReader(main_csvfile, dialect=dialect)
      main_title = None
      for main_row in main_reader:
        if main_row['Group']=='__METADATA__':
          if main_name!=None:
            raise RuntimeError( "CSVGroupDataCompiler: Main group data file '%s' has more than one '__METADATA__' Group row"
                                % path
                              )
          main_name = main_row['Member']
          data_to_write['__METADATA__'] = {'__TITLE__' : main_row['File']}
        else: 
#          self.debug("Processing member group data from CSV file: '%s'" % main_row['File'] )
          with open(main_row['File']) as mbr_csvfile:
            mbr_reader = csv.DictReader(mbr_csvfile, dialect='excel')
            group = main_row['Group']
            mbr = main_row['Member']
            if group not in data_to_write:
              data_to_write[group] = {}
            data_to_write[group][mbr] = {}
            for mbr_row in mbr_reader:
              for mbr_fld,mbr_value in mbr_row.items():
                if mbr_fld not in data_to_write[group][mbr]:
                  data_to_write[group][mbr][mbr_fld] = [mbr_value]
                else:
                  data_to_write[group][mbr][mbr_fld].append(mbr_value)
      if main_name==None:
        raise RuntimeError( "CSVGroupDataCompiler: Main group data file '%s' is missing a '__METADATA__' Group row"
                            % path
                          )
#      self.debug("Data to be written to Group Data Object (gdo) file:\n%s" % str(data_to_write))
      with shelve.open(str(self)) as store:
        store[main_name] = data_to_write

class GroupDataArchiver(Component):
  def __init__(self, name, assemblage, elements=[], logger=None):
    self.inputFilePaths = []
    for e in elements:
      if type(e) is CSVGroupDataCompiler:
        self.inputFilePaths.append(e.normalisedPath())
    if not self.inputFilePaths:
      raise RuntimeError("GroupDataArchiver: No input CSVGroupDataCompiler elements provided" )
    super().__init__(name,assemblage,elements,logger)

  def doesNotExist(self):
    does_not_exist = not os.path.exists('.'.join([str(self),'dat'])) # shelves use 3 files .dat, .bak and .dir
    self.debug("Target file(s) '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist

  def build_afterElementsActions(self):
    '''
    Opens and reads each shelve file-set and copies to output shelve file-set.
    '''
    with shelve.open(str(self)) as output_store:
      for input_store_path in self.inputFilePaths:
        with shelve.open(input_store_path) as input_store:
          for dataset_name, dataset_map in input_store.items():
            output_store[dataset_name] = dataset_map

class DirectoryComponent(Component):
  '''
  A simple sub-type of Component that ensures directories are created if
  they do not exist regardless of action so long as an action query function
  calls doesNotExist.
  '''
  def __init__(self, name, assemblage, elements=[], logger=None):
    super().__init__(name,assemblage,elements,logger)

  def doesNotExist(self):
    '''
    Unlike most doesNotExist methods the DirectoryComponent implementation
    uses a call to doesNotExist to ensure the directory does exist thus
    allowing it to be used with any action that queries doesNotExist.
    '''
    if not os.path.exists(str(self)):
      os.mkdir(str(self))
    if not os.path.exists(str(self)):
      raise OSError("Failed to create directory '%s'"%str(self))
    self.debug("Stating that directory '%s' DOES exist" % str(self))
    return False

  def hasChanged(self):
    self.debug("Stating that directory '%s' has NOT changed" % str(self))
    return False # yes directories can change but not relevant here!

def MungeSalesJan2009(records):
  first_row = True
  price_index = None
  city_index = None
#  data = {}
  output =  { '__METADATA__' : { '__TITLE__' : 'January 2009 Sales Groups' }
            , 'City'  : {}
            , 'State'  : {}
            , 'Country'  : {}
            }
  for r in records:
    if first_row:
      field_index = 0
      for f in r:
        if f=='Price':
          price_index = field_index
        if f=='City':
          city_index = field_index
        if f=='State':
          state_index = field_index
        if f=='Country':
          country_index = field_index
        field_index = field_index + 1
      if price_index is None or city_index is None:
        raise RuntimeError("MungeSalesJan2009: Data has missing column names. Require columns 'City' and 'Price'")
      first_row = False
    else:
      city = r[city_index].strip()
      state = r[state_index].strip()
      country = r[country_index].strip()
      price = float(r[price_index].replace(',',''))
      if city!='':
        if city not in output['City']:
          output['City'][city] = {'__FILE__':city.replace(' ','-').replace("'",''), '__DATA__' :[price]}
        else:
          output['City'][city]['__DATA__'].append(price) 
      if state!='':
        if state not in output['State']:
          output['State'][state] = {'__FILE__':state.replace(' ','-').replace("'",''), '__DATA__' :[price]}
        else:
          output['State'][state]['__DATA__'].append(price) 
      if country!='':
        if country not in output['Country']:
          output['Country'][country] = {'__FILE__':country.replace(' ','-').replace("'",''), '__DATA__' :[price]}
        else:
          output['Country'][country]['__DATA__'].append(price) 
  return output

class SystemTestGraphsFromCSVData(unittest.TestCase):
  def test_build_from_Python_objects_element_processors(self):
    original_data_dir = os.path.abspath('./download')
    source_dir = os.path.abspath('./source')
    build_dir = os.path.abspath('./build')
    lib_dir = os.path.abspath('./lib')
    sales_original_filestem = 'SalesJan2009'
    group_data_lib_filestem = 'group-data'
    sales_original_data = '%(p)s/%(f)s.csv'%{'p':original_data_dir, 'f':sales_original_filestem}
    sales_source_file = '%(p)s/%(f)s.csv'%{'p':source_dir, 'f':sales_original_filestem}
    sales_object_file = '%(p)s/%(f)s.gdo'%{'p':build_dir, 'f':sales_original_filestem}
    group_data_lib_file = '%(p)s/lib-%(f)s.gda'%{'p':lib_dir, 'f':group_data_lib_filestem}
    assm = Assemblage\
            (
              plan = Blueprint()
                      .setDigestCache(DigestCache(ShelfDigestStore()))
                      .addElements((source_dir,build_dir,lib_dir), DirectoryComponent)
                      .addElements(sales_original_data, FileComponent)
                      .addElements(sales_source_file, CSVDataMunger
                                  , elements=[sales_original_data, source_dir]
                                  , transformer=MungeSalesJan2009
                                  )
                      .addElements(sales_object_file, CSVGroupDataCompiler
                                  , elements=[sales_source_file, build_dir]
                                  )
                      .addElements(group_data_lib_file, GroupDataArchiver
                                  , elements=[sales_object_file, lib_dir]
                                  )
                      .setLogger(Blueprint().logger().setLevel(logging.DEBUG))
            ).apply('build')

if __name__ == '__main__':
  unittest.main()
        