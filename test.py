import SCL.Part21 as p21
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
def test_debug():
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    s = open('models/1.stp', 'r').read()
    parser = p21.Parser()

    try:
        r = parser.parse(s, debug=1)
    except SystemExit:
        pass

    return (parser, r)

test_debug()