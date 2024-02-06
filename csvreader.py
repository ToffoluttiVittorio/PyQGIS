import pandas 
import requests

def replace_spaces_with_plus(input_string):
    """Replace spaces with plus in a given string."""
    return input_string.replace(' ', '+')

url = r'C:\Users\Formation\Documents\Vittorio\-_H5fVih.csv'

data = pandas.read_csv(url)

header1 = data.columns[0]

header2 = data.columns[1]

# print(data[header1][0])

# print(data.columns[0])

nb_lignes = data.shape[0]

attributes = []

for i in range(nb_lignes):
    # print(data[header1][i], data[header2][i])
    response = requests.get("https://api-adresse.data.gouv.fr/search/?q="+replace_spaces_with_plus(data[header1][i]))
    # print(response.status_code)
    response.json()
    attributes.append(response.json())
    print(attributes)
                      
    
    


# response = requests.get("https://api-adresse.data.gouv.fr/search/?q=8+bd+du+port&lat=48.789&lon=2.789")

# print(response.status_code)

# print(response.json())



# # Exemple d'utilisation :
# input_text = "Ceci est un exemple de texte avec des espaces"
# result = replace_spaces_with_plus(input_text)
# print(result)
