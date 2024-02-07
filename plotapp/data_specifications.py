'''
"Dic_name": ("title", type(Int, str...), default, params)

type = "string": params = (maxlen, chars)
type = "int": params = (min, max)
type = "float": params = (min, max, digits)
type = "bool": params = ()
type = "list": params = ([title], [value])

    'dic_name': {
        'name': '<name>',
        'type': '<type>',
        'default': '<default>',
        'parameters': None,
        'writable': False
    } 
'''
data_specifications = {
    'speed': {
        'name': 'Scanner speer',
        'type': int,
        'default': 1000,
        'parameters': {'min':0, 'max': 9000},
        'writable': True,
    },
    'axis': {
        'name': 'Axis',
        'type': list,
        'default': 'x', 
        'parameters': (['x axis', 'y axis', 'z axis'], ['x', 'y', 'z']),
        'writable': True
    },
    'height': {
        'name': 'height',
        'type': float,
        'default': 1.60,
        'parameters': {'min': 0.00, 'max': 2.00, 'digits': 3}
    },
    'size': {
        'name': 'size',
        'type': str,
        'default': 'small',
        'parameters': None,
        'writable': True
    },
    'light': {
        'name': 'light',
        'type': bool,
        'default': True,
        'parameters': None,
        'writable': True
    },
    'text': {
        'name': 'text',
        'type': str,
        'default': 'text',
        'parameters': [40, "alphanumeric"],
        'writable': True
    },
}


#print(data['height']['default'])