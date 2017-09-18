import org.apache.commons.csv.CSVFormat
import org.apache.commons.io.FileUtils
import java.io.File
import java.io.FileReader


fun main(args: Array<String>) {
    println("Hello world")
    val input = FileReader("souradnice.csv")
    val records = CSVFormat.RFC4180.parse(input).filterIndexed { index, _ -> index > 0 }
    val locations = mutableListOf<Location>()
    for (record in records) {
        val psc = record.get(6).toInt()
        val latitude = record.get(7).toDouble()
        val longitude = record.get(8).toDouble()
        val town = record.get(0)
        val townCode = record.get(1).toInt()
        locations.add( Location(lat = latitude, lon = longitude, town = town, psc = psc, townCode = townCode))
    }
    println("Locations loaded")
    val lines = FileUtils.readLines(File("../legal_loto.csv"), "UTF-8")
    val header = lines.first() + ",lat,lon,ruian\n"
    val output = File("../legal_loto_with_locations.csv")
    FileUtils.write(output, header, "UTF-8")
    lines.forEachIndexed { index, line ->
        if (index > 0) {
            val split = line.split(",")
            val psc = split[0].toInt()
            val town = split[1]
            val location = locations.findByPscAndTown(psc, town)
            FileUtils.write(output, line+","+location.lat+","+location.lon+","+location.townCode+"\n", "UTF-8", true)
        }
    }
    println("DONE!")
}

private fun List<Location>.findByPscAndTown(psc: Int, town: String): Location {
    return this.find { it.town == town && it.psc == psc } ?: findByPsc(psc, town)
}

private fun List<Location>.findByPsc(psc: Int, town: String): Location {
    return this.find { it.psc == psc } ?: findByTown(town)
}

private fun List<Location>.findByTown(town: String): Location {
    return this.find { it.town == town } ?: throw RuntimeException("Town $town not found")
}

data class Location(val town: String, val psc: Int, val lat: Double, val lon: Double, val townCode: Int)