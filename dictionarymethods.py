import requests
import json



def meaning(query : str):
    try:
        URL = f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}"
        results = requests.get(URL).json()

        main_list = []
        for result in results:

            word = result['word']
            meaning_dict = result['meanings']
    
            for definitions in meaning_dict:

                single_defs = definitions['definitions']
                for num_of_meanings in single_defs:
                    final_meaning = num_of_meanings['definition']
                    main_list.append(final_meaning)

        return main_list

    except:
        error_message = ['Couldnt find that meaning!']
        return error_message

