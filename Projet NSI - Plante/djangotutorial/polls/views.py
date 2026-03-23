import requests
import base64
from django.shortcuts import render

PLANTNET_API_KEY = "2b10sQ5BTEgN5pHeiWL8HxPD"
PLANTID_API_KEY = "84scHUVBPHWAOBvJpzImw8I9Wx5u8mx6rnV80y19j9Pi8dJstg"


def upload(request):
    return render(request, "polls/upload.html")



def identify_plant(request):
    is_healthy = None
    disease_name = None
    disease_probability = None
    disease_url = None

    if request.method == "POST":
        image = request.FILES.get("image")

        if not image:
            return render(request, "polls/result.html", {"error": "Aucune image envoyée."})


        url_plantid = "https://plant.id/api/v3/health_assessment"
        headers = {"Api-Key": PLANTID_API_KEY}


        image_bytes = image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "images": [image_base64],
            "health": "all"
        }

        try:
            response = requests.post(url_plantid, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            resultat = response.json()
            result = resultat.get("result", {})


            is_healthy = result.get("is_healthy")
            if isinstance(is_healthy, dict):
                is_healthy = is_healthy.get("binary")


            disease_suggestions = result.get("disease", {}).get("suggestions", [])
            if disease_suggestions:
                disease_name = disease_suggestions[0].get("name")

                if disease_name:
                    disease_url = f"https://en.wikipedia.org/wiki/{disease_name.replace(' ', '_')}"

                disease_probability = round(
                    disease_suggestions[0].get("probability", 0) * 100, 2
                )

        except Exception as e:
            print("Erreur Plant.id:", e)



        image.seek(0)


        url_plantnet = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"
        files = {"images": image}

        try:
            response = requests.post(url_plantnet, files=files, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "results" not in data or len(data["results"]) == 0:
                return render(request, "polls/result.html", {"error": "Aucune plante trouvée."})

            results = data["results"][:3]
            for plant in results:
                plant["score_percent"] = round(plant.get("score", 0) * 100, 2)
                name = plant.get("species", {}).get("scientificNameWithoutAuthor", "")


                try:
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name}"
                    res = requests.get(wiki_url, timeout=5)
                    wiki_data = res.json()
                    plant["image_url"] = wiki_data.get("thumbnail", {}).get("source")
                except:
                    plant["image_url"] = None

            return render(request, "polls/result.html", {
                "results": results,
                "best_match": data.get("bestMatch"),
                "health": is_healthy,
                "disease_name": disease_name,
                "disease_probability": disease_probability,
                "disease_url": disease_url,
            })

        except Exception as e:
            return render(request, "polls/result.html", {"error": f"Erreur API PlantNet : {e}"})

    return render(request, "polls/upload.html")