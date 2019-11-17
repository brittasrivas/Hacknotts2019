__author__ = "Bethany Ebel and Brittame Srivas"

"""
Round To One with Capital One

For every transaction made on a Capital One credit card account, we calculate the round-up value to the nearest pound 
and return this donation value plus a charitable organisation that fit the customer's specified criteria. 

Additionally, we assess the risk score of the account holder. If the customer has a good risk score, we provide the 
above mentioned service. If the customer has a bad risk score, we suggest money management advice services they could
benefit from.

API's used:
Capital One: https://developer.capitalone.co.uk/api/customer/index.html#introduction
CharityBase: https://charitybase.uk/api-portal

All code below relating to Capital One's API written by Brittame Srivas
All code below relating to CharityBase API written by Bethany Ebel

We welcome any feedback/ comments!

Created on 16/11/2019
"""

import requests
import math
from decimal import *
import random

getcontext().prec = 2 # Used to accurately give monetary values to 2 decimal places

def check_risk_score(account_id):
    """
    Finds the risk score of the account and classes either donator or advisee.
    :param account_id:
    :return: class of either 'donator' or 'advisee'
    """
    account_get_url_part1 = "https://sandbox.capitalone.co.uk/developer-services-platform-pr/api/data/accounts/"
    account_get_url = account_get_url_part1 + account_id
    account_get_response = requests.get(account_get_url, headers=capitalone_request_header_dict)

    account_output = account_get_response.json()
    risk_score = account_output['Accounts'][0]['riskScore']
    #print(account_output)
    print("Account risk score is: ", risk_score)
    
    if int(risk_score) > 70:
        customer_type = "advisee"
    else:
        customer_type = "donator"

    return customer_type


def create_transaction(account_id):
    """
    Creates a transaction on the specified account.

    :param account_id:
    :return: created_transaction_id
    """

    create_transaction_url_part1 = "https://sandbox.capitalone.co.uk/developer-services-platform-pr/api/data/transactions/accounts/"
    create_transaction_url_part2 = "/create"
    create_transaction_url = create_transaction_url_part1 + account_id + create_transaction_url_part2

    # Number of transactions to create - default 1
    quantity = '{"quantity": "1"}'  # Creates transaction/s on specified account_id
    create_transaction_response = requests.post(url=create_transaction_url, headers=capitalone_request_header_dict, data=quantity)

    create_transaction_output = create_transaction_response.json()
    #print(create_transaction_output)
    created_transaction_id = create_transaction_output['Transactions'][0]['transactionUUID']
    #print(created_transaction_id)

    return created_transaction_id



def find_donation_amount(account_id, transaction_id):
    """
    Find the transaction, check it was successful, verify it was GBP, find exact amount to donate using Decimal.

    :param account_id:
    :param transaction_id:
    :return: amount to donate
    """
    transaction_get_url_part1 = "https://sandbox.capitalone.co.uk/developer-services-platform-pr/api/data/transactions/accounts/"
    transaction_get_url_part2 = "/transactions/"

    transaction_get_url = transaction_get_url_part1 + account_id + transaction_get_url_part2 + transaction_id

    transaction_get_response = requests.get(transaction_get_url, headers=capitalone_request_header_dict)

    #print(transaction_get_response.status_code)

    transaction_output = transaction_get_response.json()

    # print(transaction_output)

    if transaction_output['status'] == "Successful" and transaction_output['currency'] == "GBP":
        transaction_amount = transaction_output['amount']
        donation_amount = Decimal(Decimal(math.ceil(transaction_amount)) - Decimal(transaction_amount))
        print("Transaction amount was: ", transaction_amount)

        return donation_amount

    else:
        print("Transaction status is not successful yet or not a GBP account. So not eligible for donation.")


def get_customer_area(account_id):
    """
    :param account_id:
    :return: the area the customer lives in
    """
    account_get_url_part1 = "https://sandbox.capitalone.co.uk/developer-services-platform-pr/api/data/accounts/"
    account_get_url = account_get_url_part1 + account_id
    account_get_response = requests.get(account_get_url, headers=capitalone_request_header_dict)

    account_output = account_get_response.json()
    customer_address = account_output['Accounts'][0]['homeAddress']
    customer_address_list = customer_address.split(",")
    customer_area = customer_address_list[1].lstrip()

    return customer_area


def find_charitybase_searchterm(charity_cause):
    """

    :param charity_cause:
    :return: search_term to use when searching in CharityBase
    """
    if charity_cause == "local area":
        search_term = get_customer_area(account_id)
    elif charity_cause == "most effective charity":
        search_term = "Malaria Consortium"
    elif charity_cause == "animal welfare":
        search_term = "animal"
    elif charity_cause == "mental health":
        search_term = "mental"
    elif charity_cause == "cancer":
        search_term = "cancer"
    elif charity_cause == "disability":
        search_term = "disability"
    elif charity_cause == "random":
        cause = charity_causes[random.randint(0,len(charity_causes)-2)]
        search_term = find_charitybase_searchterm(cause)
    return search_term


