from collections import OrderedDict
import base64
import json
import urllib
import pandas as pd
from scipy.stats import beta
from mixbaba.beta_utils import calc_prob_between
import numpy as np
import warnings
from scipy.stats._continuous_distns import beta_gen

class MixpanelAPI(object):
    endpoint = 'https://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, token):
        self.token = token

    def request(self, methods, params, http_method='GET', frmt='json'):
        """
        This function call the request to the Mixpanel API. Check  http://mixpanel.com/api/2.0/events/properties/values/

        :param methods: List of methods to be joined, e.g. ['events', 'properties', 'values'] will give us
        :param params: Extra parameters associated with method
        :param http_method: self explaining
        :param frmt: the format in which you wnat the output.
        :return: what you asked
        """

        params['format'] = frmt

        request_url = '/'.join([self.endpoint, str(self.VERSION)] + methods)
        if http_method == 'GET':
            data = None
            request_url = request_url + '/?' + self.unicode_urlencode(params)
        else:
            data = self.unicode_urlencode(params)

        headers = {'Authorization': 'Basic ' + base64.b64encode(self.token.encode()).decode()}
        request = urllib.request.Request(request_url, data, headers)
        response = urllib.request.urlopen(request)
        return json.loads(response.read())

    @staticmethod
    def unicode_urlencode(params):
        """
            Convert lists to JSON encoded strings, and correctly handle any
            unicode URL parameters.
        """
        if isinstance(params, dict):
            params = list(params.items())
        for i, param in enumerate(params):
            if isinstance(param[1], list):
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.parse.urlencode(
            [(k, isinstance(v, str) and v.encode('utf-8') or v) for k, v in params]
        )


def get_funnels_list(connector: MixpanelAPI) -> pd.DataFrame:
    """
    This function returns the whole list of funnels in a table containing the funnel ID and the funnel name

    :param connector: the connector to the Mixpanel service
    :return: a pandas DataFrame
    """
    # TODO: change dataframe to simple dict
    flist = connector.request(["funnels/list"], {})
    flist_df = pd.DataFrame(flist)
    flist_df.set_index('funnel_id', inplace=True)
    return flist_df


def aggregate_mix_data(answer: dict) -> dict:
    """
    This function refactor the mixpanel data to have a more consistent dict for our needs

    :param answer: the answer from mixpanel service, as dict
    :return: a dict containing the refactored data
    """
    aggregated = OrderedDict({})

    for date, data in answer.items():
        if data != {}:
            for group, content in data.items():
                for cont in content:
                    if group in aggregated.keys():
                        if cont['step_label'] in aggregated[group].keys():
                            aggregated[group][cont['step_label']]['count'] += cont['count']
                        else:
                            aggregated[group][cont['step_label']] = {}
                            aggregated[group][cont['step_label']]['count'] = cont['count']
                    else:
                        aggregated[group] = OrderedDict({})
                        aggregated[group][cont['step_label']] = {}
                        aggregated[group][cont['step_label']]['count'] = cont['count']
    return aggregated


def calc_uplift(beta_1: beta_gen, beta_2: beta_gen) -> float:
    """
    This function calculate the relative uplift of the beta_2 PDF over the beta_1 PDF.
    Note that the mean value of the PDFs is the number we need, not the peak value.

    :param beta_1: beta function (control)
    :param beta_2: beta function (test)
    :return: the relative uplift
    """
    return (beta_2.mean() - beta_1.mean()) / beta_1.mean()


def make_ab_analysis(imps_1: int, convs_1: int, imps_2: int, convs_2: int) -> (float, float):
    """
    This function return the relative uplift of test w.r.t. control,
    and the probability for test to be greater than control

    :param imps_1: number of impressions for the sample 1
    :param convs_1:  number of conversions for the sample 1
    :param imps_2:  number of impressions for the sample 2
    :param convs_2:  number of conversions for the sample 2
    :return: a tuple, (lift, probability)
    """
    # here we create the Beta functions for the two sets
    a_1, b_1 = convs_1 + 1, imps_1 - convs_1 + 1
    beta_1 = beta(a_1, b_1)
    a_2, b_2 = convs_2 + 1, imps_2 - convs_2 + 1
    beta_2 = beta(a_2, b_2)

    # calculating the lift
    lift = calc_uplift(beta_1, beta_2)

    # calculating the probability for Test to be better than Control
    prob = calc_prob_between(beta_2, beta_1)

    return lift, prob


