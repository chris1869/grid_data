import os
import pandas as pd

import xml.etree.ElementTree as ET

type_converter = {
    "xs:byte": "float",
    "xs:double": "float",
    "xs:float": "float",
    "xs:short": "float",
    "xs:int": "float",
    "xs:long": "float",
    "xs:string": "category",
    "xs:date": "datetime64[ns]",
    "xs:dateTime": "datetime64[ns]"
}

import glob

class MastrReader:
    def __init__(self, description_file, data_dir, result_dir) -> None:
        self.description_file = description_file
        self.data_dir = data_dir
        self.result_dir = result_dir
        self.columns = None
        self.types = None
        self.categories = None
        self.df = None
        self.main_object = description_file.split(".xsd")[0].split("/")[-1]
        self.result_fname = self.result_dir + self.main_object + ".xz"

    def result_exists(self):
        return os.path.exists(self.result_fname)
    
    def store_result(self):
        self.df.to_pickle(self.result_fname)

    def read_xml_description(self):
        tree = ET.parse(self.description_file)
        root = tree.getroot()
        end_type = "xs:sequence"
        if self.main_object in ["EinheitenGeothermieGrubengasDruckentspannung", "EinheitenSolar",
                                "EinheitenVerbrennung", "EinheitenWasser", "Marktakteure"]:
            end_type = "xs:choice"
        sequence = root.find('.//xs:element[@name="%s"]/xs:complexType/xs:sequence/xs:element/xs:complexType/%s' % (self.main_object, end_type),
                            namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        
        elements = sequence.findall('.//xs:element', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
        self.columns = []
        self.types = []
        self.categories = {}
        for element in elements:
            xname = element.attrib["name"]
            self.columns.append(xname)
            if "type" in element.attrib:
                self.types.append(type_converter[element.attrib["type"]])
            else:
                enumerations = element.findall('.//xs:simpleType/xs:restriction/xs:enumeration', namespaces={'xs': 'http://www.w3.org/2001/XMLSchema'})
                self.categories[xname] = []
                for enumeration in enumerations:
                    self.categories[xname].append(int(enumeration.attrib["value"]))
                self.types.append("category")
    
    def list_files_in_chronological_order(self):

        def custom_key(s):
            # Extract the number from the string
            num_str = s.split("_")[-1].split(".xml")[0]
            # Convert the number to an integer
            num = int(num_str)
            # Return the number as the key
            return num
        
        data_fnames = glob.glob(self.data_dir + self.main_object + "*.xml")
        # Sort the list using the custom key
        if (len(data_fnames) > 1):
            data_fnames = sorted(data_fnames, key=custom_key)
        return data_fnames
    
    def read_xml_data(self):
        data_fnames = self.list_files_in_chronological_order()
        dfs = []
        for fname in data_fnames:
            print(fname)
            dfs.append(pd.read_xml(fname, encoding="utf-16"))
        self.df = pd.concat(dfs)
        
        for i, col in enumerate(self.columns):
            if col not in self.df.columns:
                print("Column ", col, "defined in description file but not found in actual data")
                if col in self.categories:
                    del self.categories[col]
                continue
            if "datetime" in self.types[i]:
                #Adapt to german time format and ensure errors are captured as NaT (e.g., 3000-01-01)
                self.df[col] = pd.to_datetime(self.df[col], dayfirst=True, format="ISO8601", errors="coerce")
            else:
                self.df[col] = self.df[col].astype(self.types[i], copy=False)

        for category in self.categories:
            old_cats = list(self.df[category].cat.categories)
            print(old_cats)
            if (type(old_cats[0]) is not str) and max(old_cats) <= 1:
                print("Boolean category not translated", category)
            else:
                if not(set(werte[werte["Id"].isin(old_cats)]["Id"]) - set(self.categories[category])):
                    #Check if all actual categories (left) have actually been mentioned in the description file (right)
                    print("Category ", category, "translated into actual Katalog values")
                    new_cats = werte[werte["Id"].isin(old_cats)][["Id", "Wert"]].set_index("Id").to_dict(orient="dict")["Wert"]
                    self.df[category] = self.df[category].cat.rename_categories(new_cats)
                else:
                    print("Mismatch in ", category, werte[werte["Id"].isin(old_cats)]["Id"], self.categories[category])

    def get_dataframe(self):
        return self.df

fnames = glob.glob("results/MaStR/xsd/*.xsd")
fnames.sort()

ddir = "results/MaStR/data/"
rdir = "results/MaStR/pandas/"

reader = MastrReader("results/MaStR/xsd/Katalogwerte.xsd", data_dir=ddir, result_dir=rdir)
reader.read_xml_description()
reader.read_xml_data()
werte = reader.get_dataframe()

for fname in fnames:
    if "Katalog" in fname:
        continue
    
    reader = MastrReader(fname, data_dir=ddir, result_dir=rdir)
    if not reader.result_exists():    
        reader.read_xml_description()
        reader.read_xml_data()
        reader.store_result()

    del reader