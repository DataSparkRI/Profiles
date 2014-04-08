import zipfile
import os

def unzip_file(src_zip, destination):
        """ Unzip src_zip to destination
            Return the name of the shape file in the directory or None if one is not found
        """
        zf = zipfile.ZipFile(src_zip)
        shp_file_name = None
        for name in zf.namelist():
            if os.path.splitext(name)[1] == ".shp":
                shp_file_name = name
            outfile = open(os.path.join(destination, name), 'wb')
            outfile.write(zf.read(name))
            outfile.close()

        return shp_file_name

