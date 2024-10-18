from pprint import pprint

class DetailedDump:
    @staticmethod
    def detailed_dump(obj):
        print(f"Object type: {type(obj)}")
        print("\nObject attributes and methods:")
        pprint(dir(obj))
        
        if hasattr(obj, '__dict__'):
            print("\nInstance variables:")
            pprint(vars(obj))