def get_mixpanel_data(api: MixpanelAPI, funnel_id: int, from_date: str, to_date: str, filters: {}, by: str) -> dict:
    """
    This function gather the data from Mixpanel using the API, eventually divided in cohort using a discriminant.

    :param api: the connector to the Mixpanel
    :param funnel_id: the funnel identifier
    :param from_date: self explaining, string formatted like "2018-01-28"
    :param to_date: self explaining
    :param filters: the filters to be used (ex. {'properties.assignment': 'control'}, or for no filters {'None': 'All'})
    :param by: the string containing the value on which breakdown the cohorts
    :return: a dict with the data
    """

    # the aggregated data will be divided by 'assignment' property (i.e. control, test, etc)
    by_type, by_val = by.split(".")
    req_dict = {
        "funnel_id": funnel_id,
        "from_date": from_date,
        "to_date": to_date,
        "on": f'{by_type}["{by_val}"]',
        'unit': 'month'
    }
    if len(filters) > 0:
        req_filt = ""
        for i_filt, (filt_type, cohort) in enumerate(filters.items()):
            if filt_type != 'None':
                if i_filt > 0:
                    req_filt += " and "
                discr_type, discriminant = filt_type.split('.')
                req_filt += f'("{cohort}" in {discr_type}["{discriminant}"]) ' \
                    f'and (defined ({discr_type}["{discriminant}"]))'
        req_dict["where"] = req_filt
    response_ = api.request(["funnels"], req_dict)

    # since by default the data is divided per month, we need to aggregate it
    return aggregate_mix_data(response_['data'])


def extract_ab_group_names(extracted_ab) -> (list, list):
    """
    This function extract the names of the control groups (up to 2) and test groups (up to nine).
    Note that here the naming convention allows only keywords `control`, `controlN`, `test`, `testN`, with N integer

    :param extracted_ab: the list of the groups
    :return: two lists: one for the control groups, the other for the test groups
    """
    max_test_groups = 9
    control_groups = []
    test_groups = []

    for group in extracted_ab:
        # trying if the word 'control' exist in this group
        splitted_group_c = group.split('control')
        if len(splitted_group_c) > 1:
            if splitted_group_c[1] == '':
                control_groups.append(group)
            else:
                try:
                    gr_n = int(splitted_group_c[1])
                    if gr_n > 2:
                        warnings.warn("Ignoring the group %s" % group)
                    control_groups.append(group)
                except ValueError:
                    warnings.warn("Ignoring the group %s" % group)
        else:
            splitted_group_t = group.split('test')
            if len(splitted_group_t) > 1:
                if splitted_group_t[1] == '':
                    test_groups.append(group)
                else:
                    try:
                        gr_n = int(splitted_group_t[1])
                        if gr_n > max_test_groups:
                            warnings.warn("Ignoring the group %s" % group)
                        test_groups.append(group)
                    except ValueError:
                        warnings.warn("Ignoring the group %s" % group)
    return control_groups, test_groups


def get_numbers(output_template: OrderedDict, where: dict, what: str, field: str, which: str) -> OrderedDict:
    """
    This function simply surrounds the number extraction with a try/except

    :param output_template: the pre-filled OrderedDict where we are going to put the numbers
    :param where: the dict containing the data we are going to extrract
    :param what: the name of the group we are interested in (ex. "control", "test", "test2", etc.)
    :param field: the name assigned to the field (ex. "AB-AB025-IMPRESSION", "Payment", etc.)
    :param which: the name which will result as column name in the final report of MixBABA (ex. "Control Impressions")
    :return: the updated OrderedDict
    """

    try:
        num = where[what][field]['count']
        output_template[which] = num
    except KeyError:
        output_template[which] = np.nan
    return output_template


def create_fg_names(filters: dict) -> (str, str):
    """
    This function simply create the names of the filter(s) which will be used in the final table

    :param filters: a dict containing the filters in the format: {"user.goal": "PREVENT", "user.$country_code": "US"}
    :return: two strings; following the example: "user.goal+user.$country_code", "PREVENT+US"
    """

    discriminant = ""
    cohort = ""
    for i_f, (discriminant_, cohort_) in enumerate(filters.items()):
        if i_f > 0:
            discriminant += '+'
            cohort += '+'
        discriminant += discriminant_
        cohort += cohort_
    return discriminant, cohort


