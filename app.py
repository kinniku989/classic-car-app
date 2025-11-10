from flask import Flask, render_template, redirect, url_for, jsonify, request
import json
import os

app = Flask(__name__)

# JSONファイルのパス
CARS_FILE = "cars.json"
FAVORITES_FILE = "favorites.json"

# ファイル読み込み
def load_json(filename):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

# ファイル保存S
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    """トップページ：車種モデルの一覧を表示"""
    cars = load_json(CARS_FILE)
    models = []
    seen_models = set()
    for car in cars:
        if car['model'] not in seen_models:
            models.append({
                'name': car['model'],
                'image': car['model_image'],
                'full_name': car['name'].split(' ')[0] + ' ' + car['name'].split(' ')[1] # 例: トヨタ スプリンタートレノ
            })
            seen_models.add(car['model'])
    return render_template("index.html", models=models)

@app.route("/model/<model_name>")
def cars_by_model(model_name):
    """車種別一覧ページ：特定のモデルの在庫車を表示"""
    all_cars = load_json(CARS_FILE)
    cars_for_model = [car for car in all_cars if car['model'] == model_name]
    
    favorites = load_json(FAVORITES_FILE)
    favorite_ids = [fav["id"] for fav in favorites]
    
    return render_template("cars_by_model.html", cars=cars_for_model, model_name=model_name, favorite_ids=favorite_ids)

@app.route("/car/<int:car_id>")
def car_detail(car_id):
    cars = load_json(CARS_FILE)
    car = next((c for c in cars if int(c["id"]) == car_id), None)
    if not car:
        return "車が見つかりません", 404

    favorites = load_json(FAVORITES_FILE)
    is_favorite = any(int(f["id"]) == car_id for f in favorites)
    return render_template("car_detail.html", car=car, is_favorite=is_favorite)

@app.route("/toggle_favorite/<int:car_id>")
def toggle_favorite(car_id):
    cars = load_json(CARS_FILE)
    car = next((c for c in cars if int(c["id"]) == car_id), None)
    if not car:
        return "車が見つかりません", 404

    favorites = load_json(FAVORITES_FILE)
    existing_ids = [f["id"] for f in favorites]

    if car_id in existing_ids:
        favorites = [f for f in favorites if f["id"] != car_id]
    else:
        favorites.append(car)

    save_json(FAVORITES_FILE, favorites)
    
    # どのページから来たかに応じてリダイレクト先を切り替える
    referrer = request.referrer
    if referrer and 'favorites' in referrer:
        return redirect(url_for('favorites'))
    if referrer and f'/car/{car_id}' in referrer:
        return redirect(url_for('car_detail', car_id=car_id))
        
    return redirect(url_for('index'))


@app.route("/favorites")
def favorites():
    favorites = load_json(FAVORITES_FILE)
    favorite_ids = [fav["id"] for fav in favorites]
    return render_template("favorites.html", favorites=favorites, favorite_ids=favorite_ids)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    # favorites.jsonがなければ作成
    if not os.path.exists(FAVORITES_FILE):
        save_json(FAVORITES_FILE, [])
    app.run(debug=True)