
import requests
from django.shortcuts import render
API_KEY = "2b10sQ5BTEgN5pHeiWL8HxPD"


# Page pour envoyer une image
def upload(request):
    return render(request, "polls/upload.html")



def identify_plant(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        url = "https://plant.id/api/v3/health_assessment"
        headers = {
            "Api-Key": "84scHUVBPHWAOBvJpzImw8I9Wx5u8mx6rnV80y19j9Pi8dJstg"}
        files = {
            "images": image}
        response = requests.post(url, headers=headers, files=files)
        print(response.status_code)
        print(response.text)
        resultat = response.json()
        health = resultat["result"]["is_healthy"]



    if request.method == "POST":

        # récupérer l'image envoyée
        image = request.FILES.get("image")

        if not image:
            return render(request, "polls/result.html", {
                "error": "Aucune image envoyée."
            })

        # URL de l'API Pl@ntNet
        url = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

        # envoyer l'image
        files = {
            "images": image
        }

        try:
            response = requests.post(url, files=files)
            data = response.json()

            print("STATUS :", response.status_code)
            print("REPONSE API :", data)

        except Exception as e:
            return render(request, "polls/result.html", {
                "error": f"Erreur API : {e}"
            })

        # vérifier si des résultats existent
        if "results" not in data or len(data["results"]) == 0:
            return render(request, "polls/result.html", {
                "error": "Aucune plante trouvée."
            })

        # prendre les 3 meilleurs résultats
        results = data["results"][:3]

        # transformer les scores en %
        for plant in results:
            plant["score_percent"] = round(plant["score"] * 100, 2)

        # envoyer au HTML
        return render(request, "polls/result.html", {
            "results": results,
            "best_match": data.get("bestMatch"),
            "health": health
        })

    # si accès direct à la page
    return render(request, "polls/upload.html")


def analyse_plante(request):
    if request.method == "POST"and request.FILES.get("image"):
        image = request.FILES["image"]
        url = "https://plant.id/api/v3/health_assessment"
        headers = {
            "Api-Key": "84scHUVBPHWAOBvJpzImw8I9Wx5u8mx6rnV80y19j9Pi8dJstg"}
        files = {
            "images": image}
        response = requests.post(url, headers=headers, files=files)
        print(response.status_code)
        print(response.text)
        resultat = response.json()
        health = resultat["result"]["is_healthy"]
        return render(request, "polls/result.html", {
            "health": health})
    return render(request, "result.html")


def identify_plant(request):
    health = None  # initialisation

    if request.method == "POST":
        image = request.FILES.get("image")
        if not image:
            return render(request, "polls/result.html", {"error": "Aucune image envoyée."})

        # Appel à Plant.id
        url_plantid = "https://plant.id/api/v3/health_assessment"
        headers = {"Api-Key": "84scHUVBPHWAOBvJpzImw8I9Wx5u8mx6rnV80y19j9Pi8dJstg"}
        files = {"images": image}
        response = requests.post(url_plantid, headers=headers, files=files)
        if response.status_code == 200:
            resultat = response.json()
            health = resultat.get("result", {}).get("is_healthy")

        # Appel à PlantNet
        url_plantnet = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"
        files = {"images": image}
        try:
            response = requests.post(url_plantnet, files=files)
            data = response.json()
        except Exception as e:
            return render(request, "polls/result.html", {"error": f"Erreur API : {e}"})

        if "results" not in data or len(data["results"]) == 0:
            return render(request, "polls/result.html", {"error": "Aucune plante trouvée."})

        results = data["results"][:3]
        for plant in results:
            plant["score_percent"] = round(plant["score"] * 100, 2)

        return render(request, "polls/result.html", {
            "results": results,
            "best_match": data.get("bestMatch"),
            "health": health
        })

    return render(request, "polls/upload.html")