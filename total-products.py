dict = {
'accessori-travestimento' : 124,
'bambole-dolls' : 100,
'biciclette' : 5,
'costumi' : 341,
'dinosauri' : 18,
'elettronica-per-bambini' : 17,
'giochi-creativi' : 19,
'giochi-da-esterno' : 79,
'giochi-da-tavolo' : 128,
'giochi-di-costruzione' : 55,
"giochi-d-imitazione" : 35,
"giochi-educativi" : 93,
"monopattini-pattini" : 56,
"occhiali-da-sole" : 32,
"peluche":18,
"personaggi" : 70,
"playset-da-gioco" : 24,
"prima-infanzia": 52,
"puzzle" : 11,
"veicoli-giocattolo" :216,
"zaini-trolley" : 78,
"prodotti-outlet" :10
}

# for k, v in dict.items():
#     k = k.lower().replace('-')
    # print(k.lower())
    # dict[k.capitalize().replace('-', ' ')']
total_value= sum(dict.values())
print(total_value)
