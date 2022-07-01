from osgeo import gdal #need to install gdal library on your local machine
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

csv_input = pd.read_csv('Millbrook1.csv')   # the csv with coordinates of Millbrook Soil Moisture data collecting stations
csv_input2 = pd.read_csv('MB.csv')   # The csv with coordinates of Millbrook Soil Moisture data collecting stations and all recorded data of soil moisture at each station for all 720 days
csv_dates = pd.read_csv('Dates.csv') # all the dates of which Soil Moisture data was collected on at the Millbrook site


#Loop through for all 720 days of data (overwriting the same csv and vrt files to save storage)
for i in range(1,721):
    
    csv_input['moisture'] = csv_input2['Day '+str(i)]      # create a new column called 'moisture' and copy the data from MB.csv's column 'Day + i' into it
    csv_input.to_csv('output.csv', index=False)           # create a new csv file called 'output.csv' with the new column created above

    csv_new = pd.read_csv('output.csv') # read the new csv file created above
    max_index = 19  # the number of stations in the Millbrook site (max number of Soil Moisture data readings in a day since some sations did not collect data for certain days)


    # loop until all the rows/stations with 0 values are removed from the csv
    while(0 in csv_new['moisture'].values):
            j = 0 #index for dropping since it does not update each time when deleting
            m = 0 #index for searching since it updates everytime we delete a row

    
            while(j <= max_index):
                if (csv_new.iloc[m]['moisture'] == 0):   # check if there is a 0 value meaning there was no data collected at that station
                    csv_new.drop([j],axis = 0,inplace=True) # delete the row if there is a 0 value
                    j += 1 # increase the row index by 1 since we have looped through the row
                    max_index -= 1 #decrease max station index by 1 since we deleted 1 station
                else:
                    j += 1 # increase the row index by 1 since we have looped through the row
                    m +=1 #here we have to increase the index since we want to go to the next row and we did not drop the current row
    
            csv_new.to_csv('output.csv',index=False)  #update the output.csv file with the deleted rows
            csv_new = pd.read_csv('output.csv')     #read the output.csv file again
          
    # creates the vrt file for gdal to read
    f = open("output.vrt", "w")
    f.write("<OGRVRTDataSource>\n\
        <OGRVRTLayer name=\"output\">\n\
            <SrcDataSource>output.csv</SrcDataSource>\n\
            <GeometryType>wkbPoint</GeometryType>\n\
            <GeometryField encoding=\"PointFromColumns\" x=\"Longitude\" y=\"Latitude\" z=\"moisture\"/>\n\
        </OGRVRTLayer>\n\
    </OGRVRTDataSource>") 
    f.close()

    #creating the month day and year format for the tiff file name (need this format to later upload these tiff files into google earth engine)
    day = str(int(csv_dates.iloc[i-1][1]))
    month = str(int(csv_dates.iloc[i-1][2]))
    year = str(int(csv_dates.iloc[i-1][3]))
    
    #adds a 0 in front if there is only 1 digit since we want 01 in the date instead of just 1
    if len(day)!= 2: 
        day = '0'+day
    if len(month)!= 2: 
        month = '0' + month

    #rasterize the data we have processed to convert from csv file to a raster file which we can later use in our google earth engine app
    r = gdal.Rasterize('SM'+month+day+year+'.tif', 'output.vrt', outputSRS= 'EPSG:4326', xRes = 0.0009, yRes = -0.0009, attribute = "moisture",noData = np.nan)
    r = None
