from TagsParser import *
import unittest

class TagsParserTest(unittest.TestCase):
    def test_appmodule_kt(self):
        functions = ["provideContext","providesPreferenceStorage","providesWifiManager","providesConnectivityManager",
         "providesClipboardManager","providesMainThreadHandler","providesAnalyticsHelper","provideAgendaRepository"
         ,"providesAppDatabase"]
        pcf = ParserCtagsFile(r"./TestingFiles/AppModule.kt.tags")
        items = pcf.get_all()
        for item in items:
            if item.type_name == "m":
                functions.remove(item.field_name)
        print(len(functions))

if __name__ == '__main__':
    unittest.main()