def analyze_funnel(api: MixpanelAPI, filters: dict, funnel_details: dict,
                   prob_th: float = 0.95) -> OrderedDict:
    """
    This function gather the data, makes the analysis and output the result for the given funnel.

    :param api: the connector to the Mixpanel
    :param filters: the filters to be used in this analysis
    :param funnel_details: the dict with the details of the funnel
    :param prob_th: optional, the probability threshold to accept the hypothesis
    :return: an OrderedDict containing the processed data
    """

    # extracting the relevant data
    funnel_id = funnel_details['ID']
    from_date = funnel_details['From Date']
    to_date = funnel_details['To Date']
    i_field = funnel_details['Impression field name']
    c_field = funnel_details['Conversion field name']
    by = funnel_details['By']
    manual_ab_names = True
    ab_groups = {}

    discriminant, cohort = create_fg_names(filters)

    output_template = OrderedDict({'Discriminant': discriminant, 'Cohort': cohort, 'Comment': " "})

    aggregated_data = get_mixpanel_data(api=api, funnel_id=funnel_id, from_date=from_date, to_date=to_date,
                                        filters=filters, by=by)

    try:
        ab_groups = funnel_details['AB Groups']
    except KeyError:
        # if the names of the groups are not inserted, we will extract them from the gathered data
        manual_ab_names = False

    # initialize as if we have not control2 group
    control2_g_name = 'None'
    control2_present = False
    if manual_ab_names:
        control_g_name = ab_groups['Control']
        # TODO foresee a manual selection of other test groups
        _test_group = ab_groups['Test']
        test_groups = [_test_group]
        if "Control2" in ab_groups.keys():
            control2_g_name = ab_groups['Control2']
            control2_present = True
    else:
        # we have to extract the groups name

        funnel_details['AB Groups'] = {}

        extracted_ab = aggregated_data.keys()
        control_groups, test_groups = extract_ab_group_names(extracted_ab)

        # TODO: spawn control groups name based on the lists just created
        control_g_name = 'control'
        if len(control_groups) > 2:
            control2_g_name = 'control2'
            control2_present = True

            funnel_details['AB Groups']['Control2'] = control2_g_name

        funnel_details['AB Groups']['Control'] = control_g_name

        for i, test_g_name in enumerate(test_groups):
            if i == 0:
                funnel_details['AB Groups']['Test'] = test_g_name
            else:
                funnel_details['AB Groups']['Test%d' % (i+1)] = test_g_name

    which = "Control Impressions"
    output_template = get_numbers(output_template=output_template, where=aggregated_data, what=control_g_name,
                                  field=i_field, which=which)
    imps_ctrl = output_template[which]

    which = "Control Conversions"
    output_template = get_numbers(output_template=output_template, where=aggregated_data, what=control_g_name,
                                  field=c_field, which=which)
    convs_ctrl = output_template[which]

    if control2_present:

        which = "Control2 Impressions"
        output_template = get_numbers(output_template=output_template, where=aggregated_data, what=control2_g_name,
                                      field=i_field, which=which)
        imps_ctrl2 = output_template[which]

        which = "Control2 Conversions"
        output_template = get_numbers(output_template=output_template, where=aggregated_data, what=control2_g_name,
                                      field=c_field, which=which)
        convs_ctrl2 = output_template[which]

        cr, prob = make_ab_analysis(imps_ctrl, convs_ctrl, imps_ctrl2, convs_ctrl2)
        if np.abs(prob - 0.5) < 0.40:  # 0.40 Number to be studied!!
            # the two control options are compatible, so we can sum up the numbers
            imps_ctrl += imps_ctrl2
            convs_ctrl += convs_ctrl2
        else:
            output_template['Comment'] = "The two control options appear different!"
            return output_template

    # Tests groups
    for test_g_name in test_groups:
        which = f"{test_g_name} Impressions"
        output_template = get_numbers(output_template=output_template, where=aggregated_data, what=test_g_name,
                                      field=i_field, which=which)
        imps_test = output_template[which]

        which = f"{test_g_name} Conversions"
        output_template = get_numbers(output_template=output_template, where=aggregated_data, what=test_g_name,
                                      field=c_field, which=which)
        convs_test = output_template[which]

        if convs_test < 1:
            output_template['Comment'] += "No conversions for %s!" % test_g_name
            # TODO: check what happens with breakdowns!
        else:
            cr, prob = make_ab_analysis(imps_ctrl, convs_ctrl, imps_test, convs_test)
            if prob > prob_th:
                output_template['Comment'] += 'Result for %s is OK! ' % test_g_name
            else:
                output_template['Comment'] += 'Result for %s is uncertain.' % test_g_name
            if 'Breakdowns' in funnel_details.keys():
                for ab_group in ab_groups.values():
                    # 'By' become a filter:
                    filters = {by: ab_group}
                    for brk_type, _ in funnel_details['Breakdowns'].items():
                        filters[discriminant] = cohort
                        aggregated_data = get_mixpanel_data(api=api, funnel_id=funnel_id, from_date=from_date,
                                                            to_date=to_date, filters=filters, by=brk_type)
                        conversions = {}
                        for d_key, d_val in aggregated_data.items():
                            conversions[d_key] = d_val[c_field]['count']
                        output_template[ab_group + " -- conversions details"] = conversions

            output_template['%s CR improvement' % test_g_name] = cr
            output_template['%s Probability' % test_g_name] = prob
    return output_template


def get_combinations(filters: dict) -> list:
    """
    Given that the cross-filtering option has been specified, this function create the combinations of the filters.

    :param filters: a dict containing the filters
    :return: a list with all the combinations
    """
    unrolled_filters = [[discriminant + ':' + cohort for cohort in cohorts] for discriminant, cohorts in
                        filters.items()]
    combinations = np.array(np.meshgrid(*unrolled_filters)).T.reshape(-1, len(filters))
    comb_dicted = []
    for comb in combinations:
        tmb_comb = {}
        for flt_val in comb:
            tmp_flt, tmp_val = flt_val.split(":")
            tmb_comb[tmp_flt] = tmp_val
        comb_dicted.append(tmb_comb)
    return comb_dicted
