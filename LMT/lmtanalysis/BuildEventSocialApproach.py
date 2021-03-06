'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Social approach" )


def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )
    
    
    approachDico = {}
    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if ( idAnimalA == idAnimalB ):
                continue
            approachDico[idAnimalA, idAnimalB] = EventTimeLineCached( connection, file, "Approach", idAnimalA, idAnimalB, minFrame=tmin, maxFrame=tmax ) 
            
    #cache mean body len
    twoMeanBodyLen = {}
    for idAnimal in range( 1 , pool.getNbAnimals()+1 ):
        twoMeanBodyLen[idAnimal] = 2*pool.animalDictionnary[idAnimal].getMeanBodyLength()

    for idAnimalA in range( 1 , pool.getNbAnimals()+1 ):
        
        for idAnimalB in range( 1 , pool.getNbAnimals()+1 ):
            if( idAnimalA == idAnimalB ):
                continue
            
            eventName = "Social approach"        
            print ( eventName )
            
            socAppTimeLine = EventTimeLine( None, eventName , idAnimalA , idAnimalB , None , None , loadEvent=False )
                           
            result={}
            
            dicA = approachDico[ idAnimalA , idAnimalB ].getDictionnary()
            
            twoMeanBodyLengthB = twoMeanBodyLen[ idAnimalB ]
            
            for t in dicA.keys():
                
                dist = pool.animalDictionnary[idAnimalA].getDistanceTo(t, pool.animalDictionnary[idAnimalB])
                
                if ( dist == None ):
                    continue
                    
                if ( dist >= 0 and dist <= twoMeanBodyLengthB ):
                    
                    result[t]=True
            
            
            socAppTimeLine.reBuildWithDictionnary( result )
            
            socAppTimeLine.endRebuildEventTimeLine(connection)
    
        
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Social Approach" , tmin=tmin, tmax=tmax )

        
    print( "Rebuild event finished." )
        
    