def findCharity(searchTerm, number):
    """
    Find most relevant charities in CharityBase for a given search term.
    :param searchTerm:
    :param number: number of charities to display which match the search term
    :return:
    """
    
    request_header_dict = {
    'Authorization': 'Apikey 1c6a358a-6144-4669-a985-90a0488d15a7'
    }
    
    str1 = "https://charitybase.uk/api/graphql?query={CHC{getCharities(\
    filters:{search:\""
    str2 = "\"}){count list(limit: "
    str3= "){orgIds{id} names{value} activities geo{region}}}}}"
    
    url = str1 + searchTerm + str2 + str(number) + str3
    response = requests.get(url, headers=request_header_dict)
    data = response.json()

    # We retrive charity name, description and region
    for item in data['data']['CHC']['getCharities']['list']: # Iterate through elements
        
        itemId = item['orgIds'][0]['id'] # Charity commission id
        itemName = item['names'][0]['value']
        itemSummary = item['activities']
        itemRegion = item['geo']['region']
        print("\nCharity: {} \nCharity Commission ID: {}\nRegion: {} \
              \nDescription: \n{}\n".format(itemName, itemId, itemRegion, \
              itemSummary))


#####################################################################################################################





charity_causes = ["local area", "most effective charity", "animal welfare", "mental health", "cancer", "disability", "random"]


#SET AUTH KEY
capitalone_auth_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJuYmYiOjE1NzM4MjM4MjQsInBsYyI6IjVkY2VjNzRhZTk3NzAxMGUwM2FkNjQ5NSIsImV4cCI6MTU3NDAzNTE5OSwiZGV2ZWxvcGVyX2lkIjoiMjdmZGVhNzA0Y2U3ODNiZTA5MWJlNzViM2Q0NmM4OTI1N2VjNTI5MDIwMDkwM2U0OTNiN2EzMWUxN2U2Nzc2YSJ9.YR4eZOaOxJhVbwuWjl4z4QJoYvQESAvTvs3PXsAsAn-X4tLqctE_GsG8EcKCbelyXZthSyZkG-wUWhChNrehJGKlfTymcqro2ztfPVKDJA9KhV6k90aaMmzClLx1E1dx38pIjsnhmiit2azg9ng8M7RoAyD1aoZOU2uzk37WdEYPUlcEJjTfERSGknrH2vrNd1IKNMw37gT4gfsKVwBlpELYjHjT2XIFNrKRTXasq1BspXPeRJ0Bh0JBNL94MV5nhaGQHFw013u4ZC9U7VUk3uua2kKu4lpreEWfyMYlbHWpcMI_FzL2tLBV5fIidoZq30zewmyn9J5yzEFkw-APqg"


capitalone_request_header_dict = {
    'Authorization': 'Bearer ' + capitalone_auth_key,
    'Content-type':'application/json',
    'version': '1.0'
    }

# Find all my accounts
accounts_get_response = requests.get("https://sandbox.capitalone.co.uk/developer-services-platform-pr/api/data/accounts", headers=capitalone_request_header_dict)
#print(accounts_get_response.status_code)

accounts_output = accounts_get_response.json()
#print(accounts_output)

# SET ACCOUNT ID
account_id = accounts_output['Accounts'][1]['accountId']
print("Account ID is: ", account_id)

customer_area = get_customer_area(account_id)
#print("Customer's local area is: ", customer_area)

# Create a transaction on that account
transaction_id = create_transaction(account_id)


customer_type = check_risk_score(account_id)
print("Customer type is: ", customer_type, "\n")



if customer_type == "donator":
    roundup_limits = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    roundup_limit = roundup_limits[random.randint(0,len(roundup_limits)-1)]
    print("Customer's round-up limit is: ",roundup_limit, "\n")   
    donation_amount = find_donation_amount(account_id, transaction_id)
    if (donation_amount != None):
        if (donation_amount < roundup_limit):
            print("Customer donation amount is: ", donation_amount)
            charity_cause = "random" # NOTE: currently set to random
            charitybase_searchterm = find_charitybase_searchterm(charity_cause)
            print("Chosen charitable cause is: ", charitybase_searchterm)
            findCharity(charitybase_searchterm, 1)
        else:  
            print("Possible donation amount: ", donation_amount)
            print("No donation made because possible donation amount > round-up limit")
elif customer_type == "advisee":
    charitybase_searchterm = "Frontline Debt Advice"
    findCharity(charitybase_searchterm, 1)

