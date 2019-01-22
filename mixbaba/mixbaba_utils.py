from collections import OrderedDict
import base64
import json
import urllib
import pandas as pd
from scipy.stats import beta
from mixbaba.beta_utils import calc_prob_between
import numpy as np


class MixpanelAPI(object):
    endpoint = 'https://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, token):
        self.token = token

    def request(self, methods, params, http_method='GET', frmt='json'):
        """
            methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
                      will give us http://mixpanel.com/api/2.0/events/properties/values/
            params - Extra parameters associated with method
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


def calc_uplift(beta_1, beta_2) -> float:
    """
    This function calculate the relative uplift of the beta_2 over the beta_1.
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
    :param filters: a dict with the filters to be used in this operation
     (ex. {'properties.assignment': 'control'}, or for no filters {'None': 'All'})
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


def return_zeros_brk(output_template: dict, ab_groups: dict) ->dict:
    for ab_group in ab_groups.values():
        output_template[ab_group + " -- conversions details"] = "None"
    return output_template


def return_zeros_det(output_template: dict) ->dict:
    output_template['Control Impressions'] = 0
    output_template['Control Conversions'] = 0
    output_template['Test Impressions'] = 0
    output_template['Test Conversions'] = 0
    return output_template


def fill_template(comment: str, output_template: OrderedDict, funnel_details: dict) -> OrderedDict:
    output_template['Comment'] = comment
    if 'Breakdowns' in funnel_details.keys():
        ab_groups = funnel_details['AB Groups']
        output_template = return_zeros_brk(output_template, ab_groups=ab_groups)
    output_template = return_zeros_det(output_template)
    return output_template


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
    funnel_id = funnel_details['ID']
    from_date = funnel_details['From Date']
    to_date = funnel_details['To Date']
    i_field = funnel_details['Impression field name']
    c_field = funnel_details['Conversion field name']
    by = funnel_details['By']
    ab_groups = funnel_details['AB Groups']

    discriminant = ""
    cohort = ""
    for i_f, (discriminant_, cohort_) in enumerate(filters.items()):
        if i_f > 0:
            discriminant += '+'
            cohort += '+'
        discriminant += discriminant_
        cohort += cohort_
    output_template = OrderedDict({'Discriminant': discriminant, 'Cohort': cohort, 'CR improvement': 0,
                                   'Probability': 0, 'Comment': " "})

    aggregated_data = get_mixpanel_data(api=api, funnel_id=funnel_id, from_date=from_date, to_date=to_date,
                                        filters=filters, by=by)

    control_group = ab_groups['Control']
    test_group = ab_groups['Test']

    # initialize as if we have not control2 group
    control2_group = 'None'
    control2_present = False
    if "Control2" in ab_groups.keys():
        control2_group = ab_groups['Control2']
        control2_present = True

    try:
        # control
        imps_ctrl = aggregated_data[control_group][i_field]['count']
        convs_ctrl = aggregated_data[control_group][c_field]['count']
        if convs_ctrl < 1:
            output_template = fill_template(comment="Too few data for control option!",
                                            output_template=output_template, funnel_details=funnel_details)
            return output_template
        if control2_present:
            # control2
            imps_ctrl2 = aggregated_data[control2_group][i_field]['count']
            convs_ctrl2 = aggregated_data[control2_group][c_field]['count']

            if convs_ctrl2 < 1:
                print("uno")
                output_template = fill_template(comment="Too few data for second control option!",
                                                output_template=output_template, funnel_details=funnel_details)
                return output_template
            else:
                cr, prob = make_ab_analysis(imps_ctrl, convs_ctrl, imps_ctrl2, convs_ctrl2)
                if np.abs(prob - 0.5) < 0.40:  # 0.45 Number to be studied!!
                    imps_ctrl += imps_ctrl2
                    convs_ctrl += convs_ctrl2
                else:
                    print("due")
                    output_template = fill_template(comment="Too few data for second control option!",
                                                    output_template=output_template, funnel_details=funnel_details)
                    return output_template
        # Test
        imps_test = aggregated_data[test_group][i_field]['count']
        convs_test = aggregated_data[test_group][c_field]['count']
        output_template['Control Impressions'] = imps_ctrl
        output_template['Control Conversions'] = convs_ctrl
        output_template['Test Impressions'] = imps_test
        output_template['Test Conversions'] = convs_test
    except KeyError:
        output_template = fill_template(comment="Too few data!",
                                        output_template=output_template, funnel_details=funnel_details)
        return output_template
    if convs_ctrl < 1 or convs_test < 1:
        output_template = fill_template(comment="Too few data!",
                                        output_template=output_template, funnel_details=funnel_details)
        return output_template
    else:
        cr, prob = make_ab_analysis(imps_ctrl, convs_ctrl, imps_test, convs_test)
        if prob > prob_th:
            output_template['Comment'] = 'Result is OK!'
        else:
            output_template['Comment'] = 'Result is uncertain! Check data'
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

        output_template['CR improvement'] = cr
        output_template['Probability'] = prob
        return output_template


def get_combinations(filters: dict) -> list:
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
