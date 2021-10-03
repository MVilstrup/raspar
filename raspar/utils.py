from furl import furl

def recursive_expansion(all_elements, validation):
    if validation(all_elements):
        return [all_elements]
    else:
        try:
            iter(all_elements)
        except:
            return []
        
        correct_elements = []
        for element in all_elements:
            correct_elements += recursive_expansion(element)
        
        return correct_elements


def url_maker(url, base_url):
    pass