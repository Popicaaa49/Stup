import bme280
 
(chip_id, chip_version) = bme280.readBME280ID()
print "Chip ID :", chip_id
print "Version :", chip_version
 
temperature,pressure,humidity = bme280.readBME280All()
 
print "Temperature : ", temperature, "C"
print "Pressure : ", pressure, "hPa"
print "Humidity : ", humidity, "%"
