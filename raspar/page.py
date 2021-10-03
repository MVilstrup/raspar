from bs4 import BeautifulSoup

class Page:
    def __init__(self, url: str, text: str, selector=""):
        self.id = hash(url + selector)
        self.url = url
        self._page = BeautifulSoup(text) if isinstance(text, str) else text
        
    def __getattr__(self, attr):
        if attr in ["id", "url", "_page"]:
            return self.__getattribute__(attr)
        else:
            return self._page.__getattr__(attr)

    def _get_element(self, node):
        # for XPATH we have to count only for nodes with same type!
        length = len(list(node.previous_siblings)) + 1
        if (length) > 1:
            return '%s:nth-child(%s)' % (node.name, length)
        else:
            return node.name

    def _path(self, node):
        path = [self._get_element(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, self._get_element(parent))
        return ' > '.join(path)

    def split_on(self, selector):
        for element in self.select(selector):
            yield Page(self.url, element, self._path(element))