from shapely.geometry import shape


__author__ = 'spousty'

from fiona import collection
from pyproj import transform, Proj

import logging

def projectPolygon(fromProj, toProj, inputGeom):
    try:
        new_coords = []
        for ring in inputGeom:
            print "before try"
            try:
                x2, y2 = transform(fromProj, toProj, *zip(*ring))
                new_coords.append(zip(x2, y2))
            except TypeError as te:
                print te.message

        print len(new_coords)
        return new_coords
    except Exception, e:
        logging.exception("Error transforming feature %s:", new_coords)




#def projectLine(fromProj, toProj, inputGeom):



#def projectPoint(fromProj, toProj, inputGeom):


def getIntersections(clip, toBeClipped, outputDir):
    '''
    This method uses shapely's intersects method and saves the files out to an output directory.
    Here is the definition of intersects in shapely:
    "Returns True if the boundary and interior of the object intersect in any way with those of the other."
    '''

    featuresToWrite = []

    #read the both files in using fiona
    with collection(clip, "r") as clipColl:
        schema = clipColl.schema.copy()

        with collection(toBeClipped) as clippedColl:
            print clippedColl.name
            geomType = clippedColl.schema['geometry']
            ##create our output shapefile
            outPath =  outputDir + '/' + clippedColl.name + '_final.shp'
#            outputFile = collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy, {'init': 'epsg=4326', 'no_defs': True}  )

            with collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy(), {'init': 'epsg:4326'} ) as output:

                for clipFeature in clipColl:

                    for intersectCheck in clippedColl:
                        clipShape = shape(clipFeature['geometry'])
                        intersectShape = shape(intersectCheck['geometry'])
                        if clipShape.intersects(intersectShape):
                            featureGeom = intersectCheck['geometry']['type']
                            #winner winner chicken dinner the shapes intersect
                            #first project to our new geo

                            if 'Polygon' == featureGeom:
                                newPolygon  = [ ]
                                newPolygon.append(projectPolygon(Proj(clippedColl.crs), Proj(output.crs),intersectCheck['geometry']['coordinates']))
                                intersectCheck['geometry']['coordinates'] = newPolygon
                                output.write(intersectCheck)

                            elif 'MultiPolygon' == featureGeom:
                                ##need to split the geometry and put it back together before saving
                                newPolygons = []
                                for geom in intersectCheck['geometry']['coordinates']:
                                    print str(type(geom)) + " :: " +str(geom)
                                    newPolygons.append(projectPolygon(Proj(clippedColl.crs), Proj(output.crs),geom))
                                intersectCheck['geometry']['coordinates'] = newPolygons
                                ##########output.write(intersectCheck)

                            elif 'LineString' == featureGeom:
                                True
                            elif 'MultiLineString' == featureGeom:
                                True
                            elif 'Point' == featureGeom:
                                True
                            else:
                                print '!!!!!!!!!!!!!!' + featureGeom


