import requests
import base64
from django.shortcuts import render
#Clé API
PLANTNET_API_KEY = "2b10sQ5BTEgN5pHeiWL8HxPD"
PLANTID_API_KEY = "84scHUVBPHWAOBvJpzImw8I9Wx5u8mx6rnV80y19j9Pi8dJstg"

#Affiche la page d'upload
def upload(request):
    return render(request, "polls/upload.html")



def identify_plant(request):
    #Initialisation des variables
    is_healthy = None
    disease_name = None
    disease_probability = None
    disease_url = None
    #Vérification que la requête est une reqête POST
    if request.method == "POST":
        #Récupération de l'image
        image = request.FILES.get("image")
        #Aucune image envoyé = erreur
        if not image:
            return render(request, "polls/result.html", {"error": "Aucune image envoyée."})

        # URL de l'API Plant.id pour analyser la santé de la plante
        url_plantid = "https://plant.id/api/v3/health_assessment"
        headers = {"Api-Key": PLANTID_API_KEY}

        #Lecture de l'image et conversion en base64 (format requis par l'API)
        image_bytes = image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        #Données envoyés à l'API
        payload = {
            "images": [image_base64],
            "health": "all"
        }

        try:
            #Envoi de la requête POST
            response = requests.post(url_plantid, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            resultat = response.json()
            result = resultat.get("result", {})

            #Planet saine ou non ?(healthy ou non?)
            is_healthy = result.get("is_healthy")
            if isinstance(is_healthy, dict):
                is_healthy = is_healthy.get("binary")

            #Récupération des maladies s'il y'en a
            disease_suggestions = result.get("disease", {}).get("suggestions", [])
            if disease_suggestions:
                #nom de la maladie la plus probable
                disease_name = disease_suggestions[0].get("name")
                # Création d'un lien Wikipédia vers la maladie
                if disease_name:
                    disease_url = f"https://en.wikipedia.org/wiki/{disease_name.replace(' ', '_')}"
                # Probabilité de la maladie (convertie en pourcentage)
                disease_probability = round(
                    disease_suggestions[0].get("probability", 0) * 100, 2
                )

        except Exception as e:
            # Affichage de l'erreur dans la console
            print("Erreur Plant.id:", e)

        # On remet le fichier image au début pour pouvoir le réutiliser car sinon la première Api se fait écraser par la deuxième donc erreur
        image.seek(0)

        # URL de l'API PlantNet pour identifier la plante
        url_plantnet = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"
        files = {"images": image}

        try:
            # Envoi de l'image à PlantNet
            response = requests.post(url_plantnet, files=files, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Vérification que l'Api trouve des résultats
            if "results" not in data or len(data["results"]) == 0:
                return render(request, "polls/result.html", {"error": "Aucune plante trouvée."})
            # On garde les 3 meilleurs résultats que l'Api a trouvé
            results = data["results"][:3]
            for plant in results:
                # Conversion du score en pourcentage
                plant["score_percent"] = round(plant.get("score", 0) * 100, 2)
                name = plant.get("species", {}).get("scientificNameWithoutAuthor", "")

                #On essaie de récupérer une image depuis Wikipédia sur la maladie s'il y'en a une
                try:
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
                    res = requests.get(wiki_url, timeout=5)
                    wiki_data = res.json()
                    plant["image_url"] = wiki_data.get("thumbnail", {}).get("source")
                except:
                    # Si erreur, aucune image
                    plant["image_url"] = None
            # Envoi des résultats au template pour qu'il s'affiche
            return render(request, "polls/result.html", {
                "results": results,
                "best_match": data.get("bestMatch"),
                "health": is_healthy,
                "disease_name": disease_name,
                "disease_probability": disease_probability,
                "disease_url": disease_url,
            })
        # rencvoie s'il y a une erreurs liées avec PlantNet
        except Exception as e:
            return render(request, "polls/result.html", {"error": f"Erreur API PlantNet : {e}"})
    # Si ce n'est pas une requête POST, on affiche simplement la page d'upload
    return render(request, "polls/upload.html")