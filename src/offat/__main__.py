from argparse import ArgumentParser


from .config_data_handler import validate_config_file_data
from .tester.tester_utils import generate_and_run_tests
from .openapi import OpenAPIParser
from .utils import get_package_version, headers_list_to_dict, read_yaml


def banner():
    print(r'''
      _/|       |\_
     /  |       |  \
    |    \     /    |
    |  \ /     \ /  |
    | \  |     |  / |
    | \ _\_/^\_/_ / |
    |    --\//--    |
     \_  \     /  _/
       \__  |  __/
          \ _ /
         _/   \_   
        / _/|\_ \  
         /  |  \   
          / v \
          OFFAT
    ''')


def start():
    '''Starts cli tool'''
    banner()

    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f', '--file', dest='fpath', type=str,
                        help='path or url of openapi/swagger specification file', required=True)
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {get_package_version()}')
    parser.add_argument('-rl', '--rate-limit', dest='rate_limit',
                        help='API requests rate limit. -dr should be passed in order to use this option', type=int, default=None, required=False)
    parser.add_argument('-dr', '--delay-rate', dest='delay_rate',
                        help='API requests delay rate in seconds. -rl should be passed in order to use this option', type=float, default=None, required=False)
    parser.add_argument('-pr', '--path-regex', dest='path_regex_pattern', type=str,
                        help='run tests for paths matching given regex pattern', required=False, default=None)
    parser.add_argument('-o', '--output', dest='output_file', type=str,
                        help='path to store test results in specified format. Default format is html', required=False, default=None)
    parser.add_argument('-of', '--format', dest='output_format', type=str, choices=[
                        'json', 'yaml', 'html', 'table'], help='Data format to save (json, yaml, html, table). Default: table', required=False, default='table')
    parser.add_argument('-H', '--headers', dest='headers', type=str,
                        help='HTTP requests headers that should be sent during testing eg: User-Agent: offat', required=False, default=None, action='append', nargs='*')
    parser.add_argument('-tdc', '--test-data-config', dest='test_data_config',
                        help='YAML file containing user test data for tests', required=False, type=str)
    parser.add_argument('-p', '--proxy', dest='proxy',
                        help='Proxy server URL to route HTTP requests through (e.g., "http://proxyserver:port")', required=False, type=str)
    parser.add_argument('-ns', '--no-ssl', dest='no_ssl', help='Ignores SSL verification when enabled',
                        action='store_true', required=False)  # False -> ignore SSL, True -> enforce SSL check
    args = parser.parse_args()

    # convert req headers str to dict
    headers_dict: dict = headers_list_to_dict(args.headers)

    # handle rate limiting options
    rate_limit = args.rate_limit
    delay_rate = args.delay_rate

    # if any is not set, then set both to None
    if (rate_limit and not delay_rate) or (not rate_limit and delay_rate):
        rate_limit = None
        delay_rate = None

    # handle test user data config file
    test_data_config = read_yaml(args.test_data_config)
    test_data_config = validate_config_file_data(test_data_config)

    if not test_data_config:
        test_data_config = None

    # parse args and run tests
    api_parser = OpenAPIParser(args.fpath)
    generate_and_run_tests(
        api_parser=api_parser,
        regex_pattern=args.path_regex_pattern,
        output_file=args.output_file,
        output_file_format=args.output_format,
        req_headers=headers_dict,
        rate_limit=rate_limit,
        delay=delay_rate,
        test_data_config=test_data_config,
        proxy=args.proxy,
        ssl=args.no_ssl,
    )


if __name__ == '__main__':
    start()
