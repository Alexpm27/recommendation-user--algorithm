from flask import Flask, request, jsonify
import requests
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import random

app = Flask(__name__)

verify = 'http://Sortir-load-balancer-391724916.us-east-1.elb.amazonaws.com/match-service/like/verify/{userId}/{likedUserId}'


def verify_like(user_id, liked_user_id):
    urlv = verify.format(userId=user_id, likedUserId=liked_user_id)
    try:
        responsev = requests.get(urlv)
        if responsev.status_code == 200:
            return responsev.text.lower() == 'true'
        else:
            return False
    except requests.RequestException as e:
        print(f"Error al verificar el like: {e}")
        return False


@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    city = request.args.get('city', '1')
    user_id = int(request.args.get('user_id', 1))

    url = f'http://Sortir-load-balancer-391724916.us-east-1.elb.amazonaws.com/user/users/{city}'
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Error al obtener los datos de usuarios'}), response.status_code

    data = response.json()

    if not data.get('success', False):
        return jsonify({'error': 'Error en la respuesta del servicio de usuarios'}), 500

    users = data.get('data', [])

    profile = defaultdict(str)
    user_details = {}

    for user in users:
        perfil = []
        for interest in user.get('interests', []):
            perfil.append(interest.get('description', ''))
            #perfil.extend(interest.get('activities', []))
        profile[user['id']] = ' '.join(perfil)
        user_details[user.get('id')] = user

    vectorizer = TfidfVectorizer()
    perfil_matrix = vectorizer.fit_transform(profile.values())

    similaridades = cosine_similarity(perfil_matrix)

    similaridades_dict = {}
    for i, user in enumerate(users):
        similaridades_dict[user['id']] = {
            users[j]['id']: float(round(similaridades[i, j], 2)) for j in range(len(users)) if i != j
        }

    if user_id not in similaridades_dict:
        return jsonify({'error': f'Usuario {user_id} no encontrado.'}), 404

    recommendations = []
    for liked_user_id, similarity in similaridades_dict[user_id].items():
        if similarity >= 0.10 and not verify_like(user_id, liked_user_id):
            recommended_user = user_details[liked_user_id]
            recommended_user['similitud'] = similarity
            recommendations.append(recommended_user)

    random.shuffle(recommendations)
    return jsonify({'recommendations': recommendations})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
