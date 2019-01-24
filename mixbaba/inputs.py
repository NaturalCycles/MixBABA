from argparse import ArgumentParser


def parse_args():
    """
    parser.add_argument("-f", "--funnels", help="The JSON file with the details about the funnels to be analyzed",
                        required=True)
    parser.add_argument("-k", "--key", help="The key to authenticate within Mixpanel",
                        required=True)
    :return:
    """
    parser = ArgumentParser()
    parser.add_argument("-f", "--funnels", help="The JSON file with the details about the funnels to be analyzed",
                        required=True)
    parser.add_argument("-k", "--key", help="The key to authenticate within Mixpanel",
                        required=True)
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                        help="increase output verbosity (max: -v)")
    parser.add_argument("-o", "--output", help="The form in which you want to get the output",
                        choices=["terminal", "csv", 'both'], default="terminal")
    parser.add_argument("-of", "--output_format", help="The format in which the output will be visualized/recorded",
                        choices=["long", 'short'], default="short")
    parser.add_argument("-x", "--crossed_filters", action='store_true',
                        help="Whether or not run with filters combinations")

    return parser
