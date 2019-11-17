import requests

# Finds most relevant charities for search
def findCharity(searchTerm, number):
    #  Number specifies how many charities to find
    
    request_header_dict = {
    'Authorization': 'Apikey 1c6a358a-6144-4669-a985-90a0488d15a7'
    }
    
    str1 = "https://charitybase.uk/api/graphql?query={CHC{getCharities(\
    filters:{search:\""
    str2 = "\"}){count list(limit: "
    str3= "){orgIds{id} names{value} activities geo{region}}}}}"
    
    url = str1 + searchTerm + str2 + str(number) + str3
    print(url)
    response = requests.get(url, headers=request_header_dict)
    data = response.json()

    # We retrive charity name, description and region
    for item in data['data']['CHC']['getCharities']['list']: # Iterate through elements
        
        itemId = item['orgIds'][0]['id'] # Charity commission id
        itemName = item['names'][0]['value']
        itemSummary = item['activities']
        itemRegion = item['geo']['region']
        print("Charity: {} \nCharity Commission ID: {}\nRegion: {} \
              \nDescription: \n{}\n".format(itemName, itemId, itemRegion, \
              itemSummary))
 
# Main code
findCharity('Malaria', 5) #Searches for cause Malaira 


effectiveCharities = ['Malaria Consortium','The Against Malaria Foundation'\
                      'The End Fund', 'Givedirectly']
