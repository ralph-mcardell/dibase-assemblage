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
import json

class BuildAction:
  @staticmethod
  def queryProcessElements(element): 
    return True   # we want to build elements we depend on
  @staticmethod
  def queryDoAfterElementsActions(element):
     # we want to build ourself after elements we need have been if we need to
    return element.doesNotExist() or element.isOutOfDate()

build = BuildAction # Demonstrate ability to create aliases for (action) classes

class CSVDataMunger(FileComponent):
  def __init__(self, name, attributes, elements=[], logger=None, transformer=None):
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
    super().__init__(name,attributes,elements,logger)
    self.xform = transformer

  def doesNotExist(self):
    does_not_exist = not os.path.exists(str(self))
    self.debug("Target file '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist

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
    datasetname = os.path.split(outfilename_stem)[1] # tail filename part
    self.debug("Writing output data for dataset '%(n)s' to main file '%(m)s' and member files with names starting '%(s)s'" 
                % {'n':datasetname,'m':main_filename, 's': outfilename_stem}
              )
    with open(main_filename,'w', newline='') as mainfile:
      main_writer = csv.writer(mainfile)
      main_writer.writerow(['Group','Member','File'])
      for grp_name,grp_data in data_to_write.items():
        if grp_name=='__METADATA__':
          main_writer.writerow([grp_name,datasetname, grp_data['__TITLE__']])
        else:
            for mbr_name,mbr_data in grp_data.items():
              mbr_filename = '.'.join([outfilename_stem,mbr_data['__FILE__'],'csv'])
              with open(mbr_filename,'w', newline='') as mbrfile:
                mbr_writer = csv.writer(mbrfile)
                mbr_writer.writerow(['Price'])
                for price in mbr_data['__DATA__']:
                  mbr_writer.writerow([price])
              main_writer.writerow([grp_name,mbr_name,mbr_filename])

class CSVGroupDataCompiler(FileComponent):
  def __init__(self, name, attributes, elements=[], logger=None):
    self.inputFilePath = None
    for e in elements:
      if type(e) is CSVDataMunger:
        if self.inputFilePath:
          raise RuntimeError("CSVGroupDataCompiler: more than 1 input CSVDataMunger elements provided")
        self.inputFilePath = e.normalisedPath()
    if not self.inputFilePath:
      raise RuntimeError("CSVGroupDataCompiler: No input CSVDataMunger element provided" )
    super().__init__(name,attributes,elements,logger)

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
              for mbr_fld,mbr_strvalue in mbr_row.items():
                mbr_value = float(mbr_strvalue)
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
  def __init__(self, name, attributes, elements=[], logger=None):
    self.inputFilePaths = []
    for e in elements:
      if type(e) is CSVGroupDataCompiler:
        self.inputFilePaths.append(e.normalisedPath())
    if not self.inputFilePaths:
      raise RuntimeError("GroupDataArchiver: No input CSVGroupDataCompiler elements provided" )
    super().__init__(name,attributes,elements,logger)

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

class BarChartDescriptionCompiler(FileComponent):
  '''
  Reads a JSON description of on e or more bar charts and constructs a
  partial HTML5/SVG document that only requires 'linking' with the appropriate
  group data archive to create a complete document that can be displayed in
  a suitable browser.
  '''
  def __init__(self, name, attributes, elements=[], logger=None):
    '''
    Passes all parameters on to the Component base.
    Expects to compile exactly 1 (sub-)element representing the JSON file
    to 'compile'.
    '''
    self.inputFilePath = None
    for e in elements:
      if type(e) is FileComponent:
        if self.inputFilePath:
          raise RuntimeError("BarChartDescriptionCompiler: more than 1 FileComponent elements to compile provided")
        self.inputFilePath = e.normalisedPath()
    if not self.inputFilePath:
      raise RuntimeError("BarChartDescriptionCompiler: No FileComponent element to compile provided" )
    super().__init__(name,attributes,elements,logger)

  def doesNotExist(self):
    does_not_exist = not os.path.exists('.'.join([str(self),'dat'])) # shelves use 3 files .dat, .bak and .dir
    self.debug("Target file '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist

  def build_afterElementsActions(self):
    '''
    Loads the JSON input file.
    Writes to the output file (str(self)) partial HTML5 text that will
    display the described bar chart once 'linked' and fixed up with the data
    source.
    '''
    class CheckedMapAccess:
      def __init__(self, map, errmsg):
        self.map = map
        self.error_message = errmsg
      def value(self, key):
        if key not in self.map:
          raise RuntimeError(self.error_message%{'key':key, 'map':str(self.map)})
        return self.map[key]
        
    def makeStyle(decl):
      checked_decl = CheckedMapAccess( decl
                                    , "BarChartDescriptionCompiler.build_afterElementsActions:"
                                      " Declaration:\n'%(map)s'\n Is missing its required '%(key)s' attribute.")
      return "#%(i)s {float: %(p)s; height: %(h)s; width: %(w)s;}"\
             %{ 'i':checked_decl.value('id'),'p':checked_decl.value('position')
              , 'h':checked_decl.value('height'), 'w':checked_decl.value('width')
              }
    def checkAttribute(map, attr, msg):
      if attr not in map:
        raise RuntimeError(msg)

    styles = ""
    panels = {}
    path = self.inputFilePath
    self.debug("Processing graphs 'source' file data from JSON file: '%s'" % path )
    doctitle = "Generated Bar charts"
    with open(path) as src_file:
      src = json.load(src_file)
      itemIndex = 0
      for decl in src:
        if type(decl) is not dict:
          raise RuntimeError( "BarChartDescriptionCompiler.build_afterElementsActions:"
                              " Expected JSON map, loaded as Python dict, describing panel or graph, found '%s'"
                              % str(type(decl)) )
        if 'panel' in decl:
          styles = '\n'.join([styles, makeStyle(decl["panel"])])
          panels[decl['panel']['id']] = {'index':itemIndex, 'graph' : {}}
        elif 'graph' in decl:
          graph = decl["graph"]
          checked_graph = CheckedMapAccess( graph
                                        , "BarChartDescriptionCompiler.build_afterElementsActions:"
                                          " Graph:\n'%(map)s'\n Is missing its required '%(key)s' attribute.")
          styles = '\n'.join([styles, makeStyle(graph)])
          graphspec = {}
          checked_data = CheckedMapAccess( checked_graph.value('data')
                                         , "BarChartDescriptionCompiler.build_afterElementsActions:"
                                           " graph['data']:\n'%(map)s'\n Is missing its required '%(key)s' attribute.")
          graphspec['dataset'] = checked_data.value('dataset')
          graphspec['group'] = checked_data.value('group')
          graphspec['field'] = checked_data.value('field')
          graphspec['reducer'] = checked_graph.value('reducer')
          graphspec['height'] = checked_graph.value('height')
          graphspec['width'] = checked_graph.value('width')
          graphspec['name'] = graph['name'] if 'name' in graph else ''
          graphspec['units'] = graph['units'] if 'units' in graph else ''
          graphspec['index'] = itemIndex
          
          checked_panels = CheckedMapAccess( panels
                                           , "BarChartDescriptionCompiler.build_afterElementsActions:"
                                             " Cannot add graph to undeclared panel '%(key)s'.")
          checked_panels.value(checked_graph.value('panel'))['graph'][checked_graph.value('id')] = graphspec
        elif 'doctitle' in decl:
          doctitle = decl['doctitle']
        else:
          raise RuntimeError( "BarChartDescriptionCompiler.build_afterElementsActions:"
                              " expected JSON object with 'panel' or 'graph' or 'doctitle' attribute, found:\n'%s'"
                              % str(decl) )
        itemIndex = itemIndex + 1
#    self.debug("Styles: '%s'"%styles)
    chunks =  { 'prologue'  : "<!DOCTYPE html><html><head>"
                              '<title>%s</title><meta charset="utf-8" />\n'% doctitle
              , 'styles'    : '\n'.join(["<style>", styles, "</style>","</head>","<body>"])
              , 'panels'    : panels
              , 'epilogue'  : "</body></html>\n"
              }
    with shelve.open(str(self)) as store:
      store["main"] = chunks

class BarChartDocumentLinker(Component):
  def __init__(self, name, attributes, elements=[], logger=None):
    self.graphObjectFilePath = []
    self.groupDataObjectFilePaths = []
    for e in elements:
      if type(e) is BarChartDescriptionCompiler:
        self.graphObjectFilePath.append(e.normalisedPath())
      elif type(e) is GroupDataArchiveFile:
        self.groupDataObjectFilePaths.append(e.normalisedPath())
    if not self.graphObjectFilePath:
      raise RuntimeError("BarChartDocumentLinker: No input graph description object elements provided" )
    elif len(self.graphObjectFilePath)!=1:
      raise RuntimeError( "BarChartDocumentLinker: Too many input graph description object elements provided; expected 1, got %d" 
                          % len(self.graphObjectFilePath)
                        )
    if not self.groupDataObjectFilePaths:
      raise RuntimeError("BarChartDocumentLinker: No input group data archive elements provided" )
    super().__init__(name,attributes,elements,logger)

  def doesNotExist(self):
    does_not_exist = not os.path.exists(str(self))
    self.debug("Target file(s) '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist

  def build_afterElementsActions(self):
    '''
    Opens and reads graph description object shelf file-set, extracts graph
    descriptions looks for data-set in group data archives and if found uses
    it to create bar chart group values using the appropriate reducer function
    '''
    def to_number(value_string):
      return float(value_string.rstrip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"£$%^&*()_-+={[}]~#@\':;?/><,|\\'))
    def resolve_dataset(dataspec, libs):
      for lib in libs:
        if dataspec['dataset'] in lib:
          return lib[dataspec['dataset']]
      return None
    
    def reduce_group_data(data, reducer):
      def Sum(data):
        reduced = {}
        for mbr,values in data.items():
          sum = 0
          for v in values:
            sum = sum + v
          reduced[mbr] = sum
        return reduced
      def PercentTotal(data):
        sums = Sum(data)
        reduced = {}
        total = 0
        for mbr_sum in sums.values():
          total = total + mbr_sum
        for mbr,sum in sums.items():
          reduced[mbr] = sum*100.0/total
        return reduced
#      self.debug("Looking for function named '%(f)s' in local names: '%(l)s'"%{'l':locals(),'f':reducer})
      fn = locals().get(reducer)
      return fn(data) if fn else None
    doc = ''
    unresolved = []
    libs = []
    with shelve.open(self.graphObjectFilePath[0]) as graph_store:
      try:
        for gda_store_path in self.groupDataObjectFilePaths:
          libs.append(shelve.open(gda_store_path))
        doc = '\n'.join([graph_store['main']['prologue'],graph_store['main']['styles']])
        for pid,panelData in sorted(graph_store['main']['panels'].items(), key=lambda itemTuple : itemTuple[1]['index']):
          graph = panelData['graph']
          doc = ''.join([doc,'\n<div id="',pid,'">\n'])
          for gid,graphspec in sorted(graph.items(), key=lambda itemTuple : itemTuple[1]['index']):
#            self.debug("Graph with id '%(id)s' has specification data: %(gs)s" % {'id':gid, 'gs':str(graphspec)})
            dataset = resolve_dataset(graphspec, libs)
            if not dataset:
              unresolved.append(graphspec['dataset'])
              continue
            if graphspec['group'] not in dataset:
              unresolved.append('.'.join([graphspec['dataset'],graphspec['group']]))
              continue
            groupData = {}
            for mbr,mbrFlds in dataset[graphspec['group']].items():
              if graphspec['field'] not in mbrFlds:
                unresolved.append('.'.join([ graphspec['dataset']
                                           , graphspec['group']
                                           , mbr, graphspec['field']
                                          ])
                                 )
                continue
              groupData[mbr] = mbrFlds[graphspec['field']]
            groupValues = reduce_group_data(groupData,graphspec['reducer'])
            if not groupValues:
              unresolved.append(''.join([ "Unknown reducer function '"
                                        , graphspec['reducer'],"'."])
                               )
              continue
            dataset_strings = {'title': dataset['__METADATA__']['__TITLE__']
                              ,'name' : graphspec['dataset']
                              }
            w = to_number(graphspec['width'])
            h = to_number(graphspec['height'])
            min_extent = 10000
            if h>w:
              viewbox_h = int((h*min_extent)/w)
              viewbox_w = min_extent
            elif w>h:
              viewbox_w = int((w*min_extent)/h)
              viewbox_h = min_extent
            else:
              viewbox_h = min_extent
              viewbox_w = min_extent
            maxValue = 0.0 # note: assumes all values positive
            for value in groupValues.values():
              if value > maxValue:
                maxValue = value
            axisXOrigin = int(0.10 * float(viewbox_w))
            axisYOrigin = int(0.85 * viewbox_h)
            axisXExtent = int(0.98 * viewbox_w)
            axisYExtent = int(0.10 * viewbox_h)
            axisXLen = (axisXExtent-axisXOrigin)
            axisYLen = (axisYOrigin-axisYExtent)
            axixYMarkLen = int(0.010 * viewbox_w)
            axixYMarkXExtent = axisXOrigin - axixYMarkLen
            axixYMarkTextX = axisXOrigin - int(0.025*viewbox_w)
            axixYMarkTextYOffset = int(0.002*viewbox_h)
            axisYLabelX = int(0.02 * viewbox_w)
            axisYLabelLenEstimate = len(graphspec['units'])*viewbox_h*0.05
            axisYLabelY = axisYExtent + int((axisYLen+axisYLabelLenEstimate)/2.0)
            axisLineWidth = 0.005*min_extent
            barWidth = int((axisXLen-axisLineWidth) / len(groupValues))
            self.debug( "viewbox width:%(vw)d  viewbox height:%(vh)d\n"
                        "AXES: Origin(x,y):(%(axo)d,%(ayo)d) ; Extent(x,y):(%(axe)d,%(aye)d) ; Length(x,y):(%(axl)d,%(ayl)d) \n"
                        "    ; YMarkLen:%(ayml)d ; YMarkXExtent:%(aymxe)d ; YMarkTextX: %(aymtx)d ; YMarkTextXOffset:%(aymtxo)d\n"
                        "    ; YLabel(x,y):(%(aylx)d,%(ayly)d) ; YLabelLenEstimate:%(aylle)d ; LineWidth:%(alw)d\n"
                        "BarWidth:%(bw)d"

                        % {'vw':viewbox_w,'vh':viewbox_h
                          ,'axo':axisXOrigin, 'ayo':axisYOrigin, 'axe':axisXExtent, 'aye':axisYExtent, 'axl':axisXLen, 'ayl':axisYLen
                          ,'ayml':axixYMarkLen, 'aymxe':axixYMarkXExtent, 'aymtx':axixYMarkTextX, 'aymtxo':axixYMarkTextYOffset
                          ,'aylx':axisYLabelX, 'ayly':axisYLabelY, 'aylle':axisYLabelLenEstimate, 'alw':axisLineWidth
                          ,'bw':barWidth
                          }
                      )
            colours = ('aquamarine', 'antiquewhite', 'cornflowerblue','coral'
                      ,'palegreen', 'gold', 'deepskyblue','orchid','lightcyan'
                      , 'tomato', 'plum', 'powderblue', 'khaki', 'salmon'
                      , 'lightcyan', 'mediumpurple', 'palegoldenrod'
                      , 'blanchedalmond'
                      )
            title = graphspec['name'] % dataset_strings
            doc = ''.join([doc,'\n<svg id="',gid,'" version="1.1" '
                               'baseProfile="full" '
                               'xmlns="http://www.w3.org/2000/svg" '
                               'viewBox="0 0 %(w)d %(h)d">\n'
                               '<rect x="0" y="0" width="100%%" height="100%%" '
                               'fill="none" stroke="black" stroke-width="0.25%%"/>'
                               '<text id="bar1txt" x="7%%" y="7%%" '
                               'font-family="Verdana" font-size="750">\n'
                               '%(t)s\n</text>'
                               %{'w':viewbox_w ,'h':viewbox_h,'t':title}
                         ])
            # axes
            labelTextSize = int(min_extent*0.06)
            doc = ''.join([doc, '\n   <line x1="%(xo)d" y1="%(yo)d" x2="%(xe)d" y2="%(yo)d" stroke="black" stroke-width="%(lw)d"/>'
                                '\n   <line x1="%(xo)d" y1="%(yo)d" x2="%(xo)d" y2="%(ye)d" stroke="black" stroke-width="%(lw)d"/>'
                                '\n   <text x="%(lx)d" y="%(ly)d" font-family="Verdana" font-size="%(fs)d"'
                                ' transform="rotate(-90 %(rx)d,%(ry)d)">%(lt)s</text>'
                               % {'xo':axisXOrigin, 'yo':axisYOrigin, 'xe':axisXExtent, 'ye':axisYExtent
                                 ,'lx':viewbox_h-axisYLabelY, 'ly':viewbox_h, 'lw':axisLineWidth
                                 ,'rx':axisYLabelX, 'ry': viewbox_h-labelTextSize
                                 ,'fs':labelTextSize, 'lt':graphspec['units']
                                 }
                         ])
            # Y-axis marks
            yAxisNumberOfGradations = 10
            labelFontSize = int(viewbox_h*0.02)
            for i in range(yAxisNumberOfGradations+1):
              markFraction = i/float(yAxisNumberOfGradations)
              yAxisMarkPos = axisYOrigin - int(axisYLen*markFraction)
              yAxisMarkValue = maxValue*markFraction
              doc = ''.join([doc, '\n   <line x1="%(xo)d" y1="%(ym)d" x2="%(ymxe)d" y2="%(ym)d" stroke="black" stroke-width="%(lw)d"/>'
                                  '\n   <text x="%(xot)d" y="%(ymt)d" font-family="Verdana" font-size="%(fs)d">%(v)02d</text>'
                                  % {'xo':axisXOrigin, 'ym':yAxisMarkPos, 'ymxe':axixYMarkXExtent
                                    ,'xot':axixYMarkTextX, 'ymt':yAxisMarkPos+axixYMarkTextYOffset
                                    ,'lw':axisLineWidth ,'v':yAxisMarkValue, 'fs':labelFontSize}
                           ])
              
              colourIndex = 0
              barX = axisXOrigin + axisLineWidth
              barYOrigin = axisYOrigin - axisLineWidth
              textSize = barWidth-2 if barWidth>min_extent*0.005 else min_extent*0.005
              barHeightScale = float(axisYLen)/float(maxValue)
              for member, value in groupValues.items():
                colour = colours[colourIndex]              
                barHeight = int(value*barHeightScale)
#                self.debug("barHeight(%(h)d) = (value(%(v)f)*barHeightScale(%(s)f))"
#                            %{'h':barHeight, 'v':value, 's':barHeightScale})
                barY = axisYOrigin - barHeight
                doc = ''.join([doc, '\n   <rect id="%(i)s"  fill="%(c)s" x="%(x)d" y="%(y)d" width="%(w)d" height="%(h)d"/>'
                                    '\n   <text x="%(lx)d" y="%(ly)d" font-family="Verdana" font-size="%(fs)d"'
                                    ' transform="rotate(-90 %(rx)d,%(ry)d)">%(lt)s</text>'
                                    % {'i':member, 'c':colour
                                      ,'x':barX, 'y':barY, 'w':barWidth, 'h':barHeight
                                      ,'lx':barX, 'ly':barYOrigin+textSize
                                      ,'rx':barX, 'ry': barYOrigin
                                      ,'fs':textSize, 'lt':member
                                      }
                             ])
                barX = barX + barWidth
                colourIndex = (colourIndex + 1)%len(colours)
            doc = '\n'.join([doc,'<\svg>'])
          doc = '\n'.join([doc,'<\div>'])
        doc = '\n'.join([doc,graph_store['main']['epilogue']])
      except:
        for file in libs:
          file.close()
        raise
      if unresolved:
        errorMessage = "BarChartDocumentLinker.build_afterElementsActions: Unresolved names:"
        for name in unresolved:
          errorMessage = ''.join([errorMessage, '\n   ', name])
        self.error(errorMessage)
      else:
        with open(str(self),'w') as docFile:
          docFile.write(doc)
class DirectoryComponent(Component):
  '''
  A simple sub-type of Component that ensures directories are created if
  they do not exist regardless of action so long as an action query function
  calls doesNotExist.
  '''
  def __init__(self, name, attributes, elements=[], logger=None):
    super().__init__(name,attributes,elements,logger)

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

class GroupDataArchiveFile(FileComponent):
  def __init__(self, name, attributes, elements=[], logger=None):
    super().__init__(name,attributes,elements,logger)

# for demonstration purposes only re-build the library if it
# does not exist - do not check to see if it has changed
# this is probably not what would be wanted in a 'real-world' case!
# Note: Assemblage does not support isOutOfDate, doesNotExist or hasChanged
#       More stuff to think on
  def build_queryProcessElements(self):
  # only pass build action application on to elements if the library file(-set) does not exist.
    return self.doesNotExist() 
  def doesNotExist(self):
    does_not_exist = not os.path.exists('.'.join([str(self),'dat'])) # shelves use 3 files .dat, .bak and .dir
    self.debug("Target file '%(f)s' does not exist? %(b)s" % {'f':str(self), 'b':does_not_exist})
    return does_not_exist
  def isOutOfDate(self):
    return False # don't bother re-building just in case library source has changed

class SystemTestGraphsFromCSVData(unittest.TestCase):
  def test_build_from_Python_objects_element_processors(self):
    original_data_dir = os.path.abspath('./download')
    source_dir = os.path.abspath('./source')
    build_dir = os.path.abspath('./build')
    lib_dir = os.path.abspath('./lib')
    graph_source_dir = './graph-source'
    doc_dir = './doc'
    sales_original_filestem = 'SalesJan2009'
    group_data_lib_filestem = 'group-data'
    sales_original_data = '%(p)s/%(f)s.csv'%{'p':original_data_dir, 'f':sales_original_filestem}
    sales_source_file = '%(p)s/%(f)s.csv'%{'p':source_dir, 'f':sales_original_filestem}
    sales_object_file = '%(p)s/%(f)s.gdo'%{'p':build_dir, 'f':sales_original_filestem}
    group_data_lib_file = '%(p)s/lib-%(f)s.gda'%{'p':lib_dir, 'f':group_data_lib_filestem}
    sales_by_country_avg_graph_filestem = "sales-avg-by-country"
    sales_by_country_avg_graph_src_file = '%(p)s/%(f)s.json'%{'p':graph_source_dir, 'f':sales_by_country_avg_graph_filestem}
    sales_by_country_avg_graph_obj_file = '%(p)s/%(f)s.gpho'%{'p':build_dir, 'f':sales_by_country_avg_graph_filestem}
    sales_by_country_avg_graph_doc_file = '%(p)s/%(f)s.html'%{'p':doc_dir, 'f':sales_by_country_avg_graph_filestem}
    libAssm = Assemblage\
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
              )
    gphAssm = Assemblage\
              (
                plan = Blueprint()
                        .setDigestCache(DigestCache(ShelfDigestStore()))
                        .addElements("group_data_lib_assemblage", libAssm)
                        .addElements(group_data_lib_file, GroupDataArchiveFile
                                    , elements=["group_data_lib_assemblage"]
                                    )
                        .addElements((doc_dir, build_dir),DirectoryComponent)
                        .addElements(sales_by_country_avg_graph_src_file, FileComponent)
                        .addElements(sales_by_country_avg_graph_obj_file, BarChartDescriptionCompiler
                                    , elements=[sales_by_country_avg_graph_src_file, build_dir]
                                    )
                        .addElements(sales_by_country_avg_graph_doc_file, BarChartDocumentLinker
                                    , elements=[sales_by_country_avg_graph_obj_file, group_data_lib_file, doc_dir]
                                    )
                        .setLogger(Blueprint().logger().setLevel(logging.DEBUG))
              ).apply('build')
if __name__ == '__main__':
  unittest.main()
