#from flask.json import JSONEncoder as BaseJSONEncoder
from collections import OrderedDict
from datetime import datetime, date
import csv, codecs, cStringIO, re, subprocess

'''
class OrderedJsonEncoder( simplejson.JSONEncoder ):
   def encode(self,o):
      if isinstance(o,OrderedDict.OrderedDict):
         return "{" + ",".join( [ self.encode(k)+":"+self.encode(v) for (k,v) in o.iteritems() ] ) + "}"
      else:
         return simplejson.JSONEncoder.encode(self, o)
'''
'''
class DictSerializable(object):
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result
'''

def num(s, default):
    try:
        return int(s)
    except ValueError:
        return default
        
def shell(command, suppressOutput=True, suppressErrors=False):
    finished = None
    error = None
    output = None
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        finished = output.split('\n')
    except Exception, e:
        error = unicode(e)
        finished = error.split('\n')
    if not suppressOutput or (not suppressErrors and error is not None):    
        for line in finished:
            print line
    return output

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
        
class AutoSerialize(object):
    'Mixin for retrieving public fields of model in json-compatible format'
    __public__ = None

    def get_public(self, exclude=(), extra=()):
        "Returns model's PUBLIC data for jsonify"
        data = {}
        keys = self._sa_instance_state.attrs.items()
        public = self.__public__ + extra if self.__public__ else extra
        for k, field in  keys:
            if public and k not in public: continue
            if k in exclude: continue
            if field.value == None: continue
            value = self._serialize(field.value)
            if value:
                data[k] = value
        return data

    @classmethod
    def _serialize(cls, value, follow_fk=False):
        if type(value) in (datetime, date):
            ret = value.isoformat()
        elif hasattr(value, '__iter__'):
            ret = []
            for v in value:
                ret.append(cls._serialize(v))
        elif AutoSerialize in value.__class__.__bases__:
            ret = value.get_public()
        else:
            ret = unicode(value)

        return ret
        
class LastUpdatedOrderedDict(OrderedDict):
    'Store items in the order the keys were last added'

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)

def ParseUrlCsv(urlVar):
    if urlVar is None:
        return urlVar
    else:
        return urlVar.split(',')
        
#def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
#    return ''.join(random.choice(chars) for _ in range(size))

def UnicodeRegexpEscape(textInput):

    # i am trying this out for postgresql regexp matches 
    # because re.escape() was erroring on CJK and emoji characters
    # perhaps there is a way to tell re.escape() to handle these upper unicode characters
    # in which case, this function could be deprecated
    
    #-- POSIX
    #-- need to be escaped: \$ \^ \* \( \) \+ \= \[ \] \\ \| '' \. \? \{ \} \~
    #-- no escaping needed: ! @ <space> ~ ` # % & _ " : ; , / -    
    output = re.sub( r'([\$\^\*\(\)\+\=\[\]\|\'\.\?\{\}\\])', r'\\\1', textInput)
    return output

def FindWhere(searchList, searchProperties):
    for searchItem in searchList:
        objMatch = True
        for k, v in searchProperties.iteritems():
            if getattr(searchItem, k) != v:
                objMatch = False
                break
        if objMatch == True:
            return searchItem
            break
    return None

def SanitizeURLName(text, keepUnderscores=False):
    text = text.lower().strip()
    if keepUnderscores:
        text = re.sub('[\s]+', '-', text)
    else:
        text = re.sub('[_\s]+', '-', text)
    return text

def json_minify(string, strip_space=True):
    tokenizer = re.compile('"|(/\*)|(\*/)|(//)|\n|\r')
    end_slashes_re = re.compile(r'(\\)*$')

    in_string = False
    in_multi = False
    in_single = False

    new_str = []
    index = 0

    for match in re.finditer(tokenizer, string):

        if not (in_multi or in_single):
            tmp = string[index:match.start()]
            if not in_string and strip_space:
                # replace white space as defined in standard
                tmp = re.sub('[ \t\n\r]+', '', tmp)
            new_str.append(tmp)

        index = match.end()
        val = match.group()

        if val == '"' and not (in_multi or in_single):
            escaped = end_slashes_re.search(string, 0, match.start())

            # start of string or unescaped quote character to end string
            if not in_string or (escaped is None or len(escaped.group()) % 2 == 0):
                in_string = not in_string
            index -= 1 # include " character in next catch
        elif not (in_string or in_multi or in_single):
            if val == '/*':
                in_multi = True
            elif val == '//':
                in_single = True
        elif val == '*/' and in_multi and not (in_string or in_single):
            in_multi = False
        elif val in '\r\n' and not (in_multi or in_string) and in_single:
            in_single = False
        elif not ((in_multi or in_single) or (val in ' \r\n\t' and strip_space)):
            new_str.append(val)

    new_str.append(string[index:])
    return ''.join(new_str)

'''
class JSONEncoder(BaseJSONEncoder):
    """Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        if isinstance(obj, JsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


class JsonSerializer(object):
    """A mixin that can be used to mark a SQLAlchemy model class which
    implements a :func:`to_json` method. The :func:`to_json` method is used
    in conjuction with the custom :class:`JSONEncoder` class. By default this
    mixin will assume all properties of the SQLAlchemy model are to be visible
    in the JSON output. Extend this class to customize which properties are
    public, hidden or modified before being being passed to the JSON serializer.
    """

    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        return rv
'''